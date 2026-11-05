#!/usr/bin/env python3
"""Apply the Korean translation patch to an existing idrive7-apps source tree."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, name):
    # Windows temp paths may contain DOS short names (RUNNER~1). Canonicalize
    # both sides so the resolved destination is compared to the same root.
    root = root.resolve()
    path = (root / name).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError('Invalid patch path: ' + name)
    return path


def apply(target, check_only=False):
    target = target.resolve()
    manifest = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    if not (target / 'apps').is_dir() or not (target / 'kit').is_dir():
        raise ValueError('Specify the original project root containing apps/ and kit/.')
    patch = safe_path(HERE, manifest['patch']['path'])
    if digest(patch.read_bytes()) != manifest['patch']['sha256']:
        raise ValueError('Patch checksum mismatch; download a fresh copy.')
    states = []
    saved = {}
    for item in manifest['files']:
        dest = safe_path(target, item['path'])
        data = dest.read_bytes() if dest.is_file() else None
        current = digest(data) if data is not None else None
        saved[item['path']] = data
        if item['kind'] == 'payload':
            source = safe_path(HERE / 'payload', item['path'])
            if digest(source.read_bytes()) != item['after_sha256']:
                raise ValueError('Payload checksum mismatch: ' + item['path'])
        if current == item['after_sha256']:
            states.append('after')
        elif current == item['before_sha256']:
            states.append('before')
        else:
            raise ValueError('Source differs from the supported version: ' + item['path'] +
                             '\nNo files were changed. Compare your changes with the patch first.')
    if all(state == 'after' for state in states):
        print('Korean patch is already applied; no changes needed.')
        return
    if 'after' in states:
        raise ValueError('Part of the patch is already applied. Use a clean supported source tree.')
    if not shutil.which('git'):
        raise ValueError('Git is required to apply the patch. Install Git and try again.')
    command = ['git', 'apply', '--whitespace=nowarn']
    subprocess.run(command + ['--check', str(patch)], cwd=target, check=True)
    if check_only:
        print('PASS: source version, payload checksums and patch applicability; no files changed.')
        return
    # Keep originals until all writes and resulting checksums have succeeded.
    with tempfile.TemporaryDirectory(prefix='idrive7-korean-backup-') as temporary:
        backup = Path(temporary)
        for name, data in saved.items():
            if data is not None:
                dest = safe_path(backup, name)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
        try:
            subprocess.run(command + [str(patch)], cwd=target, check=True)
            for item in manifest['files']:
                dest = safe_path(target, item['path'])
                if item['kind'] == 'payload':
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(safe_path(HERE / 'payload', item['path']), dest)
                if digest(dest.read_bytes()) != item['after_sha256']:
                    raise ValueError('Applied file checksum mismatch: ' + item['path'])
        except Exception:
            for name, data in saved.items():
                dest = safe_path(target, name)
                if data is None:
                    dest.unlink(missing_ok=True)
                else:
                    shutil.copyfile(safe_path(backup, name), dest)
            raise
    print('Korean patch applied. Verify with: python kit/tools/test_ko.py')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path, help='original idrive7-apps project root')
    parser.add_argument('--check', action='store_true', help='validate without modifying files')
    args = parser.parse_args()
    try:
        apply(args.project, args.check)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
