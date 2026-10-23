<template>
  <Dialog :options="{ title: dialog.title, size: '3xl' }" v-model="show">
    <template #body-content>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5">
            Assign To <span class="text-ink-red-3">*</span>
          </label>
          <Autocomplete2
            :options="_users"
            v-model="form.users"
            :multiple="true"
            placeholder="Select Users"
          />
        </div>
        <!-- Project -->
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5">Project </label>
          <Link
            doctype="Project"
            v-model="form.project"
            placeholder="Select Project"
            class="overflow-hidden"
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
          <DatePicker
            v-model="form.start_date"
            :format="dateFormat"
          />
        </div>
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >End Date <span class="text-ink-red-3">*</span>
          </label>
          <DatePicker
            v-model="form.end_date"
            :format="dateFormat"
          />
        </div>
        <FormControl
          type="time"
          label="Start Time"
          v-model="form.start_time"
          placeholder="09:00"
        />
        <FormControl
          type="time"
          label="End Time"
          v-model="form.end_time"
          placeholder="17:00"
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
        <!-- Description Text Editor here -->
        <div class="col-span-2">
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >Description
          </label>
          <TextEditor
            class="col-span-2 rounded py-1.5 px-2 border border-[--surface-gray-2] bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:bg-surface-gray-3 focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors w-full block text-xs min-h-[80px]"
            type="textarea"
            placeholder="This task is about..."
            :content="form.description"
            @change="(val) => (form.description = val)"
            :bubble-menu="true"
            editor-class="text-sm"
          />
        </div>
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
import { computed, onMounted, watch } from 'vue'
import {
  Dialog,
  FormControl,
  DatePicker,
  createResource,
  TextEditor,
  call,
} from 'frappe-ui'
import { reactive } from 'vue'
import { dateFormat, dayjs, raiseToast } from '../utils'
import { projects, priority, status } from '../data'
import Link from './Link.vue'
import Autocomplete2 from './Autocomplete2.vue'

const isElevatorInstalled = window.is_elevator_installed === true
const props = defineProps({
  users: Array,
  taskName: String,
})

const emit = defineEmits(['create'])

const show = defineModel()

const form = reactive({
  users: null,
  subject: '',
  status: 'Open',
  project: '',
  priority: 'Low',
  start_date: '',
  end_date: '',
  start_time: '',
  end_time: '',
  description: '',
  elevator: null,
  elevator_address: '',
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
    !form.users ||
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
  // Validate that end time is not before start time when on the same day
  if (
    dayjs(form.start_date).isSame(dayjs(form.end_date), 'day') &&
    form.start_time &&
    form.end_time
  ) {
    const startDateTime = dayjs(`${form.start_date} ${form.start_time}`)
    const endDateTime = dayjs(`${form.end_date} ${form.end_time}`)
    if (endDateTime.isBefore(startDateTime) || endDateTime.isSame(startDateTime)) {
      raiseToast('error', 'End Time must be after Start Time on the same day')
      return false
    }
  }
  return true
}

function resetState() {
  form.users = ''
  form.subject = ''
  form.status = ''
  form.project = ''
  form.priority = ''
  form.start_date = ''
  form.end_date = ''
  form.start_time = ''
  form.end_time = ''
  form.description = ''
  form.elevator = null
  form.elevator_address = ''
}

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

const newTask = createResource({
  url: 'planner.api.tasks.create_task',
  makeParams() {
    // Combine date and time into DateTime values for start_date and end_date
    let startDateTime = form.start_date
    let endDateTime = form.end_date
    if (form.start_time) {
      startDateTime = `${form.start_date} ${form.start_time}:00`
    }
    if (form.end_time) {
      endDateTime = `${form.end_date} ${form.end_time}:00`
    }

    return {
      task_doc: {
        ...form,
        start_date: startDateTime,
        end_date: endDateTime,
      },
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
const _users = computed(() => {
  return props.users.map((user) => ({
    label: user.full_name,
    value: user.name,
  }))
})

onMounted(() => {
  projects.fetch()
})
</script>
