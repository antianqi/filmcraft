---
name: mh-author
description: Create and edit MotionHarness animations with ordinary browser scenes, shared project time, Studio and video export. Follow the project's declared Standard or Pro type.
metadata:
  version: "3.1.0"
---

# MotionHarness authoring

New projects default to **Standard**; existing projects keep the type in `mh.json`.
For Pro (including legacy version 2), read
`mh skill --reference pro --section "Common edits"` for saved-work
changes, or `--section "Authoring rules"` for source contracts. For an explicit
Standard-to-Pro request, read `mh skill --reference conversion`.

## Scene

Create a Standard scene with `mh new <directory>`, then edit `mh.json` and `src/scene.js`
using HTML/CSS/JS, Canvas, SVG, Three.js or a framework. `width`/`height` are logical
canvas pixels, `fps` is frames per second and `duration` is seconds. Add packages
with `pnpm add <package> --ignore-workspace` and retain the lockfile.
MotionHarness handles building, serving, media preparation and export.

```js
export default function ({ root, width, height, pixelRatio }) {
  const title = document.createElement('h1');
  title.textContent = 'Hello';
  root.append(title);
  return {
    prepareFrame(time) { title.style.opacity = String(Math.min(1, time)); },
    dispose() { title.remove(); },
  };
}
```

`time` is absolute project seconds: repeated, backward and skipped times must give
the same frame. Use functions of time or seekable animation libraries. Return a
Promise for unfinished drawing; MotionHarness waits. Use `pixelRatio` for Canvas/WebGL buffers
and logical `width`/`height` for layout. Keep the scene mounted and release resources
in `dispose`. Standard needs no MotionHarness layers or parameters.

Use project-local asset URLs, such as `new URL('../assets/logo.svg', import.meta.url).href`.
MotionHarness waits for DOM images and fonts; await custom texture uploads. System fonts work
directly.

Update settings and optional music in the existing `mh.json`, preserving other fields:

```json
{
  "width": 1920, "height": 1080, "fps": 30, "duration": 12,
  "audio": [
    { "src": "assets/music.wav", "start": 0, "duration": 12, "volume": -8,
      "fadeIn": 0.2, "fadeOut": 0.5 }
  ]
}
```

`src` is project-relative; `volume` is dB (0 keeps source volume); timing is seconds.
Tracks share project time in playback and export.

## Checks

After this revision's writes finish, inspect the affected frames:

```sh
mh preview --times '[0,1]' --contact-sheet --output-dir .tmp/previews/p1
```

Use a fresh output directory each time and read the returned images together;
`--time 1 --output .tmp/frames/f1.png` captures one full-size frame. For motion or
sound, render only the interval in question and inspect that file:

```sh
mh render .tmp/motion-v1.mp4 --json '{"start":2,"duration":1}' &&
mh preview --file .tmp/motion-v1.mp4 --times '[0,0.5]' --contact-sheet
```

A `.wav` output with the same range gives the mix; `mh preview --file <file>` reports
duration, format and audio levels without opening the project. Frames and levels do
not prove motion or listening quality: review clips and audio with capable tools when
available, otherwise report them as unverified. Fix observed defects and recheck what
changed; reuse checks for unchanged inputs. Add diagnostics or dependencies only for
a concrete problem the available tools cannot check. Checks run in the background:
do not open, focus, seek or play the user's Studio page or speakers unless asked.

## Delivery

During revisions, share the saved project and Studio preview for review. For a
finished video, export the checked version to a new path and inspect the saved file:

```sh
mh render .tmp/output-v1.mp4 &&
mh preview --file .tmp/output-v1.mp4 --times '[0,6]' --contact-sheet
```

The extension selects the format: `.mp4`, `.mov`, `.gif`, `.webp`, `.apng`, `.png`,
`.zip` (PNG sequence) or `.wav`. `--json` accepts `start`, `duration`, `width`,
`height` and `codec`; `mh describe render` lists all options. Exports never overwrite
files and use the source, data and assets from when they start. `--file` times are
seconds within the saved clip. Relative paths use the terminal's directory, even with
`--project`. If delivery intent is unclear, ask once at handoff and reuse that choice.

Previews take seconds; renders take up to a few minutes. Wait for each command to
exit with the longest wait your tool allows; if it returns while the command is still
running, wait again the same way instead of checking at short intervals. For example,
in Codex use `exec_command` `yield_time_ms` 30000 with no shorter `// @exec` yield,
then an empty `write_stdin` with `yield_time_ms` 300000. Check the exit status and
result before using a file, and chain dependent commands with `&&`.

## Studio and files

Once a new project is runnable, run `mh open` to show its paused Studio to the user.
Editing commands reuse that page; `preview` and `render` never open pages. Keep the
user's Studio and the project running; do not close them or stop the daemon as
cleanup. Use `mh open --browser` only to reopen Studio on request.

Use `.tmp/` for previews, exports, logs and one-off scripts; it is excluded from
Checkpoints and packages. Keep editable source, models, materials and reusable tools
in ordinary project directories.

Read a reference section only when the task needs it:
- Images and custom fonts: `mh skill --reference materials --section "Images and fonts"`
- Video timing/textures: `mh skill --reference materials --section "Video timing"`
- Audio looping, offsets, pan or stream selection: `mh skill --reference audio`
- Output formats, transparency, motion blur, playback diagnostics, cancelling a render: `mh skill --reference rendering --section Rendering`
- Requested Studio playback and diagnostics: `mh skill --reference rendering --section "Interactive playback"`
- Saved versions and recovery: `mh skill --reference rendering --section Checkpoints`
- `.vmg` archives: `mh skill --reference rendering --section "Project packages"`
- Studio marker requests: `mh skill --reference rendering --section "User markers"`
