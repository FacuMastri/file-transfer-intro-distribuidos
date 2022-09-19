from src.client.utils import construct_packet
from src.server.utils import decode_packet


def test_construct_packet():
    payload = bytes("esto es una prueba", "utf-8")
    packet = construct_packet(257, "prueba.txt", 50, payload)
    # Se puede imprimir
    print(packet)
    # Vemos el tipo
    print("Tipo de dato: " + str(type(packet)))
    # A mi me gusta ver los bytes en decimal
    print(list(packet))

    assert packet[0] == 0
    assert packet[1] == 0
    assert packet[2] == 1
    assert packet[3] == 1

    assert packet[4] == 0
    assert packet[5] == 0
    assert packet[6] == 0
    assert packet[7] == 50

    assert packet[8] == 0
    assert packet[9] == 0
    assert packet[10] == 0
    assert packet[11] == 10


def test_decode_packet():
    payload = bytes("estoy probando", "utf-8")
    packet = construct_packet(12, "una_prueba.txt", 2, payload)

    packet_number, total_packets, filename, payload = decode_packet(packet)

    print(f"Packet number: {packet_number}")
    print(f"Total packets: {total_packets}")
    print(f"Filename: {filename}")
    print(f"Payload: {payload.decode('utf-8')}")

    assert packet_number == 12
    assert total_packets == 2
    assert filename == "una_prueba.txt"
    assert payload.decode("utf-8") == "estoy probando"
