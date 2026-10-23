import frappe

no_cache = 1

def get_context():
	csrf_token = frappe.sessions.get_csrf_token()
	frappe.db.commit()
	context = frappe._dict()
	context.csrf_token = csrf_token
	context.is_elevator_installed = "elevator" in frappe.get_installed_apps()
	return context
