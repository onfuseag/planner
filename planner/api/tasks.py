import frappe
from frappe.utils import add_days, date_diff


@frappe.whitelist()
def get_events(month_start, month_end, user_filters={}, task_filters={}):
	"""Get events grouped by user instead of employee"""
	tasks = get_tasks(month_start, month_end, user_filters, task_filters)
	events = {}

	for even in [tasks]:
		for key, value in even.items():
			if key in events:
				events[key].extend(value)
			else:
				events[key] = value
	return events


def get_tasks(month_start: str, month_end: str, user_filters: dict[str, str], task_filters):
	"""Get tasks grouped by user instead of employee"""
	cond = "AND task.status != 'Template' "

	for key, value in task_filters.items():
		if value:  # Only add filter if value is not empty/null
			cond += f"AND task.{key} = '{value}' "

	tasks = frappe.db.sql(f"""
		SELECT
			task.name,
			task.exp_start_date as start_date,
			task.exp_end_date as end_date,
			task.custom_start_time as start_time,
			task.custom_end_time as end_time,
			task.project,
			task.subject,
			task.status,
			user_item.user,
			task.color,
			task.completed_on
		FROM `tabTask` as task
		JOIN `tabUser Item` as user_item ON task.name = user_item.parent
		WHERE user_item.parenttype = 'Task'
		AND user_item.parentfield = 'users'
		AND task.exp_start_date <= "{month_end}"
		AND task.exp_end_date >= "{month_start}"
		{cond}
		""", as_dict=True)

	# group tasks by user
	user_tasks = {}
	for task in tasks:
		# Get the project name
		if task.project:
			task.project_name = frappe.db.get_value('Project', task.project, 'project_name')

		# Get user full name
		user_full_name = frappe.db.get_value('User', task.user, 'full_name')
		task.user_full_name = user_full_name

		if task.user not in user_tasks:
			user_tasks[task.user] = []
		user_tasks[task.user].append(task)

		if not task.get('color'):
			task.color = "#EFF6FE"

		if task.status == "Completed":
			task.color = "#dcfae7"

		if task.status == "Overdue":
			task.color = "#fdf0f0"

	return user_tasks

@frappe.whitelist()
def create_task(task_doc):
	new_task = frappe.new_doc('Task')
	new_task.subject = task_doc.get('subject')
	new_task.exp_start_date = task_doc.get('start_date')
	new_task.exp_end_date = task_doc.get('end_date')
	new_task.custom_start_time = task_doc.get('start_time')
	new_task.custom_end_time = task_doc.get('end_time')
	new_task.description = task_doc.get('description')
	new_task.status = task_doc.get('status')
	new_task.priority = task_doc.get('priority')
	new_task.project = task_doc.get('project', None)

	users = [u.get('value') for u in task_doc.get('users')]
	for user in users:
		new_task.append("users", {"user": user})

	new_task.save()



@frappe.whitelist()
def get_default_company():
	return frappe.defaults.get_user_default("Company")

@frappe.whitelist()
def get_task(name):
	task = frappe.get_doc("Task", name)
	return task.as_dict()

@frappe.whitelist()
def update_task(task_doc):
	task = frappe.get_doc("Task", task_doc.get('name'))
	task.exp_start_date = task_doc.get('exp_start_date')
	task.exp_end_date = task_doc.get('exp_end_date')
	task.custom_start_time = task_doc.get('start_time')
	task.custom_end_time = task_doc.get('end_time')
	task.description = task_doc.get('description')
	task.status = task_doc.get('status')
	task.priority = task_doc.get('priority')
	task.project = task_doc.get('project', None)
	task.completed_on = task_doc.get('completed_on', None)
	users = [u.get('value') for u in task_doc.get('users')]
	task.users = []
	for user in users:
		task.append("users", {"user": user})

	task.save()