import frappe
from frappe.utils import add_days, date_diff

from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee


@frappe.whitelist()
def get_events(month_start, month_end, employee_filters={}, task_filters={}):

	holidays = get_holidays(month_start, month_end, employee_filters)
	tasks = get_tasks(month_start, month_end, employee_filters,task_filters)
	leaves = get_leaves(month_start, month_end, employee_filters)
	events = {}

	for even in [holidays, tasks, leaves]:
		for key, value in even.items():
			if key in events:
				events[key].extend(value)
			else:
				events[key] = value
	return events


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


def get_tasks(month_start: str, month_end: str, employee_filters: dict[str, str],task_filters):
	filters = {
		"exp_start_date": ["between", (month_start, month_end)],
		"exp_end_date": ["between", (month_start, month_end)],
	}
	cond = ""
	for key, value in task_filters.items():
		cond += f"AND task.{key} = '{value}' "
	
	tasks = frappe.db.sql(f"""
		SELECT task.name, task.exp_start_date as start_date, task.exp_end_date as end_date, task.subject, task.status, employee_item.employee, task.color, task.completed_on
		FROM `tabTask` as task
		JOIN `tabEmployee Item` as employee_item ON task.name = employee_item.parent
		WHERE employee_item.parenttype = 'Task'
		AND employee_item.parentfield = 'employees'
		AND task.exp_start_date <= "{month_end}"
		AND task.exp_end_date >= "{month_start}"
		{cond}
		""", as_dict=True)
		
	# group tasks by employee
	employee_tasks = {}
	for task in tasks:
		if task.employee not in employee_tasks:
			employee_tasks[task.employee] = []
		employee_tasks[task.employee].append(task)
		if(not task.get('color')):
			task.color = "#EFF6FE"
	return employee_tasks


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
	new_task = frappe.new_doc('Task')
	new_task.subject = task_doc.get('subject')
	new_task.exp_start_date = task_doc.get('start_date')
	new_task.exp_end_date = task_doc.get('end_date')
	new_task.description = task_doc.get('description')
	new_task.status = task_doc.get('status')
	new_task.priority = task_doc.get('priority')
	new_task.project = task_doc.get('project',None)

	employees = [e.get('value') for e in task_doc.get('employees')]
	for employee in employees:
		new_task.append("employees", {"employee": employee})

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
	task.description = task_doc.get('description')
	task.status = task_doc.get('status')
	task.priority = task_doc.get('priority')
	task.project = task_doc.get('project',None)
	task.completed_on = task_doc.get('completed_on',None)
	employees = [e.get('value') for e in task_doc.get('employees')]
	task.employees = []
	for employee in employees:
		task.append("employees", {"employee": employee})

	task.save()