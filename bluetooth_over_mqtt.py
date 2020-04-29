import socket
import time

from multiprocessing import Process, Manager


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Discover ha-rpi-bt-ext devices."""
    devices = []

    p1 = Process(target=listen_discovery, args=(devices,))
    p1.start()

    broadcast_discovery()

    for name, device_cfg in config[CONF_DEVICES].items():
        mac = device_cfg[CONF_MAC]
        devices.append(EQ3BTSmartThermostat(mac, name))

    add_entities(devices, True)

def test():
    devices = []
    with Manager() as manager:
        dev = manager.list()
        discovery_listener_proc = Process(target=listen_discovery, args=(dev,))
        discovery_listener_proc.start()

        broadcast_discovery()

        time.sleep(1)
        discovery_listener_proc.terminate()
        discovery_listener_proc.join()

        devices = dev[:]

    print(devices[:])


def broadcast_discovery():
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
    message = b"ha-rpi-bt-ext discovery"

    for _ in range(3):
        server.sendto(message, ("<broadcast>", 35224))
        time.sleep(0.1)


def listen_discovery(devices):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP

    # Enable port reusage so we will be able to run multiple clients and servers on single (host, port).
    # Do not use socket.SO_REUSEADDR except you using linux(kernel<3.9): goto https://stackoverflow.com/questions/14388706/how-do-so-reuseaddr-and-so-reuseport-differ for more information.
    # For linux hosts all sockets that want to share the same address and port combination must belong to processes that share the same effective user ID!
    # So, on linux(kernel>=3.9) you have to run multiple servers and clients under one user to share the same (host, port).
    # Thanks to @stevenreddie
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    client.bind(("", 35224))

    while True:
        # Thanks @seym45 for a fix
        data, addr = client.recvfrom(1024)
        if data == b'ha-rpi-bt-ext discovered' and addr[0] not in devices:
            devices.append(addr[0])


test()