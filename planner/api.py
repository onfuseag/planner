# Copyright (c) 2024, ONFUSE AG
# See license.txt

import frappe
from frappe.utils import getdate, add_to_date

@frappe.whitelist()
def get_planner_tasks(department):

    users = []
    
    employees = frappe.db.get_all(
        "Employee", 
        filters={
            'department': department, 
            'status' : 'Active'
        },
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
                    "_assign": ["like", f'%{employee.user_id}%']
                }, 
                fields=['name', 'project', 'subject', 'exp_start_date', 'exp_end_date', 'expected_time', 'actual_time']
            )

            for task in tasks:
                user_task = {}

                # If there is a project attached, we should get the project name
                if task.project: 
                    user_task["project_name"] = frappe.db.get_value("Project", task.project, "project_name")

                user_task['name'] = task.name
                user_task['title'] = f'{task.project} - {task.subject}'
                user_task['startDate'] = task.exp_start_date
                user_task['endDate'] = get_one_day_later(task.exp_end_date)
                user_task['type'] = 1 # This should be a work task

                user_tasks.append(user_task)

            
            # Get the employee holidays
            attendancedata = frappe.db.get_all(
                "Attendance", 
                filters={
                    "docstatus": 1,
                    "employee": employee.name, 
                    "status" : "On Leave"
                }, 
                fields=['name', 'status', 'leave_type', 'attendance_date']
            )
            
            for attendance in attendancedata: 

                user_task = {}

                user_task['type'] = 0 # This should be a holiday task
                user_task['endDate'] = get_one_day_later(attendance.attendance_date)
                user_task['startDate'] = attendance.attendance_date
                user_task['title'] = attendance.status
                user_task['project_name'] = attendance.leave_type

                user_tasks.append(user_task)

        user['tasks'] = user_tasks
        users.append(user)

    return users

# This method will get a string and return a string one day later to it in the format YYYY-MM-DD
def get_one_day_later(strdate):
    date = frappe.utils.getdate(strdate)

    return add_to_date(date, days=1, as_string=True)