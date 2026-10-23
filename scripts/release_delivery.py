"""Bundle or safely verify/extract a self-contained public source/evidence download."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import zipfile
import zlib

from scripts.package_submission import verify_package

MEMBERS={'manifest.json','qfault-source.zip'}


def sha256(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def verify_release_archive(archive,out=None,expected_sha256=None):
    """Verify before extracting; never overwrite an existing destination."""
    work=None
    try:
        archive=Path(archive)
        if archive.is_symlink() or archive.stat().st_size>130*1024*1024:
            raise ValueError('Unsafe or oversized release archive')
        checksum=sha256(archive)
        if expected_sha256 is not None and checksum!=expected_sha256:
            raise ValueError('Downloaded archive checksum mismatch')
        target=Path(out).absolute() if out is not None else None
        if target and (target.exists() or target.is_symlink()):
            raise FileExistsError('Choose a new empty destination; existing contents are preserved')
        with zipfile.ZipFile(archive) as outer:
            entries=outer.infolist();names=[e.filename for e in entries]
            if len(names)!=2 or set(names)!=MEMBERS:
                raise ValueError('Release archive must contain exactly manifest.json and qfault-source.zip')
            for entry in entries:
                if entry.is_dir() or (entry.external_attr>>16)&0o170000==0o120000:
                    raise ValueError('Links/directories are not permitted in release members')
                limit=1024*1024 if entry.filename=='manifest.json' else 128*1024*1024
                if entry.file_size>limit:raise ValueError('Release member exceeds size limit')
            if outer.testzip():raise ValueError('Release archive CRC failure')
            parent=target.parent.resolve() if target else Path(tempfile.gettempdir()).resolve()
            parent.mkdir(parents=True,exist_ok=True)
            work=Path(tempfile.mkdtemp(prefix='.qfault-release-',dir=parent)).resolve()
            if not work.is_relative_to(parent) or work==parent:raise ValueError('Unsafe temporary destination')
            package=work/'package';package.mkdir()
            for name in MEMBERS:(package/name).write_bytes(outer.read(name))
        checked=verify_package(package)
        if not checked['valid']:raise ValueError('Inner package failed verification: '+'; '.join(checked['errors']))
        manifest=json.loads((package/'manifest.json').read_bytes())
        if target:
            project=work/'project';project.mkdir()
            # Inner membership/path/symlink/expansion checks have already passed.
            with zipfile.ZipFile(package/'qfault-source.zip') as inner:
                for entry in inner.infolist():
                    destination=(project/entry.filename).resolve()
                    if not destination.is_relative_to(project.resolve()):raise ValueError('Unsafe inner destination')
                    destination.parent.mkdir(parents=True,exist_ok=True)
                    with destination.open('xb') as stream:stream.write(inner.read(entry))
            if target.exists() or target.is_symlink():raise FileExistsError('Destination appeared during verification')
            os.rename(work,target)
        return {'valid':True,'errors':[],'archive_sha256':checksum,'source_commit':manifest['source_commit'],
            'mode':manifest['mode'],'evidence_complete':manifest['evidence_complete'],
            'extracted':str(target) if target else None,
            'assurance':'Unsigned byte consistency, not authenticity or scientific correctness'}
    except (OSError,ValueError,KeyError,TypeError,AttributeError,zipfile.BadZipFile,zlib.error) as exc:
        return {'valid':False,'errors':[type(exc).__name__+': '+str(exc)]}
    finally:
        if work and work.exists():
            # work was created and resolved under the checked parent above.
            if work.parent==parent and work.name.startswith('.qfault-release-'):shutil.rmtree(work)


def bundle_package(package,out):
    """Select only the reviewed manifest and its single inner source ZIP."""
    package,out=Path(package),Path(out)
    if out.exists() or out.is_symlink():raise FileExistsError('Release asset already exists')
    if package.is_symlink() or any((package/name).is_symlink() for name in MEMBERS):
        raise ValueError('Release inputs cannot be symlinks')
    checked=verify_package(package)
    if not checked['valid']:raise ValueError('Package is not verified: '+'; '.join(checked['errors']))
    out.parent.mkdir(parents=True,exist_ok=True)
    parent=out.parent.resolve();handle,name=tempfile.mkstemp(prefix='.qfault-download-',dir=parent);os.close(handle)
    temporary=Path(name).resolve()
    if temporary.parent!=parent:raise ValueError('Unsafe temporary archive')
    try:
        with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_STORED) as archive:
            for member in sorted(MEMBERS):archive.write(package/member,member)
        result=verify_release_archive(temporary)
        if not result['valid']:raise ValueError('; '.join(result['errors']))
        if out.exists() or out.is_symlink():raise FileExistsError('Release asset appeared during bundling')
        os.rename(temporary,out)
        return {'file':out.name,'bytes':out.stat().st_size,'sha256':sha256(out),
            'source_commit':result['source_commit'],'mode':result['mode']}
    finally:
        if temporary.exists() and temporary.parent==parent and temporary.name.startswith('.qfault-download-'):
            temporary.unlink()


def main():
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    bundle=commands.add_parser('bundle');bundle.add_argument('--package',type=Path,required=True);bundle.add_argument('--out',type=Path,required=True)
    verify=commands.add_parser('verify');verify.add_argument('--archive',type=Path,required=True);verify.add_argument('--out',type=Path);verify.add_argument('--sha256')
    args=parser.parse_args()
    try:
        result=bundle_package(args.package,args.out) if args.command=='bundle' else verify_release_archive(args.archive,args.out,args.sha256)
        print(json.dumps(result,indent=2));return 0 if result.get('valid',True) else 1
    except (OSError,ValueError) as exc:
        print(json.dumps({'valid':False,'errors':[type(exc).__name__+': '+str(exc)]}));return 1


if __name__=='__main__':raise SystemExit(main())
