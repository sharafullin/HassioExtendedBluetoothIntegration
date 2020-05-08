from . import discover, configure

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Discover ha-rpi-bt-ext devices."""
    devices = []

    hubs = discover()    

    mqtt_ip = config[CONF_MQTT][CONF_BROKER]

    dev_configs = []
    for hub in hubs:
        dev_configs += configure(hub, mqtt_ip)
