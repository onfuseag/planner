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
          <Link
            doctype="Task"
            v-model="form.task"
            placeholder="Select Task"
            :show-description="true"
            :filters="taskFilters"
            :update-filters="true"
            class="overflow-hidden"
          />
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
          <DatePicker
            v-model="form.start_date"
            :formatter="(date) => dayjs(date).format(dateFormat).split('T')[0]"
          />
        </div>
        <div>
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >End Date <span class="text-ink-red-3">*</span>
          </label>
          <DatePicker
            v-model="form.end_date"
            :formatter="(date) => dayjs(date).format(dateFormat).split('T')[0]"
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
        <div class="w-full col-span-2">
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
        <div v-if="form.status === 'Completed'">
          <label class="block text-xs text-ink-gray-5 mb-1.5"
            >Completed On <span class="text-ink-red-3">*</span>
          </label>
          <DatePicker
            v-model="form.completed_on"
            :formatter="(date) => dayjs(date).format(dateFormat).split('T')[0]"
          />
        </div>
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
    <template #actions="{ close }">
      <div class="flex space-x-3 justify-end">
        <Button
          v-if="form.task"
          label="Link to Task"
          variant="subtle"
          @click="goToBlank('/app/task/' + form.task)"
          iconLeft="external-link"
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
  DatePicker,
  TextEditor,
  call,
  createResource,
} from 'frappe-ui'
import { onMounted, reactive, watch, computed, ref } from 'vue'
import { projects, priority, status } from '../data'
import { raiseToast, dayjs, goToBlank, dateFormat } from '../utils'
import Autocomplete2 from './Autocomplete2.vue'
import Link from './Link.vue'
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

const form = reactive({
  task: null,
  project: null,
  subject: '',
  status: 'Open',
  priority: 'Medium',
  start_date: '',
  end_date: '',
  start_time: '',
  end_time: '',
  description: '',
  users: [],
  completed_by: null,
  completed_on: '',
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
    form.subject = data.subject
    form.status = data.status
    form.description = data.description
    form.priority = data.priority
    // exp_start_date and exp_end_date are DateTime fields - extract date and time separately
    const startDateTime = dayjs(data.exp_start_date)
    const endDateTime = dayjs(data.exp_end_date)
    form.start_date = startDateTime.format('YYYY-MM-DD')
    form.end_date = endDateTime.format('YYYY-MM-DD')
    // Extract time, but only if it's not midnight (00:00)
    const startTime = startDateTime.format('HH:mm')
    const endTime = endDateTime.format('HH:mm')
    form.start_time = startTime !== '00:00' ? startTime : ''
    form.end_time = endTime !== '00:00' ? endTime : ''
    form.completed_on = data.completed_on
    form.project = data.project
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
    form.task = props.taskName
  }
  // if (props.selectedUser) {
  //   form.users.push({
  //     label: props.selectedUser.label,
  //     value: props.selectedUser.value,
  //   })
  // }
})

function validateForm() {
  if (
    form.users.length === 0 ||
    !form.subject ||
    !form.start_date ||
    !form.end_date ||
    !form.status ||
    !form.priority ||
    (form.status === 'Completed' && !form.completed_on) ||
    !form.task
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
    // Combine date and time into DateTime values for exp_start_date and exp_end_date
    let startDateTime = form.start_date
    let endDateTime = form.end_date
    if (form.start_time) {
      startDateTime = `${form.start_date} ${form.start_time}:00`
    }
    if (form.end_time) {
      endDateTime = `${form.end_date} ${form.end_time}:00`
    }

    await updateTask(
      {
        name: form.task || null,
        project: form.project || null,
        status: form.status,
        priority: form.priority,
        exp_start_date: startDateTime,
        exp_end_date: endDateTime,
        users: form.users || [],
        description: form.description,
        completed_on: form.completed_on || null,
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
</script>

<style lang="scss" scoped></style>
