from virtual_icr6.civ import CIVProtocol
from virtual_esp32.civ import CIVClientProtocol

def test_bcd_encoding():
    # 118200000 Hz のBCD表現テスト
    bcd = CIVProtocol.encode_bcd(118200000, 5)
    assert len(bcd) == 5
    decoded = CIVProtocol.decode_bcd(bcd)
    assert decoded == 118200000

def test_civ_frames():
    resp = CIVProtocol.build_ack()
    assert resp.startswith(b'\xFE\xFE')
    assert resp.endswith(b'\xFD')
