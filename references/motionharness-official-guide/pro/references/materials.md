# Material originals

Import local images, fonts, video and audio from source. Builder produces asset references;
use SDK Image/Video and useFont so Scene preparation can await the actual resources.
Declare editable selection using `field.asset`; inspect installed types for accepted
kinds. Instance replacement changes that instance, not other users of the asset.

`mh asset list` lists available originals. Replace a selection with
`mh asset bind <instance> <parameter> <original-file>`. Keep originals, not transient blob URLs,
GPU textures or thumbnails. Saved references identify content by hash.

Put local source media and candidate dependency tarballs inside the project.
Avoid machine-specific absolute paths or dependencies stored outside the project.
A portable candidate SDK can be kept in vendor/ and referenced by a relative file:
dependency, with the lockfile saved alongside package.json.

An editable package carries current source/data and needed originals. It carries
no Checkpoint history, compiled output or historical-only originals. Broken source
can still be packaged. Missing referenced originals are an error to resolve, not a
reason to produce a silently incomplete package.

`Video` exposes deterministic source-time controls directly:

```tsx
<Video asset={clip} startFrom={offset} playbackRate={rate}
  holdAt={hold ? holdTime : undefined} loop={loop} />
```

Without hold, source time is `max(0, startFrom + localMhTime * playbackRate)`.
A zero rate freezes at startFrom; a negative rate seeks backwards. `holdAt` is an
absolute nonnegative source-media second and overrides time/rate/offset. Existing
media preparation then clamps to duration or wraps when loop is true. `Video`
remains paused and muted, and waits for the selected frame to decode before export. Explicit video audio uses the declared video binding and the shared audio mixer; do not unmute the DOM element. Instance remapping runs before these media parameters; see [Time remapping](time-remapping.md) when intentionally changing that content clock.

Expose rate/offset/holdTime as numeric fields and hold/loop as booleans as needed.
Changing or animating rate evaluates the complete formula from local time; it does
not integrate a speed history or start autonomous playback. Use offset to anchor
an intentional speed change. `resolveVideoTime` exports the same pure mapping for
custom code. Changing output FPS only changes sampling, not this mapping.

Declare related font originals as one family with `defineFont`, then list the
returned definition in `defineComposition({ fonts: [brand], ... })`:

```tsx
const brand = defineFont({
  family: 'Brand', cssVariable: '--mh-font-brand',
  faces: [
    { asset: regularFont, weight: 400, style: 'normal' },
    { asset: boldFont, weight: 700, style: 'normal' },
    { asset: italicFont, weight: 400, style: 'italic' },
  ],
});
```

Use `useFont(brand)` as the React fontFamily, or use
`font-family: var(--mh-font-brand)` in authored CSS. Apply fontWeight/fontStyle
normally; the browser matches the declared faces. Weight is an integer from 1 to
1000; style is normal/italic/oblique. Descriptors must describe the supplied font
file accurately. A family cannot declare two faces at the same weight/style.
Logical family names and CSS variable names must be unique in the composition.

Runtime loads all declared faces before frame preparation and supplies a distinct
family alias for each Scene. CSS variables are scoped to the composition, never
written globally to the document root. Do not hardcode the generated alias or
assume a bare logical `font-family: Brand` resolves outside this binding. Raw
`useFont(fontAsset)` remains available for a single-file family. Originals and
declarations travel with the project; reopening and export use the same matching
rules, while each Scene releases its own registrations on cleanup.

## Project asset library

`mh asset list [--json <filters>]` lists pinned originals and current
references, with display names, tags and explicit ownership. Filters are search,
kind (image/font/video/audio), tag and includeUnused. IncludeUnused additionally shows
retained noncurrent originals; those may still belong to history or live previews.

- `import <file> [label]` validates/deduplicates an original and pins it in the
  project's assetLibrary. The receipt returns an AssetReference.
- `rename <hash> <label>` and `tags <hash> <JSON array>` organize the library.
  Display names are separate from source filenames and immutable original hashes.
- `usage <hash>` identifies editable field/effect references, sound clips, source
  markers and source/default declarations. `replace <old-hash> <new-hash>` updates
  editable media references in one revision, with asset-kind/document validation. Source
  markers retain their original version and become stale; source/default
  declarations remain unchanged. Edit source explicitly when changing fixed uses.
- `remove <hash>` unpins an unused library entry. Referenced entries cannot be
  removed. Physical collection remains `checkpoint gc`, which honors Checkpoints,
  recovery, undo and viewer retention; remove never directly deletes those bytes.
- `info <hash>` decodes dimensions/duration and audio stream metadata on demand.
  `thumbnail <hash> <output.png>` writes a derived PNG: audio waveforms are 256×96;
  image, video and font previews use a 256×192 box (source-fit may be smaller). GIF
  thumbnails use a static first frame. Derived previews never replace originals.

Names, tags and pins live in project data and survive Checkpoint restore and
project packaging. Library retention is separate from scene preparation: unused
pinned originals are not all decoded into the active scene. Declared defaults are
retained even after current field values change, so reset/new instances remain
valid. Use an asset parameter or source import when consuming an original in code;
a library pin alone is not a render binding. Studio's asset center exposes these
originals and their usage; audio originals can be auditioned and added as sounds.
