import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    """Ensure the 'employees' custom field exists in the 'Task' DocType after each migration."""
    ensure_employees_field_exists()

def ensure_employees_field_exists():
    """Check if the 'employees' field exists in the 'Task' DocType and create it if missing."""
    doctype = "Task"
    fieldname = "employees"

    # Ensure the DocType exists
    if frappe.db.exists("DocType", doctype):
        # Check if the custom field already exists
        if not frappe.db.exists("Custom Field", {"fieldname": fieldname, "dt": doctype}):
            # Define the custom field
            custom_field = {
                doctype: [
                    {
                        "fieldname": fieldname,
                        "fieldtype": "Table MultiSelect",
                        "options": "Employee Item",
                        "label": "Assigned Employees",
                        "insert_after": "parent_task",
                    }
                ]
            }

            # Create the custom field
            create_custom_fields(custom_field)
            print(f"✅ Custom field '{fieldname}' created in '{doctype}'.")

        else:
            print(f"ℹ️ Custom field '{fieldname}' already exists in '{doctype}'.")

    else:
        print(f"⚠️ DocType '{doctype}' does not exist. Skipping field creation.")