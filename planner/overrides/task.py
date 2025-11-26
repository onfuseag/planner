import frappe
from frappe import _
from erpnext.projects.doctype.task.task import Task
from frappe.desk.form import assign_to

class CustomTask(Task):
	def validate(self):
		super().validate()

	def on_update(self):
		# Create Todo for assigned users
		if not self.has_value_changed("users"):
			return

		# Create todo for newly assigned users
		for u in self.users:
			user_id = u.user
			if not user_id:
				continue

			if not frappe.db.exists("ToDo",
				{"reference_type":"Task","reference_name":self.name,"allocated_to":user_id,"status":"Open"}):
				self.create_todo(user_id)

		# Cancel existing todo for removed users
		old_doc = self.get_doc_before_save()
		old_users = old_doc.users if old_doc else []
		removed_users = []

		for u in old_users:
			if u.user not in [u.user for u in self.users]:
				removed_users.append(u.user)

		for r_u in removed_users:
			user_id = r_u
			if not user_id:
				continue
			if todo:=frappe.db.exists(
				"ToDo",
				{"reference_type":"Task","reference_name":self.name,"allocated_to":user_id,"status":"Open"}
			):
				assign_to.remove("Task",self.name,user_id,True)

	def create_todo(self,user_id):
		assign_to.add(
			{
				"assign_to": [user_id],
				"doctype": "Task",
				"name": self.name,
				"description": self.subject,
			}
		)
