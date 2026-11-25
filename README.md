# 短剧剪辑工作台

基于 Python / FastAPI 的短剧剪辑工作台：脚本解析、分镜、旁白、字幕与成片合成，ASR / OCR / TTS 走云端或系统能力，不依赖本地大模型。

## 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 测试

```bash
pytest
```

## 目录

- `workbench/`：核心工作流
- `scripts/`：命令行脚本
- `tools/`：辅助工具
- `config/`：配置
- `docs/`：文档
- `tests/`：测试

## 说明

本仓库只包含自有代码。第三方参考实现（`upstream/`）因许可证限制未纳入，依赖通过 requirements 安装。

## 许可

MIT
