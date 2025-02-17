<template>
  <Dialog
    :options="{
      title: taskName ? 'Update task' : 'Assign a Task',
      size: '3xl',
    }"
    v-model="show"
  >
    <template #body-content>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >Task <span class="text-ink-red-3">*</span></label
          >
          <Autocomplete
            :options="tasks.data"
            v-model="form.task"
            placeholder="Select task"
            label="Task"
          />
        </div>
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5">Project </label>
          <Autocomplete
            :options="projects.data"
            v-model="form.project"
            placeholder="Select project"
            label="Project"
          />
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4 mt-4" v-if="form.task?.value">
        <FormControl
          type="input"
          label="Subject"
          v-model="form.subject"
          :required="true"
          placeholder="New app development"
          class="w-full col-span-2"
          disabled
        />
        <FormControl
          type="select"
          label="Status"
          v-model="form.status"
          :options="status"
          :required="true"
        />
        <FormControl
          type="select"
          label="Priority"
          v-model="form.priority"
          :options="priority"
          :required="true"
        />
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >Start Date <span class="text-ink-red-3">*</span>
          </label>
          <DatePicker v-model="form.start_date" />
        </div>
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >End Date <span class="text-ink-red-3">*</span>
          </label>
          <DatePicker v-model="form.end_date" />
        </div>
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5">
            Employees <span class="text-ink-red-3">*</span>
          </label>
          <Autocomplete
            :options="_employees"
            v-model="form.employees"
            multiple
            placeholder="Select Employee"
            label="Employee"
          />
        </div>
        <div v-if="form.status === 'Completed'">
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >Completed On <span class="text-ink-red-3">*</span>
          </label>
          <DatePicker v-model="form.completed_on" />
        </div>
        <FormControl
          type="textarea"
          label="Description"
          v-model="form.description"
          :required="true"
          placeholder="Task description"
          class="col-span-2"
        />
      </div>
    </template>
    <template #actions="{ close }">
      <div class="flex space-x-3 justify-end">
        <Button
          :label="taskName ? 'Update Task' : 'Assign Task'"
          variant="solid"
          @click="submitTask(close)"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import {
  Dialog,
  Autocomplete,
  FormControl,
  DatePicker,
  createListResource,
  call,
  createResource,
} from 'frappe-ui'
import { onMounted, reactive, watch, computed, ref } from 'vue'
import { projects, priority, status } from '../data'
import { raiseToast, dayjs } from '../utils'
const props = defineProps({
  employees: Array,
  taskName: String,
  taskSubject: String,
})
const emit = defineEmits(['update'])

const show = defineModel()

const form = reactive({
  task: null,
  project: null,
  subject: '',
  status: 'Open',
  priority: 'Medium',
  start_date: '',
  end_date: '',
  description: '',
  employees: [],
  completed_by: null,
  completed_on: '',
})

const tasks = createListResource({
  doctype: 'Task',
  fields: ['name', 'subject'],
  transform(data) {
    return data.map((task) => ({
      label: `${task.name}: ${task.subject}`,
      value: task.name,
    }))
  },
})

const _taskName = ref(props.taskName)
const task = createResource({
  url: 'planner.api.tasks.get_task',
  makeParams() {
    return {
      name: _taskName.value,
    }
  },
  onSuccess(data) {
    form.employees = getEmployeeData(data.employees)
    form.subject = data.subject
    form.status = data.status
    form.description = data.description
    form.priority = data.priority
    form.start_date = data.exp_start_date
    form.end_date = data.exp_end_date
    form.completed_on = data.completed_on
    form.project = getProject(data.project)
  },
  auto: props.taskName ? true : false,
})

const getEmployeeData = (employees) => {
  employees = employees.map((emp) => emp.employee)
  if (!employees) return
  return props.employees
    .filter((emp) => employees.includes(emp.name))
    .map((emp) => ({
      label: `${emp.name}: ${emp.employee_name}`,
      value: emp.name,
    }))
}

const getProject = (project) => {
  if (!project) return
  return projects.data?.filter((proj) => proj.value === project)[0]
}

const _employees = computed(() => {
  return props.employees.map((employee) => ({
    label: `${employee.name}: ${employee.employee_name}`,
    value: employee.name,
  }))
})

onMounted(() => {
  if (!tasks.data) tasks.fetch()
  if (!projects.data) projects.fetch()
  if (props.taskName && props.taskSubject) {
    form.task = {
      label: `${props.taskName}: ${props.taskSubject}`,
      value: props.taskName,
    }
  }
})

function validateForm() {
  if (
    form.employees.length === 0 ||
    !form.subject ||
    !form.start_date ||
    !form.end_date ||
    !form.status ||
    !form.priority ||
    (form.status === 'Completed' && !form.completed_on) ||
    !form.task?.value
  ) {
    raiseToast('error', 'Please fill all the required fields')
    return false
  }
  if (dayjs(form.start_date).isAfter(dayjs(form.end_date))) {
    raiseToast('error', 'End Date should be greater than Start Date')
    return false
  }
  return true
}

const submitTask = async (close) => {
  if (!validateForm()) return
  try {
    await updateTask(
      {
        name: form.task?.value || null,
        project: form.project?.value || null,
        status: form.status,
        priority: form.priority,
        exp_start_date: form.start_date,
        exp_end_date: form.end_date,
        employees: form.employees || [],
        description: form.description,
        completed_on: form.completed_on || null,
      },
      close,
    )
  } catch (e) {
    const err = e.messages[0] || 'Could not update task'
    raiseToast('error', err)
  }
}
async function updateTask(form, close) {
  const d = await call('planner.api.tasks.update_task', {
    task_doc: form,
  })
  raiseToast('success', 'Task updated successfully')
  close()
  emit('update')
  return d.name
}

watch(
  () => form.project,
  (newProject) => {
    if (form.task?.value) return
    if (newProject?.value) {
      tasks.filters = {
        project: newProject?.value || '',
      }
    } else {
      tasks.filters = {}
    }
    tasks.fetch()
  },
)

watch(
  () => form.task?.value,
  (newVal) => {
    if (!newVal) return
    _taskName.value = newVal
    task.fetch()
  },
)
</script>

<style lang="scss" scoped></style>
