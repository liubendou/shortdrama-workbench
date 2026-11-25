# 上游源码记录（T1）

获取方式：git 直连 github.com 超时，改用 codeload.github.com 的分支 zip 包下载并解压（见 tools/fetch_upstream.ps1）。

| 上游 | 来源 | 分支 | zip 大小 | zip SHA256 | 文件数 / 体积 | 许可证 |
|---|---|---|---|---|---|---|
| NarratoAI | github.com/linyqh/NarratoAI | main | 2,665,591 B | CB11541BC1D759AFF011A2EF9757A0F6A172CC12A2D8297466876B98CA977577 | 187 / 4.5 MB | MIT（Copyright 2024 linyq） |
| JJYB_AI_VideoAutoCut | github.com/jianjieyiban/JJYB_AI_VideoAutoCut | videoautocut | 3,404,120 B | E970B61776707693DDB3A76625BF7A50DB16D46EC005A73674D051B5C4D8CB5C | 159 / 8.6 MB | JJYB Personal Use License v1.0 |
| DramaClip | github.com/efarsoft/DramaClip | — | 未获取 | — | — | 无 LICENSE，不获取源码 |

## 目录位置
- `upstream/narratoai/`：NarratoAI 源码（只读参考，MIT，可在保留版权声明的前提下复用，复用处需注明来源）
- `upstream/jjyb/`：JJYB 源码（个人使用许可，见下）

## JJYB 许可要点（已逐条阅读 LICENSE 全文）
- 仅允许个人学习、技术研究、个人功能体验与评估；不产生直接或间接商业收益的个人创作。
- 在保留许可证、版权和作者信息的前提下，允许个人修改。
- 禁止：收费分发、商业用途、SaaS/企业项目集成、以收费为目的的再分发；未经书面授权不得分发源码、修改版或安装包。
- 第三方组件（FFmpeg、Flask、OpenCV、PyTorch 等）及模型、字体、音视频资源另有各自许可，需自行确认。
- 处理内容须自有合法权利或已取得明确授权。

**本项目约束**：仅自用；不对外分发；不把 JJYB 的代码或修改版打包发布；使用其代码时保留版权信息。

## 与「模型全部走云端」的冲突点
- JJYB requirements.txt 包含 faster-whisper、ultralytics、torch、torchvision、torchaudio、opencv 等本地模型或重依赖。本项目不安装这些依赖，只保留云端 SDK 与 FFmpeg。
- NarratoAI requirements 中 azure-cognitiveservices-speech、tencentcloud-sdk、dashscope 等可作为云端适配参考，本项目按需引入。

## 入口文件（核对存在性）
- NarratoAI：webui.py（Streamlit）、app/services/SDE/short_drama_explanation.py（短剧解说）、app/services/SDP/generate_script_short.py（短剧脚本）
- JJYB：frontend/app.py（Flask+PyWebView）、backend/api/commentary_routes_enhanced.py（解说路由）、backend/api/jianying_draft_api.py（剪映草稿）

## 校验
- 两份 zip 的 SHA256 已记录（由 fetch_upstream.ps1 计算）。
- 两个解压目录的顶层文件与 LICENSE 已核对（见 tools/inspect_upstream.ps1 输出）。
