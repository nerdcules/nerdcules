"""nerdcules-update against real git repositories in a scratch home: a bare
"remote" per app, tags pushed to it, a real makepkg build of a tiny package,
a stand-in pacman that records what it was asked to install, and release
tarballs served from file:// URLs. Nothing goes online and nothing needs sudo."""

import importlib.machinery
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPDATE = os.path.join(ROOT, "bin", "nerdcules-update")

sys.dont_write_bytecode = True  # no __pycache__ beside bin/nerdcules-update
loader = importlib.machinery.SourceFileLoader("nerdcules_update", UPDATE)
spec = importlib.util.spec_from_loader("nerdcules_update", loader)
nu = importlib.util.module_from_spec(spec)
loader.exec_module(nu)

# Reads the package's own .PKGINFO, as pacman does, and keeps a tiny database.
FAKE_PACMAN = """#!/bin/sh
db="$FAKE_DB"; mkdir -p "$db"
case "$1" in
  -Q) [ -f "$db/$2" ] || exit 1; echo "$2 $(cat "$db/$2")" ;;
  -U) info=$(bsdtar -xOf "$2" .PKGINFO)
      name=$(printf '%s\\n' "$info" | sed -n 's/^pkgname = //p')
      ver=$(printf '%s\\n' "$info" | sed -n 's/^pkgver = //p')
      echo "$ver" > "$db/$name"; echo "-U $(basename "$2")" >> "$CALLS" ;;
  *) exit 2 ;;
esac
"""

PKGBUILD = """pkgname=demo
pkgver=0.0.1
pkgrel=7
pkgdesc='a stand-in app'
arch=('any')
license=('MIT')
options=('!debug' '!strip')
package() {
  install -Dm644 "$startdir/../VERSION" "$pkgdir/usr/share/demo/VERSION"
}
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.home)
        self.calls = os.path.join(self.tmp, "calls")
        pacman = os.path.join(self.tmp, "fake-pacman")
        with open(pacman, "w") as f:
            f.write(FAKE_PACMAN)
        os.chmod(pacman, 0o755)
        self.apps = os.path.join(self.tmp, "apps.json")
        self.env = dict(os.environ, HOME=self.home, XDG_CONFIG_HOME=os.path.join(self.home, ".config"),
                        XDG_STATE_HOME=os.path.join(self.home, ".local", "state"),
                        XDG_DATA_HOME=os.path.join(self.home, ".local", "share"),
                        NERDCULES_UPDATE_APPS=self.apps, NERDCULES_UPDATE_PACMAN=pacman,
                        FAKE_DB=os.path.join(self.tmp, "db"), CALLS=self.calls,
                        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
                        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid",
                        GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
        self.origin = os.path.join(self.tmp, "origin.git")
        self.up = os.path.join(self.tmp, "upstream")
        self.git(self.tmp, "init", "-q", "--bare", "-b", "main", self.origin)
        self.git(self.tmp, "clone", "-q", self.origin, self.up)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def git(self, cwd, *args):
        return subprocess.run(["git", *args], cwd=cwd, env=self.env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, path, text, mode=None):
        full = os.path.join(self.up, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(text)
        if mode:
            os.chmod(full, mode)

    def commit(self, msg, tag=None):
        self.git(self.up, "add", "-A")
        self.git(self.up, "commit", "-q", "-m", msg)
        if tag:
            self.git(self.up, "tag", "-a", "-m", tag, tag)
        self.git(self.up, "push", "-q", "--tags", "origin", "main")
        return self.git(self.up, "rev-parse", "HEAD")

    def register(self, **entry):
        with open(self.apps, "w") as f:
            json.dump({"demo": dict(entry, repo=self.origin)}, f)

    def update(self, *args):
        return subprocess.run([UPDATE, *args], env=self.env, capture_output=True, text=True, timeout=300)

    def ok(self, *args):
        r = self.update(*args)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def checked(self):
        return json.loads(self.ok("check", "--json"))[0]

    def calls_made(self):
        if not os.path.exists(self.calls):
            return []
        with open(self.calls) as f:
            return f.read().splitlines()


class Versions(unittest.TestCase):
    def test_semantic_version_order_puts_a_release_after_its_prereleases(self):
        tags = ["v0.2.0", "v0.10.0-rc.1", "v0.10.0-rc.2", "v0.9.0", "v0.10.0-beta", "nightly", "v1.0"]
        self.assertEqual(sorted((t for t in tags if nu.parse(t)), key=nu.precedence),
                         ["v0.2.0", "v0.9.0", "v0.10.0-beta", "v0.10.0-rc.1", "v0.10.0-rc.2"])
        self.assertLess(nu.precedence("v0.10.0-rc.2"), nu.precedence("v0.10.0"))
        self.assertLess(nu.precedence("v1.0.0-rc.2"), nu.precedence("v1.0.0-rc.10"))  # numbers as numbers

    def test_stable_never_offers_a_prerelease_and_prerelease_offers_the_newest(self):
        tags = ["v0.1.0", "v0.2.0-rc.1"]
        self.assertEqual(nu.newest(tags, "stable"), "v0.1.0")
        self.assertEqual(nu.newest(tags, "prerelease"), "v0.2.0-rc.1")
        self.assertEqual(nu.newest(tags + ["v0.2.0"], "prerelease"), "v0.2.0")
        self.assertIsNone(nu.newest(["v0.3.0-rc.1"], "stable"))

    def test_pkgver_has_no_hyphen_and_pacman_orders_it_like_the_tags(self):
        self.assertEqual(nu.pkgver("v0.2.0"), "0.2.0")
        self.assertEqual(nu.pkgver("v0.2.0-rc.1"), "0.2.0rc.1")
        for older, newer in (("v0.2.0-rc.1", "v0.2.0"), ("v0.2.0-rc.1", "v0.2.0-rc.2"),
                             ("v0.1.0", "v0.2.0-rc.1"), ("v0.2.0-beta.3", "v0.2.0-rc.1")):
            self.assertEqual(nu.vercmp(nu.pkgver(older), nu.pkgver(newer)), -1, (older, newer))


class MakepkgApp(Base):
    def setUp(self):
        super().setUp()
        self.write("pkgbuild/PKGBUILD", PKGBUILD)
        self.write("VERSION", "one\n")
        self.commit("first", tag="v0.1.0")
        self.write("VERSION", "two\n")
        self.commit("try this", tag="v0.2.0-rc.1")
        self.register(kind="makepkg", package="demo", pkgbuild="pkgbuild")

    def test_stable_apply_prerelease_rollback_and_main(self):
        r = self.checked()
        self.assertEqual((r["installed"], r["target"], r["available"]), (None, "v0.1.0", True))
        self.assertIn("Install with", self.ok("check"))

        self.ok("apply", "demo")
        self.assertEqual(self.calls_made(), ["-U demo-0.1.0-1-any.pkg.tar.zst"])  # pkgver from the tag
        r = self.checked()
        self.assertEqual((r["installed"], r["available"]), ("0.1.0", False))
        self.assertIn("up to date", self.ok("apply", "demo"))

        self.ok("channel", "demo", "prerelease")
        r = self.checked()
        self.assertEqual((r["target"], r["available"]), ("v0.2.0-rc.1", True))
        self.ok("apply", "demo")
        self.assertEqual(self.checked()["installed"], "0.2.0rc.1")

        # Back to 0.1.0 from the package kept on disk: nothing is built again.
        out = self.ok("rollback", "demo")
        self.assertIn("back at 0.1.0", out)
        self.assertNotIn("Building", out)
        self.assertEqual(self.calls_made()[-1], "-U demo-0.1.0-1-any.pkg.tar.zst")
        self.assertEqual(self.checked()["installed"], "0.1.0")

        # Any tag on request, and main, versioned after the tag it follows.
        self.write("VERSION", "three\n")
        head = self.commit("untagged")
        self.ok("install", "demo", "main")
        installed = self.checked()["installed"]
        self.assertEqual(installed, f"0.2.0rc.1.r1.g{head[:7]}")
        self.ok("channel", "demo", "main")
        self.assertFalse(self.checked()["available"])

        v = json.loads(self.ok("versions", "demo", "--json"))
        self.assertEqual(v["published"], ["v0.2.0-rc.1", "v0.1.0"])
        self.assertEqual(v["prereleases"], ["v0.2.0-rc.1"])
        self.assertEqual(sorted(v["kept"]), sorted(["0.1.0", "0.2.0rc.1", installed]))
        # A tag built before is installed from its kept package, not built again.
        out = self.ok("install", "demo", "v0.2.0-rc.1")
        self.assertNotIn("Building", out)
        self.assertEqual(self.checked()["installed"], "0.2.0rc.1")

    def test_unknown_tag_and_nothing_to_roll_back_say_so(self):
        r = self.update("install", "demo", "v9.9.9")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no tag v9.9.9", r.stderr)
        r = self.update("rollback", "demo")
        self.assertEqual(r.returncode, 1)
        self.assertIn("no earlier version", r.stderr)
        self.assertEqual(self.calls_made(), [])

    def test_main_before_any_release_is_newer_than_the_pkgbuilds_version(self):
        shutil.rmtree(self.origin)
        self.git(self.tmp, "init", "-q", "--bare", "-b", "main", self.origin)
        for tag in ("v0.1.0", "v0.2.0-rc.1"):
            self.git(self.up, "tag", "-d", tag)
        self.git(self.up, "push", "-q", "origin", "main")
        head = self.git(self.up, "rev-parse", "HEAD")
        self.ok("install", "demo", "main")
        installed = self.checked()["installed"]
        self.assertEqual(installed, f"0.0.1.r2.g{head[:7]}")  # PKGBUILD says pkgver=0.0.1
        self.assertEqual(nu.vercmp(installed, "0.0.1"), 1)

    def test_no_stable_release_yet(self):
        shutil.rmtree(self.origin)
        self.git(self.tmp, "init", "-q", "--bare", "-b", "main", self.origin)
        self.git(self.up, "tag", "-d", "v0.1.0")
        self.git(self.up, "push", "-q", "--tags", "origin", "main")
        r = self.checked()
        self.assertFalse(r["available"])
        self.assertIn("no stable release yet", r["note"])


class TarballApp(Base):
    def make_release(self, tag):
        version = tag[1:]
        folder = os.path.join(self.tmp, "build", f"demo-{version}-linux-{nu.arch()}")
        os.makedirs(folder)
        with open(os.path.join(folder, "install.sh"), "w") as f:
            f.write(f'#!/bin/sh\necho "install {version}" >> "$CALLS"\n')
        assets = os.path.join(self.tmp, "assets", tag)
        os.makedirs(assets)
        with tarfile.open(os.path.join(assets, f"demo-linux-{nu.arch()}.tar.gz"), "w:gz") as t:
            t.add(folder, arcname=os.path.basename(folder))

    def setUp(self):
        super().setUp()
        self.write("README", "one\n")
        self.commit("first", tag="v1.0.0")
        self.write("README", "two\n")
        self.commit("try", tag="v1.1.0-rc.1")
        for tag in ("v1.0.0", "v1.1.0-rc.1"):
            self.make_release(tag)
        self.share = os.path.join(self.home, "demo")
        self.register(kind="release-tarball", home=self.share, command="demo-not-on-path",
                      asset="file://" + self.tmp + "/assets/{tag}/demo-linux-{arch}.tar.gz")

    def test_apply_prerelease_and_rollback_switch_current(self):
        self.ok("apply", "demo")
        self.assertEqual(self.calls_made(), ["install 1.0.0"])
        self.assertEqual(self.checked()["installed"], "1.0.0")
        self.ok("channel", "demo", "prerelease")
        self.ok("apply", "demo")
        self.assertEqual(self.checked()["installed"], "1.1.0-rc.1")
        self.ok("rollback", "demo")
        self.assertEqual(os.readlink(os.path.join(self.share, "current")), f"demo-1.0.0-linux-{nu.arch()}")
        self.assertEqual(self.calls_made(), ["install 1.0.0", "install 1.1.0-rc.1", "install 1.0.0"])
        r = self.update("channel", "demo", "main")
        self.assertEqual(r.returncode, 0)
        self.assertIn("release tarballs only", self.checked()["note"])

    def test_an_app_run_from_a_clone_is_left_alone(self):
        bin_dir = os.path.join(self.tmp, "bin")
        os.makedirs(bin_dir)
        self.write("bin/demo", "#!/bin/sh\n", mode=0o755)
        self.commit("a command")
        os.symlink(os.path.join(self.up, "bin", "demo"), os.path.join(bin_dir, "demo"))
        self.env["PATH"] = bin_dir + os.pathsep + self.env["PATH"]
        self.register(kind="release-tarball", home=self.share, command="demo",
                      asset="file://" + self.tmp + "/assets/{tag}/demo-linux-{arch}.tar.gz")
        r = self.checked()
        self.assertFalse(r["available"])
        self.assertIn("runs from your clone", r["note"])
        r = self.update("install", "demo", "v1.0.0")
        self.assertEqual(r.returncode, 1)
        self.assertIn("replace those links", r.stderr)
        self.assertEqual(self.calls_made(), [])


class FathomApp(Base):
    def test_its_own_updater_does_the_work_with_its_channel_names(self):
        bin_dir = os.path.join(self.tmp, "bin")
        os.makedirs(bin_dir)
        fake = os.path.join(bin_dir, "fake-fathom-update")
        with open(fake, "w") as f:
            f.write('#!/bin/sh\necho "$*" >> "$CALLS"\n'
                    '[ "$1" = check ] && echo \'{"version": "v0.3.0", "installed": "abc", '
                    '"target": "v0.4.0-rc.1", "available": true, "blocked": null, "note": null}\'\nexit 0\n')
        os.chmod(fake, 0o755)
        self.env["PATH"] = bin_dir + os.pathsep + self.env["PATH"]
        self.register(kind="fathom-update", command="fake-fathom-update")
        self.ok("channel", "demo", "prerelease")
        r = self.checked()
        self.assertEqual((r["installed"], r["target"], r["available"]), ("v0.3.0", "v0.4.0-rc.1", True))
        self.ok("apply", "demo")
        self.ok("rollback", "demo")
        self.assertEqual(self.calls_made(), ["channel prereleases", "check --json", "apply", "rollback"])
        r = self.update("install", "demo", "v0.2.0")
        self.assertEqual(r.returncode, 1)
        self.assertIn("newest on its channel only", r.stderr)


if __name__ == "__main__":
    unittest.main()
