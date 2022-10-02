import os
import threading
from lib.packet import Packet
from socket import AF_INET, SOCK_DGRAM, socket
from lib.blocking_queue import BlockingQueue
from lib.stop_and_wait_manager import StopAndWaitDownloaderManager, StopAndWaitUploaderManager, OldPacketReceivedError
from upload import READ_BUFFER

BUCKET_DIRECTORY = "src/server/files/"


class ClientWorker(threading.Thread):
    TIMEOUT = 3
    READ_BUFFER = 1024

    def __init__(self, blocking_queue, client_address, file_name, logger, is_upload):
        self.file = None
        self.packet_number = 0
        self.is_upload = is_upload
        self.address = client_address
        self.logger = logger
        self.file_name = file_name
        self.blocking_queue = blocking_queue
        output_socket = socket(AF_INET, SOCK_DGRAM)
        input_stream = BlockingQueue(blocking_queue)
        self.protocol = StopAndWaitDownloaderManager(output_socket, input_stream, client_address, logger) \
            if is_upload else StopAndWaitUploaderManager(output_socket, input_stream, client_address, logger)
        threading.Thread.__init__(self)


    def run(self):
        if self.is_upload:
            self.file = open(f"%s{self.file_name}" % BUCKET_DIRECTORY, "wb")
            self.protocol.send_ack(0)
            self.download_file()
        else:
            self.file = open(f"%s{self.file_name}" % BUCKET_DIRECTORY, "rb")
            self.protocol.send_ack(0)
            self.upload_file()


    def download_file(self):
        payload = 1
        while payload:
            try:
                payload = self.protocol.download_data()
                self.logger.info(f"received payload from {self.address}")
                self.file.write(payload)
            except OldPacketReceivedError:
                self.logger.info("Old packet received")
            except Exception as e:
                self.logger.info(e)
                self.file.close()
                os.remove(self.file_name) # TODO recibir ruta completa
                self.logger.info("exception ocurred, incomplete file removes")

        self.logger.info("Upload complete!")
        self.file.close()

    def upload_file(self):
        data = self.file.read(READ_BUFFER)
        while data:
            self.protocol.upload_data(data, self.file_name)
            data = self.file.read(READ_BUFFER)

        self.protocol.finish_connection(self.file_name)
        self.logger.info("Download complete!")

    def put(self, packet):
        self.blocking_queue.put(packet)
