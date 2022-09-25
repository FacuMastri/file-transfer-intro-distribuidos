class Packet:
    """
    Header size = 6 bytes
    Estructura del paquete
    4 bytes para el numero de paquete
    1 bit si es upload o download
    1 bit de terminado
    1 bit esto es un ACK
    2 bit de codigo de error:  00 - nombre repetido, 01 - todo ok, 10 - reservado uso futuro, 11 - reservado uso futuro
    1 bit de SYN
    2 bit para version de protocolo
    1 byte para el largo del filename
    El resto para el payload
    """

    HEADER_SIZE = 6

    def __init__(
        self,
        packet_number: int,
        is_upload: bool,
        finished: bool,
        ack: bool,
        syn: bool,
        status_code: int,
        version: int,
        filename: str,
        payload: bytes,
    ):
        self.packet_number = packet_number
        self.is_upload = is_upload
        self.finished = finished
        self.ack = ack
        self.syn = syn
        self.status_code = status_code
        self.version = version
        self.filename = filename
        self.payload = payload

    def to_bytes(self) -> bytes:
        flags = 0b0000_0000
        if self.is_upload:
            flags |= 0b1000_0000
        if self.finished:
            flags |= 0b0100_0000
        if self.ack:
            flags |= 0b0010_0000
        if self.syn:
            flags |= 0b0001_0000
        # Si 1 error generico
        if self.status_code == 1:
            flags |= 0b0000_0100
        if self.version == 1:
            flags |= 0b0000_0001

        packet = (
            self.packet_number.to_bytes(4, "big")
            + flags.to_bytes(1, "big")
            + len(self.filename).to_bytes(1, "big")
            + bytes(self.filename, "utf-8")
            + self.payload
        )
        return packet

    @staticmethod
    def ack_packet(packetnumber):
        # TODO agregar el numero de paquete para validar lo de la perdida de ACKs en vuelo

        packet = packetnumber.to_bytes(4, "big") + bytes([32, 0])
        return packet

    @staticmethod
    def from_bytes(bytes):
        packet_number: int = int.from_bytes(bytes[0:4], "big")
        flags: int = bytes[4]
        # filename_length máximo es 255 caracteres (1 byte)
        filename_length: int = bytes[5]
        filename: str = bytes[6 : 6 + filename_length].decode("utf-8")
        payload: bytes = bytes[6 + filename_length :]
        is_upload = False
        finished = False
        ack = False
        syn = False
        status_code = 0

        if (flags & 0b1000_0000) >> 7:
            is_upload = True
        if (flags & 0b0100_0000) >> 6:
            finished = True
        if (flags & 0b0010_0000) >> 5:
            ack = True
        if (flags & 0b0001_0000) >> 4:
            syn = True

        status_code = int((flags & 0b0000_1100) >> 2)
        version = int(flags & 0b0000_0011)

        return Packet(
            packet_number,
            is_upload,
            finished,
            ack,
            syn,
            status_code,
            version,
            filename,
            payload,
        )

    def size(self) -> int:
        return len(self.payload) + len(self.filename) + self.HEADER_SIZE

    def __str__(self):
        return "packet_number: {}, ack: {}, len(payload): {}".format(
            self.packet_number, self.ack, len(self.payload)
        )
