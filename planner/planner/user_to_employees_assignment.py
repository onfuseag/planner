import frappe


def get_assigned_users(task):
	assigned_users = frappe.get_all(
		"ToDo",fields=["allocated_to"],filters={
			"reference_type": "Task",
			"reference_name": task,
			"status": ("!=", "Cancelled"),
		},
		pluck="allocated_to",
	)
	users = list(set(assigned_users))
	return users


def run_migration_tasks():
	# Task needs an "employees" table field (Employee Item) for these rows to belong anywhere
	if not frappe.get_meta("Task").has_field("employees"):
		return

	tasks = frappe.get_all("Task",pluck="name")

	for t in tasks:
		assigned_users = get_assigned_users(t)
		for u in assigned_users:
			if(e_id:=frappe.db.exists("Employee",{ "user_id": u })):
				if frappe.db.exists("Employee Item", {"parent": t, "parenttype": "Task", "employee": e_id}):
					continue
				frappe.new_doc("Employee Item",parent=t,parentfield="employees",parenttype="Task",employee=e_id).insert()


def enqueue_migration():
	"""Run once by hand: bench --site <site> execute planner.planner.user_to_employees_assignment.enqueue_migration"""
	frappe.enqueue(run_migration_tasks,queue="long")
