# 初期状態および設定
ICR6_ADDRESS = 0x7E
CONTROLLER_ADDRESS = 0xE0
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7600

INITIAL_STATE = {
    "frequency": 118200000,  # 118.200000 MHz (Hz単位)
    "mode": "AM",            # AM, FM, WFM
    "squelch": 45,           # 0 - 255
    "squelch_open": False,
    "signal_strength": 80,   # 0 - 255
    "volume": 80,            # 0 - 255
    "attenuator": False,     # True / False
    "connected": True
}
