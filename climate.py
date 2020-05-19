import logging
import json
from .helpers.discovery import discover, configure

CONF_MQTT = "mqtt"
CONF_BROKER = "broker"

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Discover ha-rpi-bt-ext devices."""
    devices = []
    _LOGGER.warning('test')
    hubs = discover(_LOGGER)    
    _LOGGER.warning('discovered')
    _LOGGER.warning(hubs)

    c = json.dumps(config[CONF_MQTT])

    for hub in hubs:
        configure(hub, c, _LOGGER)

    return True