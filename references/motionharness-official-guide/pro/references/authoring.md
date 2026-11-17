# Authoring contract

## React and component contracts

Import authoring APIs from `@motionharness/sdk`. Read its installed declarations
for exact option types. Normal React components, props, hooks and CSS compose
normally; persistent editable instances are explicitly declared.

```tsx
import { defineComponent, defineComposition, field, Instance, Layer, basicTransformParameters, basicTransformValue } from '@motionharness/sdk';

const Title = defineComponent({
  id: 'title',
  parameters: { text: field.text({ label: '标题', default: '新品发布' }),
    ...basicTransformParameters({animations:{
      y:{keyframes:[{time:0,value:30},{time:.6,value:0,easing:'ease-out'}]},
      opacity:{keyframes:[{time:0,value:0},{time:.3,value:1}]},
    }}),
  },
  component(values) {
    return <Layer bindings="parameters" value={basicTransformValue(values)}><h1>{values.text}</h1></Layer>;
  },
});
const Poster = defineComponent({
  id: 'poster',
  parameters: {
    main: field.component({ label: '主标题', component: Title }),
    subtitle: field.component({ label: '副标题', component: Title,
      initialProps: { text: '继续探索' } }),
  },
  component({ main, subtitle }) {
    return <><Instance value={main} /><Instance value={subtitle} /></>;
  },
});
export default defineComposition({ id: 'poster', component: Poster,
  width: 1280, height: 720, fps: 30, duration: 3 });
```

The system creates identities and values. `Title` may also be used as ordinary JSX;
that alone does not create a persistent Studio-editable instance. `field.component`
references the reusable component definition, not a string lookup or a JSON tree.
Keep declaration IDs stable across implementation changes.

## Three.js and React Three Fiber

Use `ThreeCanvas` from `@motionharness/sdk/three` for 3D content. The current
integration is tested with `three@0.180.0`, `@react-three/fiber@9.8.1`,
`@types/three@0.180.0` and React/React DOM 19. Use a matching SDK/CLI and close/reopen
the project after adding the optional dependencies. Ordinary 2D projects do not need them.

```tsx
import { useTime } from '@motionharness/sdk';
import { ThreeCanvas, materialColor } from '@motionharness/sdk/three';

function Orb({ color, speed }: { color: string; speed: number }) {
  const time = useTime();
  return <mesh rotation={[0, time * speed, 0]}>
    <icosahedronGeometry args={[1, 2]} />
    <meshStandardMaterial {...materialColor(color)} roughness={0.25} />
  </mesh>;
}
// In a composition component, with values from normal declared fields:
<ThreeCanvas camera={{ position: [0, 0, 5] }}>
  <ambientLight intensity={0.5} />
  <directionalLight position={[3, 4, 5]} intensity={2} />
  <Orb color={color} speed={speed} />
</ThreeCanvas>
```

Keep Three's world coordinates/radians, R3F JSX and imports. Width/height default
to composition dimensions; explicit sizes are logical pixels. Declare editable
values with existing fields and pass them as props. `defineComponent` and `Instance`
can render 3D children and preserve local start/offset; use MotionHarness `useTime()` for that
instance's time. Put DOM/Layer outside ThreeCanvas and use `group` inside it.
Do not add a second persistent scene tree or an adapter in each authored project.

`materialColor` splits a MotionHarness CSS color into ordinary Three RGB, opacity and
transparent properties. This matters for keyframes, which may produce eight-digit
hex that Three.Color cannot parse. For emissive/uniform colors use its `.color`,
with `.opacity` applied explicitly according to the shader/material behavior.

For heavy animation, import standard R3F `useFrame` and calculate final positions
from MotionHarness time rather than accumulating deltas. The R3F clock belongs to the canvas;
first/repeated frame delta is zero and reverse seek delta is negative. Do not run
RAF, `setAnimationLoop` or a new wall clock. MotionHarness owns renderer, DPR and frame loop.

For images use standard `useLoader(TextureLoader, useAsset(image))`. The adapter
waits for its default Suspense boundary and registered MotionHarness asynchronous frame work.
An explicit nested Suspense fallback is authored content. R3F `useFrame` callbacks
must complete their rendering synchronously; register awaitable preparation with
MotionHarness `useFrame` instead. Release objects you create in effects, such as cloned
textures, PMREM targets or an EffectComposer. A positive-priority R3F frame callback
may render that composer, within the same MotionHarness frame barrier.

Set shader uniform values with current props or actual material refs. Do not
mutate a memoized uniforms props object and assume React detects its changes.
The Green Lantern example demonstrates both JSX animation and deterministic
instanced particles, plus a shader shield and standard bloom.

The first integration does not supply model-original import, video/GIF textures,
physics, R3F pointer/raycast events, WebXR or Studio 3D manipulation handles.

## Layer hierarchy

Studio's layer tree follows declared `field.component` and `field.componentList`
references, not every JSX component or DOM wrapper. An editable instance with
editable children appears as a group. `Layer` binds the current instance's
properties; it does not create another editable instance or group.

Declare only objects within the requested editing scope. Other visuals can stay
in ordinary source code. Editing structure does not prescribe render surfaces:
a shared Canvas or 3D scene can use `useInstance(reference)` to read declared
values, local time and visibility for the same frame without a separate renderer
per editable object. The shared drawing must honor the snapshot's `visible` and
use its `time` for that object's animation. Apply the parameters you declare;
`basicTransformMatrix(values)` includes rotation, skew and scale for Canvas.
Preserve shared depth, lighting, layout and effects.
The [selected-title entry](../assets/selected-title.tsx) demonstrates this in one Canvas.

- Keep flex/grid, centering, padding and reusable drawing helpers in ordinary
  React/CSS when they need no independent layer controls. A `CardLayout` helper
  can arrange editable title and image instances without becoming another instance.
- Declare a visual element directly in its meaningful owner. Bind its position,
  scale, rotation, anchor and opacity there, rather than wrapping every element in
  a one-child `TitleGroup` or `ImageGroup` just to expose those same properties.
- Keep a group when the user needs to move, trim, animate, clip or apply effects to
  its contents together. A scene controlling a title and supporting text can be
  useful even when only one child is registered as an editable instance. Nested
  groups remain valid when each supplies a distinct shared control.
- Expose requested content that needs independent selection, movement, timing or
  replacement as editable instances, and keep basic channels independently keyframeable.
  For Pro splits, follow the [conversion scope](../conversion.md#animation-keyframes)
  for which motion to turn into keys. Requested independent channels must retain
  their own controls.
  There is no fixed layer-count or nesting limit.

For example, prefer `scene -> title` over `scene -> title positioning group -> title`
when the positioning wrapper has no separate purpose. A reusable React helper around
the title can remain in the JSX without another `field.component` declaration.

In existing work, hiding a group row in the timeline is only a Studio view choice:
its children, time window, local time, layout and effects still belong to that group.
Do not delete saved instances or change their group membership merely to shorten the timeline, or infer
that a group is redundant from having one child or no keyframes. If a requested
template refactor removes a redundant wrapper, preserve instance identity and saved
edits, and account for its timing, transforms, layout, clipping and references.

## Independent basic properties

Use `field.componentList` for independently editable repeated items. When exposing
2D transform controls, use `basicTransformParameters` and `Layer`: each axis and
opacity has its own number track and easing. Layer preserves ordinary React layout; position is an
offset from its layout position. Add `basicSizeParameters(width,height)` only for
explicit dimensions. Anchor coordinates are local pixels from the layer's top-left
corner, in both saved values and keyframes. The default is `(0, 0)`; for a known
250 × 80 box use `defaults: { anchorX: 125, anchorY: 40 }` for its center. Negative
values and pivots outside the box are valid. Studio, value graphs and CLI use the
same numbers. Resizing or changing text does not implicitly rescale a saved pivot.
Do not multiply the saved anchor by the DOM size in JSX or add an editable group
just to place the pivot; normal React flex/grid and auto-sized content still work.
When adapting existing React motion, preserve its transform origin explicitly:
resolve a center or percentage origin to local pixel defaults instead of silently
replacing it with `(0, 0)`. Pixel pivots do not require flattening the React layout.

Do not replace requested independent base controls with an `entrance`, `reveal`, or
other combined progress parameter. A creation preset may write several independent
tracks. Advanced internal effects (typing, path drawing, morphing) may use composite
progress; keep requested whole-layer transforms and opacity in the base channels. `field.transform`/`Layer`
and standalone `field.geometry` data may be split explicitly; splitting
only their UI does not make their keyframes independent.

For new stock components use `Graphic`, `defineTextComponent`,
`defineMediaComponent`, and `defineContainerComponent`. Legacy names
remain available for already-authored projects. Converting old fractional anchors
requires an explicit one-time conversion of saved values and keys, not a runtime
fraction/pixel switch. Other parameter contracts must not be silently changed.
Custom parameter names can use `basicProperty` metadata and Layer `bindings`.
The semantic binding must refer to the actual editable value, not an unrelated offset.

`useTime()` reads local MotionHarness seconds. Derive the complete frame from that time;
avoid autonomous timers, CSS animation clocks and accumulating elapsed state.
Source declarations are evaluated after normal compilation; do not encode metadata
in syntax intended for an AST interpreter.

For a finite set of saved values, use `field.select` rather than free text:

```tsx
field.select({
  label: '入场方向',
  default: 'left',
  options: [{ label: '从左', value: 'left' }, { label: '从右', value: 'right' }],
  presentation: 'buttons', // omit for a dropdown
});
```

Keep option values stable; labels and ordering may change without rewriting saved
values. When `animatable: true`, choices switch at keyframes rather than interpolate.
Removing a value still used by an instance or keyframe requires explicit resolution;
changing the default does not reset existing instances.

## Parameter bounds and composition timing

Use `min`/`max` for stored number limits and `minItems`/`maxItems` for row counts.
`step` is an input increment. Check relationships between fields, inset geometry
and the complete timing budget through actual preview at varied parameter values,
row counts and times. Use `useCompositionSettings().duration` for the saved project
duration rather than repeating a source default. Extend saved duration explicitly
when an edit needs more time; do not silently truncate the ending.

MotionHarness has no author `validate(values, context)` callback. Remove this declaration and
validation type imports from old TypeScript source. Legacy JavaScript callbacks
and schema `validation` metadata are ignored. Saving only checks shared document
rules, versions and required assets; it does not certify the rendered work.
Computed outputs evaluate normally in preview, export, actions and bake, without
runtime type, range or finite-value checks. Real execution exceptions still fail.
Bake samples become saved keys and obey the normal stored-value rules.

## Standard motion functions

For a CSS cubic-bezier curve, `cubicBezier(.22, 1, .36, 1)` creates the easing
configuration; `evaluateEasing(curve, progress)` evaluates it. Progress is the
normalized input derived from MotionHarness seconds. The configuration itself is not a
callable function.

Use SDK `spring`, `inertia`, `oscillate`, and seeded `noise` instead of rebuilding
these formulas. Each takes local MotionHarness seconds as its first argument. Expose the
controls users need through the component's parameter contract. Bind a whole-layer
trajectory to its basic parameter as a named output, rather than hiding a second
transform formula inside JSX:

```tsx
// Register this as an output of the declared basic Y parameter:
y: { parameter: 'y', evaluate: ({ stiffness, damping, mass }, { time }) =>
  spring(time, { from: 30, to: 0, stiffness, damping, mass }) },
// Render that Y through Layer. Bake explicitly before editing its keys.
```

Import `spring` from `@motionharness/sdk`. `springState` and `inertiaState` additionally
return velocity in units per second. Spring requires positive stiffness and mass,
and nonnegative damping. Inertia's friction is nonnegative. Oscillation frequency
is cycles per second, phase is cycles; noise requires a stable seed.

These functions define the complete trajectory from their current inputs. Seeking
backwards or changing FPS produces the same value at the same second. Changing a
physical parameter recomputes that trajectory; animated parameters do not create a
stateful simulation with time-varying forces. No hidden timers or random state exist.

For response to an existing trajectory, use `sampleVelocity(time, source)` and
`dampedFollow(time, source, { from, damping })`. The source is an ordinary pure
`(localSeconds) => number` function. Velocity uses source units per second; damping
is a response rate in inverse seconds. Both accept `start` (default 0) and `step`
(default 1/60 second). This numerical sampling interval is independent of project
FPS. Before `start`, velocity is zero and the response retains its initial value.
The initial response defaults to `source(start)`; use `from: 0` for a resting tilt.
Each response interval holds its endpoint source value, including the last partial
interval. Seeking rebuilds the same curve, without retaining playback state.

For rebound, use `springFollow(time, source, { from, stiffness, damping, mass })`.
`springFollowState` additionally returns velocity. It retains the motion's velocity
as the target moves or stops; an underdamped spring crosses the target and settles.
`dampedFollow` cannot do this: it is first-order smoothing, not a spring.
Spring following holds each fixed interval's starting target and solves that
interval analytically. The remaining partial interval uses the same target, so
position and velocity remain continuous under arbitrary seeks and frame rates.
Both follow functions accept `start` and `step`; their damping parameters have
different meanings (response rate versus the spring equation's damping coefficient).

Inside `computed`, `context.sampleNumber(parameter, localSeconds)` reads a numeric
dependency's track, loop or upstream computed output at the requested time. List
that source in `dependencies`; the host resolves only its upstream dependencies,
not the whole instance's outputs. Temporal feedback cycles are not supported.
Ordinary `values` still contain the current inputs. Dependency samples are numeric
reads. Host-owned sample caches are
discarded on source/data changes and never stored as document keys.

```tsx
computed: {
  tilt: {
    parameter: 'tilt', dependencies: ['x', 'stiffness', 'damping', 'strength'],
    evaluate: ({ stiffness, damping, strength }, { time, sampleNumber }) =>
      springFollow(time,
        t => sampleVelocity(t, s => sampleNumber('x', s)) * strength,
        { from: 0, stiffness, damping }),
  },
}
```

Declare `x`, `tilt`, `stiffness`, `damping` and `strength` as numeric component parameters.
`tilt` is a computed output; edit the source motion/response inputs, or explicitly
bake it before independently editing its keys. Options passed from current values
describe the complete response curve, just like `spring`; animate the sampled
source when the force must change over time. This is lightweight trajectory
response, not a collision or rigid-body engine.

For an editable base with accompanying physical motion, render:

```tsx
<Layer bindings="parameters" value={basicTransformValue(values)}
  offset={{ rotation: values.tilt }}><Card /></Layer>
```

`offset.x/y` add parent-space pixels; `offset.rotation` adds degrees about the base
anchor. `applyTransformOffset(base, offset)` produces the same final pose for pins
and connections. The selection outline follows that final Layer. Numeric inputs
edit base parameters; canvas gestures subtract the offset captured at pointer-down
before writing changed base channels. A visible 20° angle with a 3° offset saves
17° of base rotation. The offset is never persisted as extra rotation keys.
Keep intentional rotation animation if the user authors it; default movement-only
examples need X/Y keys, not constant opacity, crop or physical-output tracks.
Editing a dependency recomputes the offset. Anchor compensation includes the
displayed offset, but if its X/Y edits change a physical trajectory, the response
can change too; it does not freeze all pixels under a dynamic offset or solve an
arbitrary inverse formula. Rotation-only edits leave an X/Y-driven response intact.

When the entire transform is computed with no declared editable base, use
`editable={false}`. Users edit exposed inputs or explicitly bake outputs rather
than having the host infer an inverse for an arbitrary formula. Binding ownership
is explicit and never inferred from numeric equality.

## Repeated layout and staggered animation

Use ordinary React lists or `field.componentList` for repetition. The SDK helper
`repeatTransform(index, { from, step })` computes position/rotation increments and
scale multipliers. Missing translations and angles default to 0; scales default
to 1. For example, `step: { x: spacing, rotation: angle, scaleX: .9, scaleY: .9 }`
places each successive item farther right, rotated, and at 90% of the prior size.
Expose spacing/angle/scale as component parameters when they need editing.

```tsx
items.map((item, index) => {
  const p = repeatTransform(index, { step: { x: spacing, rotation: angle } });
  return <div key={item.$instance} style={{
    position: 'absolute', transformOrigin: 'top left',
    transform: `translate(${p.x}px, ${p.y}px) rotate(${p.rotation}deg) scale(${p.scaleX}, ${p.scaleY})`,
  }}><Instance value={item} /></div>;
});
```

Keep React keys based on the instance ID, not the index. The index determines the
current layout order. This computed layout has no canvas drag binding; edit the
shared input parameters. Each child can animate from its own `useTime()` or local
keyframes. Timing is editable unless the contract declares `editableTiming: false`; use the
standard stagger operation to offset starts. No new repeater object is needed.

## Text reveal and cursor

Use `textReveal(useTime(), { text, progress, unit, cursor })` from the SDK.
Expose `text` as `field.text`, `progress` as an animatable number in [0, 1], `unit`
as a select (`character`, `word`, `line`), and any needed cursor controls as normal
component parameters. The helper returns `{ text, cursorText, cursorVisible }`:

```tsx
const result = textReveal(useTime(), {
  text, progress, unit,
  cursor: showCursor ? { text: cursorText, blinkRate } : false,
});
return <span style={{ whiteSpace: 'pre-wrap' }}>
  {result.text}<span style={{ visibility: result.cursorVisible ? 'visible' : 'hidden' }}>
    {result.cursorText}
  </span>
</span>;
```

Blink rate is complete on/off cycles per second; 0 keeps the enabled cursor visible.
The cursor remains independently controllable after the text is fully revealed.
Use an empty cursor string or conditional rendering if no reserved cursor space is
wanted. Character mode preserves grapheme clusters (including emoji and accents).
Word mode splits on whitespace and retains that whitespace; line mode uses explicit
newlines, not automatic layout wrapping. `segmentText` and `revealText` are also
available for custom per-segment rendering. Never use CSS animation or wall-clock
intervals for the cursor.

## Number counters

Use `formatCounter(value, { decimals, useGrouping, prefix, suffix, rounding })` to
render an already keyframed number parameter. `rounding` is `half-away-from-zero` (ties away
from zero), `floor` or `ceil`; decimals is an integer from 0 to 20. Use discrete
choices for an editable decimal count and convert the selected value in the
component. Keep decimals discrete rather than continuously animated. A fractional
value supplied to the formatter throws during actual execution.

Grouping defaults to true. Use `formatCounter(year, { useGrouping: false })`
for years and identifiers, so 2000 remains `2000` instead of `2,000`.

For a formula-driven count, use
`counterValue(useTime(), { from, to, start: 0, duration: 2, easing: 'ease-out' })`
and pass its result to `formatCounter`. Duration must be positive. This uses the
same MotionHarness seconds and easing functions as parameter animation, with clamped
endpoints. Do not combine a second driver with an already animated number.

Formatting uses a stable comma grouping and dot decimal separator on every
machine, preserves configured trailing decimals, and places a negative sign
before the prefix. It rounds the Number's decimal representation, so 1.005 with
two decimals is 1.01, and suppresses negative zero. This does not recover precision
already lost in upstream Number arithmetic; large integer values beyond Number's
safe range must not be assumed exact. Text-reveal helpers can also reveal the
formatted result when that effect is desired.

## Data tables without component instances

Use `field.table` for plain data rows. Columns reuse scalar field declarations;
identity names a required unique text/number column. The component receives an
array of `{ id, values }` rows, with inferred column types:

```tsx
rows: field.table({
  label: 'Sales', identity: 'code',
  columns: {
    code: field.text({ label: 'Code', default: '' }),
    amount: field.number({ label: 'Amount', default: 0, min: 0 }),
  },
  initialRows: [{ code: 'A', amount: 20 }],
});
```

Render with `rows.map(row => <Bar key={row.id} amount={row.values.amount} />)`.
`initialRows` accepts plain column objects, but rendering and stored-document checks receive
the `{ id, values }` wrapper. Keep those inferred types; extract plain column data
with `rows.map(row => row.values)` when a calculation needs it. A type assertion
does not reshape runtime data and must not be used to bypass a row-shape error.
Row IDs are scoped to the owning instance and table parameter. Tables contain
static scalar data; they are not animated as whole arrays. Check row relationships
through preview. Source defaults only initialize new values. Column type/removal or identity-contract changes
require explicit migration; no implicit data loss or identity reassignment.

For rows that need persistent component-local animations, use componentList and
the same import operation; matched instances keep their tracks and timing. Plain
data rows are never automatically converted into component instances. Avoid
React-reserved `key`/`ref` names for component props; use a data column such as
`code` and pass the stable row/instance ID as the JSX key separately.

## Data sequence animation

Wrap ordered children in SDK `Sequence`, passing an overall numeric progress and
shared timing. A child calls `useSequenceProgress()` to read its distributed
progress; no DOM wrappers or component instances are required for plain rows.

```tsx
<Sequence progress={progress} timing={{ duration: 2, stagger: .2 }}>
  {rows.map(row => <Bar key={row.id} amount={row.values.amount} />)}
</Sequence>
```

Overall progress is an ordinary animatable number. `spacing: 'fixed'` (default)
keeps each item's duration and stagger and extends total duration accordingly.
`spacing: 'fit'` uses duration as the total window and rejects a stagger that leaves
no positive item duration. No hidden 80% cap or post-easing overshoot clamp applies.
Direct children define order/count; use stable keys.

For explicit composition, call `useSequenceProgress({mode:'scale',value:reveal})`
or `{mode:'override',value:reveal}`. The mode never changes because a track appears.
The default hook returns inherited progress. For generated independent tracks,
choose override explicitly; the sequence command's optional `modeParameter` names
a declared selector that should be set to `override` in the same transaction.

## Shared-property following

Use `followNumber(time, source, { delay, offset })` for a shared deterministic
number signal. It evaluates the source at `max(0, time - delay)`, then adds offset;
there is no playback history. A source can be a pure function using SDK motion
helpers, or a sampler of a declared parameter:

```tsx
const sampleX = useNumberSampler('position');
const time = useTime();
const leaderX = sampleX(time);
const followerX = followNumber(time, sampleX, { delay, offset });
return <><Leader x={leaderX} /><Follower x={followerX} /></>;
```

`useNumberSampler` samples this persistent component instance's numeric value,
including keyframes and loops. It evaluates the source at the sampled time. Pass
the sampler and its time through ordinary React props/context to compose followers;
no persistent cross-object ID relation is required. The time argument is in the
sampler owner's local seconds. If a nested persistent instance has its own shifted
clock, pass the owner's time rather than mixing the two local timelines.

Expose delay/offset as component parameters. Keep `Layer editable={false}` for
computed follower transforms so dragging cannot implicitly rewrite the source.
This standard path covers shared numeric properties; arbitrary object-reference
relationship graphs are not introduced.

## Named computed outputs and baking

Register only computations that need later keyframe editing. Ordinary React code
and other formulas do not need registration. A component can name an output and
bind it to one declared animatable parameter:

```tsx
const Moving = defineComponent({
  id: 'moving',
  parameters: {
    speed: field.number({ label: 'Speed', default: 100 }),
    x: field.number({ label: 'Position', default: 0, animatable: true }),
  },
  computed: {
    position: { parameter: 'x', evaluate: ({ speed }, { time }) => speed * time },
  },
  component({ x }) { return <div style={{ transform: `translateX(${x}px)` }} />; },
});
```

Evaluate callbacks are synchronous, pure and use local MotionHarness seconds. They receive
one frozen snapshot of base parameter values, including input keyframes/loops;
outputs do not implicitly read each other's computed results. Reuse a common pure
function for shared logic. Numeric, transform and other supported scalar animation
parameters may be targets; structural/asset fields cannot. A target has one output
and cannot also declare defaultAnimation.

Runtime supplies the computed result as the ordinary component prop. A computed
output cannot be directly edited or keyframed, and Layer bindings to it are
read-only. Bake explicitly to create keys and switch that target to an independent
driver. Once independent, source/input changes do not overwrite its keys. Removing
its last key retains a static value, rather than silently returning to computation.
An explicit parameter reset restores the computed driver. No JSX rewriting occurs.

## SVG path trim and endpoint binding

Use `pathData(points, { kind: 'polyline' | 'cubic', closed, start, end })` to produce
SVG path data. Cubics use one start followed by groups of three control/end points.
`bindPathEndpoints` returns a copy with the first/last point replaced, preserving
interior control points. Raw SVG `d` strings can be used directly with `TrimPath`.

```tsx
const start = pointAtFraction(fromBounds, { x: 1, y: .5 }, { transform: from });
const end = pointAtFraction(toBounds, { x: 0, y: .5 }, { transform: to });
return <svg width={width} height={height}>
  <TrimPath d={pathData([start, end])} stroke="white" strokeWidth={3}
    trim={{ start: trimStart, end: trimEnd, offset: trimOffset }} />
</svg>;
```

Anchors are normalized relative to shared untransformed bounds. Optional transform
and normalized origin follow Layer's geometry (scale, rotation, then translation;
origin defaults to the center). Use one coordinate system for boxes and SVG. The
connector reads the same evaluated parameters as its objects, so moving or
animating an object updates its endpoint without screen measurements or an object
reference registry.

Trim start/end clamp to [0,1]; an end before start is empty. Offset shifts the
normalized dash pattern and wraps around path length. Empty strokes are hidden,
including round caps. `TrimPath` owns dash styles and defaults fill to none; it
uses native SVG dash behavior, including SVG's subpath rules. `trimPath` exposes
the corresponding props for custom rendering. Open trim and endpoint geometry
controls as normal component parameters and drive them with MotionHarness time/keyframes.

`TrimPath` owns `pathLength`, `strokeDasharray` and `strokeDashoffset`; supplying
those props is a type error because they would compete with trimming. Use an
ordinary `<path fill="none" strokeDasharray="6 4" ... />` for a static dashed
outline. To reveal a dashed path, place the ordinary dashed path under an SVG
mask/clipPath driven by the trim; preserve SVG's existing semantics.

For a dot that follows the drawing tip, use the same `d` and normalized progress
with `usePath`/`followPath`; see [Following a path](#following-a-path). Sampling the
rendered path avoids maintaining a separate arc/segment formula for its marker.

## Following a path

Use `usePath(d)` inside a React component, or `createPathSampler(d)` for a reusable
sampler in browser Runtime code/named-output callbacks. Both use native SVG
geometry without attaching a node or reading layout. Keep the rendered path and
the sampler's `d` identical, in the same coordinate system.

```tsx
const path = usePath(d);
const pose = followPath(path, progress, {
  orientToPath: true, rotationOffset,
});
return <svg>
  <path d={d} fill="none" stroke="white" />
  <g transform={`translate(${pose.x} ${pose.y}) rotate(${pose.rotation})`}>
    <Arrow />
  </g>
</svg>;
```

A traced path and its moving dot share one geometry and distance fraction:

```tsx
const path = usePath(d);
const dot = followPath(path, progress);
return <svg>
  <TrimPath d={d} stroke="white" trim={{ end: progress }} />
  <circle cx={dot.x} cy={dot.y} r={3} fill="white" />
</svg>;
```

Progress clamps to [0,1] and represents distance along the path, not a curve's
polynomial parameter. `sample(progress)` returns x/y and tangent angle in degrees;
`followPath` additionally supports position offset, optional tangent orientation,
a fixed rotation when orientation is disabled, and rotationOffset. Bind these
controls to normal component parameters/keyframes. Draw markers around their
intended origin, or supply an offset for their anchor.

Tangents use nearby geometry samples, with one-sided directions at endpoints and
protection against direction vectors spanning disconnected subpath jumps. At
corners a local averaged direction may be used; zero-length geometry has angle 0.
Paths may contain lines, curves, arcs and closed or disconnected subpaths. This
requires the native browser Runtime, including the controlled baking browser;
it is not a Node-only SVG parser. Register the resulting transform as a named
output when editable baked motion is needed. Geometry sampling itself has no
playback state or independent clock.

## Editable CSS/SVG effect stacks

Declare a stack with `field.effects({ label, initial: [...] })` and render it in a
known box with `<EffectStack effects={fx} width={width} height={height}>...</EffectStack>`.
Effects have stable IDs, type, enabled, intensity and typed params; they are data entries,
not component instances. IDs and defaults are initialized for the Agent. For a
code-only stack, `createEffect({ type, params }, stableId)` creates the same value.

```tsx
fx: field.effects({ label: 'Effects', initial: [
  { type: 'blur', params: { radius: 3 } },
  { type: 'color-adjust', params: { saturation: 20 } },
] });
```

Entries process the content in array order; the first entry is nearest the source.
Available types are blur, backdrop-blur, color-adjust, shadow, inner-shadow, glow,
blend-mode, effect-mask, gradient-overlay, vignette, light, grain, texture-overlay,
svg-distortion and frame. Read `EFFECT_DEFINITIONS` or CLI describe for exact params,
defaults and bounds. Shadow alpha mode uses the content silhouette; normal shadow
uses the box. Texture/frame asset params use managed image references. Frame slice
uses CSS border-image source units, so choose it for the source image dimensions.

Mix is effect-specific: filter amounts interpolate from their neutral values;
shadows and overlays adjust intensity through coverage; distortion scales displacement.
These are effect-specific intensity controls, not image interpolation. Fractional
result mixing is expressed explicitly with two GPU textures and GLSL `mix()`.
Blend mode is discrete; use enabled or GPU mixing rather than a partial intensity.

The stack uses native CSS/SVG and owned asset loading. Studio provides effect
catalog, ordering, parameter and keyframe controls for declared effects fields.
For DOM textures and managed GPU passes, use the separate APIs below; do not
reimplement their resource lifecycle inside an effect component.

## Box-scoped SVG masks

Use `Mask` for authored SVG mask content and ordinary React children:

```tsx
<Mask width={width} height={height} mode="alpha" opacity={opacity}
  inverted={inverted}
  mask={<rect width={width * reveal} height={height} fill="white" />}>
  <Artwork />
</Mask>
```

Alpha mode uses source alpha. Luminance mode uses source luminance multiplied by
source alpha, so semi-transparent mask pixels remain semi-transparent. Clip mode
uses SVG clipping geometry and ignores the shapes' color/fill opacity. Mask
opacity scales the resulting coverage; inversion is applied afterward, within
the declared width/height. Thus an inverted mask with opacity 0 reveals the whole
box. `maskCoverage` exposes this final scalar operation for custom calculations.

The mask prop contains SVG shapes, paths or text; use alpha/luminance mode for
images. A managed image can be used as `<image href={useAsset(original)} ... />`;
font declarations/useFont also work with SVG text. Clip mode requires SVG clipping
geometry, not images or HTML. Keep mask and artwork in the same coordinate system.
Each Mask owns unique SVG IDs, with no global object-reference lookup. Expose
geometry, mode, opacity and inversion through normal component contracts and MotionHarness
keyframes. No separate object-mask editor is introduced in this phase.

## Component actions and custom-control contracts

Declare actions and controls on `defineComponent` alongside parameters. Actions
are synchronous pure functions returning semantic data operations; they do not
write files, source or document objects themselves:

```tsx
actions: {
  spread: {
    label: 'Spread',
    run({ gap, items }) {
      return items.map((item, index) => ({
        type: 'timing', instanceId: item.$instance,
        timing: { start: index * gap },
      }));
    },
  },
},
```

The callback receives frozen current parameter values and a context with local
`time`, `projectTime`, `instanceId`, and `read(reference)` for owned descendants.
An action can modify only its instance/subtree, using supported data operations.
Return an empty list for a no-op. At most 128 operations form one validated commit.
The common operations retain their existing rules, including editable timing and
computed-output protection. Async callbacks and direct mutation are rejected.

A control declares label, bound `parameters`, placement (inspector/toolbar/overlay/standard)
and a React `component`. Its props provide frozen values/time, readonlyParameters,
`read`, `commit(operations)` and `invoke(actionName)`. Commit is restricted to bound
parameters and subtrees rooted in those bindings; invoke calls a separately
declared action on the same component using that action's scope. The platform
binds source/data versions and validates every proposal before persistence.

Only metadata is serialized; callback/control implementations stay in the compiled
source. Studio mounts inspector, toolbar and overlay controls for the selected
instance. Root controls with the existing placement name `standard` appear in
Pro's Quick Controls tab and remain bound to the root when selection changes.
This placement does not change the project type. Control errors are isolated from the composition;
retained callbacks from obsolete source/data versions are rejected.
Quick Controls should offer the template's necessary quick edits: text, source media,
chart data and a few broad appearance choices. Select these deliberately from
likely user tasks, rather than iterating all schema parameters. For repeated
cards or modules, show an item selector and the selected item's content fields.
Keep individual lights, shader/material settings, coordinates, anchors and
animation controls in PRO, including when a collapsed "advanced" section would
otherwise expose them in Quick Controls. Do not remove their parameter definitions or
PRO editing. These are authoring defaults, not runtime quotas or quality gates.
For panel UI, choose fields and grouping; let Studio supply the skin. Prefer
`renderField(reference, parameter)` for ordinary parameters. Custom HTML inputs,
textareas and selects inherit Studio's input palette; do not hard-code dark fills
or invent theme variables. The smoked dark readout belongs only to playback time.
Color swatches and artwork retain their actual colors.
For quick-control sections, import `ControlPanel` and `ControlGroup` from
`@motionharness/sdk`. Wrap related native fields in `<ControlGroup label="…">`;
use `description` and `defaultOpen={false}` where appropriate. Studio supplies
card borders, headers, collapse controls, spacing and theme. Preserve the intended
section boundaries when migrating a template; do not replace them with unstyled
headings or copy internal Studio CSS class names into author code.
`renderField(reference, parameter, {label, linked: [{reference, parameter}]})`
provides host-native editors for linked scalar parameters. One edit or reset
updates all targets atomically through the existing scoped commands and undo.
Declare all owning component bindings in the control's `parameters`. Use the
host's existing asset editor for imports/replacements.
Use a group's `proTargets={[{label, reference, parameter?}]}` and
`onOpenPro={props.openPro}` for its PRO shortcut. Bind the actual item and field;
when a quick-edit item selector changes, update that destination too. Studio
owns selection, timeline reveal and property focus. Do not call
commit or create a project action merely to navigate. Multiple destinations use
a chooser; pending field input finishes before navigation, and stale/missing
references are rejected by the existing control scope.
See `examples/product-intro/src/StandardPanel.tsx` and
`examples/templates/iphone-duo-unfold-3d/src/panel.tsx`.
This is an authoring/data boundary, not a security sandbox for hostile project code.

## Coordinates and editable ownership

Use the single `Layer` with independent `basicTransformParameters()` fields.
`value={basicTransformValue(values)}` supplies its presentation;
`bindings="parameters"` explicitly opts in to matching editable parameter names.
Omit bindings for formulas or decorative layers. There is no equality-based
ownership inference. JSX calls outside a persistent Instance retain normal props
but do not create a saved object or acquire another instance's editing scope.

Positions follow CSS layout and translation; pixel anchors measure from the local
top-left corner and remain fixed during resizing. For standalone absolute geometry
math, `geometryStyle` uses top-left x/y and the same pixel pivot convention.
`unit: 'composition-percent'` explicitly requests percentages of the provided
composition dimensions; it is not a CSS parent percentage. Normal JSX styles keep
normal CSS percentage behavior. `pointAtFraction` and `geometryPointAtFraction`
explicitly name normalized box attachment points; `fixedFraction` pins one during
resize. A fraction is not a stored pixel anchor.


## DOM and background texture inputs

Inside a Canvas draw callback, use the Runtime-owned `texture` reader:

```tsx
const source = useRef<HTMLDivElement>(null);
return <>
  <div ref={source}>Text, images, SVG, Canvas or MotionHarness Video</div>
  <Canvas width={240} height={160} draw={async ({ context, texture }) => {
    const input = await texture(source.current);
    context.drawImage(input.source, 0, 0, input.width, input.height);
  }} />
</>;
```

The source must be in the same Scene. To keep an input out of the visible artwork,
position its box offscreen; display:none/visibility:hidden/opacity:0 also hide it
from the captured content. Its local border-box content is captured;
root placement/transform is removed while descendant layout/styles remain. Options
may specify width/height, a local crop `region`, pixelRatio and excluded elements.
For background effects, capture an explicit background container or exclude the
output/foreground groups from a shared container. There is no automatic inference
of arbitrary CSS paint order. Self-feedback and producer dependency cycles reject.

Runtime waits for source Canvas/video and asynchronous preparation, embeds prepared
managed images/fonts and accessible CSS font resources, then rasterizes an isolated
styled SVG/foreignObject snapshot. Root iframe/object/embed, shadow/custom-element
internals and unsupported generated content require an explicit image/Canvas
source. Fetch/CORS restrictions still apply; this is not a screen-capture bypass.

Returned metadata contains logical/pixel dimensions, pixel ratio, crop origin,
project time, sRGB color space and an opaque snapshot version. Draw callback time
remains instance-local. The canvas is borrowed for that callback only: do not retain
it for later frames or release it yourself. Runtime releases it after drawing and
cancels obsolete work. For WebGL, upload the CanvasImageSource with your intended
alpha convention; the raw context uses a premultiplied drawing buffer. Shared GPU
resources/effect chaining are separate F02 work.

Stable draw callbacks refresh when source data changes even at a paused time.
Generic asynchronous `useFrame` work is awaited conservatively; an optional third
owner ref can identify its DOM subtree. Geometry and font readiness are checked
within the frame barrier, rather than using a separate animation clock.

## Managed GPU effects and shared outputs

Use `GpuCanvas` with a graph of complete GLSL shaders and explicit texture refs;
see “Standard GLSL and explicit background composition” below for a complete example.
The Scene owns the device, program cache, intermediate targets and output lifetime.
Programs are cached up to 64 entries and free targets up to 8 / 128 MiB. Active
outputs retain their own target until replaced or unmounted. Same-frame GPU output
refs can reuse textures directly. Cycles and cross-Scene inputs fail explicitly.

GPU context loss is recovered by replacing the offscreen context and retrying the
same MH-time frame, at most twice. `GpuCanvas` recreates its programs and textures
internally. With low-level `Canvas mode="webgl2"`, the draw callback may run again
with a **different context**: keep context-owned resources in a `WeakMap` keyed by
that context (or create them in the callback), and never reuse old-context handles.
Callbacks must be repeatable from the supplied time and parameters, without
advancing independent simulation state. Abort and ordinary shader errors are not
retried. Persistent loss fails frame preparation/export and preserves the previous
completed visible output; a later frame may attempt recovery again.

### Control the user's current Studio

Use these controls only for requested viewing/interaction or a Studio-specific
diagnostic. Routine visual/audio verification uses
[Background checks](rendering.md#background-checks) and preserves the user's page.
Use `mh studio sessions --project <project>` to inspect connected Studio tabs. Each has a
`clientId` and transient `state`: view revision, build/data version, playback,
viewport, timeline and stable instance/keyframe selection. `preview.displayed`
is a separate prepared-frame receipt; applying a command does not imply the new
frame has finished rendering. An independent `mh preview` may appear as a capture
session; it never controls the user's interactive session and is excluded from
implicit Studio control targeting.

For an authorized playback diagnostic, use the focused commands:

```sh
mh studio seek 2.8 && mh studio play
```

After a diagnostic, stop playback you started in the same addressed tab with
`mh studio pause`, including on failure, unless the user has taken over. Preserve
pre-existing/user-started playback; requested viewing is not diagnostic cleanup.
Command acknowledgement alone does not prove motion review or listening.
For sound activation errors, follow
the [Interactive playback recovery](rendering.md#interactive-playback) instructions.
With multiple tabs, add `--client <clientId>` using an ID from `mh studio sessions`.
Seeking pauses playback and waits for the requested frame to appear.
For other controls, write a JSON request and run
`mh studio control --file <request.json> --project <project>` (or use `--json`).
Operation families are `playback` (play/pause/seek), `timeline`
(seek/step/zoom/scroll/fit), `viewport` (pan/zoom/fit/reset), and `select`
(instances and/or keyframes using stable key references). See
`mh describe "studio control" --project <project>` for the request schema.
Seconds remain authoritative; frame stepping uses the output FPS grid.

If exactly one Studio is connected, clientId may be omitted; multiple tabs require
an explicit target. `expectedRevision` optionally guards the **view** revision,
which advances during playback. CLI also supplies current source/data versions.
These controls never save the document or enter undo/Checkpoint history.
Restore and active user gestures block control; background exports do not.
A pending control acknowledgement must finish before selecting an export version or restoring a Checkpoint. Timeout is an
uncertain outcome: inspect the session before retrying; do not automatically
repeat an incremental pan/step. Reopening Studio starts fresh transient state.

`mh keyframe list --project <project>` returns all `keys`, including
nested effect tracks. An ordinary key reference is
`{instanceId, parameter, keyframeId}`; an effect key additionally requires
`effectId` and `name` (for example `radius`, `intensity` or `enabled`). These are stable
identities, not effect stack indexes. The same references work in keyframe
selection commands and Studio selection. Operations affect only explicitly selected
keys. Multi-selection supports atomic move, scale, copy, easing and removal;
clearing the selection leaves no persistent association between keys. Removing the
last key preserves the value at the supplied MotionHarness time. Duplicating an effect or
component creates fresh key identities.


## Reuse basic editable components

Prefer existing SDK building blocks when they match the requested design:

- `Graphic` and `basicGraphicPresets`: text, rectangle and ellipse variants,
  independent base channels, style parameters, text reveal/counter and an effects stack.
- `defineTextComponent({ id, font })`: the same text controls with a real imported
  font original and Studio's font picker. Use a stable component ID.
- `defineMediaComponent({ id, asset })`: bind an imported image/video original;
  expose replacement, independent position/size/anchor channels, fitting/crop, opacity and MotionHarness playback controls.
- `defineContainerComponent({ id, component, presets, initialItems })`: a typed
  child list with free/cells-row/cells-column/cells-grid layout and editable child timing. Duplicate
  list entries and use timing/stagger operations instead of inventing a repeater
  object system. Layout cells do not resize child content automatically.

Render lists with ordinary JSX:

```tsx
const parameters = {
  graphics: field.componentList({
    label: 'Graphics', component: Graphic, presets: basicGraphicPresets,
  }),
};
// Inside the component:
return <div style={{ position: 'relative', width: '100%', height: '100%' }}>
  {graphics.map(ref => <Instance key={ref.$instance} value={ref} />)}
</div>;
```

Declare named creation presets on a list using
`presets: { featured: { label: 'Featured', values: { fontSize: 64 } } }`.
Preset values must match the child contract and cannot replace ownership
references. `list add ... --preset featured` creates a fresh instance. The
versioned list command also accepts `initialProps` for atomic creation with a
chosen asset. Updating source defaults/presets never changes existing instances;
synchronize saved values only through an explicit edit transaction.

For panel clarity, scalar fields can declare
`visibleWhen: { mode: ['text'], enabled: [true] }`. Dependencies must be static
boolean/select fields. Conditions are ANDed; alternatives within a field are
ORed. This controls inspector presentation only: hidden data, keyframes and CLI
access remain intact. Do not use hidden fields as access control or validation.

Visual instances are added through explicitly declared lists. Native sound instances may be attached through the host sounds collection without author JSX changes. A default new
project includes graphic/container lists; authored projects should expose the
appropriate list locations rather than forcing Studio to rewrite arbitrary JSX.

### Layer ranges and nested group timing

An instance's visibility window is independent of its keyframe extent. Input time
is `u = parentContentTime - start + offset`; content time is `timeRemap(u)` or `u`
without a curve. Parameters, `useTime()` and children use content time. Enclosing
windows clip the result without modifying member data. Group membership comes from
declared component references and native sounds. See [Time editing](editing.md#time-editing)
for window fields, moving and trimming; advanced clock operations are in
[Time remapping](time-remapping.md).

## Standard GLSL and explicit background composition

Prefer `GpuCanvas` for existing GLSL algorithms or multiple input textures.
`fragmentShader` is complete GLSL ES 3.00 with its own declarations, output and
`main()`. No source rewriting or injected uniforms is performed. The default
fullscreen vertex shader provides `vUV` in WebGL bottom-left coordinates; optional
`vertexShader` can provide other varyings using `gl_VertexID` and three vertices.
Use a single fragment output at location 0. General meshes belong in raw WebGL Canvas.

```tsx
<GpuCanvas width={640} height={480}
  inputs={{ background: backgroundRef }}
  graph={{ passes: [{
    id: 'tint',
    textures: { image: { input: 'background' } },
    uniforms: { amount },
    fragmentShader: `#version 300 es
precision highp float;
in vec2 vUV;
uniform sampler2D image;
uniform float amount;
out vec4 color;
void main() {
  vec4 c = texture(image, vUV);
  color = vec4(c.rgb * amount, c.a);
}`,
  }], output: { pass: 'tint' } }} />
```

Full shaders use straight RGBA by default; set `alphaMode: 'premultiplied'` for
passes that consume and produce premultiplied RGBA. The host converts between that
contract and its internal premultiplied RGBA8 textures. Channel values are sRGB
encoded, with no implicit linear-light conversion. Bind time explicitly from
`useTime()`. GLSL integer/vector/matrix/numeric-array uniform types are reflected
from the program; missing active bindings are errors. Texture sampler arrays and
uniform blocks are unsupported. `textureSize` returns physical dimensions.

Named `{ pass: id }` dependencies connect intermediate results; `size` specifies
logical width/height for downsampling. Export pixel density applies throughout.
Passes may be listed in any order; scheduling, cleanup and recovery are managed.
There is no implicit main input or mix/bypass behavior in full shaders. Use GLSL
for blending and JavaScript to select graph outputs. There is one `GpuCanvas` interface: complete shaders and explicit graph inputs.

For glass/background effects, explicitly reference the background React subtree,
with the consuming output outside it. Its internal layout may use normal flex/grid
and z-index. To crop, use `textureOptions` with a top-left local logical-pixel
`region`. Do not infer a background from DOM sibling order or include the effect's
own output in its input. Several glass controls can share the same source ref.

A replaceable wallpaper can declare
`field.asset({label:'Wallpaper',accept:['image','video'],default:image})`.
Choose `Image` or `Video` by the saved reference's `kind`; the picker, CLI and host
validate the same accepted set. A single-kind field keeps its existing behavior.
