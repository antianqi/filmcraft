# MotionHarness Pro authoring

Use this skill to create or edit animations; MotionHarness implementation follows repository
instructions. The user directs and evaluates the result; the Agent writes React
and edits saved work through the CLI.

## Common edits

For text, color, transform, keyframe or timing changes, use existing instances and
saved values. Keep unrelated edits, source defaults and `defaultAnimation` intact.
Use the CLI for saved work; do not hand-edit document.json.
New editable fields require source work; read `--section "Authoring rules"` then.

1. Use the current complete user-marker snapshot; read `mh marker list` only if
   absent, incomplete or a newer version is reported. Pending user requests are
   actionable; completed marks and Agent cues are not. Read missing attachments
   before interpreting their comments. For anchored targets, deletion intents or
   completion, read `mh skill --reference audio --section "Reading and editing markers"`.
2. Reuse known target IDs. Otherwise locate only the needed instance and parameter:
   `mh inspect --view instances --query <name>`, then
   `mh inspect --view parameters --instance <id> --parameter <name>`. Check `nextOffset`.
   Read `mh keyframe list --instance <id> --parameter <name>` when editing existing keys.
3. Use `mh param set <instance> <parameter> --value '<JSON>'` for saved values;
   animated edits need the intended project `--time`. Use `mh keyframe set` for keys
   and `mh instance timing` for its window. Query `mh describe "param set"`,
   `mh describe "keyframe set"` or `mh describe "instance timing"` only as needed.
   For several related changes, use `mh batch --file <operations.json>`; read the
   [editing reference](references/editing.md) for batch, conflict or migration details.
4. Verify affected current frames with `mh preview --time <seconds> --output <path>`
   or `mh preview --times '[0.4,1,2]' --contact-sheet`, then read the images.
   Reuse relevant current previews and inspect motion/audio in the background;
   see `--section "Preview and export"`. Complete verified marker work with its actual
   ID and read `requestVersion`; partial or failed work stays pending.

During revisions, share the saved project and Studio preview for review.
When the task calls for a finished video and the current version meets the request
and passes the relevant preview checks, export directly with the agreed settings
or project defaults. If delivery intent is unclear, ask once whether to export when
a complete version is ready for handoff, and reuse that choice in later revisions.

## Authoring rules

- Import public APIs from `@motionharness/sdk`; the CLI owns private runtime
  packages. Do not add them or a Vite setup. Drive animation from MotionHarness time in
  seconds, independently of playback order; FPS only changes sampling.
- Choose editable objects and parameters from the user's intended changes;
  keep other visuals in ordinary source code. For Pro splits, follow the
  [conversion guide](conversion.md#animation-keyframes) for which motion to transfer.
- When exposing 2D transforms, expose position, scale, rotation, anchor and opacity
  independently using `basicTransformParameters` and `Layer`; add
  `basicSizeParameters` for dimensions.
  Anchors are local pixels, default `(0, 0)`, including geometry in percent
  units. A known-size box's center is `(width / 2, height / 2)`, not `(0.5, 0.5)`.
  Preserve React flex/grid layout. Compound progress is for internal effects,
  not a substitute for independent basic controls.
- Create instances for content the user selects, animates or retimes independently.
  Ordinary React/CSS handles reuse and layout; avoid redundant one-child groups.
  Keep groups with shared timing, transforms, clipping or effects.
- Routine revisions edit saved values, existing keys and instance timing. Preserve
  user edits and live dependencies. Source defaults and `defaultAnimation` only
  initialize/reset work; change them when that behavior is requested. New editable
  features require source contracts; incompatible changes require explicit migration.
- Use SDK motion functions for their existing models. Keep movement-driven response
  live; bind editable base transforms normally and apply accompanying motion through
  `Layer offset`. Bake only for an explicit conversion to independent keys.
  See [Standard motion functions](references/authoring.md#standard-motion-functions).
- Parameter bounds must match valid rendering. Check cross-field relationships and
  timing through preview; read saved duration from `useCompositionSettings().duration`.
  Extending the composition requires an explicit project settings edit.
- Quick parameter panels live inside Pro; preserve the agreed editing scope. Use
  `ControlPanel`, `ControlGroup` and `renderField` with navigation to relevant PRO
  controls. See [custom-control contracts](references/authoring.md#component-actions-and-custom-control-contracts).
- For supplied audio, declare visual instances within the requested editing scope
  and arrange visuals around cues, preserving original sound timing unless requested.
  Mark meaningful visual/musical changes, not every beat; full grids require a request.
  See [Audio-driven creation](references/audio.md#audio-driven-creation).
- Keep source facts, estimated dimensions and artistic adjustments identifiable.
  Verify sources; scale drawings must agree with displayed dimensions and ratios.

## New projects and source changes

Create with `mh new <directory> --type pro` (installs dependencies). An existing
asset directory is fine; conflicting scaffold files are preserved. Use
`--no-install` only when preparing dependencies separately. Run commands there
or pass `--project <directory>`. Once a new project is runnable, use `mh open` to
present its paused Studio. Normal opening/editing commands open/reuse Studio once;
`preview`, `render` and `render plan` stay headless even on first preparation.
Keep the user's page and project
running after creation; MotionHarness cleans up temporary rendering resources.
`mh status` inspects the session. `mh close` is for explicitly requested closure
or troubleshooting.
Read the Authoring rules and only the needed reference sections. Use the Common
edits flow for current user requests and verification. Preserve saved work;
keep JSX in source rather than configuration.

## Preview and export

Preview waits for current source and complete frames; check success and read its
images. Match background checks to the change: frames for layout/poses and relevant
clips or audio with capable tools for motion/sound. Reuse checks for unchanged
inputs, fix observed defects and recheck affected behavior. Hand over when the
requested version meets the brief and relevant checks pass; state the inspected
version/range and unavailable checks. See [Background checks](references/rendering.md#background-checks).
Routine verification must not open/focus the user's page, seek it or play through
the user's speakers. Control Studio only for requested viewing or a Studio-specific
diagnostic; see [Interactive playback](references/rendering.md#interactive-playback)
and [Studio controls](references/authoring.md#control-the-users-current-studio).

For video delivery, `mh render .tmp/animation.mp4 --json '{"quality":"high"}'` exports
without an interactive page. Use `cliRequestSchema` and `cliExamples` from
`mh describe render` for CLI options (not HTTP `requestSchema`). Check exit status
and `saved: true`. `mh preview --file .tmp/animation.mp4` inspects saved media and
audio levels. Static frames and levels do not establish motion or listening quality.
Add diagnostics only for a concrete requirement or observed problem that available
tools cannot verify. See [rendering](references/rendering.md), or the
[bridge workflow](references/davinci.md) for Resolve.

## Saving and delivery

Commands emit JSON; `--output-format text` selects readable output. Requests accept
`--json`, `--file` or `--stdin` with the same schema. Keep stdout/stderr separate and
preserve exit status through pipes (`set -o pipefail`) and dependent commands (`&&`).
Allow preview/render calls time to finish; wait on the same running task with a
substantial wait window. A background completion notification is not proof of success;
inspect its actual result before using paths.

Use `.tmp/` for temporary previews, rendered videos, caches, logs and one-off
scripts. Keep generated models, materials and reusable tools needed for continued
editing or delivery in ordinary project directories, such as `models/`, `assets/`
or `tools/`; these names are examples, not required paths. `.tmp/` is excluded
from Checkpoints and editable packages.

Create `mh checkpoint create <label>` at a verified milestone, before a substantial
experiment, or on request, respecting the user's preference for when to keep versions.
It prepares current source, requires runnable work and returns the new saved node; `mh checkpoint list`
reads the complete history. Manual save and restore remain available.
`mh checkpoint restore <id>` restores source/data; a new saved checkpoint replaces
that restored point's old tail. MotionHarness history is separate from Git.

The project directory already preserves editable work; keeping it does not
require an early archive. Pack when the handoff needs an archive, after completing
the project files and any handoff notes that belong inside it.
`mh pack <output.vmg>` carries current work, even unfinished source, without history.
Pack and unpack verify the file inventory, sizes and SHA256 hashes. Reuse that
integrity result and delivery.config/entry (paths relative to the project directory)
in delivery notes. Add external requirements such as system fonts; dependency versions
come from package.json and its lockfile. A second file-hash inventory is unnecessary
unless requested; comparisons against original supplied materials remain separate.
Invalid dependency fields report `delivery.dependencies.required: null` with a
`diagnostic`. The unverified package preserves those files; repair package.json
before opening or rendering instead of treating it as dependency-free work.
`unverified` means no build/render check.
`mh unpack <input.vmg> <new-directory>` restores materials and prepares locked dependencies.
To re-export, directly run `mh render <output.mp4> --project <new-directory>`; no
interactive page is required. To edit interactively, use `mh open <new-directory> --browser`.
If preparation fails, retain reported material paths; never substitute an older version.

## Focused references

Read only the needed topic, for example
`mh skill --reference authoring --section "React and component contracts"`.
For saved values and keys, use `mh describe "param set"`, `mh describe "keyframe set"`,
`mh describe "instance timing"` or `mh describe batch`. These are the same CLI,
with Pro editing operations available only in Pro projects.
`mh skill --symbol TrimPath` queries the
project's installed SDK declarations, constraints and examples; `--symbol '*'` lists
symbols. Prepare project dependencies first (`mh new` for a new project); pass
`--project` for another directory. `mh doctor` resolves actual SDK/type paths.

- [Authoring](references/authoring.md), `mh skill --reference authoring`: React contracts, basic properties, layer hierarchy, motion, effects and controls.
- [Editing](references/editing.md), `mh skill --reference editing`: saved values, keyframes, timing, batches and migration.
- [Materials](references/materials.md), `mh skill --reference materials`: image/font/video/audio originals and portability.
- [Audio and markers](references/audio.md), `mh skill --reference audio`: audio-driven creation, annotation semantics and optional Agent installation.
- [Rendering](references/rendering.md), `mh skill --reference rendering`: frame preparation, preview and output.
- [Resolve](references/davinci.md), `mh skill --reference davinci`: Resolve MCP and editable handoff.
- [Time remapping](references/time-remapping.md), `mh skill --reference time-remapping`: advanced use when ordinary timing edits are insufficient.

When installing MotionHarness with Agent integration, explain automatic marker delivery and its
off switch, then follow [Agent setup](references/audio.md#agent-setup-during-installation).
Do not reinstall or repeat setup every turn; preserve opt-outs and platform trust.

For an explicit Standard-to-Pro request, read [conversion](conversion.md).
