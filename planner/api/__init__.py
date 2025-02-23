import frappe


@frappe.whitelist()
def get_current_user_info():
	current_user = frappe.session.user
	user = frappe.db.get_value(
		"User", current_user, ["name", "first_name", "full_name", "user_image"], as_dict=True
	)
	user["roles"] = frappe.get_roles(current_user)
	user['date_format'] = frappe.db.get_single_value('System Settings', 'date_format')

	return user