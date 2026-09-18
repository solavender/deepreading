# 文本、来源与阅读状态

生成以下逻辑数据，可组合存入一个 JSON。不要把 PDF 的物理分页、印刷页码、HTML 屏幕分页混为一谈。

```json
{
  "schemaVersion": 1,
  "documentId": "sha256-of-original-pdf",
  "revision": "processed-content-hash",
  "metadata": {"title": "实际标题", "authors": [], "doi": null},
  "selectedStyle": null,
  "processing": {"mode": "translate", "targetLanguage": "zh-CN", "status": "text-ready"},
  "blocks": [{
    "id": "b0001", "sectionId": "s01", "kind": "paragraph",
    "sourceText": "原始文字", "processedText": "处理后的文字",
    "pdfPages": [1], "printedPages": [],
    "sourceBlockIds": ["p001-b001"], "reviewStatus": "needs-review"
  }],
  "figures": [], "terms": [], "issues": []
}
```

稳定 ID 一旦分配就保持，不使用当前 DOM 索引、文本显示位置或随机刷新值。跨页、合并、拆分段落保留一对多／多对一源块关系。

图表记录：ID、图号、实际原图路径／嵌入数据、处理后图路径、原始与处理后图注、物理页、印刷页、是否已核对。保留原图，不把重绘图称作原图。

术语记录：原词、统一译法、简短释义、释义来源类型（原文或阅读辅助）、出现块 ID 列表。原文未支持的定义不冒充作者观点。

批注记录示例：

```json
{
  "id": "unique-annotation-id",
  "documentId": "sha256-of-original-pdf",
  "revision": "processed-content-hash",
  "side": "processed",
  "anchors": [{"blockId": "b0001", "start": 0, "end": 4,
    "exact": "处理后的", "prefix": "", "suffix": "文字"}],
  "color": "yellow", "note": "读者批注", "updatedAt": "ISO-time"
}
```

- 明确定义偏移量计数方式；浏览器实现可统一采用 JS UTF-16 code unit，与 DOM Range 保持一致。多块选区用 anchors 数组。
- 恢复顺序：文档匹配 → 稳定块 ID → 位置与 exact 文本验证 → 唯一上下文匹配。重复句匹配不唯一时保留为未定位，允许人工处理。
- 修改主题或正文装饰不改变基础文本。不要把工具按钮、隐藏原文、译注或脚注控件计入正文偏移。
- 修订正文时迁移旧锚点，保留原数据；不静默删除失败标注。
- 保存阅读位置为块 ID 与块内相对位置，而非只有 scrollY。设置独立保存，避免改变布局后跳回错误页。
- 用户上传的 HTML／Markdown、批注、来源文本均需转义或净化；不执行其中脚本。嵌入 JSON 时转义 `<`，避免结束 script 标签。
