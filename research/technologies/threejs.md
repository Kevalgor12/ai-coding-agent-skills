# Three.js — Deep Technology Research

Research date: 2026-09-09. Primary sources: the official documentation at
**https://threejs.org/docs/** (API reference, generated from JSDoc comments
in the `mrdoob/three.js` repository), the official manual at
**https://threejs.org/manual/**, and the official GitHub repository
**https://github.com/mrdoob/three.js** (releases, wiki migration guide,
`package.json`, `SECURITY.md`, `CONTRIBUTING.md`). Three.js also publishes
official LLM-oriented documentation dumps at `https://threejs.org/docs/llms.txt`
and `https://threejs.org/docs/llms-full.txt`, which were used as a navigation
aid and cross-checked against the underlying pages. Where a claim is
version-specific it is tagged explicitly. All claims are cited inline;
anything not found in official sources is marked "Not documented / could not
verify" rather than guessed.

## Canonical docs host and versioning note

[Source: https://threejs.org/docs/] Three.js's canonical documentation lives
at `threejs.org/docs/` (API reference) and `threejs.org/manual/` (guides);
both are part of the same official site and have not moved to a different
domain as of this research date.

[Source: https://github.com/mrdoob/three.js/releases] Three.js does not use
conventional `major.minor.patch` semantic versioning for its release
identity in common usage. Releases are published as sequential integers
prefixed with `r` (e.g. `r180`, `r186`) which correspond to npm package
versions `0.180.0`, `0.186.0`, etc. — i.e. the "r-number" is the npm minor
version. [Source: https://github.com/mrdoob/three.js/wiki/Migration-Guide]
Any release can contain breaking changes (see Section 13); there is no
separate "major version" boundary that gates breaking changes the way
semver would imply.

[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/package.json]
As of this research date the `dev` branch's `package.json` reports
`"version": "0.186.0"`, `"name": "three"`. [Source:
https://api.github.com/repos/mrdoob/three.js/releases/tags/r186] The most
recent published GitHub release is **r186**, published **2026-09-08**
(one day before this research date) — confirmed via the GitHub Releases
API (`published_at: 2026-09-08T19:16:16Z`). Unresolved: a plain web search
performed during this research surfaced r180 (published 2025-09-03,
a full year earlier) as if it were "current" — that search result was
stale/wrong; the GitHub Releases API was used as the authoritative source
instead. This is flagged explicitly because it demonstrates the stated risk
of relying on non-primary or cached search results for a fast-moving
project.

---

## 1. Core concepts

[Source: https://threejs.org/manual/#en/fundamentals] Three.js describes
itself (verbatim from the official Fundamentals manual page) as: "a 3D
library that tries to make it as easy as possible to get 3D content on a
webpage." The same page states three.js is often confused with WebGL, but
clarifies: "WebGL is a very low-level system that only draws points, lines,
and triangles. To do anything useful with WebGL generally requires quite a
bit of code and that is where three.js comes in. It handles stuff like
scenes, lights, shadows, materials, textures, 3d math, all things that you'd
have to write yourself if you were to use WebGL directly."

[Source: https://threejs.org/manual/#en/fundamentals] The official manual
identifies the following as the core building blocks of a three.js app,
illustrated with a diagram of an app's object graph:
- **Renderer** — "arguably the main object of three.js. You pass a Scene and
  a Camera to a Renderer and it renders (draws) the portion of the 3D scene
  that is inside the frustum of the camera as a 2D image to a canvas."
- **Scene graph** — "a tree like structure, consisting of various objects
  like a Scene object, multiple Mesh objects, Light objects, Group,
  Object3D, and Camera objects." A Scene object "defines the root of the
  scenegraph." Children are positioned/oriented relative to their parent
  (example given: wheels as children of a car).
- **Camera** — notably documented as only "half in half out" of the
  scenegraph diagram: "unlike the other objects, a Camera does not have to
  be in the scenegraph to function," though as a child of another object it
  will move/orient relative to that parent.
- **Mesh** — "represents drawing a specific Geometry with a specific
  Material." Geometry and Material objects can be shared/reused across
  multiple Mesh instances.
- **Geometry** — "represent[s] the vertex data of some piece of geometry."
- **Material** — "represent[s] the surface properties used to draw
  geometry including things like the color to use and how shiny it is,"
  and can reference one or more Texture objects.
- **Texture** — represents images, loaded from files, generated from a
  canvas, or rendered from another scene.
- **Light** — represents different kinds of lights.

[Source: https://threejs.org/manual/#en/fundamentals] The canonical minimal
example ("Hello Cube") from the official manual:
```js
import * as THREE from 'three';

const canvas = document.querySelector('#c');
const renderer = new THREE.WebGLRenderer({antialias: true, canvas});

const fov = 75, aspect = 2, near = 0.1, far = 5;
const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
camera.position.z = 2;

const scene = new THREE.Scene();

const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({color: 0x44aa88});
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

renderer.render(scene, camera);
```

[Source: https://threejs.org/manual/#en/fundamentals] The documented render
loop pattern uses `requestAnimationFrame`, not a built-in "game loop":
```js
function render(time) {
  time *= 0.001; // convert time to seconds
  cube.rotation.x = time;
  cube.rotation.y = time;
  renderer.render(scene, camera);
  requestAnimationFrame(render);
}
requestAnimationFrame(render);
```
The manual explains: "`requestAnimationFrame` is a request to the browser
that you want to animate something... `requestAnimationFrame` passes the
time since the page loaded to our function... in milliseconds." A separate,
renderer-managed alternative, `renderer.setAnimationLoop(callback)`, is
documented on the renderer classes themselves (see Section 3) and is the
form recommended specifically for `WebGPURenderer` because of its async
initialization (see Section 2).

[Source: https://threejs.org/manual/#en/fundamentals] `fov` (field of view)
for `PerspectiveCamera` is in **degrees**, while the manual notes "most
angles in three.js are in radians but for some reason the perspective
camera takes degrees" — an explicitly documented inconsistency.

[Source: https://threejs.org/docs/pages/Object3D.html.md] `Object3D` is
documented as "the base class for most objects in three.js and provides a
set of properties and methods for manipulating objects in 3D space." It
inherits from `EventDispatcher`.

## 2. Architecture

[Source: https://threejs.org/manual/#en/fundamentals] Architecturally, a
three.js application is a directed graph: a `Scene` (subclass of
`Object3D`) is the root of a hierarchical parent/child scenegraph containing
`Mesh`, `Light`, `Group`, and other `Object3D`-derived nodes; a `Renderer`
sits partly outside this graph and consumes `(scene, camera)` pairs to
rasterize a 2D image.

[Source: https://threejs.org/docs/pages/Renderer.html.md] As of the current
release line, three.js ships **two parallel renderer architectures**:
1. **`WebGLRenderer`** — [Source:
   https://threejs.org/docs/pages/WebGLRenderer.html.md] a standalone,
   long-established implementation ("This renderer uses WebGL 2 to display
   scenes") that does **not** inherit from the newer `Renderer` base class
   (confirmed by the absence of an "Inheritance:" line on its docs page,
   unlike `WebGPURenderer`).
2. **`Renderer` / `WebGPURenderer`** — [Source:
   https://threejs.org/docs/pages/WebGPURenderer.html.md] a newer,
   node-material-based renderer architecture. `WebGPURenderer` extends the
   abstract `Renderer` base class and is constructed with a pluggable
   **Backend** (WebGPU or WebGL 2). "By default, the renderer tries to use
   a WebGPU backend if the browser supports WebGPU. If not, `WebGPURenderer`
   falls back[s] to a WebGL 2 backend."

[Source: https://threejs.org/manual/#en/webgpurenderer] The official
WebGPU manual page states the design intent directly: "`WebGPURenderer` is
designed to be the modern alternative to the long-standing `WebGLRenderer`.
Its primary goal is to use WebGPU... However, it's built to be a universal
renderer... Providing a WebGL 2 backend as a fallback is a crucial design
decision since it allows applications to benefit from WebGPU but without
sacrificing the support for devices which only support WebGL 2."
`WebGPURenderer` ships with "a new node-based material system," support for
**TSL** (Three.js Shading Language — write shader logic in JavaScript,
transpiled to WGSL or GLSL depending on backend), and "a new
post-processing stack with built-in Multiple Render Targets (MRT) support."

[Source: https://threejs.org/manual/#en/webgpurenderer] Architecturally
significant maintenance-status statement from the same official page: "The
renderer itself is still in an experimental state although its maturity
level has been greatly improved in the last years... it's recommended to
upgrade to the latest version whenever possible." And on `WebGLRenderer`'s
status: "`WebGLRenderer` is still maintained and the recommended choice for
pure WebGL 2 applications. However, keep in mind that there are no plans to
add larger new features to the renderer since the project's focus is now on
`WebGPURenderer`."

[Source: https://threejs.org/manual/#en/webgpurenderer] `WebGPURenderer`
initializes asynchronously; the manual recommends using
`renderer.setAnimationLoop()` rather than manual `requestAnimationFrame`,
"since this approach will automatically ensure the renderer is initialized
when rendering the first frame." If not using `setAnimationLoop`, code must
explicitly `await renderer.init()` before the first `render()` call.

[Source: https://threejs.org/docs/pages/BufferGeometry.html.md] Geometry
data is architecturally stored as `BufferAttribute`/typed-array data inside
`BufferGeometry` (the only geometry representation in current three.js —
the legacy non-buffer `Geometry` class was removed in earlier releases per
the migration guide history, see Section 13).

[Source: https://threejs.org/manual/#en/how-to-update-things] `BufferGeometry`
buffers are fixed-size once allocated: "you cannot resize buffers (this is
very costly, basically the equivalent to creating a new geometry)... there
is no way to create a BufferGeometry that can efficiently be extended
indefinitely." Apps needing growth must pre-allocate a maximum buffer size
and use `geometry.setDrawRange()` to control how much of it is drawn.

[Source: https://threejs.org/manual/#en/how-to-update-things] `Material`
architecture separates "cheap" runtime-mutable state (uniform values,
`depthTest`, `blending`, `polygonOffset`, etc. — sent to the GPU every
frame) from "expensive" structural state (number/type of uniforms,
presence of a texture, fog, vertex colors, morphing, shadow map, alpha
test, transparency) that, if changed after first render, requires setting
`material.needsUpdate = true` and triggers **recompilation of the shader
program** — documented as "quite slow" and a possible source of frame
jerkiness, "especially on Windows, as shader compilation is slower in
DirectX than OpenGL."

[Source: https://threejs.org/docs/pages/Object3D.html.md] Matrix
architecture: every `Object3D` has a local `.matrix` and a `.matrixWorld`;
by default (`matrixAutoUpdate = true`) the engine recomputes the local
matrix from position/rotation/scale every frame, and world matrices are
propagated down the scenegraph.

## 3. APIs

[Source: https://threejs.org/docs/] The full API surface is organized into
**Core** categories (Animation, Audio, Cameras, Core, Extras, Geometries,
Helpers, Lights, Loaders, Materials, Math, Nodes, Objects, Renderers,
Scenes, Textures) plus an **Addons** section (Controls, Effects, Exporters,
additional Loaders, Physics helpers, post-processing passes, CSS renderers,
and the extensive **TSL** node-function reference — the docs describe TSL
as having "500+ TSL functions and nodes"). [Source:
https://threejs.org/docs/pages/{Name}.html.md, referenced via
https://threejs.org/docs/llms.txt] Individual class pages are also
published in plain-markdown form at `https://threejs.org/docs/pages/{ClassName}.html.md`
— an official, machine-readable mirror of the same reference content.

[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md] Selected
**`WebGLRenderer`** API surface (constructor takes an `Options` object):
- Key properties: `.domElement` (canvas), `.outputColorSpace`
  (`SRGBColorSpace | LinearSRGBColorSpace`), `.toneMapping` (one of
  `NoToneMapping`, `LinearToneMapping`, `ReinhardToneMapping`,
  `CineonToneMapping`, `ACESFilmicToneMapping`, `CustomToneMapping`,
  `AgXToneMapping`, `NeutralToneMapping`), `.toneMappingExposure`,
  `.shadowMap`, `.info` (GPU memory / draw-call statistics, resettable via
  `renderer.info.reset()`), `.xr` (a `WebXRManager`), `.capabilities`,
  `.debug` (`checkShaderErrors`, `onShaderError`).
- Key methods: `.render(scene, camera)`, `.setSize(width, height,
  updateStyle)`, `.setPixelRatio(value)`, `.setAnimationLoop(callback)`,
  `.setClearColor(color, alpha)`, `.compile(scene, camera, targetScene)` /
  `.compileAsync(...)`, `.dispose()` ("Frees the GPU-related resources
  allocated by this instance. Call this method whenever this instance is no
  longer used in your app."), `.forceContextLoss()` /
  `.forceContextRestore()`, `.readRenderTargetPixels(...)` /
  `.readRenderTargetPixelsAsync(...)`, `.getContext()` (returns the raw
  `WebGL2RenderingContext`).
- Constructor `Options` include `canvas`, `context`, `precision`
  (`'highp'|'mediump'|'lowp'`, default `'highp'`), `alpha` (default
  `false`), `premultipliedAlpha` (default `true`), `antialias` (default
  `false`), `stencil` (default `false`), `preserveDrawingBuffer` (default
  `false`), `powerPreference` (default `'default'`),
  `failIfMajorPerformanceCaveat` (default `false`), `depth` (default
  `true`), `logarithmicDepthBuffer` (default `false`), `reversedDepthBuffer`
  (default `false`, requires the `EXT_clip_control` WebGL extension).

[Source: https://threejs.org/docs/pages/WebGPURenderer.html.md] Selected
**`WebGPURenderer`** API surface: inherits the `Renderer` base class API;
constructor takes an `Options` object including `logarithmicDepthBuffer`
and (documented in the manual, Section 2 above) `forceWebGL: true` to
force the WebGL 2 backend for testing/compatibility. Common methods known
from `WebGLRenderer` such as `clear()`, `setRenderTarget()`, and
`dispose()` are present. [Source:
https://threejs.org/manual/#en/webgpurenderer] `await renderer.init()` must
be called before synchronous rendering if not using `setAnimationLoop()`.

[Source: https://threejs.org/docs/pages/Object3D.html.md] Selected
**`Object3D`** API surface: properties `.children`, `.matrix`,
`.matrixWorld`, `.matrixAutoUpdate` (engine default configurable via
`Object3D.DEFAULT_MATRIX_AUTO_UPDATE`), `.castShadow` / (implied)
`.receiveShadow`, `.frustumCulled` (default `true`), `.layers`, `.id`,
`.isObject3D` (type-testing flag), `.animations`,
`.customDepthMaterial`/`.customDistanceMaterial` (only relevant for
`WebGLRenderer` shadow rendering).

[Source: https://threejs.org/docs/pages/Mesh.html.md] **`Mesh`**
constructor: `new Mesh(geometry: BufferGeometry, material: Material |
Array<Material>)`. Properties include `.geometry`, `.material` (default
`MeshBasicMaterial` if omitted), `.count` (number of instances — "Can only
be used with `WebGPURenderer`" [version/renderer-specific]),
`.morphTargetDictionary` / `.morphTargetInfluences`. Methods:
`.getVertexPosition()`, `.intersectsFrustum()`, `.raycast()`,
`.updateMorphTargets()`.

[Source: https://threejs.org/docs/pages/Scene.html.md] **`Scene`**
(extends `Object3D`): properties `.background` (Color | Texture — cube or
equirectangular textures act as a skybox), `.backgroundBlurriness`,
`.backgroundIntensity`, `.backgroundRotation`, `.environment` (env map for
all physical materials in the scene), `.environmentIntensity`,
`.environmentRotation`, `.fog` (`Fog | FogExp2`), `.overrideMaterial`
(forces everything in the scene to render with one material, unless a
material sets `Material#allowOverride = false`).

[Source: https://threejs.org/docs/pages/Raycaster.html.md] **`Raycaster`**
constructor: `new Raycaster(origin, direction, near, far)`. Used for mouse
picking. `.layers` can restrict which objects are tested (example given:
`raycaster.layers.set(1); object.layers.enable(1);`).

[Source: https://threejs.org/docs/pages/Clock.html.md]
[VERSION-SPECIFIC, deprecated as of r183] The `Clock` class's constructor
is explicitly marked "**Deprecated:** since r183" in the current API
reference. [Source:
https://github.com/mrdoob/three.js/wiki/Migration-Guide#182--183] The
migration guide entry for 182→183 states: "`Clock` has been deprecated.
Please use `Timer` instead." [Source:
https://github.com/mrdoob/three.js/wiki/Migration-Guide#178--179] `Timer`
itself "has been moved into the core" as of the 178→179 transition and no
longer needs to be imported as a separate add-on.

## 4. Configuration

[Source: https://threejs.org/manual/#en/installation] The official manual
documents two supported ways to install/configure a project:
1. **NPM + a build tool** (documented as "the recommended approach for most
   users"): `npm install --save three`, plus a bundler such as Vite
   (`npm install --save-dev vite`). With a build tool, "importing local
   JavaScript files and npm packages should work out of the box, without
   import maps."
2. **Import maps + CDN**, for projects without a build step, e.g.:
   ```html
   <script type="importmap">
   {
     "imports": {
       "three": "https://cdn.jsdelivr.net/npm/three@<version>/build/three.module.js",
       "three/addons/": "https://cdn.jsdelivr.net/npm/three@<version>/examples/jsm/"
     }
   }
   </script>
   ```
   [Source: https://threejs.org/manual/#en/fundamentals] "As of r147, this
   is the only way to load three.js properly" — i.e. non-module
   `<script src="...three.min.js">` global-namespace loading is documented
   as obsolete since r147 [VERSION-SPECIFIC].

[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/package.json]
The published npm package (`three`, currently `0.186.0`) declares
`"type": "module"` with these `exports` map entries (directly from
`package.json`, current `dev` branch at research time):
```json
{
  ".": { "import": "./build/three.module.js", "require": "./build/three.cjs" },
  "./examples/jsm/*": "./examples/jsm/*",
  "./addons": "./examples/jsm/Addons.js",
  "./addons/*": "./examples/jsm/*",
  "./webgpu": "./build/three.webgpu.js",
  "./tsl": "./build/three.tsl.js"
}
```
This confirms distinct entry points/builds for the classic `three` (WebGL)
module vs. `three/webgpu` and `three/tsl`. [Inference, not confirmed in a
single docs prose page — synthesized directly from the `package.json`
`exports` field, which is itself an official, primary-source artifact.]

[Source: https://threejs.org/manual/#en/webgpurenderer] To use
`WebGPURenderer`, the manual instructs changing the import specifier and
import map:
```js
import * as THREE from 'three/webgpu';
```
```html
<script type="importmap">
{
  "imports": {
    "three": "../build/three.webgpu.js",
    "three/webgpu": "../build/three.webgpu.js",
    "three/tsl": "../build/three.tsl.js",
    "three/addons/": "./jsm/"
  }
}
</script>
```

[Source: https://threejs.org/manual/#en/installation] For TypeScript,
the manual states: "Community-maintained TypeScript type definitions for
three.js are available at [three-types/three-ts-types]" — i.e. official
docs point to a **community-maintained** (not first-party) `.d.ts` package
as of this research date; this is explicitly not bundled by the core
project according to the manual's own phrasing. Unresolved: whether
first-party types have since been added directly to the `three` package is
not confirmed by this fetch of the Installation page alone — the manual
text says "community-maintained," which was treated as authoritative for
this research pass.

[Source: https://threejs.org/manual/#en/webgl-compatibility-check]
Renderer/browser-capability configuration: three.js ships an official
add-on for feature detection —
```js
import WebGL from 'three/addons/capabilities/WebGL.js';
if ( WebGL.isWebGL2Available() ) {
  animate();
} else {
  document.getElementById('container').appendChild(WebGL.getWebGL2ErrorMessage());
}
```

[Source: https://threejs.org/manual/#en/color-management] Color-management
configuration: `THREE.ColorManagement.enabled` (boolean, "enabled by
default") governs whether hex/CSS color inputs are auto-converted between
color spaces; `WebGLRenderer.outputColorSpace` and `Texture.colorSpace` are
the per-object color-space configuration points (see Section 6/13 for the
historical migration of this system).

## 5. Recommended patterns

[Source: https://threejs.org/manual/#en/cleanup] Because "three.js can not
automatically clean these resources up" (GPU-backed geometries, textures,
materials — WebGL's design leaves this to the app), the manual's
recommended pattern is to call `.dispose()` explicitly on
geometries/textures/materials when no longer needed, and it presents an
official `ResourceTracker` helper pattern (`track()`/`untrack()`/`dispose()`
wrapping a `Set`) to reduce the bookkeeping burden — see full excerpt under
Section 8 (Performance) and Section 6 (Anti-patterns) below.

[Source: https://threejs.org/manual/#en/rendering-on-demand] For static
(non-continuously-animating) scenes, the manual explicitly recommends
**render-on-demand** instead of a perpetual `requestAnimationFrame` loop:
"rendering continuously is a waste of the devices power and if the user is
on portable device it wastes the user's battery." The pattern: render once
at startup, then re-render only on `OrbitControls`' `'change'` event and on
window `'resize'`, guarding against re-entrant renders with a
`renderRequested` boolean flag when `controls.enableDamping = true` is
used (damping needs its own animation-frame-driven `controls.update()`
calls, which would otherwise recurse).

[Source: https://threejs.org/manual/#en/optimize-lots-of-objects] For scenes
with many similar objects, the manual's documented optimization pattern is
**merging geometry** via `BufferGeometryUtils.mergeGeometries()`
(from the official `three/addons` utilities) — because "[e]very Mesh you
create... represents 1 or more requests by the system to draw something.
Drawing 2 things has more overhead than drawing 1 even if the results are
the same." [Inference, not confirmed in the fetched excerpt: `InstancedMesh`
is also documented elsewhere in the API reference (Section 3's
llms.txt-derived Essential API list) as the object-level API for rendering
many instances of one geometry/material efficiently, but this research
pass did not fetch the full "Optimizing Lots of Objects Animated" page
text to confirm the manual's exact recommended boundary between merged
static geometry vs. `InstancedMesh` vs. per-object `Mesh`.]

[Source: https://threejs.org/manual/#en/how-to-update-things] Recommended
pattern for static (non-moving) objects: set `object.matrixAutoUpdate =
false` and call `object.updateMatrix()` manually, avoiding the default
per-frame automatic matrix recomputation for objects that never move.

[Source: https://threejs.org/manual/#en/libraries-and-plugins] The official
manual explicitly lists community framework wrappers as an approved
integration pattern rather than discouraging them, including:
**react-three-fiber** ("React components for 3D graphics built on Three"),
**Threlte** (Svelte), **TresJS** (Vue), **A-Frame**, **Lume**, and
**Needle Engine**, alongside physics engines (`cannon-es`, `rapier`,
`ammo.js`, Jolt), `three-mesh-bvh` (raycast performance), and
`three-gpu-pathtracer`. The page caveats: "This list and the associated
packages are maintained by the community and not guaranteed to be up to
date."

[Source: https://threejs.org/manual/#en/webgpurenderer] Recommended
pattern for new custom shader work: use **TSL** (Three.js Shading Language)
with `NodeMaterial` subclasses (e.g. `MeshStandardNodeMaterial`) rather
than raw GLSL string manipulation or `onBeforeCompile()` hacks — the
official LLM guidance page states this explicitly (see Section 16).

## 6. Anti-patterns

[Source: https://threejs.org/manual/#en/cleanup] **Not disposing GPU
resources.** Documented directly: "Most three.js apps load resources at
init time and then use those resources forever until the page is closed.
But, what if you want to load and change resources over time? Unlike most
JavaScript, three.js can not automatically clean these resources up. The
browser will clean them up if you switch pages but otherwise it's up to
you to manage them." Failing to call `.dispose()` on geometries, textures,
and materials that are replaced/removed at runtime is an explicitly
documented resource-leak anti-pattern, given as costing "4 to 6meg of
memory" per uncompressed 1024×1024 texture.

[Source: https://threejs.org/manual/#en/how-to-update-things] **Toggling
"structural" material properties at runtime without expecting a shader
recompile.** Changing whether a material has a texture, uses fog, vertex
colors, morphing, a shadow map, or alpha test after the first render
forces a full shader program rebuild via `material.needsUpdate = true`,
documented as "quite slow and induce jerkiness in framerate." The manual's
suggested workaround/anti-pattern-avoidance is to keep the shader variant
constant and instead drive "dummy" values (zero-intensity lights, white
textures, zero-density fog) to emulate the visual effect of toggling a
feature.

[Source: https://threejs.org/manual/#en/how-to-update-things] **Resizing
`BufferGeometry` buffers at runtime.** "You cannot resize buffers (this is
very costly, basically the equivalent to creating a new geometry)" — the
documented correct approach is to pre-allocate a maximum-size buffer and
use `drawRange` instead of growing the underlying typed array.

[Source: https://threejs.org/manual/#en/webgpurenderer] **Assuming
`ShaderMaterial`/`RawShaderMaterial`/`onBeforeCompile()` GLSL customizations
port directly to `WebGPURenderer`.** The manual states plainly: "Custom
materials based on `ShaderMaterial`, `RawShaderMaterial` and modifications
of built-in materials via `onBeforeCompile()` are not supported in
`WebGPURenderer`. This part of your application must be ported to node
materials and TSL." Likewise `EffectComposer`-based post-processing chains
are not supported under `WebGPURenderer`, which has "a new, more modern
post-processing stack" using TSL node composition instead.

[Source: https://threejs.org/manual/#en/fundamentals] **Loading three.js
via a classic non-module `<script>` tag / outdated CDN URL pattern.** The
official LLM guidance (Section 16 below) flags this explicitly as "WRONG —
outdated pattern," contrasting it with the import-map pattern.

[Source: https://threejs.org/manual/#en/rendering-on-demand] **Always
running a perpetual `requestAnimationFrame` loop even for static scenes** —
documented as wasteful of device power/battery, with render-on-demand as
the recommended alternative (Section 5).

## 7. Security

[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/SECURITY.md]
Three.js's official security policy (`SECURITY.md` in the GitHub repo)
states: "If you have discovered a security vulnerability in this project,
please report it privately. **Do not disclose it as a public issue.**"
Reports should be sent to `hello@mrdoob.com`, with "a description of the
vulnerability and its impact" and reproduction steps. The policy adds:
"This project is maintained by volunteers on a reasonable-effort basis. As
such, we ask that you give us 90 days to work on a fix before public
exposure." This is the entirety of the project's documented security
policy — there is no separate, more detailed "Security" guide page in the
manual or API docs found during this research pass.

[Source: https://threejs.org/docs/pages/Texture.html.md /
https://threejs.org/manual/#en/loading-3d-models] Not documented / could
not verify: this research pass did not locate an official, dedicated page
covering cross-origin texture/asset loading security (e.g. `crossOrigin`
attribute handling on loaders, canvas tainting from cross-origin images,
or Content-Security-Policy guidance for shader compilation/WebGL/WebGPU
contexts). These are commonly-discussed community topics for WebGL/Canvas
apps generally, but this research did not confirm an official three.js
page addressing them directly, so no citation is given — flagged as
**Unresolved** rather than fabricated.

[Inference, not confirmed in docs] Because three.js primarily executes
client-side in the browser sandbox, most classic "backend security"
concerns (SQL injection, auth, secrets handling) are out of scope for the
library itself; the closest first-party guidance is the general
vulnerability-disclosure policy above.

## 8. Performance

[Source: https://threejs.org/manual/#en/optimize-lots-of-objects] The
manual's dedicated performance article on scenes with many objects opens
by framing the core cost model: "Every Mesh you create and three.js
represents 1 or more requests by the system to draw something. Drawing 2
things has more overhead than drawing 1 even if the results are the same
so one way to optimize is to merge meshes." The documented technique uses
`BufferGeometryUtils.mergeGeometries()` (an official `three/addons`
utility) to combine many small geometries into fewer draw calls.

[Source: https://threejs.org/manual/#en/rendering-on-demand] Render-on-demand
(Section 5) is documented explicitly as a battery/performance optimization
for non-continuously-animated scenes.

[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md] The renderer
exposes `.info` (a `WebGLRenderer~Info` object) "hold[ing] a series of
statistical information about the GPU memory and the rendering process.
Useful for debugging and monitoring." By default it resets every render
call; for multi-pass rendering (e.g. post-processing) the docs recommend
`renderer.info.autoReset = false` plus a manual `renderer.info.reset()`
call once per completed frame.

[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md] The
`debug.checkShaderErrors` flag is documented with an explicit
performance/dev-tradeoff note: "It may be useful to disable this check in
production for performance gain. It is strongly recommended to keep these
checks enabled during development."

[Source: https://threejs.org/manual/#en/cleanup] Memory-cost figures given
directly by the manual: "A 3D model might be 1 to 20 meg memory for all of
its vertices... Each 1024x1024 texture takes 4 to 6meg of memory" once
decompressed for GPU use, regardless of the on-disk compressed (e.g. JPG)
size — motivating the disposal patterns in Section 5/6.

[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md]
`logarithmicDepthBuffer` option is documented with a performance caveat:
"this setting uses `gl_FragDepth` if available which disables the Early
Fragment Test optimization and can cause a decrease in performance" — an
explicitly documented perf/correctness tradeoff for scenes with huge scale
differences.

## 9. Testing

[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/.github/CONTRIBUTING.md]
Three.js's official testing documentation is aimed at **contributors to
the three.js library itself**, not at application developers testing
three.js-based apps: `CONTRIBUTING.md` documents `npm run test` (lint +
unit tests, via `npm run lint` and `npm run test-unit`) and
`npm run test-e2e` (an end-to-end suite that "can take quite a long time
and installs ~200 MB Chromium browser," "primarily intended to be run only
by GitHub Actions"). The r186 changelog (Section 13) additionally shows
active work on "GPU-native unit tests for TSL" and screenshot-based
example regression testing ("Update screenshots," "Stabilize input and
video screenshots").

[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/.github/CONTRIBUTING.md]
The project's own e2e strategy is screenshot-comparison-based: "It's good
to also add an example and screenshot for it, for showing how it's used
and for end-to-end testing," and "If you modify existing code, run
relevant examples to check they didn't break and there wasn't a
performance regression."

Not documented / could not verify: an official, first-party guide for how
*application developers* (as opposed to three.js contributors) should
unit-test or visually-regression-test their own three.js-based
applications (e.g. recommended headless-WebGL test harnesses, canvas
pixel-diffing tools, or WebGPU CI strategies for consumer apps) was not
found in the manual's table of contents during this research pass. This
gap is worth flagging explicitly per this project's "do not pad" rule
rather than inferring recommendations that aren't in the docs.

## 10. Deployment

[Source: https://threejs.org/manual/#en/installation] The manual documents
a standard static-site build/deploy flow: "Every three.js project needs at
least one HTML file... and a JavaScript file to run your three.js code,"
with an optional `public/` (a.k.a. "static") folder for textures, audio,
and 3D models that "are pushed to the website unchanged." A build tool
(Vite is used as the canonical example) is used in development (`npx vite`
/ `npm run dev`) and the resulting build output is what gets deployed; the
manual notes `node_modules/` "is used only during development, and
shouldn't be uploaded to your web hosting provider or committed to version
history."

[Source: https://threejs.org/manual/#en/installation] For the no-build-tool
path, deployment is simply hosting static files referenced by an import
map pointing at either a CDN (`cdn.jsdelivr.net/npm/three@<version>/...`)
or self-hosted copies of `three.module.js` / `examples/jsm/`.

[Inference, not confirmed in docs] Because three.js is purely a
client-side rendering library with no server component, "deployment" in
the traditional server/infra sense (databases, servers, containers) does
not apply — deployment is equivalent to standard static-asset web hosting,
which is exactly what the Installation page documents. No dedicated
"Deployment" or "Production build" manual page beyond Installation was
found; this is treated as the full extent of official deployment guidance
rather than padded further.

## 11. Migration

[Source: https://github.com/mrdoob/three.js/wiki/Migration-Guide] Three.js
maintains an official, actively-updated **Migration Guide** on its GitHub
wiki, with one section per version-to-version transition, going back many
releases. The guide opens with an explicit official recommendation on
upgrade cadence: **"When updating old projects, it's recommended to update
the library in increments of 10 ⚠️ ... Updating in steps helps manage API
changes, as deprecation warnings last for 10 releases."** [VERSION-POLICY,
applies generally] This "10-release deprecation window" is the project's
documented compatibility/migration policy in lieu of semver-style major
versions.

There is no dedicated "migrating from a comparable alternative" guide
(e.g. from Babylon.js or PlayCanvas) in the official docs found during
this research — migration coverage is exclusively **version-to-version**
within three.js itself. See Section 13 for the specific breaking-change
content of this guide, which is the actual substance of "migration" for
this library per official docs.

## 12. Version information

[Source: https://api.github.com/repos/mrdoob/three.js/releases (GitHub
Releases API)] Confirmed recent release history (tag → `published_at`):

| Tag | Published (UTC) |
|---|---|
| r186 | 2026-09-08T19:16:16Z |
| r185 | 2026-07-01T23:22:26Z |
| r184 | 2026-04-16T16:49:08Z |
| r183 | 2026-02-20T15:31:38Z |
| r182 | 2025-12-10T16:46:04Z |
| r181 | 2025-11-19T04:42:16Z |
| r180 | 2025-09-03T11:48:45Z |
| r179 | 2025-08-02T00:55:52Z |

[Source: same GitHub Releases API data] **Current stable version as of this
research date (2026-09-09): r186 / npm `0.186.0`**, published one day prior
to this research. [Source:
https://raw.githubusercontent.com/mrdoob/three.js/dev/package.json]
Confirmed against `package.json` on the `dev` branch (`"version":
"0.186.0"`).

[Source: same table] **Release cadence**: releases are not on a strict
fixed schedule. Observed real gaps in the table above range from
approximately 4 weeks (r179→r180) up to roughly 11 weeks (r182→r183,
r184→r185). [Inference, not confirmed in a single docs prose statement:
averaging the eight data points above gives roughly a 5–9 week
cadence, but three.js does not publish an explicit "we release every N
weeks" policy statement in the docs pages fetched during this research —
this is a description of observed release timestamps, not a documented
SLA.]

[Source: https://github.com/mrdoob/three.js/wiki/Migration-Guide] There is
**no LTS (long-term-support) release line** documented. The project's only
documented support/compatibility mechanism is the "update in increments of
10, deprecation warnings last 10 releases" policy quoted in Section 11 —
i.e. rolling support via deprecation windows rather than parallel
maintained release branches.

[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md] Browser/API
support floor, version-specific: "WebGL 1 is not supported since `r163`"
— i.e. `WebGLRenderer` requires **WebGL 2** as of r163 onward
[VERSION-SPECIFIC].

## 13. Breaking changes

[Source: https://github.com/mrdoob/three.js/wiki/Migration-Guide] All
entries below are quoted/paraphrased directly from the official GitHub
wiki Migration Guide, the canonical source for three.js breaking changes.
Selected recent transitions (most recent first) — this is not the full
guide, which extends back many more versions:

**186 → 187** [VERSION-SPECIFIC, next/unreleased-at-fetch-time entry
visible in the guide]: `WebGLRenderer.setViewport()` and
`.setScissor()` no longer scale by pixel ratio when a render target is
bound.

**185 → 186** (current stable, r186):
- `Object3D` gained a `.dispose()` method; custom `Object3D` subclasses
  with their own `dispose()` must call `super.dispose()`.
- `GTAONode`'s distance model changed; `distanceExponent` and
  `distanceFallOff` are deprecated and now no-ops.
- `BufferGeometryUtils.toTrianglesDrawMode()` now mutates the geometry
  **in-place** instead of cloning it — apps relying on the old clone
  behavior must manually `.clone()` first.
- `LightProbeGrid` renamed to `LightProbeGridWebGL`; `LightProbeGridHelper`
  to `LightProbeGridHelperWebGL`.
- `PCFSoftShadowMap` with `WebGPURenderer` was **removed**; use
  `PCFShadowMap`, "which is now soft as well."
- `SimplifyModifier` reimplemented on `meshoptimizer` (different output
  mesh) and `.modify()` is now **async**.
- `Source` renamed to `TextureSource`.
- `Sky`/`SkyMesh` `up` uniform removed; always assumes +Y up now.

**184 → 185**:
- `WebGPURenderer` premultiplied-alpha implementation changed — apps
  seeing blending regressions should configure an opaque `Scene.background`
  or clear color.
- `SSAAPassNode.clearColor`/`.clearAlpha` removed (must set on the
  renderer).
- `SVGLoader.createShapes()` deprecated in favor of `shapePaths.toShapes()`.
- `AnamorphicNode` removed; use `BloomNode`.
- `DRACOLoader.setDecoderConfig()` deprecated ("will always use WASM").
- `PLYLoader` now honors PLY data types (e.g. `float64` fields now produce
  `Float64Array`, previously coerced).
- `GTAONode` AO computation made "more physically correct" — output is
  darker and reaches wider; `radius`/`scale` may need lowering to
  compensate (visual regression risk on upgrade).
- `LWOLoader` deprecated.
- TSL `positionLocal` no longer reflects vertex transforms (e.g.
  `SkinnedMesh`) in `material.positionNode`; use `positionGeometry`.
- `TiledLighting` removed; use `ClusteredLighting`.
- `Matrix3.translate()/scale()/rotate()` deprecated.

**183 → 184**:
- Background/environment-map rotation behavior aligned to standard 3D
  object rotation semantics (visual-change risk on upgrade).
- `FirstPersonControls` got "a new interaction model and improved mobile
  support" (behavior change).
- `FBXLoader` now **automatically converts +Z-up models to +Y-up** — "manual
  rotations on app level can be removed" (apps compensating manually will
  now double-rotate).
- `VTKLoader` deprecated.
- `FileLoader.load()` / `ImageBitmapLoader.load()` **no longer return a
  value** — callers must use the `onLoad()` callback only.

**182 → 183**: `PostProcessing` renamed to `RenderPipeline`; `Clock`
deprecated in favor of `Timer`; `WebGLCubeRenderTarget` can no longer be
used with `WebGPURenderer` (use `CubeRenderTarget`); a "legacy gamma
correction" of `Sky`/`SkyMesh` was removed with no way to restore the old
look via parameters.

**181 → 182**: `PCFSoftShadowMap` with `WebGLRenderer` deprecated (use
`PCFShadowMap`, now soft); `WebGPURenderer`'s `colorBufferType` param
renamed to `outputBufferType`.

**180 → 181**: PBR indirect specular light computation improved
(appearance change for existing materials); rough materials (roughness >
0.5) now render brighter due to better energy conservation; several
`WebGPURenderer` async methods (`renderAsync()`, `computeAsync()`, etc.)
deprecated in favor of auto-initialization via `setAnimationLoop()` or
explicit `await renderer.init()`; **the API documentation itself switched
to a new JSDoc-generated system, and internationalization (i18n) is no
longer supported — docs are English-only from this point forward**
[meta/documentation-infrastructure breaking change, notable for anyone
relying on non-English official docs].

**179 → 180**: `DepthOfFieldNode` reimplemented with a new API;
`RGBELoader` renamed `HDRLoader`; `RGBMLoader` removed entirely (migrate to
`EXRLoader`/`HDRLoader`/`HDRCubeTextureLoader`/`UltraHDRLoader`).

[Source: https://github.com/mrdoob/three.js/wiki/Migration-Guide] Older,
historically significant breaking changes documented in the same guide:
- **r160 → r161** [VERSION-SPECIFIC]: legacy `build/three.js` and
  `build/three.min.js` UMD/global-namespace build files were **removed**
  from the distribution.
- **r152 onward — Color Management overhaul** [VERSION-SPECIFIC,
  multi-release rollout]: `WebGLRenderer.outputEncoding` replaced by
  `outputColorSpace` (default `SRGBColorSpace`); `Texture.encoding`
  replaced by `Texture.colorSpace` (default `NoColorSpace`);
  `ColorManagement.enabled` became `true` by default; `sRGBEncoding` →
  `SRGBColorSpace`, `LinearEncoding` → `LinearSRGBColorSpace`. This is the
  single largest visually-breaking change documented in the guide's
  historical section and is the reason a dedicated "Color Management"
  manual page (Section 4) exists.
- **r147 and earlier**: the `examples/js` (non-module, global-namespace)
  directory was removed; only ES6-module `examples/jsm` remains
  supported — matching the "as of r147... the only way to load three.js
  properly" statement quoted in Section 4.

[Source: https://api.github.com/repos/mrdoob/three.js/releases/tags/r186]
The r186 GitHub release notes additionally show (Build section): **"Deprecate
CommonJS build"** and **"Remove minified builds"** [VERSION-SPECIFIC, r186].
Unresolved: `package.json` on the `dev` branch (fetched same day) still
lists `"main": "./build/three.cjs"` with a `require` export condition, so
the CJS build is *deprecated* but was not yet fully removed as of this
research date — the exact removal release was not identified in this
research pass.

## 14. Limitations

[Source: https://threejs.org/manual/#en/webgpurenderer] `WebGPURenderer`
is explicitly documented as still experimental: "The renderer itself is
still in an experimental state... depending on your application and scene
setup, you will encounter missing features or a better performance with
`WebGLRenderer`." Specific documented gaps: `ShaderMaterial` /
`RawShaderMaterial` / `onBeforeCompile()` are **not supported**;
`EffectComposer`-based post-processing is **not supported** (a different,
TSL-based post-processing stack must be used instead).

[Source: https://threejs.org/manual/#en/how-to-update-things]
`BufferGeometry` buffers have a hard, documented ceiling: "there is no way
to create a BufferGeometry that can efficiently be extended indefinitely"
— apps must pre-allocate a maximum vertex count.

[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md] `WebGLRenderer`
requires **WebGL 2**; WebGL 1 support was dropped as of r163
[VERSION-SPECIFIC] — devices/browsers without WebGL 2 cannot use
`WebGLRenderer` at all (mitigated only by the `WebGL.isWebGL2Available()`
detection helper in Section 4, which lets an app show a fallback message,
not actually render).

[Source: https://threejs.org/manual/#en/color-management] The color
management guide notes a platform-level limitation, not a three.js one:
"While some modern displays support wider gamuts like Display-P3, the web
platform's graphics APIs largely rely on sRGB. Applications using three.js
today will typically use only the sRGB and Linear-sRGB color spaces" — a
documented ceiling on color fidelity for typical web deployment.

[Source: https://threejs.org/manual/#en/cleanup] Manual memory management
is a structural limitation, not a bug: "three.js can not automatically
clean these resources up... it's up to you to manage them" for GPU-backed
resources — there is no garbage collector for GPU memory.

## 15. Debugging

[Source: https://threejs.org/manual/#en/debugging-javascript] Three.js has
a dedicated official manual page, **"Debugging JavaScript,"** which is
explicitly framed as general browser-devtools guidance rather than
three.js-specific tooling ("Most of this article is not directly about
THREE.js but is rather about debugging JavaScript in general"). Documented
techniques:
- Use browser devtools (Chrome/Firefox/Safari/Edge), disable cache during
  development ("Disable Cache (while DevTools is open)").
- Use the JavaScript console; `console.log()` on a three.js object (e.g. a
  loaded glTF scene root) allows interactive inspection/expansion in the
  console.
- `console.error()` for red messages with a stack trace.
- "Put data on screen": overlay `<div>`/`<pre>` elements showing live
  values (e.g. object position), or an official-pattern
  **`ClearingLogger`** class that buffers per-frame debug strings and
  clears them each render, avoiding per-value DOM element churn.

[Source: https://threejs.org/manual/#en/debugging-glsl] A companion page,
**"Debugging - GLSL,"** gives shader-specific debugging techniques (for
apps writing raw GLSL, e.g. via `ShaderMaterial`):
- Set `gl_FragColor` to a solid color (e.g. red) first, to isolate whether
  an object renders at all before debugging the actual shading logic.
- Visualize intermediate values by mapping them into the `[0,1]` color
  range, e.g. `gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1);` for normals,
  or `vec4(fract(vUv), 0, 1);` for UVs (using `fract()` to handle
  `texture.repeat > 1`).
- Inspect matrices via a breakpoint right after `renderer.render(scene,
  camera)`, checking the camera's world/projection matrices and each
  object's world matrix for `NaN`s or implausible magnitude.
- Pass suspect vertex-shader values to the fragment shader via a
  `varying` to visualize them the same way.
- Simplify: "Can you draw your data with `MeshBasicMaterial`?" as a
  known-good baseline to isolate whether an issue is shader-specific.

[Source: https://threejs.org/docs/pages/WebGLRenderer.html.md] The
renderer's `.info` object (Section 8) and `.debug.checkShaderErrors` /
`.debug.onShaderError` callback are the documented first-party
introspection/debugging hooks built into `WebGLRenderer` itself.

Not documented / could not verify: this research did not find an official
first-party browser-extension "inspector" (analogous to React/Vue
devtools) in the manual/API docs proper, though the r186 GitHub changelog
(Section 13 source) shows very active first-party development of an
"Inspector" tool (entries like "Add split screen, list grid mode and
revisions," "Support nonce and CSP compliance") under the `Addons` /
`Inspector` heading — suggesting an official debugging inspector exists in
the codebase, but this research pass did not fetch a dedicated docs page
describing its usage, so treat its existence as **[Inference, not
confirmed via a docs/manual page — only inferred from changelog entry
titles under "Inspector" in the r186 release notes]**.

## 16. Integration

[Source: https://threejs.org/docs/llms.txt] Three.js's own official
LLM-guidance file gives explicit, first-party integration/authoring rules
worth citing verbatim as they represent the project's stated current
best-practice stance:
- "Use Import Maps (Not Old CDN Patterns)" — with the exact CORRECT/WRONG
  code contrast shown in Section 4/6 above.
- Choosing between `WebGLRenderer` ("Maximum browser compatibility...
  Most examples and tutorials use this") and `WebGPURenderer` ("Custom
  shaders/materials using TSL... Compute shaders... Advanced node-based
  materials").
- Use TSL instead of raw GLSL/`onBeforeCompile()` hacks when targeting
  `WebGPURenderer`, citing benefits: "Works with both WebGL and WebGPU
  backends... No string manipulation or onBeforeCompile hacks... Type-safe,
  composable shader nodes... Automatic optimization."
- Use `NodeMaterial` subclasses (`MeshBasicNodeMaterial`,
  `MeshStandardNodeMaterial`, `MeshPhysicalNodeMaterial`,
  `LineBasicNodeMaterial`, `SpriteNodeMaterial`) when using TSL.

[Source: https://threejs.org/manual/#en/libraries-and-plugins] Officially
listed (community-maintained, but linked directly from the manual)
integration points across categories: Physics (`cannon-es`, `rapier`,
`ammo.js`, `enable3d`, `Oimo.js`, Jolt), Postprocessing (`postprocessing`
by @vanruesc, layered on top of the official
`examples/jsm/postprocessing` passes), raycast acceleration
(`three-mesh-bvh`), path tracing (`three-gpu-pathtracer`), additional
loaders (URDF, 3D Tiles, WebWorker-OBJ, IFC.js — layered on top of
official `examples/jsm/loaders`), text/UI (`troika-three-text`,
`three-mesh-ui`), particles (`three.quarks`, `three-nebula`), inverse
kinematics (`THREE.IK`, `fullik`, `closed-chain-ik`), game AI (`yuka`,
`three-pathfinding`, `recast-navigation-js`), and **framework wrappers**:
A-Frame, Lume, **react-three-fiber** (React), Threlte (Svelte), TresJS
(Vue), Needle Engine, threepipe, Giro3D, Mattercraft.

[Source: https://threejs.org/docs/llms-full.txt "Loading a GLTF Model"
example] First-party official integration pattern for loading external 3D
assets:
```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
const loader = new GLTFLoader();
loader.load('model.glb',
  (gltf) => { scene.add(gltf.scene); },
  (progress) => { console.log((progress.loaded / progress.total * 100) + '% loaded'); },
  (error) => { console.error('Error loading model:', error); }
);
```

[Source: https://threejs.org/manual/#en/webgpurenderer] Integration with
**WebXR** is documented as supported by both renderers (`.xr` property on
`WebGLRenderer`; the r186 changelog shows active `WebXR`/`WebGPURenderer`
XR work — MSAA support, camera-selection fixes, transmission-during-XR
fixes), though a full dedicated WebXR integration guide beyond the
manual's "WebXR" section (VR - Basics / Look To Select / Point To Select)
was not deeply fetched in this research pass.

## 17. Production considerations

[Source: https://threejs.org/manual/#en/webgpurenderer] For production
choice-of-renderer decisions, the manual's own guidance (already quoted in
Sections 2 and 14) is directly actionable: **use `WebGLRenderer`** for
"pure WebGL 2 applications" needing maximum stability/compatibility today,
since "there are no plans to add larger new features" to it but it "is
still maintained and the recommended choice"; **use `WebGPURenderer`**
only if the app needs TSL/node materials, compute shaders, or the newer
post-processing stack, while accepting that it "is still in an
experimental state" and forward-compatibility requires "upgrad[ing] to the
latest version whenever possible" (i.e. it is not documented as a
stable target to pin against long-term without staying current).

[Source: https://threejs.org/manual/#en/cleanup] Production memory
management: explicit resource disposal (Section 5/6/8) is a documented
production requirement for any app that loads/unloads assets during a
session (as opposed to a single static scene that lives for the page's
whole lifetime, where the browser's page-teardown cleanup is documented as
sufficient).

[Source: https://threejs.org/manual/#en/installation] Production build
output is the standard static-asset bundle produced by the app's chosen
build tool (Vite in the manual's example); `node_modules/` is explicitly
documented as **not** to be deployed ("shouldn't be uploaded to your web
hosting provider").

[Source: https://threejs.org/manual/#en/rendering-on-demand] Battery/power
consumption on portable devices is called out as a first-party production
concern, with render-on-demand as the documented mitigation (Section 5/8).

[Source: https://github.com/mrdoob/three.js/wiki/Migration-Guide] Because
any release can carry breaking or visually-altering changes (Section 13
has multiple examples of "appearance will look different now" changes to
lighting/AO/PBR math), the documented "upgrade in increments of 10"
migration policy (Section 11) is itself effectively production guidance:
pinning to a specific release and batching upgrades is the project's own
recommended strategy, rather than continuous auto-upgrading — despite the
WebGPURenderer-specific advice above to "upgrade... whenever possible" for
that experimental renderer specifically. [Note: these two pieces of
official guidance are in some tension — general apps are told to batch
upgrades in 10s, while `WebGPURenderer` users are told to stay as current
as possible — both are quoted as officially stated, and the apparent
tension is left visible rather than resolved by inference.]

[Source: https://raw.githubusercontent.com/mrdoob/three.js/dev/SECURITY.md]
Production vulnerability handling relies on the private-disclosure email
channel (`hello@mrdoob.com`) described in Section 7; there is no
documented CVE program, security advisory feed, or automated
dependency-scanning integration described in official sources found
during this research.

---

## Summary of sources cited

- https://threejs.org/docs/ — API reference index and category structure
- https://threejs.org/docs/pages/{ClassName}.html.md — individual class
  API pages (Object3D, Scene, WebGLRenderer, WebGPURenderer, Renderer,
  BufferGeometry, Mesh, Raycaster, EventDispatcher, Clock, Group,
  Material, Texture)
- https://threejs.org/docs/llms.txt and https://threejs.org/docs/llms-full.txt
  — official machine-readable documentation summaries
- https://threejs.org/manual/ — narrative guide (Fundamentals, Installation,
  Color Management, Cleanup, Debugging JavaScript, Debugging GLSL,
  Rendering on Demand, Optimize Lots of Objects, WebGPURenderer,
  How to Update Things, Libraries and Plugins, WebGL Compatibility Check)
- https://github.com/mrdoob/three.js — repository root, `package.json`,
  `SECURITY.md`, `.github/CONTRIBUTING.md`
- https://github.com/mrdoob/three.js/releases and the GitHub Releases API
  — version/release-date ground truth
- https://github.com/mrdoob/three.js/wiki/Migration-Guide — official
  breaking-change/migration record
