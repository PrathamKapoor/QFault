import json
import subprocess
import zipfile
import hashlib
import struct

import pytest

from scripts import package_submission as packaging


def repository(tmp_path):
    repo = tmp_path / 'repo'
    repo.mkdir()
    def git(*args):
        return subprocess.run(['git', '-c', f'safe.directory={repo}', '-C', str(repo), *args], check=True, capture_output=True)
    git('init', '-b', 'main')
    git('config', 'user.name', 'PrathamKapoor')
    git('config', 'user.email', 'prathamkapoor027@gmail.com')
    (repo / 'README.md').write_text('Safe source\n')
    (repo / '.gitignore').write_text('artifacts/\n')
    git('add', 'README.md', '.gitignore')
    git('commit', '-m', 'test fixture')
    return repo


def test_source_only_package_needs_no_private_runtime_and_contains_no_history(tmp_path):
    repo = repository(tmp_path)
    build = getattr(packaging, 'build_package', None)
    assert callable(build), 'a source-only packaging API is required'
    output = repo / 'artifacts' / 'release'
    manifest = build(repo, output, 'source-only')
    assert manifest['mode'] == 'source-only'
    assert manifest['evidence_complete'] is False
    assert manifest['source_commit']
    with zipfile.ZipFile(output / 'qfault-source.zip') as archive:
        assert set(archive.namelist()) == {'.gitignore', 'README.md'}
    assert packaging.verify_package(output)['valid']
    with (output / 'qfault-source.zip').open('ab') as stream:
        stream.write(b'tampered')
    assert not packaging.verify_package(output)['valid']


def test_full_package_missing_current_evidence_creates_no_success_manifest(tmp_path):
    repo = repository(tmp_path)
    build = getattr(packaging, 'build_package', None)
    assert callable(build), 'evidence-inclusive preflight is required'
    output = repo / 'artifacts' / 'release'
    with pytest.raises((FileNotFoundError, ValueError), match='evidence|summary'):
        build(repo, output, 'evidence-inclusive')
    assert not output.exists()


def test_package_schema_is_an_integer_not_a_coercible_value(tmp_path):
    repo=repository(tmp_path)
    output=repo/'artifacts'/'strict-schema'
    packaging.build_package(repo,output,'source-only')
    path=output/'manifest.json'; original=json.loads(path.read_bytes())
    for invalid in (True,1.0,'1'):
        changed={**original,'schema_version':invalid}
        path.write_text(json.dumps(changed))
        assert not packaging.verify_package(output)['valid']


def test_package_verifier_rejects_unsupported_schema_and_truncated_zip(tmp_path):
    repo = repository(tmp_path)
    build = getattr(packaging, 'build_package', None)
    assert callable(build), 'package schema verifier is required'
    output = repo / 'artifacts' / 'release'
    build(repo, output, 'source-only')
    path = output / 'manifest.json'
    data = json.loads(path.read_bytes())
    data['schema_version'] = 999
    path.write_text(json.dumps(data))
    assert not packaging.verify_package(output)['valid']


def test_package_verifier_returns_invalid_for_rehashed_broken_deflate(tmp_path):
    repo=repository(tmp_path);output=repo/'artifacts'/'release'
    packaging.build_package(repo,output,'source-only')
    path=output/'qfault-source.zip';raw=bytearray(path.read_bytes())
    # First local member data follows 30-byte header, filename and extra field.
    name_length,extra_length=struct.unpack_from('<HH',raw,26)
    raw[30+name_length+extra_length]=0xff
    path.write_bytes(raw)
    manifest_path=output/'manifest.json';manifest=json.loads(manifest_path.read_bytes())
    manifest['packages'][0]['sha256']=hashlib.sha256(raw).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    assert not packaging.verify_package(output)['valid']


def test_package_verifier_rejects_truncation_and_traversal_without_extracting(tmp_path):
    repo=repository(tmp_path);output=repo/'artifacts'/'release'
    packaging.build_package(repo,output,'source-only')
    path=output/'qfault-source.zip';path.write_bytes(path.read_bytes()[:20])
    assert not packaging.verify_package(output)['valid']
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('../escape.txt',b'not allowed')
    manifest_path=output/'manifest.json';manifest=json.loads(manifest_path.read_bytes())
    manifest['packages'][0].update(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    manifest['source_members_sha256']={'../escape.txt':hashlib.sha256(b'not allowed').hexdigest()}
    manifest_path.write_text(json.dumps(manifest))
    assert not packaging.verify_package(output)['valid']
    assert not (output.parent/'escape.txt').exists()
