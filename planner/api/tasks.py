import frappe
from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee
from frappe.utils import add_days, date_diff


@frappe.whitelist()
def get_events(month_start, month_end, task_filters={}):
	tasks = get_tasks(month_start, month_end, task_filters)
	holidays = get_holidays_for_users(month_start, month_end)
	leaves = get_leaves_for_users(month_start, month_end)

	# Return tasks as-is (original format), but add metadata for holidays/leaves
	return {
		'tasks': tasks,
		'holidays': holidays,
		'leaves': leaves
	}


@frappe.whitelist()
def get_daily_events(date, task_filters={}):
	"""
	Get tasks for a specific day (used by daily view)
	"""
	tasks = get_tasks(date, date, task_filters)
	return tasks


def get_holidays(month_start: str, month_end: str, employee_filters: dict[str, str]) :
	holidays = {}
	holiday_lists = {}

	for employee in frappe.get_list("Employee", filters=employee_filters, pluck="name"):
		if not (holiday_list := get_holiday_list_for_employee(employee, raise_exception=False)):
			continue
		if holiday_list not in holiday_lists:
			holiday_lists[holiday_list] = frappe.get_all(
				"Holiday",
				filters={"parent": holiday_list, "holiday_date": ["between", [month_start, month_end]]},
				fields=["name as holiday", "holiday_date", "description", "weekly_off"],
			)
		holidays[employee] = holiday_lists[holiday_list].copy()

	return holidays


def get_holidays_for_users(month_start: str, month_end: str):
	"""
	Get holidays for users who are employees
	Maps users to their employee records and fetches holidays from holiday list
	"""
	from frappe.utils import getdate

	holidays_by_user = {}

	# Get all users who are employees
	user_employee_map = frappe.db.sql("""
		SELECT user.name as user, emp.name as employee
		FROM `tabUser` as user
		JOIN `tabEmployee` as emp ON user.name = emp.user_id
		WHERE user.enabled = 1
		AND emp.status = 'Active'
	""", as_dict=True)

	# Build a map of user to employee
	user_to_employee = {item['user']: item['employee'] for item in user_employee_map}

	# Get holidays for each employee's holiday list
	holiday_lists = {}
	for user, employee in user_to_employee.items():
		holiday_list = get_holiday_list_for_employee(employee, raise_exception=False)
		if not holiday_list:
			continue

		if holiday_list not in holiday_lists:
			holiday_lists[holiday_list] = frappe.get_all(
				"Holiday",
				filters={"parent": holiday_list, "holiday_date": ["between", [month_start, month_end]]},
				fields=["holiday_date", "description", "weekly_off"],
			)

		# Map holidays to dates for this user
		if user not in holidays_by_user:
			holidays_by_user[user] = {}

		for holiday in holiday_lists[holiday_list]:
			date_str = str(holiday['holiday_date'])
			holidays_by_user[user][date_str] = {
				'description': holiday['description'],
				'weekly_off': holiday['weekly_off']
			}

	return holidays_by_user


def get_leaves_for_users(month_start: str, month_end: str):
	"""
	Get approved leaves for users who are employees
	Maps users to their employee records and fetches approved leave applications
	"""
	from frappe.utils import getdate, add_days

	leaves_by_user = {}

	# Get all users who are employees
	user_employee_map = frappe.db.sql("""
		SELECT user.name as user, emp.name as employee
		FROM `tabUser` as user
		JOIN `tabEmployee` as emp ON user.name = emp.user_id
		WHERE user.enabled = 1
		AND emp.status = 'Active'
	""", as_dict=True)

	# Build a map of employee to user
	employee_to_user = {item['employee']: item['user'] for item in user_employee_map}

	if not employee_to_user:
		return leaves_by_user

	# Get all approved leave applications for these employees
	leave_applications = frappe.db.sql("""
		SELECT
			employee,
			leave_type,
			from_date,
			to_date
		FROM `tabLeave Application`
		WHERE docstatus = 1
		AND status = 'Approved'
		AND employee IN %(employees)s
		AND from_date <= %(end_date)s
		AND to_date >= %(start_date)s
	""", {
		'employees': list(employee_to_user.keys()),
		'start_date': month_start,
		'end_date': month_end
	}, as_dict=True)

	# Map leaves to users and dates
	for leave in leave_applications:
		user = employee_to_user.get(leave['employee'])
		if not user:
			continue

		if user not in leaves_by_user:
			leaves_by_user[user] = {}

		# Add leave for each date in the range
		current_date = getdate(leave['from_date'])
		end_date = getdate(leave['to_date'])

		while current_date <= end_date:
			# Only include dates within the requested range
			if getdate(month_start) <= current_date <= getdate(month_end):
				date_str = str(current_date)
				leaves_by_user[user][date_str] = {
					'leave_type': leave['leave_type']
				}
			current_date = add_days(current_date, 1)

	return leaves_by_user


def get_tasks(month_start: str, month_end: str, task_filters):
	"""
	Fetch tasks assigned to users via ToDo List doctype
	Groups tasks by the allocated_to user
	"""
	cond = "AND task.status != 'Template' "

	# Remove department from task_filters if present (department filters users, not tasks)
	if isinstance(task_filters, dict):
		task_filters.pop('department', None)

	for key, value in task_filters.items():
		if value and value != '':  # Skip null/empty values
			cond += f"AND task.{key} = '{value}' "

	# Query tasks through ToDo assignments
	# exp_start_date and exp_end_date are DateTime fields containing both date and time
	tasks = frappe.db.sql(f"""
		SELECT
			task.name,
			task.exp_start_date as start_date,
			task.exp_end_date as end_date,
			task.project,
			task.subject,
			task.status,
			todo.allocated_to as user,
			task.color,
			task.completed_on,
			task.priority
		FROM `tabTask` as task
		JOIN `tabToDo` as todo ON task.name = todo.reference_name
		WHERE todo.reference_type = 'Task'
		AND todo.status = 'Open'
		AND task.exp_start_date <= "{month_end}"
		AND task.exp_end_date >= "{month_start}"
		{cond}
		""", as_dict=True)

	# Debug logging
	import json
	frappe.log_error(
		title="get_tasks Debug",
		message=json.dumps({
			'month_start': month_start,
			'month_end': month_end,
			'task_filters': task_filters,
			'result_count': len(tasks),
			'tasks': [{'name': t.name, 'user': t.user, 'start': str(t.start_date), 'end': str(t.end_date)} for t in tasks]
		}, indent=2, default=str)
	)

	# group tasks by user
	user_tasks = {}
	for task in tasks:
		# Get the project name
		if task.project:
			task.project_name = frappe.db.get_value('Project', task.project, 'project_name')

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


def get_leaves(month_start, month_end, employee_filters):
	LeaveApplication = frappe.qb.DocType("Leave Application")
	Employee = frappe.qb.DocType("Employee")

	query = (
		frappe.qb.select(
			LeaveApplication.name.as_("leave"),
			LeaveApplication.employee,
			LeaveApplication.leave_type,
			LeaveApplication.from_date,
			LeaveApplication.to_date,
		)
		.from_(LeaveApplication)
		.left_join(Employee)
		.on(LeaveApplication.employee == Employee.name)
		.where(
			(LeaveApplication.docstatus == 1)
			& (LeaveApplication.status == "Approved")
			& (LeaveApplication.from_date <= month_end)
			& (LeaveApplication.to_date >= month_start)
		)
	)

	for filter in employee_filters:
		query = query.where(Employee[filter] == employee_filters[filter])

	return group_by_employee(query.run(as_dict=True))


def group_by_employee(events: list[dict]) -> dict[str, list[dict]]:
	grouped_events = {}
	for event in events:
		grouped_events.setdefault(event["employee"], []).append(
			{k: v for k, v in event.items() if k != "employee"}
		)
	return grouped_events

@frappe.whitelist()
def create_task(task_doc):
	from frappe.desk.form import assign_to

	new_task = frappe.new_doc('Task')
	new_task.subject = task_doc.get('subject')
	# exp_start_date and exp_end_date are DateTime fields (contain both date and time)
	new_task.exp_start_date = task_doc.get('start_date')
	new_task.exp_end_date = task_doc.get('end_date')
	new_task.description = task_doc.get('description')
	new_task.status = task_doc.get('status')
	new_task.priority = task_doc.get('priority')
	new_task.project = task_doc.get('project', None)

	new_task.save()

	# Assign to users using Frappe's native assignment system
	users = [u.get('value') for u in task_doc.get('users', [])]
	if users:
		assign_to.add({
			"assign_to": users,
			"doctype": "Task",
			"name": new_task.name,
			"description": new_task.subject,
		})

	return new_task.name



@frappe.whitelist()
def get_default_company():
	return frappe.defaults.get_user_default("Company")

@frappe.whitelist()
def get_users_with_tasks(month_start, month_end):
	"""
	Get all users who have tasks assigned via ToDo in the given date range
	"""
	users = frappe.db.sql("""
		SELECT DISTINCT
			user.name,
			user.full_name,
			user.user_image as image,
			user.email
		FROM `tabUser` as user
		JOIN `tabToDo` as todo ON user.name = todo.allocated_to
		JOIN `tabTask` as task ON todo.reference_name = task.name
		WHERE todo.reference_type = 'Task'
		AND todo.status = 'Open'
		AND task.exp_start_date <= %(month_end)s
		AND task.exp_end_date >= %(month_start)s
		AND user.enabled = 1
		ORDER BY user.full_name
	""", {"month_start": month_start, "month_end": month_end}, as_dict=True)

	# Debug logging
	import json
	frappe.log_error(
		title="get_users_with_tasks Debug",
		message=json.dumps({
			'month_start': month_start,
			'month_end': month_end,
			'result_count': len(users),
			'users': [u.name for u in users]
		}, indent=2)
	)

	return users


@frappe.whitelist()
def get_users_with_daily_tasks(date):
	"""
	Get all users who have tasks on a specific day (for daily view)
	"""
	return get_users_with_tasks(date, date)


@frappe.whitelist()
def get_all_enabled_users():
	"""
	Get all enabled users in the system (for task assignment dropdowns)
	"""
	users = frappe.db.sql("""
		SELECT
			user.name,
			user.full_name,
			user.user_image as image,
			user.email
		FROM `tabUser` as user
		WHERE user.enabled = 1
		AND user.name NOT IN ('Administrator', 'Guest')
		AND user.user_type = 'System User'
		ORDER BY user.full_name
	""", as_dict=True)

	return users


@frappe.whitelist()
def get_users_for_planner(department=None):
	"""
	Get users for planner views, optionally filtered by department.
	When department is specified, only returns users whose Employee belongs to that department.
	"""
	if department:
		# Filter users by their Employee's department
		users = frappe.db.sql("""
			SELECT
				user.name,
				user.full_name,
				user.user_image
			FROM `tabUser` as user
			JOIN `tabEmployee` as emp ON user.name = emp.user_id
			WHERE user.enabled = 1
			AND user.name NOT IN ('Administrator', 'Guest')
			AND user.user_type = 'System User'
			AND emp.status = 'Active'
			AND emp.department = %(department)s
			ORDER BY user.full_name
		""", {'department': department}, as_dict=True)
	else:
		# Return all enabled system users
		users = frappe.db.sql("""
			SELECT
				user.name,
				user.full_name,
				user.user_image
			FROM `tabUser` as user
			WHERE user.enabled = 1
			AND user.name NOT IN ('Administrator', 'Guest')
			AND user.user_type = 'System User'
			ORDER BY user.full_name
		""", as_dict=True)

	return users


@frappe.whitelist()
def get_all_departments():
	"""
	Get all departments in the system (for department filter dropdown)
	"""
	departments = frappe.db.sql("""
		SELECT
			name,
			department_name
		FROM `tabDepartment`
		ORDER BY department_name
	""", as_dict=True)

	return departments

@frappe.whitelist()
def get_task(name):
	task = frappe.get_doc("Task", name)
	task_dict = task.as_dict()

	# Get current ToDo assignments for this task
	assignments = frappe.get_all(
		"ToDo",
		filters={
			"reference_type": "Task",
			"reference_name": name,
			"status": "Open"
		},
		fields=["allocated_to", "name"]
	)

	# Add assigned users to the response
	task_dict["assigned_users"] = [
		{
			"value": a.allocated_to,
			"label": frappe.db.get_value("User", a.allocated_to, "full_name") or a.allocated_to
		}
		for a in assignments
	]

	return task_dict

@frappe.whitelist()
def update_task(task_doc):
	from frappe.desk.form import assign_to

	task = frappe.get_doc("Task", task_doc.get('name'))
	# exp_start_date and exp_end_date are DateTime fields (contain both date and time)
	task.exp_start_date = task_doc.get('exp_start_date')
	task.exp_end_date = task_doc.get('exp_end_date')
	task.description = task_doc.get('description')
	task.status = task_doc.get('status')
	task.priority = task_doc.get('priority')
	task.project = task_doc.get('project', None)
	task.completed_on = task_doc.get('completed_on', None)

	task.save()

	# Update assignments using Frappe's native assignment system
	users = [u.get('value') for u in task_doc.get('users', [])]

	# Get current assignments
	current_assignments = frappe.get_all(
		"ToDo",
		filters={
			"reference_type": "Task",
			"reference_name": task.name,
			"status": "Open"
		},
		pluck="allocated_to"
	)

	# Remove users who are no longer assigned
	for user in current_assignments:
		if user not in users:
			assign_to.remove("Task", task.name, user)

	# Add new users
	new_users = [u for u in users if u not in current_assignments]
	if new_users:
		assign_to.add({
			"assign_to": new_users,
			"doctype": "Task",
			"name": task.name,
			"description": task.subject,
		})
