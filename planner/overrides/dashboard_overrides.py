
from frappe import _ 

def get_dashboard_project(data): 

    data['fieldname'] = 'project'

    data["transactions"].append(
        {
            "label" : _("Planner"), 
            "items" : ["Project Checklist"]
        }
    )

    return data