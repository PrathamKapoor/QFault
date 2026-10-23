"""A public media flag cannot substitute for source-bound, unchanged capture bytes."""
import importlib
import json
import pytest


def producer():
    try:m=importlib.import_module('scripts.prepare_release_assets')
    except ModuleNotFoundError:m=None
    assert m is not None, 'deliberate public demo asset selection is missing'
    return m


def test_recording_from_another_source_is_not_relabelled(tmp_path):
    m=producer();(tmp_path/'recording.json').write_text(json.dumps({'source_commit':'a'*40}))
    with pytest.raises(ValueError,match='source'):
        m.make_demo_archive(tmp_path,tmp_path/'public.zip','b'*40)
    assert not (tmp_path/'public.zip').exists()


def test_embedded_playback_success_does_not_override_changed_media_bytes(tmp_path):
    m=producer();source='a'*40
    (tmp_path/'recording.json').write_text(json.dumps({'source_commit':source,'media':'guided-demo-silent.webm','sha256':'0'*64}))
    (tmp_path/'playback-verification.json').write_text(json.dumps({'source_commit':source,'valid':True,'sha256':'0'*64}))
    (tmp_path/'guided-demo-silent.webm').write_bytes(b'Changed recording')
    with pytest.raises(ValueError,match='digest'):
        m.make_demo_archive(tmp_path,tmp_path/'public.zip',source)
    assert not (tmp_path/'public.zip').exists()
