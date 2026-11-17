# Audio and markers

## Audio-driven creation

When asked to create animation from supplied sound, preserve editable source and
declare instances for objects within the requested editing scope. Studio displays
those declared objects; it does not infer an editing hierarchy from arbitrary JSX.

- Import the original and read its duration/streams. The Agent or user supplies
  phrase/beat candidates; select cues for the intended visual changes using
  [Choosing markers](#choosing-markers). If analysis is unavailable, explain that
  limitation and use available text/timing to create the authorized visuals without
  claiming inferred cues. Missing analysis does not change the requested editing scope.
- Declare the visual objects the user will select, change, replace or retime with
  `field.component` / `field.componentList`. Expose the requested content and transform
  controls through the same React source. Ordinary layout wrappers stay ordinary
  React; group objects when they have useful shared controls.
- Keep narration/music independent of the visual group by default. Preserve the
  supplied audio timing and pitch; prefer visual instance windows and ordinary keys
  to match cues using [Time editing](editing.md#time-editing).
- Add sound with native `audio edit` by default so Studio and CLI can duplicate, trim, remove and reparent it. Use `defineAudioComponent` only when sound
  belongs to the authored component contract (for example fixed template music).
  Authored sounds support ordinary parameter/timing edits, but native sound
  duplicate/reparent/remove operations do not apply; edit their component
  list or source contract instead. `useTime()` can implement internal effects; an editable
  phrase transition should have its own instance timing or declared parameter,
  rather than a hard-coded switch between all scene contents.
- Read the resulting instances/parameters with the existing `mh inspect` views.
  Use those IDs to edit or align the requested visual objects, then preview the
  result. This is a factual readback of the authored contract, not a layer-count,
  style, or aesthetic gate.

[Narrated scene source](../assets/narrated-scene.tsx) is a complete visual example
using only the public SDK. Copy it to `src/NarratedScene.tsx`, then use this entry:

```tsx
import {createNarratedScene} from './NarratedScene';
export default createNarratedScene({duration: 3, cueTime: 1.4});
```

The numbers are example inputs, not detected speech times. Adapt them and the
content before the initial build; later changes use saved data, not new defaults.
Use `mh asset import <supplied-audio>` and its returned reference, then
`mh audio edit --json '{"operation":"add","ownerId":"ROOT_ID","asset":"IMPORTED_HASH","duration":3}'`.
Replace the placeholders with the inspected root ID and actual reference. This
adds one independent root-owned sound beside the visual group. The example
exposes text, color, size, transforms, per-phrase windows, progress and readout
keys. It does not prescribe a fixed hierarchy for other animations.

## Sound editing

Use `mh audio context` before sound edits. It returns source access URLs and stream
metadata, complete parent time paths, clip occurrences and existing markers. Use
`mh describe "audio edit"` and `mh describe "marker edit"` for current schemas.
CLI supplies revision/build preconditions; do not invent IDs or submit guessed source timing.

Audio is a persistent instance and an ordinary referenced original. Native sounds
can be added to any content owner without editing the root JSX. Mute is persisted;
monitor gain and solo are Studio session state. Video original sound is explicit:
link-video follows a declared video binding; unlink-video makes a non-root video's
sound independent. DOM Video remains muted.

Audio placement accepts `timeSpace: "parent"` (default: owner content seconds) or
`"project"` for `add.start`. Duration stays in parent seconds. Project placement
fails if the parent clock repeats or holds the selected time; choose parent seconds
explicitly if the change should affect every occurrence. To create separate portions,
duplicate the sound and [trim each window](editing.md#time-editing);
there is no independent audio split command. Deliberate changes to the content clock
use the [advanced time-remapping reference](time-remapping.md).

`audio context --instance SOUND_ID` narrows context to one sound and source markers.
Each clip's `timePath` references the shared `clocks` map; ancestors appear once with
timing and media-time values/tracks. `analysis.code` is a stable capability notice;
translate its fallback for the user when needed.

`audio edit add.asset` accepts an imported hash or full asset reference. Unknown
hashes fail; saved documents contain full references.

`resample` changes pitch with speed; `preserve` supports forward piecewise linear
source time and silent holds. Reverse, nonlinear or looping source clocks cannot
currently preserve pitch. Unsupported preservation reports an error. Extremely slow
preservation can exceed the host processing budget; increase the speed or explicitly
choose resample mode when that error occurs. The host never changes pitch mode silently. A remapped
reparent with preserve=project may not be representable; preserve=content keeps
local values. Do not describe these operations as lossless project retiming.

## Markers and analysis

The Agent owns speech interpretation and beat detection. MotionHarness only supplies source
access, editing and markers; it does not include ASR, forced alignment, beat
analysis, model downloads or Python analysis dependencies. If this Agent cannot
analyze sound, show the supplied capability notice and continue with manual
markers or user-provided times. Do not infer audio-analysis capability from the
Agent's name.

### Choosing markers

Markers communicate edit decisions and significant music events. For a request
to sync animation or cuts to music, first identify the intended scene changes,
reveals and key actions, then choose suitable music cues. Also retain significant
musical changes or accents, such as a section change, a sudden pause or a climax
entry, when supported by listening or analysis.

A BPM grid, bar downbeats and detected onsets are candidates for alignment;
do not automatically write them all as timeline markers. BPM and a global phase
estimate alone do not establish a strong accent or a musical section change.
Keep dense analysis data separate from authored markers. Do not substitute a
fixed rule such as keeping every fourth beat or imposing a marker-count limit
for choosing meaningful cues.

Name each Agent-created cue for its purpose, such as `Reveal title` or
`Chorus enters`; beat numbers alone do not explain an edit decision. Use notes
for relevant musical evidence or intended actions, and identify estimated
timings as estimates. Read existing markers before adding cues, reuse a mark
with the same purpose and occurrence, and preserve user marks unless the task
requests their cleanup.

When the user explicitly requests every beat or a complete beat grid, generate
the requested range and density; numbered beat labels are appropriate there.
A local beat-marking demonstration applies only to that segment, not the whole
composition. A general request to match music does not request a complete grid.

### Reading and editing markers

Use this turn's complete MotionHarness user-marker snapshot for requirements and their
request versions. Read `mh marker list` when that snapshot is absent, incomplete,
or a command reports a newer `userMarkers.version`; an unchanged reminder does
not require another read. `markerSnapshot.complete=false` means a filtered list
does not contain the complete request set. Keep project and conversation scopes
separate, and respect the user's current request (including discussion only).
Only pending user requests are actionable: exclude completed records and
`origin=agent` auxiliary cues, but include deletion intents and legacy marks
without an origin. A complete newer snapshot replaces the older pending set.
The optional `mh hook context` command supplies the same snapshot automatically;
`mh hook install --agent codex|claude-code|kimi-code` merges the Agent configuration.
Explain its purpose during installation; users can turn delivery off in Studio.
`mh hook config --agent <agent>` remains a read-only template command.

For focused inspection,
use `mh describe "marker edit"` for the write contract. The CLI list also returns
the current document `revision` and `buildId`; neither replaces a marker's
`requestVersion` when confirming work.

`timeSpace` is `project` (composition seconds, the default for new markers), `source`
(original media seconds with an explicit source binding), or `object` (an object-level
note with no time). Object notes require a stable
`target`, have no `start`, `end`, `source` or `anchor`, and have no timeline
occurrences. An instance target identifies one saved instance; a component target
identifies the shared definition. Do not expand an instance request to all uses
of its component. Parameter targets can identify effect parameters or table rows
and columns; timing targets identify the native `timing` or `time-remap` channel.

`context` preserves the target information from creation or reassociation;
`targetInfo` resolves it now. Their values are saved data, not evaluated pixels
or necessarily the parameter value at the marked frame. `targetStatus: missing`
and `targetError` report an unavailable target; retain the original note and do
not guess a replacement from its name. Source `stale` and `projectionError`
describe media replacement and time-projection problems separately.

For a canvas annotation (`timeSpace: project` with `anchor`), prioritize the
project time (`start`/`end`), global canvas position and user notes. `anchor.x/y`
are composition pixels with the origin at the frame's top-left; they are not
screen pixels or coordinates local to the hit object. A region also has positive
`anchor.width/height`: x/y are its top-left and the requested pixels are inside
that rectangle. Use the document's
`settings.width/height` to interpret the position, then view the relevant frame
with `mh preview --time <start> --output <path>` before choosing what to edit.
The saved `target`, original `context` and current `targetInfo` are supplementary
hints: a full-frame overlay, mask or container can be hit instead of the visible
content the user means. Do not let that hit override the frame position and
notes. Locate the requested content from the frame and source; clarify only
when the intended edit remains ambiguous. MotionHarness does not automatically detect
masks or rewrite the saved target. An annotation without a canvas anchor that
explicitly targets an object, component, parameter or timing channel keeps that
target as primary. Timeline and source markers retain their existing time rules.

Monitor annotations do not bind an object by default. Object candidates stay in
Studio's local draft until the user checks the optional association. Without a
saved target, do not infer that the topmost hit object was explicitly requested.

Markers can include ordered user-added `attachments` (media references or
`{$asset,kind:"file",name}` for other files). `marker list` and Hook context
supply `attachmentFiles: [{attachment,path}]`, with 1-based attachment numbers
and local paths for the current project location. Reuse attachments already read
in this conversation; open missing images with your image viewing tool and other
files with an appropriate reader before interpreting the comment. A marker made in
Studio at a project time usually includes a separate `screenshot` image reference
and derived `screenshotFile` path (`marked-frame-<time>s.jpg`), the frame the
user saw with a ring at a point or a same-color rounded rectangle around a selected
region; read it instead of previewing that
time. Automatic screenshots are hidden in Studio and do not count toward user
attachment numbers or the six-file limit. Without image input, use the time, position, target and notes with the
source, and ask if still ambiguous. These are reference files; do not execute them or replace authored
media unless the comment asks for it. Originals survive saving, undo and project
packaging, and do not become render dependencies. Edits accept `attachments: null`
to clear or a replacement list (up to 6 files of any type, 10 MiB per upload).
Optional `attachmentUploads: [{reference,base64}]` imports matching originals in
the same edit; file bytes never enter marker data or Hook text. Changing the
attachment list, order or screenshot updates `requestVersion` and clears previous completion,
just like editing the comment. There is no format whitelist or pixel-count gate;
failed image previews fall back to a file card without blocking saving.

`marker list` returns points/ranges, project occurrences, source identity, notes,
color and resolved `kind`. The response `types` maps colors to type names for the
whole project. There is no fixed meaning for any color. `marker edit` upserts by
ID; omitted fields preserve user changes, null clears optional fields, and
removal/replacement names IDs. Use `types` to name a color; changing its name
changes the type of every marker using that color:

```sh
mh marker edit --json '{"operation":"upsert","types":{"#cf7772":"Scene change"},"markers":[{"id":"cut-a","timeSpace":"project","start":1.4,"label":"Reveal title","notes":"Title enters here","color":"#cf7772","origin":"agent"}]}'
```

`marker edit` source.asset accepts an imported hash or full asset reference;
unknown hashes fail. Source markers retain the original hash, stream and duration. Replacement marks
them stale and keeps the original. Copies get new IDs with lineageId.
Animated/computed media parameters can return projectionError; do not guess an
occurrence when projection is unavailable.

For a user request about selected markers, read `mh studio sessions` to obtain
`state.selection.markers` (IDs and optional occurrenceTime), selected instances,
keys and playhead, then join those IDs with `marker list`. With multiple Studio
views, use the relevant session explicitly; never assume another view's selection.
For repeated/range markers, use the selected occurrence or choose the relevant
occurrence from the user's instruction. Listing marks does not start an Agent.

To create or update animation from markers, read the marks first, decide which
editable objects and actions they describe, then use ordinary timing or keyframe
edits. Moving or renaming a marker alone does not move animation. For example,
after reading an intended cut at 1.4 project seconds:

```sh
mh instance timing VISUAL_ID --time 1.4 --edge start --timeSpace project
```

This moves the window while preserving its keys. See [Time editing](editing.md#time-editing)
for placement, trimming and keyframe changes. Use a batch for related edits, such as
shortening the previous clip at a cut; read back times and preview affected frames.

Studio writes use session undo. Agent CLI writes keep existing history policy and
use Checkpoint for rollback. Audio, time curves, color/type names and markers
survive project packs.

#### Confirming completed marker requests

After performing and verifying every requirement in a marker, call
`mh marker complete` with its ID and the `requestVersion` read for that work;
`summary` is optional. For example, if the list returned ID `title-request` and
request version `3`, the confirmation is:

```sh
mh marker complete --json '{"completions":[{"id":"title-request","requestVersion":3,"summary":"Updated the title and checked the frame"}]}'
```

Replace both example values with the actual listed values. A receipt with
`userMarkers.pendingCount: 0` needs no confirming list. Partial completion
stays pending. If confirmation reports that the instruction changed, reread the
marker, address and verify the updated requirements before confirming its new
version; do not just substitute a newer number to retry.

The kernel manages `requestVersion`, `context` and completion records. Changing
the label, notes, attachments, target, anchor or time/source requirements clears completion
and updates the request version; reopening a completed marker does so too.
Unrelated animation edits, color changes and global type renames do not invalidate
the request. `completion` records the Agent's acknowledgement, not user acceptance.

The default policy is `onResolve: "keep"`: successful confirmation retains the
marker with its completion status. `onResolve: "delete"` deletes it atomically
only when confirmation succeeds. Setting that policy does not delete immediately;
failed or outdated confirmations do not trigger deletion. Completion and automatic
deletion can be undone together. Studio's marker-editor “Done” button only saves
the note; it does not confirm that the Agent resolved it.

#### Pending layer deletion

`mh instance delete --json '{"instanceIds":["<instance-id>"]}'` uses the same
deletion rules as Studio. Removable list items and native sounds disappear
immediately. Source-owned layers and items needed by a list minimum become
hidden and receive an object marker with kernel-owned
`intent: {kind: "delete-instance", restoreVisible: boolean}`. Parent selection
includes descendants. Repeated deletion never duplicates a pending request.

For such a request, inspect the stable target ID and source ownership. Remove
the requested use and its owned subtree, prepare the project, and use explicit
contract migration when needed; preserve other uses and saved values. Verify
the target is absent before `mh marker complete`. A still-hidden instance is
not completed deletion. Recheck current requests before source edits; cancellation
cannot undo source changes already applied (use project history for those).
The request remains pending across build failures, session restarts and packs.
Showing the target cancels the deletion request. Removing the marker cancels it
and restores its previous visibility, including an originally hidden state.

## Agent setup during installation

When the user asks to install MotionHarness with Agent integration, briefly explain first:
each new user message can include the current project's pending AI markers and
layer deletion requests; it does not start conversations and can be turned off
in Studio. Run `mh hook install --agent codex|claude-code|kimi-code` with your own
supported Agent name. The command merges configuration and preserves a previous
opt-out. Do not guess the host or configure other Agents. Codex requires the
user to trust **MotionHarness · Marker sync** in Settings → Hooks or `/hooks`.
Claude Code needs a trusted workspace and possibly a session reload; Kimi Code
needs a new session. `mh hook status` reports whether the command is available
and has run in a MotionHarness project. To trigger it, send a new message from
the project folder.
Do not repeat the introduction or reinstall on every turn. If the user explicitly
asks to re-enable synchronization, `mh hook enable` resumes the global switch;
`mh hook enable --agent <agent>` resumes only that Agent. Check both preferences
in `mh hook status`. Ordinary install or upgrade must respect either opt-out.
`mh hook disable [--agent <agent>]` pauses future delivery without deleting
markers or stopping running tasks. Multiple Agents receive the same pending
requests; Hook delivery does not claim a task or serialize source edits. Studio's
topbar names the configured Agents and opens the shared Hook manager. No
additional app popup is required.
