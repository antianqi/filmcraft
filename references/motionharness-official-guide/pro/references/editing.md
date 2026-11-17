# Editing saved work

Locate the target with `mh inspect --view instances --query <name>` and
`mh inspect --view parameters --instance <id> --parameter <name>`. Bare `mh inspect`
returns the session summary. Same-name instances
remain separate candidates; choose a stable ID. Focused lists default to 100 items;
use `--offset`/`--limit` and check `nextOffset`.
The CLI supplies version preconditions internally. A successful save and a displayed
frame are different receipts; verify the requested time after visual edits.

- `mh param set <instance> <parameter> --value '<JSON value>' [--time <seconds>]`
- `mh keyframe set <instance> <parameter> --time <seconds> [--value <JSON>]`
- `mh keyframe remove <instance> <parameter> <keyframe-id> --time <seconds>`
- `mh keyframe edit <instance> <parameter> <keyframe-id> --time <seconds> [--easing <name-or-JSON>]`
- `mh list add <owner> <parameter> [--preset <id>]`
- `mh list duplicate|remove <owner> <parameter> <instance>`
- `mh list move <owner> <parameter> <instance> --index <index>`
- `mh instance timing <instance> --start <seconds> [--duration <seconds|none>]`
- `mh instance timing <instance> --time <seconds> --edge start|end --timeSpace project|parent`
- `mh project settings --json '<JSON settings>'`

Without keyframes, edit changes a static value. With keys, supply the intended
project time so edit adds or updates its key. List results distinguish project
`time` from stored `localTime`. There is no track enable switch.
Removing the final key preserves the current evaluated value as static data.

Source implementation changes keep saved values. Added fields receive initial
values; incompatible contract changes wait for explicit migration. For a rename:
`mh project migrate rename <component-id> <old-name> <new-name>`.
Inspect the pending contract first. Do not use reset/drop just to silence errors
when values or animation should migrate. Conflicts require inspecting latest work
and applying the intended change again, not blindly overwriting it.
Ordinary edits to the current work do not require rewriting source defaults or
`defaultAnimation`. Defaults govern initialization and explicit reset, not the
last saved edit. Change them only when the task includes new template/reset
behavior; use Checkpoints for historical restoration.

One source writer operates alongside user parameter edits. Export locks both;
wait for completion or explicitly cancel with `mh render cancel`.

For related edits, write an array of operations to a JSON file under the project
`.tmp/` directory, then call `mh batch --file <operations.json>`:

```json
[
  { "type": "edit", "instanceId": "<from inspect>", "parameter": "lower", "value": 20 },
  { "type": "edit", "instanceId": "<from inspect>", "parameter": "upper", "value": 30 }
]
```

A batch accepts 1–128 operations. `type` selects edit, keyframe/set,
keyframe/remove, keyframe/edit, timing, settings or list; the remaining fields
match that operation. Do not put version fields inside operations: the CLI binds
the whole request to its inspected source/data version. Core prepares a candidate,
shared document rules validate the final stored state, and the host saves one revision.
A later failure does not leave earlier edits saved. This is atomic submission,
not an instruction to create a Checkpoint or put Agent edits in ordinary undo.
Operations evaluate in order; atomic saving does not make individual key moves
simultaneous. Use selection `scale` for retiming a set, rather than sorting many
single-key moves to avoid temporary collisions. `mh describe batch --type
keyframe/edit` returns just that variant. CLI input is an operation array; HTTP
request schemas include a wrapper and version preconditions supplied by the CLI.


For an unknown operation, discover it through `mh capabilities`; otherwise query
the needed action directly with
`mh describe edit <instance> <parameter>`. Focused descriptions include
allowed enum values, numeric limits and whether animated edits require a time.
`requestSchema` is the HTTP
payload for routed actions; CLI usage is listed separately and the CLI supplies
version preconditions automatically. Capability availability is a current-state
observation, not a reservation: execution still checks versions and final values.
When the host is stopped, the catalogue reports that availability cannot yet be checked. Project operations
start sessions on demand; open is only needed to obtain a Studio URL. Do not invent commands
for capabilities that are not listed.

## Keyframes

A key's easing controls the segment leaving that key. Besides the named
curves, pass a JSON object to `keyframe edit` or a batch operation:

```json
{ "type": "cubic-bezier", "x1": 0.25, "y1": -0.2, "x2": 0.75, "y2": 1.2 }
```

Control x coordinates must be in [0, 1]; y coordinates are finite and may
overshoot. Exact controls are saved, not baked to the output FPS. SDK code can
use `cubicBezier(x1, y1, x2, y2)` and `evaluateEasing(curve, progress)` with the
same solver as Runtime keyframes. PRO exposes the same curves in its keyframe editor.

Use `mh keyframe list` to read key identities. For a multi-key
operation, put `operation` and explicit `keys` (instanceId, parameter, keyframeId references
from inspect) in a JSON file, then call
`mh keyframe apply --file <selection.json>`. The same request is a batch operation
with `type: "keyframes/selection"`.

- `move` applies one `delta` in the chosen `timeSpace` (`project` by default, or `local`). Project movement is clamped as a whole to the composition interval. Collisions reject the whole operation.
- `scale` takes `anchor` in that time space and positive `factor`: `newTime = anchor + (time - anchor) * factor`. Targets are computed together; collisions or out-of-project targets reject the whole project edit. Key IDs, values and easing are preserved. Loop ranges stay unchanged unless `scaleLoopRanges: true`; that requires selecting every key on each affected looping track.
- `copy` uses `delta` and the selected time space to create new key identities while preserving originals.
- `easing` applies the supplied named or Bezier `easing` to selected keys.
- `remove` requires current `time` in the selected time space; when all keys of a parameter disappear, its pre-removal evaluated value becomes static.

Key listings include `localTime` and projected `occurrences`; project `time` is
null when no unique point exists. Pass an explicit `occurrenceTime` on each
ambiguous project key reference or edit in local time. Ordinary keys use the
instance's content seconds locally. See [Time editing](#time-editing) for choosing
between editing keys and changing a content clock.

A single reference selects only that key. Use an explicit `keys` array to edit
multiple parameters or instances together; the selection creates no persistent
association between keys.

For example, to compress selected parameter-key spacing around 0.8 seconds, select
the relevant keys from `mh keyframe list --instance <id> --parameter <name>` and
submit `{ "operation": "scale", "anchor": 0.8, "factor": 0.5, "keys": [...] }`.
Include related screen/effect tracks explicitly; unrelated animation is not
automatically part of the selection. The CLI receipt reports net time changes.
This changes the selected keys, not every time-driven effect in an instance.
Prefer it for ordinary animation timing edits; coordinate other affected timing
using [Time editing](#time-editing).

Named easings now include linear, ease-in, ease-out, ease-in-out, smooth,
sine-in-out, power2-in-out, power4-out, power4-in-out, expo-in-out, step-start
and step-end. Read `NAMED_EASINGS` from the SDK or use describe to discover them.
`ease`, `ease-in`, `ease-out` and `ease-in-out` use CSS cubic-Bezier semantics;
`smooth` is smoothstep, while `quad-in`/`quad-out` are explicit quadratic curves.
`step-start` jumps at the starting key; `step-end` holds until the arriving key.
Use the SDK evaluator when matching saved keyframes in source formulas.

For a parameter loop, use
`mh keyframe loop <instance> <parameter> --json '{"start":0,"end":1,"mode":"repeat"}'`.
Use `ping-pong` for forward/backward motion, or JSON `null` to clear the loop.
The range is in instance-local seconds and requires existing keys. Source defaults
can declare the same `loop` alongside defaultAnimation.keyframes; code formulas
can use SDK `mapAnimationTime(time, loop)`.

The first forward pass includes its endpoint. Subsequent cycles wrap or reverse
that interval. Current-value edits and key insertion map the project playhead to
the evaluated base-key time; editing an identified key's position edits its base
time directly. Loop metadata does not duplicate keys or change output FPS. A loop
is not a separate enabled-track switch, and defaults never overwrite saved loops.

## Time editing

For editable actions, pauses and cue alignment, prefer existing keys and exposed
timing controls. Move/scale selected key times as described in [Keyframes](#keyframes).
Coordinate affected windows, loops, markers and source-driven effects; moving keys
alone does not retime `useTime()` code.

An instance's visibility window is independent of its keyframe extent. `timing.start`
and optional `duration` use parent content seconds; `offset` is input time at the
window start and defaults to zero. Move a whole instance/group by changing its start
once, without also shifting child keys. To trim the head while retaining the motion's
placement, increase start and offset by the same amount and reduce duration. A tail
trim changes duration only. Keep out-of-range keys; the window clips their visibility.

Use `mh instance timing <id> --time <seconds> --edge start|end --timeSpace project|parent`
to place an edge; parent-space end placement needs an explicit duration. Direct
`--start/--duration/--offset` options edit those stored fields. All times are seconds,
not frame indices. An unrepresentable project edge reports an error rather than
guessing a position.

Read [Time remapping](time-remapping.md) only for media, an intentionally reused whole
sequence whose internal timing should stay intact, explicit user requests, existing
user-tuned maps, or procedural motion whose direct retiming would break useful
dependencies or require dense sampling. Preserve user edits; do not automatically
flatten existing maps.

For ordered entrances, write `{ "instanceIds": [/* IDs from inspect */],
"start": 0, "step": 0.15 }` to a JSON request and call
`mh instance stagger --file <request.json>`. Every selected instance must have
`editableTiming` enabled by its owner contract. The request sets each start to
`start + index * step` in its containing group's local seconds, preserving duration and local
keyframes. Negative step reverses timing order. One invalid instance rejects the
whole request. This also works in a batch with `type: "stagger"`.

This is an explicit edit, not a persistent timing rule: moving, inserting or
removing list entries preserves existing starts. Inspect the new order and call
stagger again when the intended effect requires re-spacing all starts.

## Collections

`mh table import --file <request.json>` replaces a data table or component list.
Use `describe <directory> table <instance> <parameter>` to inspect column contracts.
A request contains `instanceId`, `parameter`, and exactly one of `rows` (an array of
objects) or `text` (CSV/Excel clipboard TSV). Text requires unique headers; set
`delimiter` to `","` or `"\t"`. Optional `columns` maps source headers to declared
columns one-to-one. Unknown headers, ragged rows, invalid cells and duplicate row
identities reject the entire request. TSV/CSV supports quoted separators, escaped
quotes and multiline cells; formulas remain text and are never executed.

Tables use their declared identity column. Component-list imports additionally
require `identity`, naming a nonanimated text/number child parameter. The input is
a full replacement: matching rows retain IDs, omitted columns and unrelated
animation/timing; unmatched rows and child subtrees are deleted; new rows receive
new IDs and declared defaults. Row order follows input order. To edit a subset,
first inspect and include all retained rows in the replacement. Empty input clears
the collection only when its bounds permit. A changed animated column is rejected;
use explicit keyframe editing instead of silently overwriting its driver.

Example request: `{ "instanceId": "<inspect ID>", "parameter": "rows",
"text": "code,amount\nA,30\nB,20" }`. The same request is a batch operation with
`type: "table"`; the final combined state passes shared document validation before saving.
No table grid or clipboard UI is shipped in this phase.

`mh keyframe sequence --file <request.json>` generates missing item progress tracks
for the standard SDK Sequence mapping. The request contains `instanceId`,
`parameter` (component list), `progress` (owner numeric field), `itemProgress`
(child animatable numeric field), `timing` (the same duration/stagger/easing used
in source), `start`/`end` in project seconds, and optional `sampleRate` (default 60).
Sample rate is independent of output FPS. For example:

```json
{
  "instanceId": "<inspect ID>", "parameter": "rows",
  "progress": "progress", "itemProgress": "reveal",
  "timing": { "duration": 2, "stagger": 0.2 },
  "start": 0, "end": 2, "sampleRate": 60
}
```

Existing item tracks are never replaced. The engine samples current overall
progress plus each unanimated item's static multiplier, then writes the candidate
tracks in one validated edit. Generated key times use the child's local time;
range endpoints and owner key times are included. Values between samples are
linear interpolation, so this is a sampled approximation for nonlinear formulas
or discontinuities, not a claim of exact equality at every continuous time.
Outside the sampled interval generated tracks hold their endpoints. The candidate
is limited to 100,000 keys. Delete an independent track explicitly before choosing
to regenerate it. To return to inherited motion, remove all its keys and restore
its static reveal multiplier to 1.

For data updates, combine `type: "table"` and `type: "sequence"` in one batch.
The generator sees new stable IDs in the candidate and initializes only missing
tracks. This specialized operation does not replace the general named-output
animation baking capability.

Use `mh param reset --file <request.json>` for explicit restoration of selected
current source defaults. Select `parameters` as `{instanceId, parameter}` pairs,
`settings` as width/height/fps/duration names, and/or `timings` as instance IDs.
At least one target is required; all selected changes form one validated edit.
The same request works in a batch with `type: "reset"`.

A parameter reset restores the component field's current default value and its
declared default keyframes/loop (or removes the track if none is declared). It is
not an edit at the current playhead and does not preserve user keys on that field.
Resetting component/component-list fields recreates their declared initial subtree
with new identities; resetting a table recreates its initial rows with new row IDs.
Do not combine a subtree reset with a target inside that replaced subtree.

Timing reset requires editableTiming and uses the owning field's declared initial
timing. Settings reset uses the current composition declaration. Unselected fields,
settings and timing remain untouched. These are current source defaults, not a
historical snapshot of when the instance was first created; use Checkpoint for a
historical restoration. Source default changes alone still do not alter saved
instance values. There is no reset button/UI in this phase.

Ordinary undo/redo is a host-session history for Studio edits. `mh history undo`
and `mh history redo` apply that history when explicitly requested; CLI/Agent
mutations themselves never create ordinary undo records. Use Checkpoint for Agent
code/data rollback. Inspect `undoHistory` or capabilities to see available steps.
No undo buttons or shortcut bindings are added in this phase.

Undo applies only the data paths changed by the user operation, with version and
current-value checks plus final shared document validation. Disjoint Agent changes survive;
Agent changes to the same parameter/structural target invalidate conflicting user
records instead of being overwritten. A new Studio edit discards redo. A failed
validation/save does not consume the prepared undo record. Histories retain needed
asset originals during garbage collection.

Any activated contract change clears ordinary history (including rename/delete);
Checkpoint restore, explicit external-document reload and closing/reopening do so
as well. Pure code changes with an unchanged contract keep data records, but undo
still validates against the currently active document schema. History is memory-only,
bounded to 100 user steps, and never serialized into project packages/Checkpoints.
The Studio HTTP adapter marks its writes as Studio-origin; the CLI always marks
writes as Agent-origin. This origin label is bookkeeping, not an authorization
boundary. Atomic batch submission remains separate from undo policy.

Use `mh keyframe bake --file <request.json>` for registered outputs. Inspect component
`outputs` or `describe <directory> bake <instance>` to find their names. For example:

```json
{
  "targets": [{ "instanceId": "<inspect ID>", "output": "position" }],
  "start": 0, "end": 2, "sampleRate": 60
}
```

Start/end are project seconds; each callback receives its instance-local time.
Sample rate defaults to 60 and is independent of output FPS. Both range endpoints
are sampled. A request supports multiple targets and up to 100,000 total keys.
The host fixes source/data, samples in the controlled Runtime, checks the entire
candidate against stored-document rules, then commits keys and drivers in one revision. Source/data
changes or execution/document errors discard the candidate. No ordinary undo step
is created for Agent baking; use Checkpoint for a previous creative state.

Generated keys interpolate according to the parameter's normal rules (linear for
numbers/transforms; discrete for choices/text/booleans). Values between samples
are an approximation; outside the baked range the endpoint value holds. Increase
sampling when needed. Existing independent outputs are not overwritten: explicitly
reset before rebaking. `reset` also clears the target's independent driver so its
formula runs again. General formula output baking and the specialized `sequence`
command are separate operations; neither parses arbitrary JSX.

`mh effect apply --file <request.json>` edits one declared effects parameter.
Each request has `instanceId`, `parameter` and `operation`. Read IDs and effect
schemas with inspect/describe; do not rewrite the whole saved stack by hand.

- `add`: provide `effect: { type, params?, enabled?, mix? }` and optional index.
- `duplicate`, `remove`, `move`: provide effectId; move also requires index.
- `set`: provide effectId, name and value. Name is enabled, mix or a type-specific
  param. Static params change directly; animated params require project time and
  insert/update a key at the evaluated base time.
- `keyframe-set`: provide effectId, name and time; value may be omitted to sample.
- `keyframe-edit`: provide effectId, name, keyframeId and time and/or easing.
- `keyframe-remove`: provide effectId, name, keyframeId and current project time;
  removing the last key retains the current evaluated value as static.
- `loop`: provide effectId, name and a local-time loop object or null.

Effect IDs survive reorder and parameter edits; duplicates get new effect/key IDs.
Stacks are limited to 128 effects. Numbers/colors interpolate through the shared
animation engine; enabled/options switch discretely. Asset and arbitrary CSS text
params are static. The same request uses `type: "effects"` in an atomic batch.
Managed effect images participate in original retention, packaging and undo.

`mh component action <instance> <action-name> [--time <seconds>]` runs a declared component
action in the current source Runtime (time defaults to project second 0). Inspect
or `describe <directory> component.action <instance>` lists actual declarations.
The host fixes source/data versions, evaluates the callback, checks owned scope,
applies the candidate batch and validates it before one save. Errors or intervening
source/data changes discard the proposal. Agent actions do not enter ordinary undo.

`mh component control --file <request.json>` exercises the same backend used by future
custom UI. Provide instanceId, control, time and operations. The named control must
exist, and proposals may modify only its bound parameters/owned bound subtrees.
Studio-origin submissions enter session undo; Agent/CLI submissions do not.

Supported component operations are edit, keyframe/set/remove/edit/loop,
keyframes/selection, list, timing, time-remap, time-remap/stretch, stagger, reset,
table, sequence, geometry and effects. Parameter controls cannot change their own
instance clock; clock operations must respect the declared action/owned-subtree scope.
Every explicitly selected key is checked against the bound scope. IDs may be omitted for operations on
the current instance/owner; the runtime supplies the explicit playhead for edit,
key insertion/removal and effect edits when time is omitted. Reset cannot include
project settings. Project settings, source, history, render, assets import and
other platform jobs are outside this entry point. Use the dedicated CLI commands
for those tasks. No operations bypass normal parameter or shared document validation.

`mh instance geometry --file <request.json>` targets instanceId + parameter and uses:

- `set`: value may contain x/y/rotation/scaleX/scaleY.
- `resize`: width and/or height in the current unit; optional lockAspect overrides
  the stored resize preference for this operation. fixedFraction pins a normalized
  point while resizing; otherwise the current anchor stays fixed. Two supplied
  dimensions must agree with the ratio when locked.
- `anchor`: local pixel anchor `{x,y}` and optional preserveAppearance (default true).
  Coordinates are measured from the layer's top-left corner, even if position/size
  use percent. For an 80 × 40 px layer, its center is `{x:40,y:20}`, not `{x:.5,y:.5}`.
- `unit`: px or percent; converts base and every key while preserving key IDs and
  current pixel geometry.
- `aspect-lock`: enabled boolean; synchronizes the preference across base and keys.

Set/resize/anchor require project time when animated and follow normal current-key
editing rules. Unit/aspect-lock are whole-parameter metadata operations. Mixed-unit
keys are rejected. Low-level full-value edits are explicit poses; use resize to
apply the aspect-lock preference. All operations work in batch and scoped component
commands with `type: "geometry"`, share document validation and reject computed
outputs before baking. This adds no canvas handle UI.
