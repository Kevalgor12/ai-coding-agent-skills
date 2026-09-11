---
name: Three.js
description: >-
  Three.js 3D graphics: scene-graph/renderer/camera/geometry/material
  model, WebGLRenderer-vs-WebGPURenderer choice, r-number versioning (no
  semver — e.g. r186), WebGL2 floor since r163, module loading since r147,
  and GPU resource disposal. Use when the stack has a `three` dependency,
  WebGL/WebGPU 3D scene work, or the task names Three.js, a Three.js class,
  or TSL. Not for generic frontend structure (frontend-architecture),
  2D-only Canvas/SVG visualization, or a different WebGL/3D library.
spec_version: "1.0"
---

## Purpose & scope

Apply Three.js correctly and version-appropriately — the scene-graph/
renderer/camera/geometry/material object model, the WebGLRenderer-vs-
WebGPURenderer choice, the r-number (non-semver) versioning scheme, and GPU
resource disposal. The generic frontend structuring/framework-selection
method comes from the parent skill
([SK-FE-001, frontend-architecture](../frontend-architecture/SKILL.md)) and
is not repeated here.

## When to use / When not to use

**Use** when the stack has a `three` npm dependency or an import from
`'three'`/`'three/webgpu'`/`'three/addons'`, the task builds or modifies a
WebGL/WebGPU 3D scene, or the task names Three.js, a Three.js class, or TSL.
**Do not use** for generic frontend component/state structure with no 3D
rendering involved (route to `SK-FE-001`), 2D-only Canvas/SVG/charting
visualization, a different WebGL/3D library (Babylon.js, PlayCanvas, raw
WebGL — this skill's content is Three.js-specific), or backend-only work.

## Knowledge

**Core object model.** A Three.js app is a directed graph: a `Renderer`
consumes a `(scene, camera)` pair and rasterizes the camera's frustum to a
canvas as a 2D image [Source: https://threejs.org/manual/#en/fundamentals].
`Scene` (an `Object3D` subclass) is the root of a hierarchical parent/child
scene graph of `Mesh`, `Light`, `Group`, and other `Object3D`-derived nodes;
children are positioned/oriented relative to their parent. A `Camera` is
only "half in half out" of the scene graph — it does not have to be a
scene-graph member to function, though as a child of another object it
moves/orients relative to that parent. A `Mesh` pairs one `Geometry` (vertex
data, stored as `BufferAttribute`/typed-array data inside `BufferGeometry` —
the only geometry representation in current Three.js) with one or more
`Material` objects (surface properties, may reference `Texture` objects);
Geometry and Material instances can be shared across multiple `Mesh`
instances [Source: https://threejs.org/manual/#en/fundamentals;
https://threejs.org/docs/pages/BufferGeometry.html.md].

**Two renderer architectures ship in parallel.** `WebGLRenderer` is the
long-established, standalone implementation — "uses WebGL 2 to display
scenes" — and does not inherit the newer `Renderer` base class.
`Renderer`/`WebGPURenderer` is the newer node-material-based architecture:
it extends the abstract `Renderer` base class, is constructed with a
pluggable Backend, tries WebGPU first and falls back to WebGL 2
automatically, and supports TSL (Three.js Shading Language — shader logic
written in JS, transpiled to WGSL/GLSL) [Source:
https://threejs.org/docs/pages/Renderer.html.md;
https://threejs.org/docs/pages/WebGPURenderer.html.md;
https://threejs.org/manual/#en/webgpurenderer]. The manual states plainly
that `WebGPURenderer` "is still in an experimental state," while
`WebGLRenderer` "is still maintained and the recommended choice for pure
WebGL 2 applications," with no plans for larger new `WebGLRenderer`
features since project focus has moved to `WebGPURenderer` [Source:
https://threejs.org/manual/#en/webgpurenderer].

**No semver — r-number releases, module loading since r147.** Three.js
ships sequential `r`-number releases (e.g. r180, r186), each mapping to an
npm `0.<r>.0` version [Source: research/knowledge-maps/version-matrix.md;
https://github.com/mrdoob/three.js/wiki/Migration-Guide]. Any
version-compatibility tooling that assumes a semver-shaped string will
misparse Three.js's version. **As of r147, ES-module loading is the only
supported way to load Three.js** — non-module global-namespace
`<script src="three.min.js">` loading is obsolete since r147, and the
legacy UMD/global build files were removed entirely at the r160→r161
transition [Source: https://threejs.org/manual/#en/fundamentals;
https://github.com/mrdoob/three.js/wiki/Migration-Guide]. A no-build-tool
install path exists via an import map pointing at the jsDelivr CDN
(`"three": "https://cdn.jsdelivr.net/npm/three@<version>/build/three.module.js"`)
[Source: https://threejs.org/manual/#en/installation].

**WebGL2 floor since r163.** `WebGLRenderer` requires WebGL 2 — "WebGL 1 is
not supported since r163" [Source:
https://threejs.org/docs/pages/WebGLRenderer.html.md]. Devices/browsers
without WebGL 2 cannot use `WebGLRenderer` at all; the official
`WebGL.isWebGL2Available()` add-on only detects and shows a fallback
message, it does not provide a WebGL1 rendering path [Source:
https://threejs.org/manual/#en/webgl-compatibility-check].

**Color-management overhaul, r152 onward.** A multi-release rollout
replaced `WebGLRenderer.outputEncoding` with `outputColorSpace`,
`Texture.encoding` with `Texture.colorSpace`, and made
`ColorManagement.enabled` default to `true` [Source:
https://github.com/mrdoob/three.js/wiki/Migration-Guide]. This is the
single largest visually-breaking change in the migration guide's history —
upgrading across r152 should be expected to produce visual regressions, not
just renamed properties.

**Clock → Timer.** `Clock` is deprecated as of the r182→r183 transition in
favor of `Timer`; `Timer` itself moved into core (no longer a separate
add-on import) as of the r178→r179 transition [Source:
https://threejs.org/docs/pages/Clock.html.md;
https://github.com/mrdoob/three.js/wiki/Migration-Guide].

**Upgrade cadence — no LTS.** No LTS release line exists. The official
Migration Guide states: "it's recommended to update the library in
increments of 10 ⚠️ ... deprecation warnings last for 10 releases" [Source:
https://github.com/mrdoob/three.js/wiki/Migration-Guide]. That is the core
version-management practice for anyone maintaining a Three.js dependency —
pin to a release and batch upgrades in tens, except `WebGPURenderer`
specifically, where the manual separately advises staying as current as
possible given its experimental status (an acknowledged tension in the
official guidance itself).

A full r-number breaking-changes table (r147 through the current release)
is in [references/breaking-changes.md](references/breaking-changes.md) —
consult it before any upgrade that crosses r147, r152, r160–161, r163,
r178–179, or r182–183.

## Decision framework

1. **Is Three.js actually warranted, or would a simpler CSS/SVG/Canvas-2D
   visualization do?** (simplest-first / anti-overengineering.) Reach for
   Three.js only when the task genuinely needs a 3D scene graph or
   GPU-accelerated rendering — not for 2D charts, diagrams, or UI effects
   that a lighter tool handles without the GPU-resource-lifecycle burden
   this skill's Anti-patterns section describes.
2. **WebGLRenderer vs. WebGPURenderer.** Default to `WebGLRenderer` for
   stability/compatibility — the manual's own guidance for "pure WebGL 2
   applications." Choose `WebGPURenderer` only when the app genuinely needs
   TSL/node materials, compute shaders, or the newer post-processing stack,
   while accepting its documented experimental status and the
   recommendation to stay on the latest release. Don't default to
   `WebGPURenderer` on a "newest is best" assumption.
3. **Upgrade cadence.** With no LTS line, follow the official 10-release
   increment cadence for routine maintenance. Treat any upgrade crossing
   r147 (module loading), r152 (color management), or r163 (WebGL2 floor)
   as requiring an explicit read of the relevant Migration Guide entries,
   never a blind version bump.
4. **Many similar objects.** Merge geometry
   (`BufferGeometryUtils.mergeGeometries()`) or use `InstancedMesh` rather
   than one `Mesh` per object once draw-call count is the actual
   bottleneck — not as a default optimization applied preemptively [Source:
   https://threejs.org/manual/#en/optimize-lots-of-objects].
5. **Render loop.** Continuous `requestAnimationFrame` rendering only for
   scenes that are actually animating; for static scenes, render-on-demand
   (re-render on control `'change'`/window `'resize'` only) is the
   documented, simpler, battery-friendlier default [Source:
   https://threejs.org/manual/#en/rendering-on-demand].

## Workflow

1. Determine the installed r-number (not a semver string) before making any
   version-specific recommendation.
2. Choose `WebGLRenderer` vs. `WebGPURenderer` per the decision framework.
3. Build/modify the scene graph (`Scene`, `Camera`, `Mesh(Geometry,
   Material)`, `Light`) per the object model above.
4. Load external assets (e.g. `GLTFLoader`) with progress/error callbacks;
   be aware of the cross-origin-loading documentation gap (see Security).
5. Choose a render-loop pattern (continuous vs. render-on-demand) based on
   whether the scene actually animates.
6. Add explicit `.dispose()` calls for any geometry/material/texture
   created and later replaced or removed.
7. For an upgrade, walk the Migration Guide entries for every r-number
   crossed, prioritizing r147/r152/r163/r178–179/r182–183 as the documented
   high-impact transitions (see
   [references/breaking-changes.md](references/breaking-changes.md)).
8. Verify (see Outputs & verification) before declaring done.

## Engineering rules

- Determine the r-number before making any version claim; never infer
  semver-style compatibility from it.
- Load Three.js only via ES modules (npm+bundler or an import map) — never
  via a legacy global `<script>` tag; that path has been obsolete since r147.
- Call `.dispose()` on any geometry, material, or texture that's replaced
  or removed at runtime — Three.js does not reclaim GPU-side memory itself.
- Don't toggle "structural" material properties (texture presence, fog,
  vertex colors, shadow map, alpha test) after first render without
  expecting a shader recompile (`material.needsUpdate = true`, documented
  as "quite slow" and a source of frame jerkiness); drive dummy values
  instead if the visual effect can be emulated that way [Source:
  https://threejs.org/manual/#en/how-to-update-things].
- Pre-allocate `BufferGeometry` buffers to a maximum size and use
  `setDrawRange()` for anything that needs to grow — buffers cannot be
  resized in place.
- For `WebGPURenderer`, use TSL/`NodeMaterial` subclasses for custom
  shaders; `ShaderMaterial`/`RawShaderMaterial`/`onBeforeCompile()` and
  `EffectComposer`-based post-processing are not supported there [Source:
  https://threejs.org/manual/#en/webgpurenderer].

## Trade-offs

`WebGLRenderer` trades cutting-edge features (compute shaders, TSL, the
newer post-processing stack) for documented stability and "no plans for
larger new features" — the safer default for most production apps today.
`WebGPURenderer` trades that stability for TSL/node-material/compute-shader
capability, at the cost of an explicitly experimental status and an
official recommendation to "upgrade to the latest version whenever
possible" — in tension with the general "upgrade in tens" guidance for the
rest of the library. Merging geometry/`InstancedMesh` reduces draw calls
but adds bookkeeping complexity — worth it once per-object `Mesh` count is
the actual bottleneck, not by default.

## Anti-patterns

- **Not disposing GPU resources** (geometries/materials/textures) loaded or
  swapped over a session — documented cost is 4–6 MB per decompressed
  1024×1024 texture alone; leaks accumulate silently since the JS garbage
  collector doesn't reclaim GPU-side memory [Source:
  https://threejs.org/manual/#en/cleanup].
- **Loading Three.js via a legacy non-module `<script>` tag** or an
  outdated global-namespace CDN URL — obsolete since r147; the official LLM
  guidance flags this pattern explicitly as "WRONG — outdated pattern"
  [Source: https://threejs.org/manual/#en/fundamentals;
  https://threejs.org/docs/llms.txt].
- **Bumping the version number across r152 (color management), r163
  (WebGL2 floor), or r147 (module loading) without reading the Migration
  Guide entries** — the color-management change in particular is the
  single largest visually-breaking change documented in the guide's
  history.
- **Resizing a `BufferGeometry`'s buffers at runtime** instead of
  pre-allocating and using `drawRange` — documented as "very costly,
  basically the equivalent to creating a new geometry" [Source:
  https://threejs.org/manual/#en/how-to-update-things].
- **Reaching for Three.js/WebGL for what's actually 2D UI/data
  visualization** — the over-engineering trap for this domain; plain
  CSS/SVG/Canvas-2D avoids the entire GPU-resource-lifecycle and
  renderer-choice burden when there is no real 3D requirement.
- **Running a perpetual `requestAnimationFrame` loop for a scene that
  isn't actually animating** — documented as wasteful of device
  power/battery; render-on-demand is the recommended alternative for
  static scenes [Source: https://threejs.org/manual/#en/rendering-on-demand].

## Security

Three.js's entire documented security policy is its `SECURITY.md`: report
vulnerabilities privately to `hello@mrdoob.com` (never as a public issue),
with "a description of the vulnerability and its impact" and reproduction
steps; the project commits to a 90-day fix window before public disclosure,
"maintained by volunteers on a reasonable-effort basis" [Source:
https://raw.githubusercontent.com/mrdoob/three.js/dev/SECURITY.md]. That is
the full extent of what's documented — there is no separate, more detailed
security guide in the manual or API docs.

**Unresolved:** no official page covers cross-origin texture/asset loading
security — `crossOrigin` handling on loaders, canvas tainting from
cross-origin images, or CSP guidance for shader/WebGL/WebGPU contexts is
not documented by Three.js itself [Source: research/technologies/threejs.md
§7]. Treat this as an open gap, not a solved concern, when loading assets
from third-party origins.

**Scope boundary:** Three.js executes entirely client-side in the browser
sandbox; classic backend security concerns (SQL injection, auth, secrets
handling) are out of scope for the library itself. Deep cross-cutting
threat modeling is owned by security-engineering (see
[skill-catalog.md](../../core/taxonomy/skill-catalog.md)), not restated
here.

## Performance

Each 1024×1024 texture costs 4–6 MB of memory once decompressed for GPU
use, regardless of on-disk compressed size — this is why explicit disposal
(Engineering rules, Anti-patterns) matters: the GPU/JS garbage collector
does not automatically reclaim GPU-side memory for geometries, materials,
or textures [Source: https://threejs.org/manual/#en/cleanup]. For scenes
with many similar objects, merge geometries
(`BufferGeometryUtils.mergeGeometries()`) or use `InstancedMesh` to reduce
draw-call count — "drawing 2 things has more overhead than drawing 1 even
if the results are the same" [Source:
https://threejs.org/manual/#en/optimize-lots-of-objects]. For
non-continuously-animating scenes, render-on-demand avoids wasting device
power/battery compared to a perpetual `requestAnimationFrame` loop [Source:
https://threejs.org/manual/#en/rendering-on-demand]. `renderer.info`
exposes GPU memory/draw-call statistics for debugging; set
`.info.autoReset = false` with a manual `.info.reset()` for multi-pass
rendering [Source: https://threejs.org/docs/pages/WebGLRenderer.html.md].
Deep cross-cutting performance method is owned by performance-engineering
(see [skill-catalog.md](../../core/taxonomy/skill-catalog.md)).

## Testing

Three.js's own official testing documentation is aimed at contributors to
the library itself (`npm run test`/`test-e2e`, a screenshot-comparison-based
e2e suite), not at application developers testing Three.js-based apps
[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/.github/CONTRIBUTING.md].
**Unresolved:** no official first-party guide for how application
developers should unit-test or visually-regression-test their own
Three.js-based apps (headless-WebGL harnesses, canvas pixel-diffing,
WebGPU CI strategies) was found in this research — state this gap rather
than inventing a testing recommendation. Deep test-strategy method is owned
by testing-strategy (see
[skill-catalog.md](../../core/taxonomy/skill-catalog.md)).

## Failure handling

- If the installed r-number cannot be determined, ask for it or explicitly
  state the r-number range the guidance assumes — never assume "latest"
  silently, and never infer compatibility from an r-number as if it were a
  semver string.
- If shell is unavailable, degrade to advisory scene/renderer code edits
  and state that a build/dev-server run was not performed.

## Escalation

- Upgrading across the r152+ color-management overhaul, the r163 WebGL2
  floor, or the r147 module-loading change requires explicit user
  confirmation before applying, since the Migration Guide documents visual
  regressions and hard compatibility breaks, not just renamed properties.

## Outputs & verification

- **Outputs:** version-correct scene/renderer/material/asset-loading code,
  r-number upgrade edits, or a renderer-choice/upgrade-cadence analysis
  with rationale.
- **Verify:** every version-specific claim is tagged with the r-number
  range it holds for; geometries/materials/textures created and later
  replaced or removed are explicitly disposed; a renderer choice states its
  rationale and, if `WebGPURenderer`, its experimental-status caveat.

## References

- [references/breaking-changes.md](references/breaking-changes.md) —
  Tier-2 full r-number breaking-changes table.
- Source list: see `skill.yaml.source_references` (Three.js official docs/
  manual/GitHub wiki, retrieved 2026-09-10, via
  `research/technologies/threejs.md`).
