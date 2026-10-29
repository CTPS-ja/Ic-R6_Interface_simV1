# Icom CI-V プロトコル エンコーダー / デコーダー
# プレリアブル: FE FE, 相手アドレス, 自アドレス, コマンド, [サブコマンド], データ..., FD

class CIVProtocol:
    PREAMBLE = b'\xFE\xFE'
    EOD = b'\xFD'
    ICR6_ADDR = 0x7E
    CONTROLLER_ADDR = 0xE0

    @staticmethod
    def encode_bcd(value: int, length: int) -> bytes:
        """整数をBCDコードに変換 (例: 118200000 -> 00 00 82 11 01 のようなIC-R6周波数表現)"""
        s = f"{value:0{length*2}d}"
        bcd = bytearray()
        for i in range(len(s) - 2, -1, -2):
            high = int(s[i])
            low = int(s[i+1])
            bcd.append((high << 4) | low)
        return bytes(bcd)

    @staticmethod
    def decode_bcd(data: bytes) -> int:
        """BCDコードを整数に変換"""
        val = 0
        mul = 1
        for b in data:
            high = (b >> 4) & 0x0F
            low = b & 0x0F
            val += (high * 10 + low) * mul
            mul *= 100
        return val

    @classmethod
    def build_response(cls, cmd: int, subcommand=None, data: bytes = b'') -> bytes:
        packet = bytearray()
        packet.extend(cls.PREAMBLE)
        packet.append(cls.CONTROLLER_ADDR)
        packet.append(cls.ICR6_ADDR)
        packet.append(cmd)
        if subcommand is not None:
            packet.append(subcommand)
        packet.extend(data)
        packet.extend(cls.EOD)
        return bytes(packet)

    @classmethod
    def build_ack(cls) -> bytes:
        return cls.build_response(0xFB) # ACK

    @classmethod
    def build_nak(cls) -> bytes:
        return cls.build_response(0xFA) # NAK
