import frappe


def execute():
	"""Replace the auto-generated "Planner" workspace tile with the app's own desktop icon.

	Frappe creates app icons from add_to_apps_screen only when an app is installed, and
	skips them when another icon already holds the app's title. Sites that installed
	Planner before it declared add_to_apps_screen therefore only have a generic workspace
	tile named "Planner", which blocks the app icon.
	"""
	if not frappe.db.has_column("Desktop Icon", "icon_type"):
		return  # no app icons before Frappe v16

	from frappe.desk.doctype.desktop_icon.desktop_icon import create_desktop_icons_from_installed_apps

	old = frappe.db.get_value(
		"Desktop Icon", "Planner", ["icon_type", "link_type", "link_to", "standard"], as_dict=True
	)
	# only the generated workspace link; leave an app icon or anything set up by hand alone
	if old and old.icon_type == "Link" and old.link_type == "Workspace Sidebar" and old.link_to == "Planner" and not old.standard:
		frappe.delete_doc("Desktop Icon", "Planner", ignore_permissions=True, force=True)

	create_desktop_icons_from_installed_apps()
	# every user's cached desktop, not only the user running the migration
	frappe.cache.delete_key("desktop_icons")
	frappe.cache.delete_key("bootinfo")
