import base64
from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import today

from planner.api.checklists import create_from_template


class TestChecklistTemplates(IntegrationTestCase):
	def setUp(self):
		super().setUp()
		frappe.set_user("Administrator")
		self.checklist_type = frappe.get_doc(
			{"doctype": "Project Checklist Type", "type": "Template test " + frappe.generate_hash(length=8)}
		).insert()
		self.template = frappe.get_doc(
			{
				"doctype": "Project Checklist",
				"type": self.checklist_type.name,
				"status": "Template",
				"pretext": "Inspect the installation",
				"checklist": [
					{"category": "Measurements", "task": "Voltage", "data": "230 V", "status": "Data"},
					{"category": "Optional", "task": "Roof access", "status": "Not applicable"},
				],
			}
		).insert()

	def tearDown(self):
		frappe.set_user("Administrator")
		super().tearDown()

	def draft(self):
		return {
			"doctype": "Project Checklist",
			"type": self.template.type,
			"status": "Open",
			"date": today(),
			"pretext": self.template.pretext,
			"checklist": [
				{
					"doctype": "Project Checklist Point",
					**{field: row.get(field) for field in ("category", "task", "data", "status", "image")},
				}
				for row in self.template.checklist
			],
		}

	def attach_image(self):
		image = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": "template-" + frappe.generate_hash(length=8) + ".png",
				"is_private": 1,
				"attached_to_doctype": "Project Checklist",
				"attached_to_name": self.template.name,
				"content": base64.b64decode(
					"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jFz0AAAAASUVORK5CYII="
				),
			}
		).insert()
		self.template.checklist[0].image = image.file_url
		self.template.save()
		return image

	def test_inserts_new_identities_and_independent_image_reference(self):
		source_file = self.attach_image()
		before = frappe.get_doc("Project Checklist", self.template.name).as_dict()
		draft = self.draft()
		# Reusing the image on two points needs one File reference per checklist.
		draft["checklist"][1]["image"] = source_file.file_url
		created = create_from_template(self.template.name, draft)
		self.assertNotEqual(created.name, self.template.name)
		self.assertEqual(created.status, "Open")
		self.assertEqual(created.checklist[0].status, "Data")
		self.assertEqual(created.checklist[1].status, "Not applicable")
		self.assertEqual([row.idx for row in created.checklist], [1, 2])
		self.assertTrue({row.name for row in created.checklist}.isdisjoint(row.name for row in self.template.checklist))
		self.assertEqual(frappe.get_doc("Project Checklist", self.template.name).as_dict(), before)
		copies = frappe.get_all(
			"File",
			filters={"attached_to_doctype": "Project Checklist", "attached_to_name": created.name},
			pluck="name",
		)
		self.assertEqual(len(copies), 1)
		copied_file = frappe.get_doc("File", copies[0])
		self.assertNotEqual(copied_file.name, source_file.name)
		self.assertEqual(copied_file.file_url, source_file.file_url)
		self.assertEqual(copied_file.content_hash, source_file.content_hash)
		frappe.delete_doc("File", source_file.name)
		self.assertTrue(copied_file.exists_on_disk())
		self.assertTrue(copied_file.get_content())

	def test_external_images_remain_references_without_a_fetch(self):
		self.template.checklist[0].image = "https://example.com/template-image.png"
		self.template.save()
		created = create_from_template(self.template.name, self.draft())
		self.assertEqual(created.checklist[0].image, self.template.checklist[0].image)
		self.assertFalse(frappe.db.exists("File", {"attached_to_name": created.name}))

	def test_rejects_unreadable_template_before_inserting(self):
		draft = self.draft()
		count_before = frappe.db.count("Project Checklist")
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			create_from_template(self.template.name, draft)
		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.count("Project Checklist"), count_before)

	def test_parent_insert_keeps_create_permission_checks(self):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": "template-test-" + frappe.generate_hash(length=8) + "@example.com",
				"first_name": "Template reader",
				"send_welcome_email": 0,
			}
		).insert()
		frappe.share.add("Project Checklist", self.template.name, user=user.name, read=1)
		draft = self.draft()
		# Client permission flags must not bypass the fresh parent's normal insert.
		draft["flags"] = {"ignore_permissions": True}
		frappe.set_user(user.name)
		with self.assertRaises(frappe.PermissionError):
			create_from_template(self.template.name, draft)

	def test_rejects_existing_identities_and_wrong_doctypes(self):
		for update in (
			{"doctype": "Task"},
			{"name": self.template.name},
			{"docstatus": 1},
			{"checklist": [{"name": self.template.checklist[0].name}]},
			{"checklist": [{"doctype": "Task"}]},
		):
			with self.subTest(update=update), self.assertRaises(frappe.ValidationError):
				create_from_template(self.template.name, {**self.draft(), **update})

	def test_rejects_non_template_sources_and_unrelated_images(self):
		draft = self.draft()
		draft["checklist"][0]["image"] = "/private/files/unrelated.png"
		with self.assertRaises(frappe.ValidationError):
			create_from_template(self.template.name, draft)
		self.template.status = "Open"
		self.template.save()
		with self.assertRaises(frappe.ValidationError):
			create_from_template(self.template.name, self.draft())

	def test_checks_source_file_read_permission(self):
		source_file = self.attach_image()
		from frappe.core.doctype.file.file import File

		original_check_permission = File.check_permission

		def deny_source_file(file, *args, **kwargs):
			if file.name == source_file.name:
				raise frappe.PermissionError
			return original_check_permission(file, *args, **kwargs)

		count_before = frappe.db.count("Project Checklist")
		with patch.object(File, "check_permission", deny_source_file):
			with self.assertRaises(frappe.PermissionError):
				create_from_template(self.template.name, self.draft())
		self.assertEqual(frappe.db.count("Project Checklist"), count_before)
