import frappe
from frappe import _
from erpnext.projects.doctype.task.task import Task
from frappe.desk.form import assign_to

class CustomTask(Task):
	def validate(self):
		super().validate()
	
	def on_update(self):
		# Create Todo
		if not self.has_value_changed("employees"):
			return
		for e in self.employees:
			user_id = self.get_user(e.employee)
			if not user_id:
				continue
			
			if not frappe.db.exists("ToDo",
				{"reference_type":"Task","reference_name":self.name,"allocated_to":user_id,"status":"Open"}):
				self.create_todo(user_id)
		
		# cancel existing todo for removed employees
		old_doc = self.get_doc_before_save()
		old_employees = old_doc.employees if old_doc else []
		removed_employees = []

		for e in old_employees:
			if e.employee not in [e.employee for e in self.employees]:
				removed_employees.append(e.employee)
		for r_e in removed_employees:
			user_id = self.get_user(r_e)
			if not user_id:
				continue
			if todo:=frappe.db.exists(
				"ToDo",
				{"reference_type":"Task","reference_name":self.name,"allocated_to":user_id,"status":"Open"}
			):
				assign_to.remove("Task",self.name,user_id,True)


	def get_user(self, emp):
		return frappe.db.get_value("Employee", emp, "user_id")

	def create_todo(self,user_id):
		assign_to.add(
			{
				"assign_to": [user_id],
				"doctype": "Task",
				"name": self.name,
				"description": self.subject,
			}
		)
