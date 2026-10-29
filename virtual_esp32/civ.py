class CIVClientProtocol:
    @staticmethod
    def create_read_frequency():
        return b'\xFE\xFE\x7E\xE0\x00\xFD'

    @staticmethod
    def create_set_frequency(freq_hz: int):
        s = f"{freq_hz:010d}"
        bcd = bytearray()
        for i in range(len(s)-2, -1, -2):
            high = int(s[i])
            low = int(s[i+1])
            bcd.append((high << 4) | low)
        packet = bytearray(b'\xFE\xFE\x7E\xE0\x05')
        packet.extend(bcd)
        packet.append(0xFD)
        return bytes(packet)

    @staticmethod
    def create_set_mode(mode_str: str):
        code = 1 if mode_str == "AM" else (0 if mode_str == "FM" else 2)
        return bytes([0xFE, 0xFE, 0x7E, 0xE0, 0x06, code, 0xFD])

    @staticmethod
    def create_read_status_batch():
        # 定期ポーリング用のコマンド群
        return [
            b'\xFE\xFE\x7E\xE0\x00\xFD',                    # Freq
            b'\xFE\xFE\x7E\xE0\x03\xFD',                    # Mode
            b'\xFE\xFE\x7E\xE0\x14\x0E\xFD',                # Squelch
            b'\xFE\xFE\x7E\xE0\x14\x02\xFD',                # S-Meter
            b'\xFE\xFE\x7E\xE0\x14\x01\xFD',                # Volume
            b'\xFE\xFE\x7E\xE0\x14\x16\xFD',                # ATT
        ]
