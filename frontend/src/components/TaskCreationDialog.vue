<template>
  <Dialog :options="{ title: dialog.title, size: '3xl' }" v-model="show">
    <template #body-content>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5">
            Employee <span class="text-ink-red-3">*</span>
          </label>
          <Autocomplete
            :options="_employees"
            v-model="form.employees"
            multiple
            placeholder="Select Employee"
            label="Employee"
          />
        </div>
        <!-- Project -->
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5">Project </label>
          <Link
            doctype="Project"
            v-model="form.project"
            placeholder="Select Project"
          />
        </div>

        <FormControl
          type="input"
          label="Subject"
          v-model="form.subject"
          :required="true"
          placeholder="New app development"
          class="w-full col-span-2"
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
        <FormControl
          class="col-span-2"
          type="textarea"
          label="Description"
          v-model="form.description"
          placeholder="This task is about..."
        />
      </div>
    </template>
    <template #actions>
      <div class="flex space-x-3 justify-end">
        <Button
          size="md"
          label="Delete"
          theme="red"
          class="w-2"
          v-if="taskName"
        />
        <Button
          size="md"
          variant="solid"
          :disabled="dialog.actionDisabled"
          class="w-28"
          @click="dialog.action"
        >
          {{ dialog.button }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import {
  Dialog,
  FormControl,
  DatePicker,
  Autocomplete,
  createResource,
} from 'frappe-ui'
import { reactive } from 'vue'
import { dayjs, raiseToast } from '../utils'
import { projects, priority, status } from '../data'
import Link from './Link.vue'

const props = defineProps({
  employees: Array,
  taskName: String,
})

const emit = defineEmits(['create'])

const show = defineModel()

const form = reactive({
  employees: null,
  subject: '',
  status: 'Open',
  project: '',
  priority: 'Low',
  start_date: '',
  end_date: '',
  description: '',
})

const dialog = computed(() => {
  if (props.taskName)
    return {
      title: `[${selectedDate.value}] Task Assignment ${props.taskName}`,
      button: 'Update',
      action: () => {},
    }
  return {
    title: 'New Task Creation',
    button: 'Submit',
    action: createTask,
    actionDisabled: false,
  }
})

function createTask() {
  if (!validateForm()) return
  newTask.submit()
}

function validateForm() {
  if (
    !form.employees ||
    !form.subject ||
    !form.start_date ||
    !form.end_date ||
    !form.status ||
    !form.priority
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

function resetState() {
  form.employees = ''
  form.subject = ''
  form.status = ''
  form.project = ''
  form.priority = ''
  form.start_date = ''
  form.end_date = ''
  form.description = ''
}

const newTask = createResource({
  url: 'planner.api.tasks.create_task',
  makeParams() {
    return {
      task_doc: form,
    }
  },
  onSuccess() {
    raiseToast('success', 'Task(s) created successfully')
    emit('create')
    show.value = false
    resetState()
  },
})

// All select options
const _employees = computed(() => {
  return props.employees.map((employee) => ({
    label: `${employee.name}: ${employee.employee_name}`,
    value: employee.name,
    employee_name: employee.employee_name,
  }))
})

onMounted(() => {
  projects.fetch()
})
</script>
