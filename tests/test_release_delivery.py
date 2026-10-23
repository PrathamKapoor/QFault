"""Public downloads must retain the real manifest and fail safely before extraction."""
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import zipfile
import pytest
from scripts.package_submission import build_package


def delivery():
    try:module=importlib.import_module('scripts.release_delivery')
    except ModuleNotFoundError:module=None
    assert module is not None, 'portable public package verification is missing'
    return module


def prepared(tmp_path):
    repo=tmp_path/'repo';repo.mkdir()
    def git(*args):return subprocess.check_output(['git','-c','safe.directory='+repo.as_posix(),'-C',str(repo),*args],text=True).strip()
    git('init','-b','main');git('config','user.name','PrathamKapoor');git('config','user.email','prathamkapoor027@gmail.com')
    (repo/'README.md').write_text('Reviewed public source\n');(repo/'.gitignore').write_text('artifacts/\n')
    git('add','README.md','.gitignore');git('commit','-m','Public package fixture')
    package=repo/'artifacts'/'package';manifest=build_package(repo,package,'source-only')
    return package,manifest


def test_downloadable_outer_archive_preserves_manifest_and_extracts_exact_source(tmp_path):
    m=delivery();package,manifest=prepared(tmp_path);archive=tmp_path/'source.zip'
    m.bundle_package(package,archive)
    target=tmp_path/'reviewed';result=m.verify_release_archive(archive,target,hashlib.sha256(archive.read_bytes()).hexdigest())
    assert result['valid'],result
    assert result['source_commit']==manifest['source_commit'] and result['mode']=='source-only'
    assert result['evidence_complete'] is False
    assert (target/'project/README.md').read_text()=='Reviewed public source\n'
    assert (target/'package/manifest.json').read_bytes()==(package/'manifest.json').read_bytes()
    assert not (target/'project/.git').exists()


@pytest.mark.parametrize('kind',['truncated','traversal','symlink','false-valid','missing'])
def test_corrupt_unsafe_or_incomplete_outer_download_never_creates_reviewed_project(tmp_path,kind):
    m=delivery();package,_=prepared(tmp_path);archive=tmp_path/'download.zip'
    if kind=='truncated':
        m.bundle_package(package,archive);archive.write_bytes(archive.read_bytes()[:-15])
    else:
        manifest=json.loads((package/'manifest.json').read_bytes())
        if kind=='false-valid':manifest['valid']=True;manifest['source_members_sha256']['README.md']='0'*64
        with zipfile.ZipFile(archive,'w') as z:
            if kind!='missing':z.writestr('manifest.json',json.dumps(manifest))
            z.write(package/'qfault-source.zip','qfault-source.zip')
            if kind=='traversal':z.writestr('../escape','unsafe')
            if kind=='symlink':
                entry=zipfile.ZipInfo('unsafe-link');entry.create_system=3;entry.external_attr=0o120777<<16;z.writestr(entry,'../escape')
    target=tmp_path/'reviewed';result=m.verify_release_archive(archive,target)
    assert not result['valid']
    assert not target.exists() and not (tmp_path/'escape').exists()


def test_download_checksum_and_existing_destination_prevent_overwrite(tmp_path):
    m=delivery();package,_=prepared(tmp_path);archive=tmp_path/'source.zip';m.bundle_package(package,archive)
    assert not m.verify_release_archive(archive,tmp_path/'bad-digest','0'*64)['valid']
    assert not (tmp_path/'bad-digest').exists()
    target=tmp_path/'owner-data';target.mkdir();sentinel=target/'keep.txt';sentinel.write_text('Preserved')
    assert not m.verify_release_archive(archive,target)['valid']
    assert sentinel.read_text()=='Preserved'
    with pytest.raises(FileExistsError):m.bundle_package(package,archive)
