def decode_packet(packet: bytes):
    packet_number: int = int.from_bytes(packet[0:4], "big")
    total_packets: int = int.from_bytes(packet[4:8], "big")
    filename_length: int = int.from_bytes(packet[8:12], "big")
    filename: str = packet[12 : 12 + filename_length].decode("utf-8")
    payload: bytes = packet[12 + filename_length :]

    return packet_number, total_packets, filename, payload
