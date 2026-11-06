# Copyright (c) 2024, ONFUSE AG and Contributors
# See license.txt

import json
from html.parser import HTMLParser
from pathlib import Path
from unittest import TestCase

import frappe


class _ImageParser(HTMLParser):
	def __init__(self):
		super().__init__()
		self.images = []

	def handle_starttag(self, tag, attrs):
		if tag == "img":
			self.images.append(dict(attrs))


class TestProjectChecklist(TestCase):
	def test_print_format_escapes_checklist_image_urls(self):
		fixture = (
			Path(__file__).resolve().parents[2]
			/ "print_format/project_checklist/project_checklist.json"
		)
		layout = json.loads(json.loads(fixture.read_text(encoding="utf-8"))["format_data"])
		image_fields = [
			field for field in layout if "task.image" in field.get("options", "")
		]
		self.assertEqual(len(image_fields), 3)

		payload = "https://example.invalid/x' onerror='alert(1)' x='"
		rows = [
			frappe._dict(status=status, task="Test", image=payload, data="")
			for status in ("Open", "Done", "Data")
		]
		for field in image_fields:
			with self.subTest(field=field["options"][:30]):
				html = frappe.render_template(
					field["options"], {"doc": frappe._dict(checklist=rows)}
				)
				parser = _ImageParser()
				parser.feed(html)
				self.assertEqual(len(parser.images), 1)
				self.assertEqual(parser.images[0]["src"], payload)
				self.assertNotIn("onerror", parser.images[0])
				self.assertNotIn("x", parser.images[0])
