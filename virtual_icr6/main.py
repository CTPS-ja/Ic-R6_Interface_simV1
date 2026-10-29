import socket
import threading
import time
from .config import DEFAULT_HOST, DEFAULT_PORT
from .radio_state import RadioState
from .civ import CIVProtocol
from .console import cli_console, start_demo_loop

radio = RadioState()
stop_event = threading.Event()

def handle_client(conn, addr):
    print(f"[IC-R6] Client connected from {addr}")
    buffer = bytearray()
    while not stop_event.is_set():
        try:
            chunk = conn.recv(1024)
            if not chunk:
                break
            buffer.extend(chunk)

            # CI-Vフレーム解析 (FE FE ... FD)
            while True:
                start_idx = buffer.find(b'\xFE\xFE')
                if start_idx == -1:
                    break
                end_idx = buffer.find(b'\xFD', start_idx)
                if end_idx == -1:
                    break # フレーム未完

                frame = buffer[start_idx:end_idx+1]
                del buffer[:end_idx+1] # バッファから消化

                print(f"[CI-V RX] {frame.hex(' ').upper()}")

                # Fault Injectionの処理
                if radio.fault_mode == "timeout":
                    print("[FAULT] Timeout triggered: ignoring packet")
                    continue
                elif radio.fault_mode == "nak":
                    print("[FAULT] NAK triggered: sending NAK")
                    conn.sendall(CIVProtocol.build_nak())
                    continue

                # コマンド解析 (簡易実装)
                # 0x00: 周波数取得, 0x05: 周波数設定, 0x03: モード取得, 0x06: モード設定 等
                if len(frame) >= 5:
                    cmd = frame[4]
                    response = b''

                    if cmd == 0x00: # Read Frequency
                        freq_bcd = CIVProtocol.encode_bcd(radio.get("frequency"), 5)
                        response = CIVProtocol.build_response(0x00, data=freq_bcd)
                    elif cmd == 0x05: # Set Frequency (データ部がBCD)
                        if len(frame) >= 11:
                            f_val = CIVProtocol.decode_bcd(frame[5:10])
                            radio.set("frequency", f_val)
                            response = CIVProtocol.build_ack()
                    elif cmd == 0x03: # Read Mode
                        m = radio.get("mode")
                        m_code = b'\x01' if m == "AM" else (b'\x00' if m == "FM" else b'\x02')
                        response = CIVProtocol.build_response(0x03, data=m_code)
                    elif cmd == 0x06: # Set Mode
                        if len(frame) >= 7:
                            code = frame[5]
                            m_str = "AM" if code == 1 else ("FM" if code == 0 else "WFM")
                            radio.set("mode", m_str)
                            response = CIVProtocol.build_ack()
                    elif cmd == 0x14: # Other reads/writes (Squelch, Volume, ATT等)
                        if len(frame) >= 7:
                            sub = frame[5]
                            if sub == 0x0e: # Squelch read
                                sql_bcd = CIVProtocol.encode_bcd(radio.get("squelch"), 2)
                                response = CIVProtocol.build_response(0x14, subcommand=0x0e, data=sql_bcd)
                            elif sub == 0x01: # Volume read
                                vol_bcd = CIVProtocol.encode_bcd(radio.get("volume"), 2)
                                response = CIVProtocol.build_response(0x14, subcommand=0x01, data=vol_bcd)
                            elif sub == 0x02: # S-Meter read
                                sig_bcd = CIVProtocol.encode_bcd(radio.get("signal_strength"), 2)
                                response = CIVProtocol.build_response(0x14, subcommand=0x02, data=sig_bcd)
                            elif sub == 0x16: # ATT read
                                att_val = b'\x01' if radio.get("attenuator") else b'\x00'
                                response = CIVProtocol.build_response(0x14, subcommand=0x16, data=att_val)
                            else:
                                response = CIVProtocol.build_ack()
                    else:
                        response = CIVProtocol.build_ack()

                    if response:
                        time.sleep(0.01)
                        conn.sendall(response)
                        print(f"[CI-V TX] {response.hex(' ').upper()}")

        except Exception as e:
            print(f"[IC-R6] Connection error: {e}")
            break
    conn.close()
    print("[IC-R6] Client disconnected")

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((DEFAULT_HOST, DEFAULT_PORT))
    server.listen(1)
    print(f"[IC-R6] Simulator started on {DEFAULT_HOST}:{DEFAULT_PORT}")

    while not stop_event.is_set():
        try:
            server.settimeout(1.0)
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
        except socket.timeout:
            continue
        except Exception:
            break
    server.close()

if __name__ == "__main__":
    t_server = threading.Thread(target=run_server, daemon=True)
    t_server.start()

    t_demo = threading.Thread(target=start_demo_loop, args=(radio,), daemon=True)
    t_demo.start()

    cli_console(radio, stop_event)
