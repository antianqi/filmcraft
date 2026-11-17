# 依赖与引擎

## 定位顺序

1. 优先使用当前宿主技能目录提供的准确路径；显式用户路径优先于默认候选。
2. 读取 `motionharness/SKILL.md` 和 `video-shotcraft/SKILL.md`。两者是外部依赖，本插件不嵌入副本。
3. 无目录线索时可运行 `python3 <本技能目录>/scripts/discover_dependencies.py`。候选根目录依次为显式 `--skill-root`、`FILMCRAFT_SKILL_ROOTS`、用户的 `.agents/skills`、`.codex/skills`；输出保留全部候选，所选项遵循此顺序。多版本时核对实际路径与版本，不把默认根等同最新版。
4. 需要制作时加 `--require-render --require-shotcraft`；缺少组件返回非零，脚本不自动安装。设计或只读审查只要求本次分支实际需要的依赖。

## 职责

| 组件 | 职责 | 不应宣称 |
| --- | --- | --- |
| Video Shotcraft | 分镜配方、准确 demo、节奏/音效方法、审查规则、可选模板 | 仅看卡名就等于采用了完整配方；移植等于直接运行了 Remotion 模板 |
| MotionHarness | 本地场景、Studio、预览、逐帧渲染、音轨和 checkpoint | 安装了技能就拥有可执行工具；Standard 自动拥有 Pro 图层编辑 |
| Filmcraft | 范围、任务故事、视觉选择、素材与原创动画的组织、证据和交付 | 工作流本身会自动作曲或生成真实产品执行结果 |
| FFmpeg/ffprobe | 媒体探查、解码、音频处理、精确拼接与封装 | 解码正常等于真人看过/听过；修音频需要重画全部画面 |

MotionHarness 的权威说明用 `mh skill`、`mh skill --list` 和相应 reference 读取，避免写死运行时哈希路径。需要 SDK/Three.js/Remotion API 时继续读取当前安装版本的官方文档。

## 按需读取 Video Shotcraft

- 全片制作：`references/pipeline.md`；共同创作再读 `references/guided-free-creation.md`。
- 镜头选择：`gallery/api/library.json` → 选中卡片 → 卡片指定的准确 demo；记录卡名、变体、源路径与保留/改变的动作参数。
- 视觉与终检：`references/aesthetic-rules.md`、`references/final-review.md`。
- 配乐/音效：`references/sound-design.md`、`references/sfx-sourcing.md`；强节奏音乐再读 `references/music-beat-sync.md`。

参考视频不能播放时，尝试可用替代来源；仍缺失则按本地文档/源码做适配，并把动态参考一致性列为未验证。严禁凭静态海报声称看过样片。
