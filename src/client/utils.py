def construct_packet(
    packet_number: int, filename: str, total_packets: int, payload: bytes
):
    """
    Estructura del paquete
    4 bytes para el numero de paquete
    4 bytes para el numero total de paquetes
    4 bytes para el largo del filename
    El resto de bytes para la data del archivo enviado
    """
    packet_number = packet_number.to_bytes(4, "big")
    total_packets = total_packets.to_bytes(4, "big")
    filename_length = len(filename).to_bytes(4, "big")

    packet = (
        packet_number
        + total_packets
        + filename_length
        + bytes(filename, "utf-8")
        + payload
    )

    return packet
