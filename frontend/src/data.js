import { createListResource } from 'frappe-ui'

export const projects = createListResource({
  doctype: 'Project',
  fields: ['name', 'project_name'],
  cache: ['Projects'],
  transform(data) {
    return data.map((project) => ({
      label: `${project.name}: ${project.project_name}`,
      value: project.name,
    }))
  },
})

export const tasks = createListResource({
  doctype: 'Task',
  fields: ['name', 'subject'],
  cache: ['Tasks'],
  makeParams: ({ project }) => {
    return {
      filters: {
        project: project,
      },
    }
  },
  transform(data) {
    return data.map((task) => ({
      label: `${task.name}: ${task.subject}`,
      value: task.name,
    }))
  },
})

export const getTask = createListResource({
  doctype: 'Task',
  fields: [
    'name',
    'subject',
    'status',
    'description',
    'project',
    'priority',
    'employee',
  ],
  makeParams: ({ id }) => {
    return {
      filters: {
        name: id,
      },
    }
  },
})

export const priority = ['Low', 'Medium', 'High', 'Urgent'].map((value) => ({
  label: value,
  value,
}))

export const status = [
  'Open',
  'Working',
  'Pending Review',
  'Overdue',
  'Completed',
  'Cancelled',
].map((value) => ({
  label: value,
  value,
}))

export const departments = createListResource({
  doctype: 'Department',
  fields: ['name', 'department_name'],
  cache: ['Departments'],
  pageLength: 99999,
  transform(data) {
    return data.map((dept) => ({
      label: dept.department_name,
      value: dept.name,
    }))
  },
})
