from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


extractor = load_module("extract_pdf", ROOT / "scripts" / "extract_pdf.py")
builder = load_module("build_reader", ROOT / "scripts" / "build_reader.py")


def write_pdf(path: Path) -> None:
    writer = PdfWriter()
    for text in ("First page workflow verification.", "Second page provenance verification."):
        page = writer.add_blank_page(width=612, height=792)
        font = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})
        })
        stream = DecodedStreamObject()
        stream.set_data(f"BT /F1 12 Tf 50 700 Td ({text}) Tj ET".encode())
        page[NameObject("/Contents")] = writer._add_object(stream)
    writer.write(str(path))


def sample_document() -> dict:
    return {
        "schemaVersion": 1,
        "documentId": "test-document",
        "revision": "r1",
        "metadata": {"title": "测试阅读器", "subtitle": "可复现构建"},
        "selectedStyle": "books",
        "blocks": [
            {"id": "b0001", "sectionId": "s01", "kind": "heading",
             "sourceText": "第一章", "processedText": "第一章", "pdfPages": [1]},
            {"id": "b0002", "sectionId": "s01", "kind": "paragraph",
             "sourceText": "原始文字", "processedText": "整理后文字", "pdfPages": [1]},
        ],
        "figures": [],
        "terms": [],
        "issues": [],
    }


class WorkflowTests(unittest.TestCase):
    def test_extraction_preserves_pages_and_whole_document(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "sample.pdf", root / "output"
            write_pdf(source)
            manifest = extractor.extract(source, output)
            pages = json.loads((output / "pages.json").read_text())
            self.assertEqual(manifest["page_count"], 2)
            self.assertEqual([page["pdf_page"] for page in pages], [1, 2])
            self.assertIn("First page", pages[0]["markdown"])
            self.assertIn("Second page", pages[1]["markdown"])
            self.assertIn("First page", (output / "document.md").read_text())
            self.assertTrue(manifest["whole_document_extraction"])

    def test_builder_supports_every_style_and_is_self_contained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            document = root / "document.json"
            document.write_text(json.dumps(sample_document(), ensure_ascii=False))
            for style in builder.STYLES:
                output = root / f"{style}.html"
                builder.build(document, output, ROOT / "assets" / "reader-template.html", root, style)
                text = output.read_text()
                self.assertIn("测试阅读器", text)
                self.assertIn(f'"selectedStyle":"{style}"', text)
                self.assertNotIn("__DOCUMENT_DATA__", text)
                self.assertNotIn('src="http', text)

    def test_builder_rejects_duplicate_block_ids(self):
        data = sample_document()
        data["blocks"][1]["id"] = data["blocks"][0]["id"]
        with self.assertRaisesRegex(ValueError, "unique"):
            builder.validate_document(data)


if __name__ == "__main__":
    unittest.main()
