import socket
import time

from multiprocessing import Process, Manager

from homeassistant.components.mqtt.climate import MqttClimate

CONF_MQTT = "mqtt"
CONF_BROKER = "broker"

PORT = 35224
DISCOVERY_MESSAGE = b"ha-rpi-bt-ext discovery"
DISCOVERED_MESSAGE = b'ha-rpi-bt-ext discovered'

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Discover ha-rpi-bt-ext devices."""
    devices = []

    hubs = discover()    

    mqtt_ip = config[CONF_MQTT][CONF_BROKER]

    dev_configs = []
    for hub in hubs:
        dev_configs += configure(hub, mqtt_ip)


def discover(logger):
    result = []
    with Manager() as manager:
        hubs = manager.list()
        discovery_listener_proc = Process(target=listen_discovery, args=(hubs,logger))
        discovery_listener_proc.start()

        broadcast_discovery(logger)

        time.sleep(5)
        discovery_listener_proc.terminate()
        discovery_listener_proc.join()

        result = hubs[:]
    
    return result


def configure(hub_ip, configuration, logger) -> str:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (hub_ip, PORT)
    sock.connect(server_address)
    try:
        # Send data
        sock.sendall(configuration.encode())

        # Look for the response

        data = sock.recv(1048576)
        logger.warning('returned:')
        logger.warning(data)
        
        return data
    finally:
        sock.close()


def broadcast_discovery(logger):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Enable port reusage so we will be able to run multiple clients and servers on single (host, port).
    # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
    # For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
    # So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
    # Thanks to @stevenreddie
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Enable broadcasting mode
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    server.settimeout(0.2)

    logger.warning("discovery started")
    for _ in range(3):
        server.sendto(DISCOVERY_MESSAGE, ("<broadcast>", PORT))
        logger.warning("discovery")
        time.sleep(0.1)
    logger.warning("discovery finished")


def listen_discovery(devices, logger):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP

    # Enable port reusage so we will be able to run multiple clients and servers on single (host, port).
    # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
    # For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
    # So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
    # Thanks to @stevenreddie
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    client.bind(("", PORT))
    logger.warning("discovery listening")

    while True:
        # Thanks @seym45 for a fix
        data, addr = client.recvfrom(1024)
        if data == DISCOVERED_MESSAGE and addr[0] not in devices:
            logger.warning("discovery received message")
            logger.warning(data)
            devices.append(addr[0])