from .config import INITIAL_STATE

class RadioState:
    def __init__(self):
        self.state = INITIAL_STATE.copy()
        self.demo_running = False
        self.fault_mode = "off" # off, timeout, nak

    def get(self, key):
        return self.state.get(key)

    def set(self, key, value):
        self.state[key] = value
        # スケルチ開閉の簡易連動（デモモード外での手動変更時などの判定）
        if key == "signal_strength" or key == "squelch":
            self.update_sql_state()

    def update_sql_state(self):
        # シグナルがスケルチ設定値（簡易換算）を超えたらOPEN
        threshold = (self.state["squelch"] / 255.0) * 150 + 20
        if self.state["signal_strength"] >= threshold:
            self.state["squelch_open"] = True
        else:
            self.state["squelch_open"] = False

    def get_status_dict(self):
        return self.state
