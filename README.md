# NTVector Runtime

GPL-3.0 ROM integration for [Vector](https://github.com/JingMatrix/Vector).
The original signed Vector v2.2 (3080) manager is a system app in `system_ext`,
with a launcher icon. Users install Xposed module APKs normally, then enable
modules and select their scopes in Vector. No module is bundled or enabled by default.

The loader and daemon start from Android init in their own SELinux domain.
Users do not need Magisk, KernelSU, `su` or a root-manager module. The native
loader uses a dedicated ROM mode and a private engine directory.

## Contents

- `runtime/`: tested installer, init services, split-policy integration and verified binaries.
- `source/NeoZygisk/`: complete patched native loader source, including its pinned lsplt dependency.
- `upstream/Vector/`: matching original Vector source, pinned as a Git submodule.
- `runtime/neozgyisk-rom.patch`: changes against the original NeoZygisk revision.
- `runtime/upstream.txt`: revisions, upstream release URL and SHA256 pins.
- `runtime/verification.json`: device checks and their scope.

## Install into an extracted ROM

Run `python3 runtime/install.py <images-root>` after enabling Toolbox. The tree
must contain `system_ext` and its SELinux policy. For a standalone tree pass
`--vendor-policy-version` from the target vendor partition explicitly.
See [runtime documentation](runtime/README.md) for paths and startup behavior.

Vector compiler wrappers stay in the compiler-service namespace. App Zygotes use
original ART compiler binaries; startup rechecks handle OEM namespace changes.
Both owned-probe module hooks and VNeID were verified after reboot. The existing
NT partition service remains available.

## Build and corresponding source

Clone with `git clone --recurse-submodules`, or run
`git submodule update --init --recursive` after cloning. Build the patched loader:

```sh
python3 runtime/build-loader.py --source source/NeoZygisk --sdk /path/to/android-sdk --out build
```

The original Vector source and dependency revisions are in `upstream/Vector`.
The ROM loader build uses the committed Cargo.lock from the tested payload with `--locked`.
Its signed manager and engine binaries are unchanged. Refer to its Gradle build
and upstream release instructions when rebuilding Vector.
See [licensing and provenance](NOTICE.md).

## Validation

Tested on ColorOS 17 / Android 17 with SELinux enforcing: cold boot, manager
activation, module enable/disable against an owned probe, full partition
readback, and app compiler namespace separation. The previous root-manager Vector
module stayed disabled. Module compatibility depends on its Android/API support.
