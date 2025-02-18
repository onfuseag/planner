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
	tasks = frappe.get_all("Task",pluck="name")

	for t in tasks:
		assigned_users = get_assigned_users(t)
		for u in assigned_users:
			if(e_id:=frappe.db.exists("Employee",{ "user_id": u })):
				frappe.new_doc("Employee Item",parent=t,parentfield="employees",parenttype="Task",employee=e_id).insert()

frappe.enqueue(run_migration_tasks,queue="long")