"""Offline payload and image integration checks."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("vector_installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def test_shipped_payload_hashes_and_runtime_checksums(self):
        installer.verify()
        for line in (ROOT / "SHA256SUMS").read_text().splitlines():
            digest, name = line.split(None, 1)
            source = ROOT / ("config/" + name if name in {"start.sh", "app-art.sh"} else name)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), digest)

    def test_repeated_install_preserves_existing_policy_and_partition_service(self):
        with tempfile.TemporaryDirectory(prefix="ntvector-image-test-") as temp:
            images = Path(temp)
            policy_dir = images / "system_ext/etc/selinux"
            policy_dir.mkdir(parents=True)
            for suffix in ("", "_debug"):
                (policy_dir / ("system_ext_sepolicy" + suffix + ".cil")).write_text("; original ROM policy\n")
            mapping = policy_dir / "mapping/202504.cil"
            mapping.parent.mkdir()
            mapping.write_text("; original mapping\n")
            service = images / "system_ext/etc/init/ntpartition.rc"
            service.parent.mkdir(parents=True)
            service.write_bytes(b"original partition writer service\n")
            contexts = policy_dir / "system_ext_file_contexts"
            contexts.write_text("/system_ext/bin/ntpartition u:object_r:system_file:s0\n")
            fs = images / "config/system_ext_fs_config"
            fs.parent.mkdir()
            fs.write_text("system_ext/bin/ntpartition 0 0 0755\n")
            installer.install(images, vendor_policy_version="202504")
            before = {p.relative_to(images): p.read_bytes() for p in images.rglob("*") if p.is_file()}
            installer.install(images, vendor_policy_version="202504")
            self.assertEqual(before, {p.relative_to(images): p.read_bytes() for p in images.rglob("*") if p.is_file()})
            self.assertEqual(service.read_bytes(), b"original partition writer service\n")
            self.assertIn("system_ext/bin/ntpartition 0 0 0755", fs.read_text())
            self.assertEqual(mapping.read_text(), "; original mapping\n")
            for suffix in ("", "_debug"):
                policy = policy_dir / ("system_ext_sepolicy" + suffix + ".cil")
                self.assertEqual(policy.read_text().count(installer.BEGIN), 1)
                self.assertTrue(policy.read_text().startswith("; original ROM policy\n"))
                expected = hashlib.sha256(policy.read_bytes() + mapping.read_bytes()).hexdigest()
                self.assertEqual((policy_dir / ("system_ext_sepolicy_and_mapping" + suffix + ".sha256")).read_text().strip(), expected)
            self.assertEqual((images / "system_ext/etc/ntvector/start.sh").read_bytes(), (ROOT / "config/start.sh").read_bytes())

    def test_verification_failure_prevents_image_writes(self):
        with tempfile.TemporaryDirectory(prefix="ntvector-image-test-") as temp:
            images = Path(temp)
            (images / "system_ext").mkdir()
            with patch.object(installer, "verify", side_effect=ValueError("bad payload")):
                with self.assertRaisesRegex(ValueError, "bad payload"):
                    installer.install(images)
            self.assertEqual(list((images / "system_ext").iterdir()), [])


if __name__ == "__main__":
    unittest.main()
