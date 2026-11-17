# DaVinci Resolve mixed editing

Read this only when combining Resolve MCP with MotionHarness or delivering MotionHarness motion
graphics to a Resolve timeline. Use Resolve's official MCP for footage, audio
and native editing; use MotionHarness CLI for editable motion sources and
`mh bridge davinci` for linked delivery. No additional MCP server is needed.

The bridge does not enforce a minimum Resolve version or a version/build/CPU
allowlist. Older hosts can use any operation their scripting APIs can complete;
missing APIs and failed calls report their actual errors. Version information in
`mh bridge davinci doctor` is diagnostic only. The complete native bridge package
currently ships for macOS.

## Default delivery

Use bridge `send` to render, import, insert and associate a MotionHarness source with a
Resolve media-pool item. Do not replace this with `mh render` followed by ordinary
MCP import: that does not establish the association. Use background project previews
and necessary short clip/audio checks during revisions; see
[Background checks](rendering.md#background-checks). Standalone delivery and checks that need an encoded file
can use `mh render`; use bridge `send` for the linked deliverable.

1. Check `mh bridge davinci status`. If the optional component is missing or
   unavailable, report the blocker and install/repair only within the user's
   authorized scope. Do not silently fall back to unlinked media.
2. Read the intended project and timeline through Resolve MCP, then use
   `mh bridge davinci timeline` to obtain the bridge's scope and frame coordinates.
   Verify they identify the same destination.
3. Create or edit the MotionHarness source with public SDK/CLI operations. Match the intended
   duration, dimensions and frame rate; use supported transparent ProRes export
   options for overlays. Follow the task's rendering authorization.
4. Read `mh bridge davinci describe --json '{"operation":"send"}'`, then submit
   `mh bridge davinci send --project <source> --json '<request>'`.
   Include a fresh `idempotencyKey`, verified `scope`, `timelineId`, `track`,
   `recordFrame` and desired `export` options. Do not guess IDs or rely on a
   playhead that may have moved.
5. Query `mh bridge davinci task --json '{"taskId":"..."}'` until terminal.
   Require a successful applied result, retain its `bindingId`, and verify source
   and media identity with bridge `inspect`. A queued receipt or visible clip
   alone does not prove linked delivery. If a response is lost, query with the
   original `idempotencyKey`; inspect/recover unknown outcomes before another
   send to avoid duplicate insertion.
   When a completed send returns `sidebarHint`, mention that adding the sidebar
   entry is optional and give the Effects Library search/drag steps to the user.
   `mh bridge davinci sidebar-guide` returns the local illustrated guide path.
   Do not imply the effect was attached automatically or repeat this hint on
   routine updates.

## Editing and updates

Continue native timeline edits through Resolve MCP. After changing the MotionHarness source,
use bridge `update` with its `bindingId` and a new idempotency key; read the
installed operation schema first. Do not overwrite the video or import a new
render through MCP as an update. Recover missing binding IDs by inspecting the
target association, not by guessing from filenames.

An update relinks the existing media-pool object and affects its references in
the current Resolve project. For an independently editable occurrence, use the
bridge's explicit independent-copy operation. If output specifications conflict,
retain the old video and send a new asset only when that change is intended.

People can open the same source in Studio and send/update from its export area.
Removing an entry control does not erase the association. Check the core result:
correct source, intended timeline placement and the applied updated video.
Do not expand this into testing Resolve's native editing features. Exporting the
finished Resolve film is a separate task.
