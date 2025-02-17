import frappe
from frappe import _
from frappe.desk.doctype.todo.todo import ToDo


class CustomToDo(ToDo):

	def validate(self):
		super().validate()
	
	def on_update(self):
		self.add_employees_to_task()  	

	def add_employees_to_task(self):		
		if(self.reference_type == "Task" and self.reference_name):
			employee_id = frappe.db.exists("Employee", {"user_id": self.allocated_to})
			if not employee_id:
				return
			if(self.status == "Cancelled"):
				# remove employee from task
				task = frappe.get_doc("Task", self.reference_name)
				employees = [employee.employee for employee in task.employees]
				if employee_id in employees:
					task.employees = [employee for employee in task.employees if employee.employee != employee_id]
					task.save()
				return

			# add employee to task
			task = frappe.get_doc("Task", self.reference_name)
			employees = [employee.employee for employee in task.employees]
			if employee_id in employees:
				return
			task.append("employees", {"employee": employee_id})
			task.save()