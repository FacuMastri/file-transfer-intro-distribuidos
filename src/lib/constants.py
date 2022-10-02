SAW_PROTOCOL = "saw"
GBN_PROTOCOL = "gbn"


DEFAULT_SERVER_PORT = 12000
DEFAULT_SERVER_ADDRESS = "127.0.0.1"
DEFAULT_PROTOCOL = SAW_PROTOCOL

# Para el socket, server y la queue
TIMEOUT = 0.5
# Cantidad de reintentos para los protocolos
RETRIES = 20

# Buffers varios
BUFFER_RECV_SOCKET = 4096
READ_BUFFER = 1024


# Green
COLOR_UPLOAD = "\033[0;32m"
END_COLOR = "\033[0m"
# Blue
COLOR_DOWNLOAD = "\033[0;34m"
