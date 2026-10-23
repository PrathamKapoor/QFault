"""The release asset allowlist must reject accidental private contents and corruption."""
import hashlib
import importlib
import pytest


def tool():
    try:m=importlib.import_module('scripts.public_release')
    except ModuleNotFoundError:m=None
    assert m is not None, 'reviewed public release tooling is missing'
    return m


def test_checksums_bind_existing_files_and_do_not_discover_unlisted_runtime_data(tmp_path):
    m=tool();asset=tmp_path/'source.zip';asset.write_bytes(b'reviewed')
    checksum=hashlib.sha256(b'reviewed').hexdigest()
    (tmp_path/'SHA256SUMS').write_text(checksum+'  source.zip\n')
    (tmp_path/'private.db').write_bytes(b'Unlisted fixture; must not be discovered for upload')
    assert m.read_checksums(tmp_path)=={'source.zip':checksum}
    asset.write_bytes(b'changed')
    with pytest.raises(ValueError):m.read_checksums(tmp_path)


@pytest.mark.parametrize('name',['../private','/absolute','C:/private','nested/private','.env','source.zip\nextra'])
def test_checksum_member_names_cannot_escape_or_include_private_configuration(tmp_path,name):
    m=tool();(tmp_path/'SHA256SUMS').write_text('0'*64+'  '+name+'\n')
    with pytest.raises(ValueError):m.read_checksums(tmp_path)


def test_duplicate_checksum_names_fail(tmp_path):
    m=tool();(tmp_path/'source.zip').write_bytes(b'safe');h=hashlib.sha256(b'safe').hexdigest()
    (tmp_path/'SHA256SUMS').write_text((h+'  source.zip\n')*2)
    with pytest.raises(ValueError):m.read_checksums(tmp_path)
