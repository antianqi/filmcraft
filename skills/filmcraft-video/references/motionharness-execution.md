# MotionHarness 执行

先读取本机 `motionharness` 技能和 `mh skill`，当前 CLI 指南优先于本文示例。通过 `mh describe` 或 `--help` 确认参数，尤其在升级后。

## 工程与资产

- 本地成片优先 Standard；用户要求拖拽图层、关键帧或参数时选 Pro。交付时如实描述编辑能力。
- 把项目和中间文件放在任务目录，使用 `.tmp/` 保存试片、原生中间导出和旧版，正式文件放 `out/`。不要把素材、私有会话和审查草稿塞进产品源码仓库。
- 用普通静态导入，例如 `import imageUrl from '../assets/image.png?url'`；动态拼接 `new URL(variable, import.meta.url)` 可能不能让构建器发现资产。实际测试图片、字体与纹理加载。
- 场景只依赖绝对时间和固定种子。等待图片解码与字体就绪；相同时间的重复跳转和逐帧导出应一致。跨镜元素要显式隐藏/退出，避免后续镜头挂着旧对象。

## 预览与渲染

```bash
mh preview --time 3 --output .tmp/frame.png
mh preview --times '[0,1,3]' --contact-sheet --output-dir .tmp/frames
mh render .tmp/short-check.mp4 --json '{"start":0,"duration":2}'
mh render out/native-v1.mp4
mh preview --file out/native-v1.mp4 --times '[0,3]' --contact-sheet --output-dir .tmp/encoded
```

一帧用 `--time` 与 `--output`，多帧用 `--times` 与 `--output-dir`，不要混用。本次核验过的 CLI 每批最多 32 个时间点；以当前版本的错误/帮助信息为准，超量拆批，不降低检查覆盖。

接触表用于总览，文字锐度、边框遮挡和小控件看全尺寸帧。运动、卡顿和声音同步需要编码片段或播放检查。先渲染短段测量开销，尤其是 motion blur；成片参数与实际耗时写入记录。

## 局部修正和母版

字幕底、单镜遮挡等局部修正可只渲染受影响范围。替换时记录真实起止帧，探查片段帧数，以完整帧边界拼接并验证全片总帧数、音轨、替换入口/出口和编码质量。需要任意帧精确切割时，不把非关键帧 stream-copy 当成已验证的精确编辑。

已有画面不变、只换声音时可复制编码视频流并重新封装音轨。两版视频流相同是强一致性证据；若不同但本来就重新渲染，需用帧比较等适当方式验证，不能仅凭相同时长声称相同。

```bash
python3 <本技能目录>/scripts/inspect_delivery.py \
  --video out/final.mp4 --compare-video out/sfx-only.mp4 \
  --duration 60 --fps 30 --width 1920 --height 1080 \
  --decode --audio-levels --report out/qa/technical.json
```

## Studio 与交付

用 `mh checkpoint create` 存有效里程碑，`mh status` 读取实际 Studio URL。需要呈现工程时用 `mh open`；默认浏览器打开失败，可按宿主提供的浏览器能力打开已返回地址。预览和导出保持后台，不替用户切换或关闭正在使用的 Studio。

`mh preview --file <成片> --check-playback` 可验证隔离浏览器的完整播放与掉帧数；静音播放不构成听音检查。最终交付文件经过 FFmpeg 修订时，还要检查最终文件，不能只检查原生中间片。
