import frappe
from frappe import _
from erpnext.projects.doctype.task.task import Task

class CustomTask(Task):
	def validate(self):
		super().validate()
	
	def before_save(self):
		# Create  Todo
		for e in self.employees:
			user_id = self.get_user(e.employee)
			if not user_id:
				continue
			
			if not frappe.db.exists("ToDo",
				{"reference_type":"Task","reference_name":self.name,"allocated_to":user_id,"status":"Open"}):
				self.create_todo(user_id)
		
		# cancel existing todo for removed employees
		old_employees = self.get_doc_before_save().employees
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
				frappe.db.set_value("ToDo",todo,"status","Cancelled")


	def get_user(self, emp):
		return frappe.db.get_value("Employee", emp, "user_id")

	def create_todo(self,user_id):
		todo = frappe.new_doc(
			"ToDo",
			reference_type="Task",
			reference_name=self.name,
			allocated_to=user_id,
			description=self.subject,
			assigned_by=frappe.session.user
		).insert()
