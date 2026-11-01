import frappe
from frappe import _
from frappe.model import display_fieldtypes


@frappe.whitelist(methods=["POST"])
def create_from_template(template: str, doc: dict | str):
	"""Insert a new checklist and its template image references in one transaction."""
	values = frappe.parse_json(doc)
	if (
		not isinstance(values, dict)
		or values.get("doctype") != "Project Checklist"
		or values.get("name")
		or values.get("docstatus", 0) != 0
	):
		frappe.throw(_("A new Project Checklist is required."))

	source = frappe.get_doc("Project Checklist", template)
	source.check_permission("read")
	source.apply_fieldlevel_read_permissions()
	if source.status != "Template":
		frappe.throw(_("Only checklists with status Template can be used as a template."))

	rows = values.get("checklist") or []
	if not isinstance(rows, list) or any(
		not isinstance(row, dict)
		or row.get("name")
		or row.get("doctype", "Project Checklist Point") != "Project Checklist Point"
		for row in rows
	):
		frappe.throw(_("Template checklist items must be new Project Checklist Points."))

	attachments = _template_image_files(source, rows)
	new_doc = frappe.new_doc("Project Checklist")
	# Accept schema fields rather than client lifecycle fields or permission flags.
	new_doc.update(_content_fields(new_doc.meta, values))
	new_doc.set("checklist", [])
	point_meta = frappe.get_meta("Project Checklist Point")
	for index, row in enumerate(rows, 1):
		point = new_doc.append("checklist", _content_fields(point_meta, row))
		point.idx = index
	new_doc.insert()
	for attachment in attachments:
		attachment.create_attachment_copy("Project Checklist", new_doc.name)
	return new_doc.as_dict()


def _content_fields(meta, values):
	return {
		field.fieldname: values[field.fieldname]
		for field in meta.fields
		if field.fieldname in values and field.fieldtype not in display_fieldtypes
	}


def _template_image_files(source, rows):
	source_images = {point.image for point in source.checklist if point.image}
	source_points = {point.name for point in source.checklist}
	attachments = []
	for image in dict.fromkeys(row.get("image") for row in rows if row.get("image")):
		if not isinstance(image, str) or image not in source_images:
			frappe.throw(_("Checklist images must come from the selected template."))
		if image.startswith(("https://", "http://")):
			# Keep external references without downloading remote content.
			continue
		if not image.startswith(("/files/", "/private/files/")):
			frappe.throw(_("The template contains an unsupported image reference."))

		files = frappe.get_all(
			"File",
			filters={"file_url": image},
			fields=["name", "attached_to_doctype", "attached_to_name"],
		)
		file_name = next(
			(
				file.name
				for file in files
				if (
					file.attached_to_doctype == "Project Checklist"
					and file.attached_to_name == source.name
				)
				or (
					file.attached_to_doctype == "Project Checklist Point"
					and file.attached_to_name in source_points
				)
			),
			None,
		)
		if not file_name:
			frappe.throw(_("An image attachment is missing from the selected template."))
		attachment = frappe.get_doc("File", file_name)
		attachment.check_permission("read")
		attachments.append(attachment)
	return attachments
