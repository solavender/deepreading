# PDF Reading Workflow / PDF 阅读工作流

一个用于 Codex 等支持 `SKILL.md` 的代理环境的工作流技能：

**PDF → Microsoft MarkItDown → Markdown → 按需翻译／整理 → 选择四种风格 → 可批注 HTML 阅读器。**

文本处理完成后，代理会询问：极简知识型、沉浸阅读型、玻璃质感型或研究批注型。若当前任务已明确选择，则直接复用。核心阅读功能不随风格删减。

## 使用

把本目录安装到代理环境支持的个人技能目录，或通过该环境的技能安装功能导入本仓库。启动请求示例：

> 使用 $pdf-reading-workflow 把这份 PDF 全文翻译成中文。文本处理完成后让我选择阅读器风格，再生成可批注的 HTML。

依赖 Python 3.10+。在独立虚拟环境安装 `requirements.txt` 后，提取脚本可独立运行：

```bash
python scripts/extract_pdf.py /path/to/input.pdf /path/to/new-output
```

提取脚本产出页级溯源、整文提取和清单，不会自行翻译。文本处理完成并生成 `document.json` 后，可使用内置构建器生成四种风格之一的正式阅读器：

```bash
python scripts/build_reader.py /path/to/document.json /path/to/reader.html --style books
```

提取目录包含 `source.md`（逐页溯源）、`document.md`（整文转换）、`pages.json` 和 `manifest.json`。正文整理时应同时参考两份 Markdown，并在发生冲突时核对 PDF 原页。

运行回归测试：

```bash
python -m unittest discover -s tests -v
```

## 内容

- `SKILL.md`：主 SOP 与工具协作规则。
- `references/`：MarkItDown 转换、四种风格、数据模型、功能规范和验收清单。
- `scripts/extract_pdf.py`：实际调用 MarkItDown 的逐页转换工具。
- `scripts/build_reader.py`：将标准内容数据构建为自包含 HTML 阅读器。
- `assets/style-preview.html`：可离线打开的一页四风格演示；笔记刷新后重置。
- `assets/reader-template.html`：四种风格共用的正式阅读器模板与批注运行时。
- `agents/openai.yaml`：技能显示信息。
- `tests/`：提取、数据校验和四风格构建回归测试。

正式阅读器目标包括高亮批注、保存恢复、备份迁移、搜索筛选、原文对照、页码引用、术语表、图表查看、阅读设置和笔记导出。这些是代理需要实现和验证的功能契约，不是风格预览页已经具备的完整应用。

## 集成与边界

使用 [Microsoft MarkItDown](https://github.com/microsoft/markitdown) 作为转换依赖，不包含上游源码或 Adobe 依赖。默认本地提取，不启用云 OCR、第三方插件或外部 AI 服务。扫描文档、复杂表格和原图仍需实际核验。

文件管理、PDF 视觉核对、原生 DOCX 生成与 Sites 发布，仅在目标环境提供相应技能且任务需要时调用。HTML 本身不会执行 Python；托管网页不意味着批注云同步。

本仓库可独立发布；不含用户 PDF、私人站点地址、账户身份或凭据。不代表 Microsoft、Notion、Arc、Apple 或其他产品官方项目；产品名称只用于说明界面参考方向。
