import asyncio
import socket
from .civ import CIVClientProtocol

class RadioController:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.connected = False
        
        self.state = {
            "frequencyHz": 118200000,
            "mode": "AM",
            "squelch": 45,
            "squelchOpen": False,
            "signalStrength": 80,
            "volume": 80,
            "attenuator": False,
            "connected": False
        }

    async def connect(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.connected = True
            self.state["connected"] = True
            print("[ESP32] Connected to Virtual IC-R6")
        except Exception as e:
            self.connected = False
            self.state["connected"] = False
            print(f"[ESP32] Connection failed: {e}")

    async def send_command(self, cmd_bytes):
        if not self.connected or not self.writer:
            await self.connect()
            if not self.connected:
                return None
        try:
            self.writer.write(cmd_bytes)
            await self.writer.drain()
            print(f"[CI-V TX] {cmd_bytes.hex(' ').upper()}")
            
            # 応答読み取り（タイムアウト付き）
            data = await asyncio.wait_for(self.reader.read(1024), timeout=0.8)
            if not data:
                raise ConnectionResetError("Connection closed by peer")
            print(f"[CI-V RX] {data.hex(' ').upper()}")
            return data
        except (asyncio.TimeoutError, Exception) as e:
            print(f"[ESP32] Communication timeout or error: {e}")
            self.connected = False
            self.state["connected"] = False
            return None

    def decode_bcd(self, data: bytes) -> int:
        val = 0
        mul = 1
        for b in data:
            high = (b >> 4) & 0x0F
            low = b & 0x0F
            val += (high * 10 + low) * mul
            mul *= 100
        return val

    async def poll_status(self):
        while True:
            if self.connected:
                # 周波数取得
                resp = await self.send_command(b'\xFE\xFE\x7E\xE0\x00\xFD')
                if resp and len(resp) >= 11:
                    self.state["frequencyHz"] = self.decode_bcd(resp[5:10])

                # モード取得
                resp = await self.send_command(b'\xFE\xFE\x7E\xE0\x03\xFD')
                if resp and len(resp) >= 7:
                    code = resp[5]
                    self.state["mode"] = "AM" if code == 1 else ("FM" if code == 0 else "WFM")

                # Sメータ取得
                resp = await self.send_command(b'\xFE\xFE\x7E\xE0\x14\x02\xFD')
                if resp and len(resp) >= 8:
                    sig = self.decode_bcd(resp[6:8])
                    self.state["signalStrength"] = sig
                    # スケルチ開閉簡易判定
                    threshold = (self.state["squelch"] / 255.0) * 150 + 20
                    self.state["squelchOpen"] = (sig >= threshold)

                self.state["connected"] = True
            else:
                await self.connect()
            await asyncio.sleep(1.0)

    async def set_freq(self, freq: int):
        cmd = CIVClientProtocol.create_set_frequency(freq)
        await self.send_command(cmd)
        self.state["frequencyHz"] = freq

    async def set_mode(self, mode: str):
        cmd = CIVClientProtocol.create_set_mode(mode)
        await self.send_command(cmd)
        self.state["mode"] = mode

    async def set_squelch(self, val: int):
        s = f"{val:04d}"
        bcd = bytearray()
        for i in range(len(s)-2, -1, -2):
            bcd.append((int(s[i]) << 4) | int(s[i+1]))
        cmd = bytearray(b'\xFE\xFE\x7E\xE0\x14\x0E')
        cmd.extend(bcd)
        cmd.append(0xFD)
        await self.send_command(bytes(cmd))
        self.state["squelch"] = val
