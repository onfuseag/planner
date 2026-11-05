<template>
  <Dialog
    :title="taskName ? 'Update task' : 'Assign a Task'"
    size="3xl"
    v-model:open="show"
  >
    <template #default>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >Task <span class="text-ink-red-5">*</span></label
          >
          <Link
            doctype="Task"
            v-model="form.task"
            placeholder="Select Task"
            :show-description="true"
            :filters="taskFilters"
            :update-filters="true"
            class="overflow-hidden"
          >
            <template #item-label="{ option }">
              <div class="flex min-w-0 flex-1 flex-col gap-0.5">
                <span class="text-xs-bold leading-4">
                  {{ option.value }}
                </span>
                <span
                  v-if="getTaskSubject(option)"
                  class="break-words text-base leading-5"
                >
                  {{ getTaskSubject(option) }}
                </span>
              </div>
            </template>
          </Link>
        </div>
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5">Project </label>
          <Link
            doctype="Project"
            v-model="form.project"
            placeholder="Select Project"
            class="overflow-hidden"
          />
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4 mt-4" v-if="form.task">
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
          class="[&_button]:w-full"
          label="Status"
          v-model="form.status"
          :options="status"
          :required="true"
        />
        <FormControl
          type="select"
          class="[&_button]:w-full"
          label="Priority"
          v-model="form.priority"
          :options="priority"
          :required="true"
        />
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >Start Date & Time <span class="text-ink-red-5">*</span>
          </label>
          <DateTimePicker
            v-model="form.exp_start_date"
            placeholder="Select start date & time"
          />
        </div>
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >End Date & Time <span class="text-ink-red-5">*</span>
          </label>
          <DateTimePicker
            v-model="form.exp_end_date"
            placeholder="Select end date & time"
          />
        </div>
        <template v-if="isElevatorInstalled">
          <div>
            <label class="block text-xs text-ink-gray-5 mb-1.5">Elevator</label>
            <Link
              doctype="Elevator"
              v-model="form.elevator"
              placeholder="Select Elevator"
              class="overflow-hidden"
            />
          </div>
          <div>
            <label class="block text-xs text-ink-gray-5 mb-1.5">Elevator Address</label>
            <FormControl
              type="input"
              v-model="form.elevator_address"
              placeholder="Auto-filled from elevator"
              disabled
            />
          </div>
        </template>
        <div class="w-full col-span-2">
          <label class="block text-xs text-ink-gray-5 mb-1.5">
            Assign To <span class="text-ink-red-5">*</span>
          </label>
          <Autocomplete2
            :options="_users"
            v-model="form.users"
            :multiple="true"
            placeholder="Select Users"
          />
        </div>
        <div v-if="form.status === 'Completed'">
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >Completed On <span class="text-ink-red-5">*</span>
          </label>
          <DatePicker
            v-model="form.completed_on"
            :format="dateFormat"
          />
        </div>
        <div class="col-span-2">
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >Description
          </label>
          <TaskDescriptionEditor v-model="form.description" />
        </div>
      </div>
    </template>
    <template #actions="{ close }">
      <div class="flex space-x-3 justify-end">
        <Button
          v-if="form.task"
          label="Link to Task"
          variant="subtle"
          @click="goToBlank('/app/task/' + form.task)"
          icon-left="lucide-external-link"
        />
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
  FormControl,
  DateTimePicker,
  DatePicker,
  call,
  createResource,
} from 'frappe-ui'
import { onMounted, reactive, watch, computed, ref } from 'vue'
import { projects, priority, status } from '../data'
import { raiseToast, dayjs, goToBlank, dateFormat } from '../utils'
import Autocomplete2 from './Autocomplete2.vue'
import Link from './Link.vue'
import TaskDescriptionEditor from './TaskDescriptionEditor.vue'
const props = defineProps({
  users: Array,
  taskName: String,
  taskSubject: String,
  selectedUser: {
    type: Object || null,
    default: null,
  },
})
const emit = defineEmits(['update'])

const show = defineModel()

function getTaskSubject(option) {
  const subject =
    option.title !== option.value ? option.title : option.description
  return subject === option.value ? '' : subject
}

const isElevatorInstalled = window.is_elevator_installed === true

const form = reactive({
  task: null,
  project: null,
  subject: '',
  status: 'Open',
  priority: 'Medium',
  exp_start_date: '',
  exp_end_date: '',
  description: '',
  users: [],
  completed_by: null,
  completed_on: '',
  elevator: null,
  elevator_address: '',
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
    form.users = data.assigned_users || []

    // If selectedUser is provided (clicked "+" on user row), add them if not already assigned
    if (props.selectedUser) {
      const isAlreadyAssigned = form.users.some(
        (u) => u.value === props.selectedUser.value
      )
      if (!isAlreadyAssigned) {
        form.users.push({
          label: props.selectedUser.label,
          value: props.selectedUser.value,
        })
      }
    }

    form.subject = data.subject
    form.status = data.status
    form.description = data.description
    form.priority = data.priority

    // Set datetime fields directly
    form.exp_start_date = data.exp_start_date || ''
    form.exp_end_date = data.exp_end_date || ''

    // Default exp_end_date to today if empty
    if (!form.exp_end_date) {
      form.exp_end_date = dayjs().format('YYYY-MM-DD HH:mm:ss')
    }

    form.completed_on = data.completed_on
    form.project = data.project
    form.elevator = data.elevator || null
    form.elevator_address = data.elevator_address || ''
  },
})


const _users = computed(() => {
  const allUsers = props.users.map((user) => ({
    label: user.full_name,
    value: user.name,
  }))

  // Get the values of currently assigned users
  const assignedValues = new Set(form.users.map((u) => u.value))

  // Sort: assigned users first, then others (preserving original order within groups)
  return allUsers.sort((a, b) => {
    const aAssigned = assignedValues.has(a.value)
    const bAssigned = assignedValues.has(b.value)
    if (aAssigned && !bAssigned) return -1
    if (!aAssigned && bAssigned) return 1
    return 0
  })
})

onMounted(() => {
  if (props.taskName && props.taskSubject) {
    // Editing existing task - don't set defaults
    form.task = props.taskName
  } else {
    // Creating new task - set defaults
    // Default exp_end_date to today if not already set
    if (!form.exp_end_date) {
      form.exp_end_date = dayjs().format('YYYY-MM-DD HH:mm:ss')
    }
    // Default user from selectedUser prop if provided
    if (props.selectedUser && form.users.length === 0) {
      form.users.push({
        label: props.selectedUser.label,
        value: props.selectedUser.value,
      })
    }
  }
})

function validateForm() {
  if (
    form.users.length === 0 ||
    !form.subject ||
    !form.exp_start_date ||
    !form.exp_end_date ||
    !form.status ||
    !form.priority ||
    (form.status === 'Completed' && !form.completed_on) ||
    !form.task
  ) {
    raiseToast('error', 'Please fill all the required fields')
    return false
  }
  // Validate end datetime is after start datetime
  if (dayjs(form.exp_start_date).isAfter(dayjs(form.exp_end_date))) {
    raiseToast('error', 'End Date & Time should be after Start Date & Time')
    return false
  }
  if (dayjs(form.exp_start_date).isSame(dayjs(form.exp_end_date))) {
    raiseToast('error', 'End Date & Time must be after Start Date & Time')
    return false
  }
  return true
}

const submitTask = async (close) => {
  if (!validateForm()) return
  try {
    await updateTask(
      {
        name: form.task || null,
        project: form.project || null,
        status: form.status,
        priority: form.priority,
        exp_start_date: form.exp_start_date,
        exp_end_date: form.exp_end_date,
        users: form.users || [],
        description: form.description,
        completed_on: form.completed_on || null,
        elevator: form.elevator || null,
      },
      close,
    )
  } catch (e) {
    const err = e.messages[0] || 'Could not update task'
    console.log(e)
    raiseToast('error', err)
  }
}
async function updateTask(form, close) {
  await call('planner.api.tasks.update_task', {
    task_doc: form,
  })
  raiseToast('success', 'Task updated successfully')
  close()
  emit('update')
}

const taskFilters = ref({})

watch(
  () => form.project,
  (newProject) => {
    if (form.task) return
    if (newProject) {
      taskFilters.value = { project: newProject }
    } else {
      taskFilters.value = {}
    }
  },
)

watch(
  () => form.task,
  (newVal) => {
    if (!newVal) return
    _taskName.value = newVal
    task.fetch()
  },
)

watch(
  () => form.elevator,
  async (newVal) => {
    if (!newVal) {
      form.elevator_address = ''
      return
    }
    try {
      const result = await call('frappe.client.get_value', {
        doctype: 'Elevator',
        filters: newVal,
        fieldname: 'title',
      })
      form.elevator_address = result?.title || ''
    } catch {
      form.elevator_address = ''
    }
  },
)
</script>

<style lang="scss" scoped></style>
