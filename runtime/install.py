#!/usr/bin/env python3
"""Install ROM-owned Vector and its original launcher app into system_ext."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from policy import cil

HERE = Path(__file__).resolve().parent
BEGIN = '; NTVector begin'
END = '; NTVector end'

def verify(payload=HERE):
    manifest = json.loads((payload / 'manifest.json').read_text())
    for rel, expected in manifest['sha256'].items():
        path = payload / rel
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Vector payload checksum mismatch: ' + rel)
    return manifest

def install(images, payload=HERE, vendor_policy_version=None):
    images = Path(images).resolve()
    ext = images / 'system_ext'
    if not ext.is_dir(): raise ValueError('system_ext is required for Vector')
    verify(payload)
    code = ext / 'etc/ntvector'
    code.mkdir(parents=True, exist_ok=True)
    shutil.copytree(payload / 'dist', code / 'dist', dirs_exist_ok=True)
    shutil.copyfile(payload / 'config/start.sh', code / 'start.sh')
    shutil.copyfile(payload / 'config/app-art.sh', code / 'app-art.sh')
    shutil.copyfile(payload / 'SHA256SUMS', code / 'SHA256SUMS')
    init = ext / 'etc/init/ntvector.rc'
    init.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(payload / 'config/ntvector.rc', init)
    app = ext / 'app/Vector/Vector.apk'
    app.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(payload / 'dist/vector/manager.apk', app)
    for p in code.rglob('*'):
        p.chmod(0o755 if p.is_dir() else 0o644)
    app.chmod(0o644); init.chmod(0o644)
    selinux = ext / 'etc/selinux'
    normal = selinux / 'system_ext_sepolicy.cil'
    if not normal.is_file(): raise ValueError('system_ext split SELinux policy is required')
    vf = images / 'vendor/etc/selinux/plat_sepolicy_vers.txt'
    version = vendor_policy_version or (vf.read_text().strip() if vf.exists() else '')
    if version and not re.fullmatch(r'[0-9]{2,8}(?:[.][0-9]+)?', version): raise ValueError('Invalid vendor mapping version')
    mapping = selinux / 'mapping' / (version + '.cil')
    mapping_bytes = mapping.read_bytes() if mapping.is_file() else b''
    for suffix in ['', '_debug']:
        path = selinux / ('system_ext_sepolicy' + suffix + '.cil')
        if not path.exists(): continue
        text = re.sub(re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n?', '', path.read_text(), flags=re.S).rstrip() + '\n'
        path.write_text(text + BEGIN + '\n' + cil() + END + '\n', encoding='utf-8', newline='\n')
        digest = hashlib.sha256(path.read_bytes() + mapping_bytes).hexdigest() + '\n'
        (selinux / ('system_ext_sepolicy_and_mapping' + suffix + '.sha256')).write_text(digest, newline='\n')
    contexts = {selinux / 'system_ext_file_contexts', images / 'config/system_ext_file_contexts'}
    metadata_dirs = [images.parent / 'config']
    if images.parent.parent.name == 'build': metadata_dirs.append(images.parent.parent.parent / 'config')
    contexts.update(p / 'system_ext_file_contexts' for p in metadata_dirs if p.is_dir())
    rules = {
        '/system_ext/etc/ntvector(/.*)?': 'u:object_r:system_file:s0',
        '/system_ext/etc/init/ntvector[.]rc': 'u:object_r:system_file:s0',
        '/system_ext/app/Vector(/.*)?': 'u:object_r:system_file:s0',
        '/data/misc/ntlsposed(/.*)?': 'u:object_r:ntvector_data_file:s0',
        '/data/adb/modules/zygisk_vector(/.*)?': 'u:object_r:xposed_file:s0',
    }
    for path in contexts:
        old = path.read_text() if path.exists() else ''
        lines = [line for line in old.splitlines() if not any(x in line for x in ['/system_ext/etc/ntvector', '/system_ext/etc/init/ntvector', '/system_ext/app/Vector', '/data/misc/ntlsposed', '/data/adb/modules/zygisk_vector'])]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(lines + [a + ' ' + b for a,b in rules.items()]) + '\n', encoding='utf-8', newline='\n')
    for directory in metadata_dirs + [images / 'config']:
        fs = directory / 'system_ext_fs_config'
        if not fs.exists(): continue
        lines = [line for line in fs.read_text().splitlines() if not any(x in line.split(' ')[0] for x in ['system_ext/etc/ntvector', 'system_ext/etc/init/ntvector.rc', 'system_ext/app/Vector'])]
        targets = [code, *code.rglob('*'), init, app.parent, app]
        lines += [p.relative_to(images).as_posix() + (' 0 0 0755' if p.is_dir() else ' 0 0 0644') for p in targets]
        fs.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    print('[Vector] Original manager installed in system_ext/app; init-owned loader installed')

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('images',type=Path)
    p.add_argument('--vendor-policy-version');a=p.parse_args()
    install(a.images,vendor_policy_version=a.vendor_policy_version)
