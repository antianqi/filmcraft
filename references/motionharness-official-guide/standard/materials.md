# Standard images, fonts and video

Procedural Three.js geometry, lighting and surface materials use ordinary Three.js APIs.

Keep originals inside the project. Use ordinary module URL imports, CSS URLs,
or `new URL('./image.png', import.meta.url).href`; the build and project package
carry these files. Avoid absolute filesystem paths and remote mutable media.
No asset registry or MotionHarness layer owner is required.

## Images and fonts

Images use ordinary DOM or Canvas. MotionHarness waits for DOM images and fonts after
`prepareFrame`. Await custom image/texture uploads in your own frame callback.
Load font files you provide with CSS `@font-face` or the browser `FontFace` API.
System fonts work in preview and export; for a handoff, name them as external
requirements instead of copying system font files, which are usually not licensed
for redistribution.

## Video timing

For video, use the host's existing decoder/readiness helper:

```js
import clipUrl from '../assets/clip.mp4?url';
export default async function ({ root, media }) {
  const video = await media.video(clipUrl);
  root.append(video.element);
  return {
    async prepareFrame(time) { await video.prepareFrame(time); },
    dispose() { video.element.remove(); },
  };
}
```

The video stays paused and seeks to source seconds, including backward/repeated
seeks. The helper owns decoder cancellation and disposal. For a Three.js texture,
prepare the video before rendering and mark the texture for update.

### Video audio

Video elements are muted. For video with sound, add its track to `mh.json`
(`mh skill --reference audio`). The scene can import that
same entry so timing is maintained once. For the audio guide's clip with duration 3:

```js
import config from '../mh.json';
const clip = config.audio.find(track => track.src === 'assets/clip.mp4');
// Inside prepareFrame(time), using the video created above:
const elapsed = time - (clip.start ?? 0);
video.element.hidden = elapsed < 0 || elapsed >= clip.duration;
if (!video.element.hidden) await video.prepareFrame(elapsed + (clip.offset ?? 0));
```

Keep the static asset import above for the video URL. DOM autoplay is not an
export audio connection; GIFs and third-party players also need project time.
