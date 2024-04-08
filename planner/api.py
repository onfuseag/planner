# Copyright (c) 2024, ONFUSE AG
# See license.txt

import frappe
from frappe.utils import getdate, add_to_date

@frappe.whitelist()
def get_planner_tasks(department):


    # Employees and tasks assigned to the
    users = []
    
    employees = frappe.db.get_all(
        "Employee", 
        filters={
            'department': department, 
            'status' : 'Active'
        },
        order_by="employee_name asc",
        fields=['name', 'employee_name', 'user_id', 'image']
    )

    for employee in employees: 
        user = {}
        user['name'] = employee.name
        user['user_id'] = employee.user_id
        user['image'] = employee.image
        user['employee_name'] = employee.employee_name

        # Final variabable all the tasks go into
        user_tasks = [] 

        if (employee.user_id):
            # Get all the tasks with a timeline assigned to them 60 days ago and 60 days into the future
            tasks = frappe.db.get_all(
                "Task", 
                filters={
                    "_assign": ["like", f'%{employee.user_id}%'], 
                    "exp_start_date": ["is", "set"], # Make sure the start and end dates are set, else we cannot show this in timeline
                    "exp_end_date": ["is", "set"]
                }, 
                fields=['name', 'project', 'subject', 'exp_start_date', 'exp_end_date', 'expected_time', 'actual_time', 'color']
            )

            for task in tasks:
                user_task = {}
                tasktitle = ""

                # If there is a project attached, we should get the project name
                if task.project: 
                    user_task["project_name"] = frappe.db.get_value("Project", task.project, "project_name")
                    tasktitle = f'{task.project} - {task.subject}'
                else: 
                    tasktitle = task.subject

                user_task['name'] = task.name
                user_task['title'] = tasktitle
                user_task['startDate'] = task.exp_start_date
                user_task['endDate'] = get_one_day_later(task.exp_end_date)
                user_task['color'] = task.color
                user_task['type'] = 1 # This should be a work task

                user_tasks.append(user_task)

            
            # Get the employee holidays
            holidaydata = frappe.db.get_all(
                "Leave Application", 
                filters={
                    "docstatus": 1,
                    "employee": employee.name, 
                    "status" : "Approved"
                }, 
                fields=['name', 'from_date','to_date', 'total_leave_days', 'leave_type']
            )
            
            for holiday in holidaydata: 

                user_task = {}

                user_task['type'] = 0 # This should be a holiday task
                user_task['endDate'] = get_one_day_later(holiday.to_date)
                user_task['startDate'] = holiday.from_date
                user_task['title'] = holiday.leave_type
                user_task['project_name'] = ""

                user_tasks.append(user_task)

        user['tasks'] = user_tasks
        users.append(user)

    return users

@frappe.whitelist()
def planner_change_date_task(task, exp_start_date, exp_end_date): 

    # Update the values
    frappe.db.set_value('Task', task, {
        "exp_start_date" : exp_start_date, 
        "exp_end_date" : exp_end_date
    })


@frappe.whitelist()
def planner_get_backlog(searchtext, projectText):

    bfilters = {
        'status': ["in", ["Overdue", "Open", "Working"]], 
        '_assign' : ["not like", f'%@%'] # Make sure this is not assigned to anyone
    }

    if (searchtext):
        bfilters['subject'] = ['like', f'%{searchtext}%']

    if (projectText): 
        bfilters['project'] = ['like', f'%{searchtext}%']

    backlogdata = frappe.db.get_all(
        "Task", 
        filters=bfilters,
        page_length=100, # Do not overload the ERP
        order_by='exp_start_date asc',
        fields=['name', 'subject', 'type', 'status', 'expected_time', 'priority', 'exp_start_date', 'project', 'color']
    )

    for bdata in backlogdata: 
        # If there is a project attached, we should get the project name
        if bdata.project: 
            bdata["project_name"] = frappe.db.get_value("Project", bdata.project, "project_name")

    return backlogdata

# This method will get a string and return a string one day later to it in the format YYYY-MM-DD
def get_one_day_later(strdate):
    date = frappe.utils.getdate(strdate)

    return add_to_date(date, days=1, as_string=True)


@frappe.whitelist(allow_guest=True)
def oauth_providers():
	from frappe.utils.html_utils import get_icon_html
	from frappe.utils.password import get_decrypted_password
	from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys

	out = []
	providers = frappe.get_all(
		"Social Login Key",
		filters={"enable_social_login": 1},
		fields=["name", "client_id", "base_url", "provider_name", "icon"],
		order_by="name",
	)

	for provider in providers:
		client_secret = get_decrypted_password("Social Login Key", provider.name, "client_secret")
		if not client_secret:
			continue

		icon = None
		if provider.icon:
			if provider.provider_name == "Custom":
				icon = get_icon_html(provider.icon, small=True)
			else:
				icon = f"<img src='{provider.icon}' alt={provider.provider_name}>"

		if provider.client_id and provider.base_url and get_oauth_keys(provider.name):
			out.append(
				{
					"name": provider.name,
					"provider_name": provider.provider_name,
					"auth_url": get_oauth2_authorize_url(provider.name, "/crm"),
					"icon": icon,
				}
			)
	return out

@frappe.whitelist(allow_guest=True)
def get_user_info(user=None):
	if frappe.session.user == "Guest":
		frappe.throw("Authentication failed", exc=frappe.AuthenticationError)

	filters = {"roles.role": ["like", "Gameplan %"]}
	if user:
		filters["name"] = user

	users = frappe.qb.get_query(
		"User",
		filters=filters,
		fields=["name", "email", "enabled", "user_image", "full_name", "user_type"],
		order_by="full_name asc",
		distinct=True,
	).run(as_dict=1)

	roles = frappe.db.get_all("Has Role", filters={"parenttype": "User"}, fields=["role", "parent"])
	user_profiles = []
	user_profile_map = {u.user: u for u in user_profiles}
	for user in users:
		if frappe.session.user == user.name:
			user.session_user = True
		user_profile = user_profile_map.get(user.name)
		if user_profile:
			user.user_profile = user_profile.name
			user.user_image = user_profile.image
			user.image_background_color = user_profile.image_background_color
			user.is_image_background_removed = user_profile.is_image_background_removed
		user_roles = [r.role for r in roles if r.parent == user.name]
		user.role = None
		for role in ["Gameplan Guest", "Gameplan Member", "Gameplan Admin"]:
			if role in user_roles:
				user.role = role
	return users
