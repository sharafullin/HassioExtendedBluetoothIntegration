import udp
from multiprocessing import Process

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Discover ha-rpi-bt-ext devices."""
    devices = []

    p1 = Process(target=udp.listen_discovery)
    p1.start()

    udp.broadcast_discovery()

    for name, device_cfg in config[CONF_DEVICES].items():
        mac = device_cfg[CONF_MAC]
        devices.append(EQ3BTSmartThermostat(mac, name))

    add_entities(devices, True)
