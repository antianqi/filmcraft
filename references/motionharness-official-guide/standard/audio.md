# Standard audio

Add tracks to `mh.json`; they follow project time in playback and export.

```json
"audio": [
  { "src": "assets/music.wav", "start": 0, "duration": 6, "volume": -8,
    "fadeIn": 0.15, "fadeOut": 0.3 },
  { "src": "assets/clip.mp4", "start": 2, "offset": 0.5, "duration": 3 }
]
```

Paths are relative to the project. `start`, `offset`, `duration`, `fadeIn` and
`fadeOut` are seconds; `volume` is dB (0 keeps source volume). `pan` ranges from
-1 to 1. `loop`, `muted` and a nonnegative `stream` index are optional. If duration
is omitted, playback ends at the original's end after its offset. Looping across
a longer interval needs an explicit duration. For matching video, import this
same config in the scene to reuse its timing; the materials guide has the example:
`mh skill --reference materials --section "Video timing"`.

Use local originals. `mh preview --file assets/music.wav` reads duration, audio
format and levels without opening a project. It also accepts MP3 and video files;
omit frame times for pure audio. To check the project mix, render only the affected
interval with `mh render .tmp/mix-check-v1.wav --json '{"start":0,"duration":1}'`,
then inspect the file. Use actual audio input with a capable
tool for listening judgments; levels alone are not listening. See
[Background checks](rendering.md#background-checks). Routine checks do not play
through the user's Studio or speakers.


Studio can move, trim, change volume and fades on these existing references.
Those edits write back to `mh.json` and share its preview/export results. They do
not require additional declarations or changes to the scene's JavaScript.

When a user later requests deletion, Studio mutes only that reference and creates
an ordinary pending marker with `intent.kind=delete-standard-audio`. Its
`reference.id` matches the configuration entry's `referenceId`; the host assigns
that identity at deletion time. Do not add identities during initial authoring.
Use the saved index/snapshot as context, never delete every reference to the same
file. Check scene/config dependencies, remove the selected reference, keep its
original media, check the affected interval with a background mix/preview, then confirm the
marker's requestVersion.
Removing the marker cancels the request and restores the previous mute state.
