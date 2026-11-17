# Time remapping (advanced)

Read this when the [time-editing conditions](editing.md#time-editing)
apply. Routine keyframe and window edits stay in the editing guide. Reuse the
appropriate clock owner; avoid accumulating correction maps or separately editable
copies of one pacing table. Any requested removal/flattening needs visual and
editing checks, including holds, repeats, reversals and nonlinear curves.

## Time mapping and key occurrences

Time-remap input is `parent content - start + offset`; curve values are content
seconds. Parameters, `useTime()` and children use content time; media parameters
apply afterwards. Use `mh time remap` to edit the native curve; `remap: null`
restores identity mapping. Read `mh describe "time remap"` for the current schema.
Root remapping affects descendant visuals and sound together; use it only when
the intended change covers the whole composition.

Move/trim do not rewrite content keys. `mh time stretch` uses a positive factor to
change the window and curve input times together, preserving content keys and mapping values. Root
stretching also scales project duration, root placement start and explicit root
duration; the content offset is preserved, including negative-start pre-roll.

A source key can have several project occurrences or a held range. Listings return
`localTime` and `occurrences`; project `time` is null without a unique point. Supply
`occurrenceTime` for an ambiguous project edit, or use `timeSpace: local`. Never
guess an inverse branch. Native time keys use `channel: time-remap` without a
parameter and use mapping-input seconds
locally.

| Operation | Supported `timeSpace` | Default | Meaning of local time |
| --- | --- | --- | --- |
| Ordinary parameter keys/selections | `project`, `local` | `project` | Content time after this instance's remap |
| Time-remap keys; retime add/move | `project`, `local` | `project` | Input time before this instance's remap |
| Whole `time remap` track | `local` | `local` | Key times are input seconds; values are content seconds |

Local selections require one instance and one clock domain. Ordinary content keys
and native mapping-input keys have distinct local clocks. Seconds are never frame
indices. Window fields and edge placement are covered by [Time editing](editing.md#time-editing).

## Speed segments

Use `mh time retime` for ensure, add, move, remove, speed, easing or reset.
Add/move accept a project `time`; point edits use `keyframeId`. Move ripples later
speed points and the clip tail, preserving later interval speeds. Use boundary=start/end
to move an implicit clip edge without first creating a curve. Moving the start edge
changes the first interval and clip start while later project positions stay fixed.
Reset restores forward 100% over the current source span and adjusts clip length.

Speed uses a signed, nonzero `percent` with the segment's existing direction. It
changes that input interval, shifts later input anchors and adjusts only the clip's
duration; source keys and independent clips stay intact. Root edits also map the
project end through that change. Percent is average content seconds per input second,
not instantaneous speed or speed after ancestor maps. Zero-average segments need
point/curve editing. Omit keyframeId for speed/easing on the first segment.

Add preserves the exact curve, using native `curveSlice` where needed. Explicit value
edits clear adjacent slices; easing edits clear the outgoing slice. Preserve slice
data when copying keys. Only documents using slices require v3; older documents
remain readable.

Retime segments report `projectDuration`, the sum of visible occurrence lengths in
project seconds, alongside the average `percent` in the instance's input clock.
`mh describe "time retime"` returns the CLI syntax, capability ID `time-retime`, and
route/batch type `time-remap/retime`. Audio pitch limitations remain in
[Sound editing](audio.md#sound-editing).
