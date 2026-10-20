# Vector built into the ROM

Source distribution: [NTVector Runtime](https://github.com/ncd03-nb/NTVector-Runtime), GPL-3.0.

Vector v2.2 (3080), modern API 102 and legacy Xposed API, with a ROM-owned NeoZygisk loader.
The original, signed Vector manager is installed at `/system_ext/app/Vector/Vector.apk` and has
its own launcher icon. Install module APKs normally, enable them and select their scopes in Vector.
No module APK is preinstalled or automatically enabled. This component supplies the general Xposed module framework; unrelated NTManager hooks remain in place.

## Layout and startup

- `/system_ext/etc/ntvector`: verified engine and loader payload, root-owned, read-only ROM files.
- `/system_ext/etc/init/ntvector.rc`: init starts prepare, monitor, readiness and daemon services.
- `app-art.sh`: restores original ART compiler binaries in app Zygote mount namespaces while
  retaining the compiler-service wrappers in init/artd. It also rechecks after boot and
  Zygote restarts because OEM startup can replace a Zygote namespace. Only exact Vector
  compiler bind mounts are removed; init's namespace is explicitly protected.
- `/data/misc/ntlsposed`: private loader state and sockets.
- `/data/misc/ntlsposed/modules/zygisk_vector`: the private ROM engine, separate from root-manager modules.
  Other native modules are never scanned/loaded.
- `/data/adb/modules/zygisk_vector/bin/liboat_hook{32,64}.so`: two fixed compatibility paths in
  upstream Vector. A previous ROM-owned module here is disabled and is not the ROM engine.
  Fresh installations do not publish a module.prop or native Zygisk module in this directory.
- `/data/adb/lspd`: upstream configuration and scope database, retained across ROM updates.

Init starts the service as UID 0 in the separate `ntvectord` SELinux domain. Applications and
end users do not need `su`, Magisk or KernelSU. `RootImpl::Rom` skips root-manager detection,
root permission checks and root-manager mount namespace handling. SELinux remains enforcing.
Preparation migrates upstream configuration labels restored by the base ROM before starting
the monitor; a relabel failure must not be mistaken for an unsupported framework.
The upstream daemon attempts a best-effort `resetprop` adjustment after its dex2oat bind mounts;
the ROM does not ship or require that command, and failure does not prevent wrapper operation.

`/data/misc/ntlsposed/disable` disables startup for recovery. The monitor stops injecting after
repeated Zygote crashes. Services are oneshot and do not loop-restart the Android framework.
Payload checksum failures or an unrelated user-owned Vector installation skip ROM startup.
Disabling a previous Vector module in the root manager does not disable the private ROM engine.
Preparation waits at most five seconds for the monitor before allowing boot to continue.

## ROM installation

Run `python3 install.py <images-root>` with a real `system_ext` split-policy tree. The installer
adds the init service, original manager, CIL rules, contexts and kitchen filesystem metadata.
Vendor mapping is read from `<images-root>/vendor/etc/selinux/plat_sepolicy_vers.txt`.
For a standalone extracted tree pass `--vendor-policy-version` from the target device explicitly.
Policy changes and matching normal/debug policy digests are updated together. Vendor, ODM,
boot, vendor_boot, vbmeta and partition metadata are not changed by this installer.

The supplied native loader is arm64. It is tested on ColorOS 17 / Android 17; matching ART
32/64-bit compiler wrappers are included. Module compatibility still depends on the module's
Android/API support. Do not assume every module supports every app or Android release.

## Source and rebuild

Pinned source commits, download URL and ZIP checksum are in `upstream.txt`. The release Vector
engine and manager are unmodified; only its shell CLI is adapted to use the fixed ROM path.
`neozgyisk-rom.patch` contains all changes to the NeoZygisk source, including the datagram bounds
fix and disabling root-manager namespace operations in ROM mode. GPLv3 licenses are included.

To rebuild the native loader on Linux/WSL:

1. Clone NeoZygisk at the pinned commit and initialize its pinned lsplt submodule.
2. Apply `git apply /path/to/neozgyisk-rom.patch` from that source checkout.
3. Install the Android Rust target `aarch64-linux-android` and `cargo-ndk`.
4. Keep the source Cargo.lock matching `zygiskd.Cargo.lock` (the build helper copies it when absent).
5. Run `python3 build-loader.py --source <checkout> --sdk <sdk> --out <output>`.
6. Copy `native-arm64-v8a/libzygisk_ptrace.so`, `native-arm64-v8a/libzygisk.so` and
   `rust-target/aarch64-linux-android/release/zygiskd` into their corresponding `dist` paths,
   then regenerate `manifest.json` and `SHA256SUMS` before distributing.

## Validation scope

See `verification.json`. Live tests use a root shell only to stage temporary files, apply the
same policy rules and enter the production SELinux domain; the loader and daemon do not use
root-manager APIs. Tests cover the launcher manager becoming active, engine IPC, enabling a
legacy module for an owned probe app (`HOOKED`), then disabling it (`ORIGINAL`). Probe apps
are uninstalled afterward; user-selected modules are preserved. A complete cold boot from the flashed system_ext image also passed on ColorOS 17 / Android 17,
with the previous root-manager Vector module disabled and no live policy injection. The original
manager reported loaded SELinux policy, injected system framework and supported dex2oat.
The full system_ext partition readback matched the packed image SHA256. The existing partition
service was retained and verified running after boot.

Compiler wrapper namespace validation also passed after a full reboot: the original ART
binaries remain visible to app Zygotes while init/artd keep the Vector compiler wrappers.
VNeID CA-E005 reproduced with inherited wrappers and disappeared when only those app-visible
mounts were removed. After data reset, the flashed fix passed and the user confirmed normal
VNeID use. No VNeID APK, app integrity check, or integrity-service result was modified.
The owned hook probe still returned HOOKED when enabled and ORIGINAL when disabled.
