# Convert Standard to an independent Pro project

Use the user's specified objects and intended edits as the conversion scope.
A name, time, canvas position or existing marker can identify a target without
Standard layer IDs. Ask if the target cannot be identified. Open internal parts
only when the user wants to edit them separately.

Create a separate Pro project with `mh new <new-directory> --type pro`; preserve
the Standard original. Read
`mh skill --reference pro --section "Authoring rules"`
for the requested editing contracts and adapt the scene entry, preserving picture, timing and sound.
Changing projectType alone is insufficient.
Declare instances and parameters only for the agreed edits. Keep remaining
visuals in reusable source code. Include parent groups only where layout, shared
timing, clipping or effects need them.

Preserve the original drawing structure where possible. Editable objects can
share a Canvas or 3D scene; separate edit controls do not require separate render
surfaces. Keep shared depth, lighting and effects together.
When a shared renderer reads `useInstance(reference)`, use its `visible` to
decide whether to draw that object, its `time` for any remaining code-driven motion,
and its evaluated `values` for declared controls. Unopened drawing can keep project time.
Apply every declared transform, including skew; `basicTransformMatrix` provides
the existing rotation, skew and scale calculation for Canvas.
For a minimal single-Canvas example, read [selected title](assets/selected-title.tsx).
Use it as a Pro project's entry (for example `src/project.tsx`, with matching
`mh.json.entry`): the title's fade is editable on its opacity track, and the
animated background stays in drawing code. The title is editable through its layer
row, parameter panel and timeline.

Compare representative background frames and, where needed, short clips/audio at
the original settings; follow [Background checks](references/rendering.md#background-checks). Then
exercise the requested controls and timing. Hide and show an opened layer, move its
start time, and check that declared transforms affect its drawing. Explain which objects and properties
are editable in Pro and which remain source-edited. When opening more objects
later, extend the existing Pro project while preserving instance IDs, saved
values and keyframes.

There is no automatic converter, mode switch or bidirectional synchronization.
Each project owns its own checkpoint history. Reopening the Standard original
opens a different project.

## Animation keyframes

By default, a Pro split includes the selected object's main existing motion as
editable timeline tracks. Follow any narrower scope in the marker notes or control
choices: a text-only edit or a request to change only the layer's start or end can
leave its motion in source. The Studio `animation` shortcut (“Timing and animation”)
requests actual keyframes for the existing motion in scope. Keep static properties
static and leave unrelated motion and internal procedural effects in source.

Preserve meaningful key times, values, easing and loops from the original motion.
For new instances, seed tracks with `defaultAnimation` in instance-local seconds.
For saved instances, use `mh keyframe set` or a batch; see
[editing keyframes](references/editing.md#keyframes) for time spaces and easing.
Keep existing saved keys unless the request changes them. Render each converted
channel from its evaluated parameter value and remove its old time formula.

Before handoff, confirm the saved keys with
`mh keyframe list --instance <id> --parameter <name>` in the Pro project. Compare
the original and new motion at and between the keys. Temporarily edit a representative
key to confirm it changes the drawing, then restore the intended value. If requested
motion cannot be converted faithfully, explain what remains in source and leave that
request pending.

## Requests from Studio and returning the result

Clicking PRO in Standard enters a marking workflow; the project remains Standard
until conversion succeeds. `intent.kind: "pro-edit"` marks an explicit request to
open editing. Its optional `controls` (`content`, `transform`, `appearance`,
`animation`) are user-intent shortcuts, not parameter names or a required schema.
Use the marker time, canvas anchor, notes and attachments to locate the object.
Preserve each marker's `onResolve` choice while publishing. Completion retains a
`keep` request or removes a `delete` request; both publish the local Pro continuation.
Once committed, cleaning up completed annotations does not remove that continuation.
Continue using the original renderer where appropriate.

After comparing previews and exercising the requested edits, complete the source
requests with `mh marker complete` and a handoff result:

```sh
mh marker complete --project /absolute/source-project --json '{"completions":[{"id":"<read-marker-id>","requestVersion":<read-version>,"summary":"Title editing is ready"}],"handoff":{"project":"/absolute/pro-project","instanceIds":["<read-instance-id>"],"time":1.2}}'
```

Read actual marker versions and destination instance IDs. The destination must
be a prepared Pro project. This command checks the destination and publishes an
Open Pro action in Studio. Verify visual parity and the requested tracks before calling it.
Pro request completion requires this handoff result. Do not batch it. A stale request, missing instance or failed preparation
leaves the requests pending. Standard source and its checkpoints remain intact.

After the handoff, create and edit in the Pro directory, using its explicit
`--project` path for CLI commands. The local Hook follows the completed source
handoff and includes any unfinished source requests separately. Studio opens
Pro at the result time and reveals its editable layer. The local handoff link
is not included in `.vmg` packages; the Pro project itself stays portable.

To expose another object later, click PRO in the existing Pro project. Preserve
its existing saved values, keyframes and instance IDs. Complete with the same
Pro directory as the destination. Adding fields/instances is supported; renaming,
removing or changing existing contracts must use the normal migration workflow.
Do not rebuild from the Standard original or reset saved data to resolve a migration.
