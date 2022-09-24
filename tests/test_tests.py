from src.lib.packet import Packet


def test_packet():
    payload = bytes("esto es una prueba", "utf-8")
    packet = Packet(12, 1, 0, 0, 0, 0, 1, "prueba.txt", payload)

    p_bytes = packet.to_bytes()
    # Se puede imprimir
    print(p_bytes)
    # Vemos el tipo
    print("Tipo de dato: " + str(type(p_bytes)))
    # A mi me gusta ver los bytes en decimal
    print(list(p_bytes))

    # 4 bytes para sequence number
    assert p_bytes[0] == 0
    assert p_bytes[1] == 0
    assert p_bytes[2] == 0
    assert p_bytes[3] == 12

    # Byte 6 para el largo del filename
    assert p_bytes[5] == 10

    packet = Packet.from_bytes(p_bytes)

    assert packet.filename == "prueba.txt"
    assert packet.payload == bytes("esto es una prueba", "utf-8")


def test_packet_no_name():
    payload = bytes("esto es una prueba", "utf-8")
    try:
        Packet(12, 1, 0, 0, 0, 0, 1, "", payload)
    except:
        assert True


def test_packet_size():
    payload = bytes("esto es una prueba", "utf-8")
    packet = Packet(12,  1, 0, 0, 0, 0, 1, "donald.jpeg", payload)

    assert packet.size() == 35
