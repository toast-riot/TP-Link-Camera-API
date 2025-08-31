from .client import TPLinkIPCClient
from . import api_types

class TPLinkIPC():
    def __init__(self, url: str, username: str = None, password: str = None):
        self._client = TPLinkIPCClient(url, username, password)
        self._client.login()

    # chances are, these will not be available for all devices
    # there are methods for retrieving available features, but I haven't implemented them
    class NightVisionMode:
        HUMAN_TRIGGERED_COLOR = "human_triggered_color"
        AUTO_COLOR = "auto_color"
        AUTO_IR = "auto_ir"
        WHITE_LED_ALWAYS_ON = "white_led_always_on"
        IR_ALWAYS_ON = "ir_always_on"
        OFF = "off"
        CUSTOM = "custom"

    night_vision_mode = api_types.BasicValue("_client", ("image", "switch", "pre_night_vision_mode"), ("image", "switch"))