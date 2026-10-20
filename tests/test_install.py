"""Installer invariants: scripts, metadata, repeat installs and payload integrity."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNTIME = Path(__file__).resolve().parents[1] / 'runtime'


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.images = Path(self.temp.name) / 'images'
        selinux = self.images / 'system_ext/etc/selinux'
        (selinux / 'mapping').mkdir(parents=True)
        for name in ['system_ext_sepolicy.cil', 'system_ext_sepolicy_debug.cil']:
            (selinux / name).write_text('; existing policy\n')
        (selinux / 'mapping/34.0.cil').write_text('; existing mapping\n')
        (self.images / 'config').mkdir()
        (self.images / 'config/system_ext_fs_config').write_text('system_ext 0 0 0755\n')

    def install(self):
        subprocess.run([sys.executable, str(RUNTIME / 'install.py'), str(self.images),
                        '--vendor-policy-version', '34.0'], capture_output=True, check=True)

    def snapshot(self):
        return {p.relative_to(self.images).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.images.rglob('*') if p.is_file()}

    def test_install_is_idempotent_and_includes_app_art_worker(self):
        self.install()
        before = self.snapshot()
        self.install()
        self.assertEqual(before, self.snapshot())
        ext = self.images / 'system_ext'
        self.assertEqual((ext / 'etc/ntvector/app-art.sh').read_bytes(),
                         (RUNTIME / 'config/app-art.sh').read_bytes())
        self.assertEqual((ext / 'app/Vector/Vector.apk').read_bytes(),
                         (RUNTIME / 'dist/vector/manager.apk').read_bytes())
        rc = (ext / 'etc/init/ntvector.rc').read_text()
        self.assertIn('on property:sys.boot_completed=1\n    start ntvector-app-art', rc)
        for suffix in ['', '_debug']:
            policy = ext / f'etc/selinux/system_ext_sepolicy{suffix}.cil'
            expected = hashlib.sha256(policy.read_bytes() +
                                      (ext / 'etc/selinux/mapping/34.0.cil').read_bytes()).hexdigest()
            actual = (ext / f'etc/selinux/system_ext_sepolicy_and_mapping{suffix}.sha256').read_text().strip()
            self.assertEqual(expected, actual)
        metadata = (self.images / 'config/system_ext_fs_config').read_text()
        self.assertIn('system_ext/etc/ntvector/app-art.sh 0 0 0644', metadata)

    def test_all_distributed_payload_pins_match(self):
        manifest = json.loads((RUNTIME / 'manifest.json').read_text())
        for rel, expected in manifest['sha256'].items():
            with self.subTest(path=rel):
                self.assertEqual(hashlib.sha256((RUNTIME / rel).read_bytes()).hexdigest(), expected)
        sums = (RUNTIME / 'SHA256SUMS').read_text()
        self.assertIn('  app-art.sh\n', sums)


if __name__ == '__main__':
    unittest.main()
