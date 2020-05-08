import logging
from .helpers.discovery import discover, configure

CONF_MQTT = "mqtt"
CONF_BROKER = "broker"

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Discover ha-rpi-bt-ext devices."""
    devices = []

    hubs = discover()    

    mqtt_ip = config[CONF_MQTT][CONF_BROKER]

    for hub in hubs:
        configure(hub, mqtt_ip, _LOGGER)

    return True