import pytest

from workbench.srt import SrtError, dump_srt, format_time, parse_srt, parse_time, validate_non_overlapping


SAMPLE = """\ufeff1
00:00:01,000 --> 00:00:03,500
大小姐，你回来了。

2
00:00:04,000 --> 00:00:06,000
我不是你的大小姐。
"""


def test_parse_basic_and_bom():
    cues = parse_srt(SAMPLE)
    assert len(cues) == 2
    assert cues[0].start == pytest.approx(1.0)
    assert cues[0].end == pytest.approx(3.5)
    assert cues[1].text == "我不是你的大小姐。"


def test_roundtrip_time_format():
    assert format_time(3661.255) == "01:01:01,255"
    assert parse_time("01:01:01,255") == pytest.approx(3661.255)


def test_dump_then_parse_roundtrip():
    cues = parse_srt(SAMPLE)
    again = parse_srt(dump_srt(cues))
    assert [(c.start, c.end, c.text) for c in cues] == [(c.start, c.end, c.text) for c in again]


def test_end_before_start_rejected():
    with pytest.raises(SrtError):
        parse_srt("1\n00:00:05,000 --> 00:00:04,000\nbad\n")


def test_overlap_detected():
    cues = parse_srt("1\n00:00:01,000 --> 00:00:05,000\na\n\n2\n00:00:04,000 --> 00:00:06,000\nb\n")
    with pytest.raises(SrtError):
        validate_non_overlapping(cues)


def test_crlf_input():
    cues = parse_srt("1\r\n00:00:00,000 --> 00:00:01,000\r\n你好\r\n")
    assert cues[0].text == "你好"
