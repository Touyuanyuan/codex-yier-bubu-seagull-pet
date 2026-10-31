"""Exercise installers in temporary folders, never in the real Codex profile."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PET_ID = 'yier-bubu-handholding-seagull'
SHELL = os.environ.get('PET_TEST_SHELL') or ((shutil.which('bash') or shutil.which('sh')) if os.name == 'posix' else None)

class Installers(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='seagull-pet-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / '中文 package with spaces'
        self.package.mkdir()
        shutil.copytree(ROOT/'pet', self.package/'pet')
        for name in ('install.ps1', 'install.sh', 'install.command'):
            shutil.copy2(ROOT/name, self.package/name)
        self.destination = self.root/'custom codex home'

    def run_install(self, kind, expected=0):
        if kind == 'windows':
            cmd = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                   str(self.package/'install.ps1'), '-CodexHome', str(self.destination)]
        else:
            cmd = [SHELL, (self.package/'install.sh').as_posix(), self.destination.as_posix()]
        result = subprocess.run(cmd, capture_output=True)
        self.assertEqual(result.returncode, expected, result.stdout.decode(errors='replace')+result.stderr.decode(errors='replace'))

    def check_lifecycle(self, kind):
        self.run_install(kind)
        target = self.destination/'pets'/PET_ID
        self.assertEqual((target/'spritesheet.webp').read_bytes(), (ROOT/'pet/spritesheet.webp').read_bytes())
        self.run_install(kind)
        other = self.destination/'pets/other-pet'
        other.mkdir()
        (other/'keep.txt').write_text('preserve other pet')
        prior = b'{"id":"old-version-marker"}'
        (target/'pet.json').write_bytes(prior)
        self.run_install(kind)
        self.assertEqual((target/'pet.json').read_bytes(), (ROOT/'pet/pet.json').read_bytes())
        self.assertTrue(any(p.read_bytes() == prior for p in (self.destination/'pet-backups').glob('*/pet.json')))
        self.assertEqual((other/'keep.txt').read_text(), 'preserve other pet')

    @unittest.skipUnless(os.name == 'nt', 'Windows installer requires Windows')
    def test_windows_lifecycle(self):
        self.check_lifecycle('windows')

    @unittest.skipUnless(SHELL, 'No shell available')
    def test_shell_lifecycle(self):
        self.check_lifecycle('shell')

    @unittest.skipUnless(SHELL, 'No shell available')
    def test_shell_missing_payload(self):
        (self.package/'pet/spritesheet.webp').unlink()
        self.run_install('shell', expected=1)
        self.assertFalse(self.destination.exists())

    @unittest.skipUnless(SHELL, 'No shell available')
    def test_shell_syntax(self):
        for name in ('install.sh','install.command'):
            subprocess.run([SHELL,'-n',str(self.package/name)], check=True)

    @unittest.skipUnless(os.uname().sysname == 'Darwin' if hasattr(os, 'uname') else False, 'macOS plutil only')
    def test_macos_invalid_manifest(self):
        config=self.package/'pet/pet.json'
        pet=json.loads(config.read_text(encoding='utf-8'));pet['spriteVersionNumber']=1
        config.write_text(json.dumps(pet),encoding='utf-8')
        self.run_install('shell', expected=1)
        self.assertFalse(self.destination.exists())

if __name__ == '__main__':
    unittest.main()
