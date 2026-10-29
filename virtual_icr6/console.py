import sys
import threading
import time

def cli_console(radio, server_stop_event):
    print("\n[Virtual IC-R6 CLI] Ready. Type 'help' for commands.")
    while not server_stop_event.is_set():
        try:
            line = input("IC-R6> ").strip()
            if not line:
                continue
            parts = line.split()
            cmd = parts[0].lower()

            if cmd == "help":
                print("Commands: status, freq <hz>, mode <AM|FM|WFM>, sql <0-255>, sqlstate <open|closed>,")
                print("          signal <0-255>, volume <0-255>, att <on|off>, demo <start|stop>,")
                print("          fault <off|timeout|nak>, quit")
            elif cmd == "status":
                print(radio.get_status_dict())
            elif cmd == "freq" and len(parts) > 1:
                radio.set("frequency", int(parts[1]))
                print(f"Frequency set to {radio.get('frequency')} Hz")
            elif cmd == "mode" and len(parts) > 1:
                m = parts[1].upper()
                if m in ["AM", "FM", "WFM"]:
                    radio.set("mode", m)
                    print(f"Mode set to {m}")
                else:
                    print("Invalid mode. Use AM, FM, WFM")
            elif cmd == "sql" and len(parts) > 1:
                radio.set("squelch", int(parts[1]))
                radio.update_sql_state()
                print(f"Squelch set to {radio.get('squelch')}")
            elif cmd == "sqlstate" and len(parts) > 1:
                st = parts[1].lower()
                radio.state["squelch_open"] = (st == "open")
                print(f"SQL State set to {radio.get('squelch_open')}")
            elif cmd == "signal" and len(parts) > 1:
                radio.set("signal_strength", int(parts[1]))
                radio.update_sql_state()
                print(f"Signal Strength set to {radio.get('signal_strength')}")
            elif cmd == "volume" and len(parts) > 1:
                radio.set("volume", int(parts[1]))
                print(f"Volume set to {radio.get('volume')}")
            elif cmd == "att" and len(parts) > 1:
                att_val = (parts[1].lower() == "on")
                radio.set("attenuator", att_val)
                print(f"ATT set to {att_val}")
            elif cmd == "demo" and len(parts) > 1:
                sub = parts[1].lower()
                if sub == "start":
                    radio.demo_running = True
                    print("Demo Mode STARTED")
                elif sub == "stop":
                    radio.demo_running = False
                    print("Demo Mode STOPPED")
            elif cmd == "fault" and len(parts) > 1:
                f_type = parts[1].lower()
                if f_type in ["off", "timeout", "nak"]:
                    radio.fault_mode = f_type
                    print(f"Fault Mode set to {f_type}")
                else:
                    print("Available faults: off, timeout, nak")
            elif cmd == "quit":
                print("Exiting...")
                server_stop_event.set()
                sys.exit(0)
            else:
                print(f"Unknown command: {line}")
        except Exception as e:
            print(f"CLI Error: {e}")

def start_demo_loop(radio):
    # デモモード時の信号変動パターン
    pattern = [20, 30, 60, 100, 150, 200, 160, 100, 50, 20]
    idx = 0
    while True:
        if radio.demo_running:
            sig = pattern[idx]
            radio.set("signal_strength", sig)
            radio.update_sql_state()
            idx = (idx + 1) % len(pattern)
        time.sleep(1.5)
