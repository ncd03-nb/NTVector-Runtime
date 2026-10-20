# Licensing and provenance

This ROM integration is distributed under GNU GPL version 3. See [LICENSE](LICENSE).
Upstream copyright, license headers and attribution remain in the corresponding sources.

## Vector

- Project: JingMatrix and Vector contributors, https://github.com/JingMatrix/Vector
- Revision: `88f8e1faa8b4e7ce20aefabe9c295cd746ea038e` (v2.2, 3080).
- Corresponding original source: `upstream/Vector`, including its pinned dependency revisions.
- Unmodified release manager and engine: `runtime/dist/vector`.
- License copy: `runtime/Vector-LICENSE`.

## NeoZygisk ROM loader

- Project: JingMatrix and NeoZygisk contributors, https://github.com/JingMatrix/NeoZygisk
- Base revision: `225b32b802cff876c09a4a8ec4a1677ce0538c39`.
- Modified corresponding source: `source/NeoZygisk`.
- Changes: `runtime/neozgyisk-rom.patch`; build: `runtime/build-loader.py`.
- License copy: `runtime/NeoZygisk-LICENSE`.

## Dependencies

- lsplt revision `2cfb537d7e8588abefbd3ddc55cacf3188662f9e` is included under
  `source/NeoZygisk/loader/src/external/lsplt` with its license and notices.
- Vector dependencies retain their original licenses in its recursive source submodules.
- Payload checksums and original release provenance are recorded in `runtime/manifest.json`
  and `runtime/upstream.txt`.
