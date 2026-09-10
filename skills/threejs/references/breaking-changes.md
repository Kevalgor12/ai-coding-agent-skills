# Three.js — r-number breaking-changes reference (Tier-2)

Source: the official GitHub wiki Migration Guide
[Source: https://github.com/mrdoob/three.js/wiki/Migration-Guide], via
`research/technologies/threejs.md` §13, retrieved 2026-09-10. Quoted/
paraphrased directly from the guide. Not exhaustive — the guide extends back
many more versions; this covers the recent and the historically
high-impact transitions. Three.js has **no semver**; every entry below is
keyed to an r-number transition, not a major/minor/patch boundary.

Use this file before any upgrade that crosses one of these boundaries —
per the official policy, "it's recommended to update the library in
increments of 10 ⚠️ ... deprecation warnings last for 10 releases"
[Source: https://github.com/mrdoob/three.js/wiki/Migration-Guide]. That
policy is the reason a 10-release jump can still land on a documented
breaking change: deprecation windows expire inside a single 10-release hop.

## High-impact historical transitions

- **r147 and earlier** — the `examples/js` (non-module, global-namespace)
  directory was removed; only ES6-module `examples/jsm` remains supported.
  Matches the fundamentals-manual statement that "as of r147, this is the
  only way to load three.js properly" (ES-module loading via npm+bundler or
  an import map).
- **r152 onward — Color Management overhaul** (multi-release rollout):
  `WebGLRenderer.outputEncoding` → `outputColorSpace` (default
  `SRGBColorSpace`); `Texture.encoding` → `Texture.colorSpace` (default
  `NoColorSpace`); `ColorManagement.enabled` became `true` by default;
  `sRGBEncoding` → `SRGBColorSpace`, `LinearEncoding` →
  `LinearSRGBColorSpace`. The single largest visually-breaking change
  documented in the guide's historical section.
- **r160 → r161** — legacy `build/three.js` and `build/three.min.js`
  UMD/global-namespace build files were **removed** from the distribution
  entirely.
- **r163** — `WebGLRenderer` dropped WebGL 1 support: "WebGL 1 is not
  supported since r163." `WebGLRenderer` requires WebGL 2 from this point
  forward.

## Recent transitions (most recent first, as captured at research time)

**r186 → r187** (next/unreleased at research time): `WebGLRenderer.setViewport()`
and `.setScissor()` no longer scale by pixel ratio when a render target is bound.

**r185 → r186** (current stable, r186):
- `Object3D` gained a `.dispose()` method; custom `Object3D` subclasses with
  their own `dispose()` must call `super.dispose()`.
- `GTAONode`'s distance model changed; `distanceExponent`/`distanceFallOff`
  are deprecated no-ops.
- `BufferGeometryUtils.toTrianglesDrawMode()` now mutates the geometry
  **in-place** instead of cloning — callers relying on clone behavior must
  `.clone()` first.
- `LightProbeGrid` renamed `LightProbeGridWebGL`; `LightProbeGridHelper`
  renamed `LightProbeGridHelperWebGL`.
- `PCFSoftShadowMap` with `WebGPURenderer` removed; use `PCFShadowMap`
  ("now soft as well").
- `SimplifyModifier` reimplemented on `meshoptimizer` (different output
  mesh); `.modify()` is now async.
- `Source` renamed `TextureSource`.
- `Sky`/`SkyMesh` `up` uniform removed; always assumes +Y up.

**r184 → r185**:
- `WebGPURenderer` premultiplied-alpha implementation changed — blending
  regressions may need an opaque `Scene.background` or clear color.
- `SSAAPassNode.clearColor`/`.clearAlpha` removed (set on the renderer instead).
- `SVGLoader.createShapes()` deprecated for `shapePaths.toShapes()`.
- `AnamorphicNode` removed; use `BloomNode`.
- `DRACOLoader.setDecoderConfig()` deprecated (WASM always used now).
- `PLYLoader` now honors PLY data types (e.g. `float64` fields now produce `Float64Array`).
- `GTAONode` AO computation made "more physically correct" — output is
  darker/wider; `radius`/`scale` may need lowering (visual regression risk).
- `LWOLoader` deprecated.
- TSL `positionLocal` no longer reflects vertex transforms (e.g.
  `SkinnedMesh`) in `material.positionNode`; use `positionGeometry`.
- `TiledLighting` removed; use `ClusteredLighting`.
- `Matrix3.translate()/scale()/rotate()` deprecated.

**r183 → r184**:
- Background/environment-map rotation aligned to standard 3D object
  rotation semantics (visual-change risk).
- `FirstPersonControls` got a new interaction model and improved mobile support.
- `FBXLoader` now automatically converts +Z-up models to +Y-up — manual
  compensating rotations must be removed or the model double-rotates.
- `VTKLoader` deprecated.
- `FileLoader.load()` / `ImageBitmapLoader.load()` no longer return a
  value — use the `onLoad()` callback only.

**r182 → r183**: `PostProcessing` renamed `RenderPipeline`; `Clock`
deprecated in favor of `Timer`; `WebGLCubeRenderTarget` can no longer be
used with `WebGPURenderer` (use `CubeRenderTarget`); a "legacy gamma
correction" of `Sky`/`SkyMesh` was removed with no parameter to restore it.

**r181 → r182**: `PCFSoftShadowMap` with `WebGLRenderer` deprecated (use
`PCFShadowMap`, now soft); `WebGPURenderer`'s `colorBufferType` param
renamed `outputBufferType`.

**r180 → r181**: PBR indirect specular light computation improved
(appearance change); rough materials (roughness > 0.5) render brighter due
to better energy conservation; several `WebGPURenderer` async methods
(`renderAsync()`, `computeAsync()`, etc.) deprecated in favor of
auto-initialization via `setAnimationLoop()` or explicit `await
renderer.init()`; API docs switched to a JSDoc-generated system and
internationalization is no longer supported — docs are English-only from
this point forward.

**r179 → r180**: `DepthOfFieldNode` reimplemented with a new API;
`RGBELoader` renamed `HDRLoader`; `RGBMLoader` removed entirely (migrate to
`EXRLoader`/`HDRLoader`/`HDRCubeTextureLoader`/`UltraHDRLoader`).

**r178 → r179**: `Timer` moved into core — no longer needs to be imported
as a separate add-on.

## Unresolved / in-flux at research time

- `package.json` on the `dev` branch (fetched same day as this research)
  still lists `"main": "./build/three.cjs"` with a `require` export
  condition, so the CommonJS build is documented as deprecated (r186
  release notes: "Deprecate CommonJS build," "Remove minified builds") but
  was **not yet fully removed** as of the research date — the exact removal
  release was not identified.

## Cross-reference

Full narrative context for the color-management overhaul, the r163 WebGL2
floor, and the r147 module-loading rule is in
[../SKILL.md](../SKILL.md#knowledge). Source list:
`skill.yaml.source_references`.
