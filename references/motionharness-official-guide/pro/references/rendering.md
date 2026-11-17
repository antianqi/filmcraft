# MotionHarness time and output

## Rendering

Every animation is driven entirely by MotionHarness time. A 3-second composition samples
90 frames at 30 FPS and 180 at 60 FPS. Seeking back to a time must reproduce its
frame independently of playback history.

SDK Video is positioned by MotionHarness time and stays paused. SDK Canvas and useFrame
register asynchronous drawing with the Scene. Honor the supplied AbortSignal;
await work that contributes to a frame. Canvas callbacks receive logical dimensions
and actual pixel dimensions so higher-resolution exports preserve layout.

`mh preview --time <seconds> --output <output.png>` checks the visible frame and reports
current source/data. It waits for the current source to compile and activate before
capture, then returns only after the image is saved. No sleep or status polling is
needed after editing source. Build errors, pending migrations and external data
conflicts return a diagnosis instead of a frame from old source.

For several poses, `mh preview --times '[0.4,2.15,3.5,4]' --contact-sheet`
captures 1–32 frames sequentially with one browser and one build/revision. Use a
returned fresh directory under `.tmp/previews/<run-id>`; `--output-dir <directory>`
selects an explicit directory and refuses to overwrite existing preview files.
Numbered PNG files preserve duplicates and request order. `--contact-sheet` adds
`contact-sheet.png` with frame numbers and project seconds; `--columns 1` through
`--columns 8` changes its layout (default 4). Read returned paths after the command
completes successfully; there is no separate image-processing step.
Read `manifest.json`: `complete: false` means the set is incomplete, even when
some files exist. A source/data change aborts the set rather than mixing versions.
Failed sets are retained. stderr returns the underlying error, `errorCode`, the
manifest path when available, and a retry command using a new automatic directory.
Fix source/migration/data errors before retrying. A contact sheet is saved only
for a complete same-version set. `.tmp` output does not trigger source rebuilds or
enter source snapshots, Checkpoints or editable packages. Use it for temporary
previews, rendered videos, caches, logs and one-off scripts. Keep generated models,
materials and reusable tools needed for continued editing or delivery in ordinary
project directories, such as `models/`, `assets/` or `tools/`; no fixed directory
names are required.

Choose evidence for the edit: background project frames for layout and repeated/
backward seeks; short clips for continuous motion; actual audio input for listening;
parameter changes for new controls; unpack/reopen for an editable archive.
See [Background checks](#background-checks). Distinguish generated files, viewed
frames, analyzed audio and actual motion review/listening. Command success or
nonzero levels do not prove continuous motion or listening quality.
Reuse successful checks while their inputs are unchanged. Add browser automation,
per-frame comparisons or extra dependencies for a specific requirement or observed
problem that available tools cannot check. Fix observed defects and verify the
affected behavior before delivery.

For video delivery, export the finished version after relevant preview checks.
For checks that need an encoded file, such as codec compatibility, export the
smallest relevant range:

```sh
mh render .tmp/output-check.mp4 --json '{"start":8,"duration":2}'
```

`mh render <output.png|output.mp4|output.mov> --json '<options>'` performs formal
capture and saves output without an interactive page. Options include start,
duration, width, height, fps, codec and alpha.
Pass options directly, for example:

```sh
mh render .tmp/video.mp4 --json '{"fps":30,"quality":"high"}'
mh render .tmp/frame.png --json '{"start":1.5}'
mh render .tmp/blur.mp4 --json '{"motionBlur":{"shutterAngle":180,"samples":8}}'
mh render .tmp/overlay.mov --json '{"codec":"prores-4444","alpha":"straight"}'
```

`mh describe render` supplies `cliRequestSchema` and runnable CLI examples.
Its `requestSchema` describes HTTP: the CLI supplies owner/version preconditions
and wraps the options in `request`. Do not put that wrapper in CLI JSON, file or
stdin payloads. An omitted render format is inferred from the output extension.
Preview and render wait for completion. Wait on the running task and continue as
soon as its final result arrives; a wait limit is an upper bound, not a fixed sleep.
Avoid short repeated polls or restarts. The file may not exist until it succeeds.
Success returns `saved: true`, the output path and media details; preserve its exit
status and JSON result. Chain dependent commands with `&&`; the completion receipt
needs no confirming status request.
`mh render status` independently reports progress or helps diagnose a problem;
`mh render cancel` cancels it.

Motion blur is off by default. `motionBlur` accepts a shutter angle >0–360° and
2–32 integer samples per frame (180°/8 is a useful starting point). It uses the
same `useTime()`/frame preparation at fractional absolute times, blends with
correct alpha weighting, and leaves FPS, duration and audio unchanged. Higher
sample counts smooth trails but cost more rendering. The host protects the
selected export bounds, not arbitrary internal cuts. Omit the option when the
authored work already includes temporal trails; ordinary shadows or depth blur
need not be removed. Check export motion blur with Studio's current-frame and
one-second effect previews, which share the native pipeline. Live playback shows
the scene before export motion blur.

PNG captures a complete browser frame without FFmpeg. MP4 sends complete PNG
frames directly to native FFmpeg for H.264 or H.265 encoding. Released CLI
binaries include standalone LGPL FFmpeg and ffprobe; no separate installation
is needed. Set `MH_FFMPEG` / `MH_FFPROBE` to use compatible external programs.
Development hosts may use PATH. ProRes needs FFmpeg 7 or newer. `mh doctor`
reports actual encoder availability. Inspect the saved video with video-capable
tools in the background to verify the actual encoded motion.
If none is available, report saved/encoding results and any inspected static frames
as such, and leave continuous motion verification explicitly unverified. Container
metadata and file size do not replace decoding or playback.

`mh preview --file .tmp/video.mp4` reads actual media details without opening a
project, including file size in `bytes` and container-declared `frameCount` (`null`
when unknown, without a full decode or fps-based estimate).
`encodedWidth`/`encodedHeight` precede display rotation. `width`/`height` include
right-angle rotation (`rotation` is counter-clockwise degrees within [0,360));
non-right-angle rotations leave metadata sizes unknown (`null`). Extracted PNGs report
their actual pixel dimensions.
Add `--times '[0,1.5]' --contact-sheet` to extract PNGs and a labelled
contact sheet, or `--time 1.5 --output .tmp/frame.png` for one PNG. Times start at
the video's beginning, even for range exports; each decode selects the first
available frame at or after the requested time. Choose times before the end.
Inspection uses the released CLI's bundled ffprobe/FFmpeg; `MH_FFPROBE` /
`MH_FFMPEG` select compatible overrides and development hosts may use PATH.
Contact sheets need drawtext and xstack filters. Audio inspection decodes the first
audio stream and returns mean/peak levels when available. These and selected frames
do not establish continuous playback or listening quality.

For technical playback-to-end checks, use the existing entry:

```sh
mh preview --file .tmp/output-v1.mp4 --check-playback
```

This optional check plays the saved file once in an isolated silent browser and
reports completion, browser errors, total/dropped video frame counts and observed
frame timing. It takes roughly the clip's duration and never controls the user's
Studio. Browser codec support is separate from FFmpeg support: a failed browser
check does not by itself mean the export is corrupt. `completed` means playback
reached the end; inspect `droppedVideoFrames` separately. This does not judge visual
quality, motion design, audio timing or listening quality. Keep those checks explicit.

When video delivery includes encoded-frame checks, export and inspect selected
frames in one terminal invocation, continuing only after successful export:

```sh
mh render .tmp/video.mp4 &&
mh preview --file .tmp/video.mp4 --times '[0,1]' --contact-sheet
```

Choose times within the saved clip; give the call time for both commands before
reading the images.

Frame preparation errors must be fixed; do not replace awaited media with an
arbitrary sleep. Export snapshot and cleanup behavior are described below.

Before rendering, `mh render plan [--json <options>]` returns normalized
parameters, frame count, last sampled project time, encoded duration, target
bitrate and estimated video payload bytes without editing or locking the project.
It uses the same planner as export startup. It does not reserve a version or prove
that browser/codec preparation will succeed.
It accepts the same flat options; `mh describe "render plan"` supplies its CLI schema
and example. An omitted plan format defaults to MP4.

Options include format (default mp4), start/duration in seconds, output width and
height, sampling FPS and quality (balanced/high/master). Omitted video duration means
the remaining composition after start. Fractional FPS, including values below 1,
is preserved. Frame count rounds up to complete samples; encoded duration can
therefore exceed the requested interval by less than one frame. The last sample
stays within the requested interval. PNG samples one time (including the exact
composition endpoint) and has no video bitrate/duration estimate.

Bitrate/size are H.264 target estimates, not guaranteed codec output. ProRes
does not reuse an H.264 size estimate. Output settings
never rewrite composition settings. Invalid options are rejected before starting.
Exports keep their starting source, data and assets while editing and preview continue.
Later changes are excluded from the running export. One export runs per project
until renderer cleanup finishes. Studio shows progress and initiator in the top bar;
the details can be dismissed. The export panel uses the same planner.


### Native output formats

File extensions select the output. MP4 defaults to H.264; request `{"codec":"hevc"}` for H.265. MOV defaults to ProRes 4444 with straight alpha. Use `prores-422` or `prores-422-hq` for opaque 4:2:2 editing media; `prores-4444-xq` also supports straight alpha. Hardware failure retries the same MP4 codec in software when available. Check the local encoder capabilities with `mh doctor`.

`.gif` (binary transparency, default up to 20 fps), `.webp` (lossless, full alpha), and `.apng` produce silent infinite loops. `.zip` selects `png-sequence`: numbered PNGs and a timing manifest. Animated images and sequences default to straight alpha; authored opaque backgrounds remain opaque. PNG, APNG, PNG sequences and WAV need no FFmpeg. `.wav` writes only the selected mixed stereo audio at 48 kHz/24-bit PCM with sample-accurate duration; omit motion blur for audio. A silent selection produces silence.


## Transparent video

MOV defaults to `codec: "prores-4444"` and `alpha: "straight"`.
`prores-4444-xq` is also available. `alpha: "none"` keeps an opaque host
backdrop. Transparent PNG uses `alpha: "straight"`; MP4/H.264 rejects that
option. Authored backgrounds remain part of the artwork in every format.

The native encoder converts sRGB capture to Rec.709 and preserves straight
alpha. The capture source is 8-bit RGBA; a ProRes container does not increase
the precision of the authored image. Validate transparency, semitransparent
edges, shadows and opaque black objects against both light and dark footage.
FFmpeg decoding alone is insufficient evidence of Apple/Resolve compatibility.

## Session lifecycle

Project commands start/reuse sessions. Normal opening/editing commands automatically
open or reuse Studio once per session without waiting for connection. `preview`,
`render` and `render plan` stay headless even on first preparation and leave that
one-time opening available for a later normal command. Use `mh open` to present
a new project's first runnable version, initially paused. Keep the
user's page and project running after creation; edits and exports do not close it
or reopen a closed tab. `MH_NO_BROWSER=1` disables automatic opening for batch/server
use. `mh open [directory] --browser` explicitly opens/reuses Studio and waits for
connection, including when automatic opening is disabled.
Preview and render run directly. Studio connections and running work keep sessions
alive. Disconnected sessions close after 30 idle minutes; an empty daemon exits
after 10 minutes. `mh status` does not start a session. `mh close` refuses busy or
unsaved work; `mh daemon status` lists sessions and `mh daemon stop` stops them all.
Use close/stop only for explicit closure or troubleshooting, not routine creation cleanup.

## Interactive playback

These commands control the user's real page. Use them only for requested viewing
or diagnosing Studio playback/interaction. Routine checks use [Background checks](#background-checks).
For an authorized interactive check, run `mh open --browser`, then:

```sh
mh studio seek 2.8 && mh studio play
```

After a diagnostic, use `mh studio pause` on the same addressed page to stop
playback you started, including on failure. Respect later user actions; do not
pause playback the user already started or stop requested viewing at handoff.
Open waits for a connection; with one interactive page it returns `browser.clientId`.
Seeking pauses playback and waits for the requested frame. With multiple pages,
use `mh studio sessions` to choose one and add `--client <clientId>` to the control.
`studio sessions` includes inactive last-known pages. Select a page with
`connected: true`; `heartbeatAgeMs` and `visibility` explain its freshness and
whether it is hidden. Inactive pages remain identifiable but cannot receive
controls. A reused `open --browser` receipt does not confirm focus;
`visibility: "hidden"` reports a hidden tab, which may still process controls.
If it becomes unresponsive, activate that same page only when authorized to diagnose it. Recovery on a different `clientId` does not prove
the original page recovered.
For other controls, use `mh studio control --json` with the request schema from
`mh describe "studio control"`.
Project preview images do not move the working Studio.

For a Studio-specific sound diagnostic, if CLI playback reports that sound is
blocked or the device is unavailable, a trusted Play click in that same page may
be needed. Confirm actual recovery before resuming CLI control.
If it still fails, check the output device and reported error before retrying.
Repeated CLI play calls do not supply a browser interaction. Keep the failed
command's exit status/result: a later successful `sessions` query only lists pages.
Sound in an exported file does not prove Studio playback has recovered.

## Execution waits

Wait on the same task, respect host limits and keep cancellation available.
Continue immediately after checking the terminal exit status and result;
progress reaching 100% alone is not completion. Chain known dependent work with `&&`.

Relative file/output paths use the terminal working directory, even with
`--project`. Use absolute paths when operating from another directory:

```sh
mh render /absolute/work/.tmp/output-v1.mp4 --project /absolute/work/film &&
mh preview --file /absolute/work/.tmp/output-v1.mp4
```

## Background checks

`mh preview` captures independent complete frames; `mh render` captures an
independent version snapshot and mixes project audio. Both run without opening,
focusing, seeking or starting playback in the user's Studio, even when they start
the project session. Hidden/minimized user tabs need not be activated for these checks.
Opening or editing a project normally still opens Studio once; use `mh open` to
show a new project's first runnable version, initially paused. Keep existing user
pages and their playback/view state under the user's control.

Finish input writes before capture; keep them stable during previews. Independent
work and edits after a render starts can continue.

For motion or sound diagnostics, render the smallest interval covering the action
and its joins, using a range inside the project's duration:

```sh
mh render .tmp/motion-check-v1.mp4 --json '{"start":0,"duration":1}' &&
mh preview --file .tmp/motion-check-v1.mp4 --times '[0,0.5]' --contact-sheet
```

The contact sheet checks selected frames. Review the same clip at normal speed
with a video-capable tool for motion judgments.

For mix-only checks, render a `.wav` with the same `start`/`duration`, then use
`mh preview --file <mix.wav>` for duration, format and mean/peak levels. Read the
actual audio with an audio-capable tool for listening judgments; levels alone do
not establish listening quality. Report unavailable motion/audio review as unverified.
Do not use the user's speakers or loop `mh studio play` as a fallback.

Use fresh `.tmp/` output paths and reuse checks for unchanged inputs. Full-film
export belongs to requested video delivery or a check that actually needs it.
Wait for completion and preserve errors/partial manifests; files alone are not a
successful result. The host retires export workers and failed capture pages;
successful capture pages can be reused for up to 60 idle seconds. When cancelling
an owned render, interrupt its original waiting CLI invocation and await its
terminal result; that invocation cancels its own task ID and waits for cleanup.
`mh render cancel` addresses the project's current export: use it only for
explicitly targeted cancellation after checking ownership, not as generic cleanup.
Do not cancel another caller's export or close the user's project/daemon.

## Checkpoints

`mh checkpoint create <label>` prepares current source and saves a runnable milestone.
`mh checkpoint list` reads saved history;
`mh checkpoint restore <id>` restores source and work data. Respect the user's
preference for when to keep versions. A checkpoint is not required for packaging.

## Project packages

Finish project files and handoff notes, then use `mh pack <output.vmg>` to save
current source, editable data and original assets without history or build caches.
`mh unpack <input.vmg> <new-directory>` verifies integrity and prepares dependencies.
Continue editing with `mh open <new-directory> --browser`, or re-export directly
with `mh render <output.mp4> --project <new-directory>`.
Retain package.json and its lockfile. Keep local `file:` dependencies inside the
project when they need to travel with the archive, or use installable published
versions. State external requirements such as system fonts.
Reuse the pack/unpack integrity receipt. `unverified` means the archive itself
has no compile/render check; verify the unpacked project separately.

## User markers

Reuse a complete marker snapshot for the current project/version; otherwise read
`mh marker list`. Complete the read request version with `mh marker complete`
after implementing and checking it. Pro editing requests also require the normal
handoff described in [conversion](../conversion.md#requests-from-studio-and-returning-the-result).
