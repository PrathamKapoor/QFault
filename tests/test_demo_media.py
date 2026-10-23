"""Caption time boundaries must remain valid for genuine recorded playback."""
import importlib
import pytest


def module():
    try:result=importlib.import_module('scripts.record_guided_demo')
    except ModuleNotFoundError:result=None
    assert result is not None, 'genuine guided recording and caption support is missing'
    return result


def test_caption_timestamps_preserve_milliseconds_and_hour_rollover():
    m=module()
    assert m.stamp(62.345)=='00:01:02.345'
    assert m.stamp(3601.125)=='01:00:01.125'
    for invalid in (-1,float('nan'),float('inf')):
        with pytest.raises(ValueError):m.stamp(invalid)


def test_captions_reject_reversed_or_outside_recording_intervals():
    m=module()
    with pytest.raises(ValueError):m.captions([{'seconds':2,'text':'later'},{'seconds':1,'text':'earlier'}],3)
    with pytest.raises(ValueError):m.captions([{'seconds':4,'text':'outside'}],3)
    text=m.captions([{'seconds':0,'text':'Original source'},{'seconds':1.5,'text':'Measured evidence'}],3)
    assert '00:00:00.000 --> 00:00:01.500' in text
    assert '00:00:01.500 --> 00:00:03.000' in text
