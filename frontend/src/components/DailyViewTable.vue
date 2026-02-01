<template>
  <div
    ref="tableContainer"
    class="rounded-lg border max-h-[90%] max-w-[100%] overflow-scroll table-container"
    :class="loading && 'animate-pulse pointer-events-none'"
  >
    <table class="border-separate border-spacing-0">
      <!-- Header Row -->
      <thead>
        <tr class="sticky top-0 bg-white z-10">
          <!-- User Search -->
          <th
            class="p-2 border-b border-r min-w-72 max-w-72 sticky left-0 bg-surface-white"
          >
            <Autocomplete
              :options="userSearchOptions"
              v-model="userSearch"
              placeholder="Search User"
              :multiple="true"
            />
          </th>

          <!-- Hour Columns -->
          <th
            v-for="hour in hours"
            :key="hour"
            class="font-medium border-b min-w-32"
            :class="{ 'border-l': true }"
          >
            {{ hour }}:00
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(user, rowIdx) in users" :key="user.name">
          <!-- Users List -->
          <td
            v-if="
              !userSearch?.length ||
              userSearch?.some((item) => item.value === user?.name)
            "
            class="px-2 py-7 z-[5] border-r min-w-72 max-w-72 sticky left-0 bg-surface-white"
            :class="{ 'border-t': rowIdx }"
          >
            <div class="flex items-center">
              <Avatar
                :label="user.full_name"
                :image="user.user_image"
                size="2xl"
              />
              <div class="flex flex-col ml-2 my-0.5 truncate">
                <div class="truncate text-base font-medium">
                  {{ user.full_name }}
                </div>
                <div class="text-xs text-gray-500 font-normal">
                  Assigned Tasks: {{ getUserTaskCount(user.name) }}
                </div>
              </div>
            </div>
          </td>

          <!-- Task Cells by Hour -->
          <td
            v-if="
              !userSearch?.length ||
              userSearch?.some((item) => item.value === user?.name)
            "
            v-for="hour in hours"
            :key="hour"
            class="p-1.5 z-[1] border-t border-l align-top"
            :class="{
              'bg-gray-50':
                (dropCell.user === user.name && dropCell.hour === hour) || (hour === '00' && getHolidayForDay(user.name)),
              'bg-orange-50': hour === '00' && getLeaveForDay(user.name),
            }"
            @mouseenter="
              () => {
                hoveredCell.user = user.name
                hoveredCell.hour = hour
              }
            "
            @mouseleave="
              () => {
                hoveredCell.user = ''
                hoveredCell.hour = null
              }
            "
            @dragover.prevent
            @dragenter="
              () => {
                dropCell.user = user.name
                dropCell.hour = hour
              }
            "
            @drop="
              () => {
                loading = true
                swapShift.submit()
              }
            "
          >
            <!-- Holiday/Leave Indicator (only in first hour column) -->
            <div v-if="hour === '00'" class="mb-2">
              <div
                v-if="getHolidayForDay(user.name)"
                class="text-xs px-2 py-1 bg-gray-100 border border-gray-300 rounded"
              >
                <div class="font-semibold text-gray-800">
                  Holiday: {{ getHolidayForDay(user.name).description || 'Holiday' }}
                </div>
                <div v-if="getHolidayForDay(user.name).weekly_off" class="text-gray-700">
                  (Weekly Off)
                </div>
              </div>
              <div
                v-else-if="getLeaveForDay(user.name)"
                class="text-xs px-2 py-1 bg-orange-100 border border-orange-300 rounded"
              >
                <div class="font-semibold text-orange-800">
                  On Leave: {{ getLeaveForDay(user.name).leave_type }}
                </div>
              </div>
            </div>

            <!-- Tasks -->
            <div
              class="flex flex-col space-y-1.5 translate-x-0 translate-y-0 max-w-40 min-w-36"
            >
              <div
                v-for="task in getTasksForHour(user.name, hour)"
                :key="task.name"
                @mouseenter="
                  onTaskMouseEnter(task, user.name, hour, $event)
                "
                @mouseleave="onTaskMouseLeave()"
                class="rounded border-2 p-2 cursor-pointer space-y-1.5"
                :class="[
                  dropCell.user === user.name &&
                    dropCell.hour === hour &&
                    dropCell.task === task.name &&
                    'scale-105',
                  hoveredCell.user === user.name &&
                    hoveredCell.hour === hour &&
                    hoveredCell.task === task.name &&
                    dropCell.user &&
                    'opacity-0',
                ]"
                :style="{
                  backgroundColor: task.color || colors[task.color][50],
                }"
                @click="
                  () => {
                    selectedTask.task = task.name
                    selectedTask.subject = task.subject
                    showTaskAssignmentDialog = true
                  }
                "
                draggable="true"
                @dragstart="
                  () => {
                    hoveredCell.user = user.name
                    hoveredCell.hour = hour
                    hoveredCell.task = task.name
                  }
                "
              >
                <div class="text-xs pointer-events-none truncate">
                  {{ task['subject'] }}
                </div>
                <div class="truncate pointer-events-none text-xs font-bold">
                  {{ task['project_name'] ?? '' }}
                </div>
                <div
                  class="text-xs text-gray-500 pointer-events-none space-y-1.5"
                >
                  <div class="flex items-center space-x-1">
                    <span>
                      {{ task['status'] }}
                    </span>
                  </div>
                  <div
                    class="flex items-center space-x-1 text-xs"
                    v-if="task.start_time && task.end_time"
                  >
                    <span>
                      {{ task.start_time }} - {{ task.end_time }}
                    </span>
                  </div>
                  <div
                    class="flex items-center space-x-1 text-xs"
                    v-if="task.status === 'Completed'"
                  >
                    <FeatherIcon
                      name="check"
                      class="stroke-gray-600"
                      :style="{
                        height: '0.82rem',
                        width: '0.82rem',
                      }"
                    />
                    <span>
                      {{ dayjs(task['completed_on']).format(dateFormat) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Add Task Button -->
              <Button
                variant="outline"
                icon="plus"
                class="border-2 active:bg-white w-full"
                :class="
                  hoveredCell.user === user.name &&
                  hoveredCell.hour === hour &&
                  !dropCell.user
                    ? 'visible'
                    : 'invisible'
                "
                @click="
                  () => {
                    selectedTask.task = ''
                    selectedTask.subject = ''
                    selectedTask.user = {
                      label: user.full_name,
                      value: user.name,
                    }
                    showTaskAssignmentDialog = true
                  }
                "
              />
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <TaskAssignmentDialog
    v-if="showTaskAssignmentDialog"
    v-model="showTaskAssignmentDialog"
    :users="props.users"
    :task-name="selectedTask.task"
    :task-subject="selectedTask.subject"
    :selected-user="selectedTask.user"
    @update="() => events.reload()"
  />
  <TaskHoverPopover
    v-if="hoveredCell.task"
    :data="hoveredCell"
    :position="hoverPosition"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import colors from 'tailwindcss/colors'
import { Avatar, Autocomplete, createResource, FeatherIcon } from 'frappe-ui'
import { dateFormat, dayjs, raiseToast } from '../utils'
import TaskAssignmentDialog from '../components/TaskAssignmentDialog.vue'
import TaskHoverPopover from '../components/TaskHoverPopover.vue'

const props = defineProps({
  selectedDay: {
    required: true,
  },
  users: {
    required: true,
  },
  taskFilters: {
    required: true,
  },
})

const showTaskAssignmentDialog = ref(false)

const userSearch = ref()
const userSearchOptions = computed(() => {
  return props.users.map((user) => ({
    value: user.name,
    label: `${user.name}: ${user.full_name}`,
  }))
})

// Generate hours array (00 to 23)
const hours = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, '0'))

const hoveredCell = ref({
  user: '',
  user_display: '',
  hour: null,
  task: '',
  subject: '',
  shift_status: '',
  priority: '',
  project: '',
})

const selectedTask = ref({
  task: null,
  subject: '',
  user: null,
})

const dropCell = ref({ user: '', hour: null, task: '' })

const loading = ref(false)

const tableContainer = ref(null)

const hoverPosition = ref({ x: 0, y: 0 })

// RESOURCES
const events = createResource({
  url: 'planner.api.tasks.get_events',
  auto: true,
  makeParams() {
    return {
      month_start: props.selectedDay?.format('YYYY-MM-DD'),
      month_end: props.selectedDay?.format('YYYY-MM-DD'),
      task_filters: props.taskFilters,
    }
  },
  onSuccess() {
    loading.value = false
  },
  onError(error) {
    console.log(error)
    raiseToast('error', error)
    loading.value = false
  },
  transform(data) {
    const mappedEvents = {}

    // Handle new response structure with separate tasks, holidays, leaves
    const tasks = data.tasks || data
    const holidays = data.holidays || {}
    const leaves = data.leaves || {}

    // Process tasks
    for (const user in tasks) {
      if (!mappedEvents[user]) {
        mappedEvents[user] = {}
      }

      const dateString = props.selectedDay.format('YYYY-MM-DD')

      // Add tasks for this user on this date
      for (const task of tasks[user]) {
        const startDate = dayjs(task.start_date)
        const endDate = dayjs(task.end_date)
        const targetDate = dayjs(dateString)

        if (targetDate.isBetween(startDate, endDate, null, '[]')) {
          if (!mappedEvents[user][dateString]) {
            mappedEvents[user][dateString] = []
          }
          if (Array.isArray(mappedEvents[user][dateString])) {
            mappedEvents[user][dateString].push(task)
          }
        }
      }
    }

    // Process holidays
    for (const user in holidays) {
      if (!mappedEvents[user]) {
        mappedEvents[user] = {}
      }
      const dateString = props.selectedDay.format('YYYY-MM-DD')
      if (holidays[user][dateString]) {
        if (!mappedEvents[user][dateString]) {
          mappedEvents[user][dateString] = {
            tasks: [],
            holiday: holidays[user][dateString]
          }
        } else if (Array.isArray(mappedEvents[user][dateString])) {
          mappedEvents[user][dateString] = {
            tasks: mappedEvents[user][dateString],
            holiday: holidays[user][dateString]
          }
        } else {
          mappedEvents[user][dateString].holiday = holidays[user][dateString]
        }
      }
    }

    // Process leaves
    for (const user in leaves) {
      if (!mappedEvents[user]) {
        mappedEvents[user] = {}
      }
      const dateString = props.selectedDay.format('YYYY-MM-DD')
      if (leaves[user][dateString]) {
        if (!mappedEvents[user][dateString]) {
          mappedEvents[user][dateString] = {
            tasks: [],
            leave: leaves[user][dateString]
          }
        } else if (Array.isArray(mappedEvents[user][dateString])) {
          mappedEvents[user][dateString] = {
            tasks: mappedEvents[user][dateString],
            leave: leaves[user][dateString]
          }
        } else {
          mappedEvents[user][dateString].leave = leaves[user][dateString]
        }
      }
    }

    return mappedEvents
  },
})

const swapShift = createResource({
  url: 'planner.api.tasks.update_task',
  onSuccess() {
    events.reload()
    loading.value = false
    hoveredCell.value = {
      user: '',
      user_display: '',
      hour: null,
      task: '',
      subject: '',
      shift_status: '',
      priority: '',
      project: '',
    }
    dropCell.value = { user: '', hour: null, task: '' }
  },
  onError(error) {
    raiseToast('error', error)
    loading.value = false
  },
})

function onTaskMouseEnter(task, userName, hour, event) {
  hoveredCell.value.task = task.name
  hoveredCell.value.subject = task.subject
  hoveredCell.value.shift_status = task.status
  hoveredCell.value.priority = task.priority
  hoveredCell.value.project = task.project_name
  hoveredCell.value.hour = hour
  hoveredCell.value.user = userName
  hoveredCell.value.user_display =
    props.users.find((u) => u.name === userName)?.full_name ||
    userName

  const rect = event.currentTarget.getBoundingClientRect()
  hoverPosition.value = {
    x: rect.left + rect.width / 2 + window.scrollX,
    y: rect.top + window.scrollY,
  }
}

function onTaskMouseLeave() {
  hoveredCell.value.task = ''
  hoveredCell.value.subject = ''
  hoveredCell.value.shift_status = ''
  hoveredCell.value.priority = ''
  hoveredCell.value.project = ''
}

watch(
  () => props.selectedDay?.format('YYYY-MM-DD'),
  () => {
    loading.value = true
    events.fetch()
  },
)

watch(
  () => props.taskFilters,
  () => {
    loading.value = true
    events.fetch()
  },
  { deep: true },
)

const mapEventsToDates = (data, mappedEvents, user) => {
  const dateString = props.selectedDay.format('YYYY-MM-DD')

  for (const event of data[user]) {
    if (!mappedEvents[user]) {
      mappedEvents[user] = {}
    }

    if (event.leave) {
      handleShifts(event, dateString, mappedEvents, user, 'leave')
    } else if (event.holiday) {
      handleShifts(event, dateString, mappedEvents, user, 'holiday')
    } else {
      handleShifts(event, dateString, mappedEvents, user)
    }
  }
}

const handleShifts = (event, date, mappedEvents, user, key) => {
  const startDate = dayjs(event.from_date || event.holiday_date || event.start_date)
  const endDate = dayjs(event.to_date || event.holiday_date || event.end_date)
  const targetDate = dayjs(date)

  if (targetDate.isBetween(startDate, endDate, null, '[]')) {
    if (!mappedEvents[user][date]) {
      if (key === 'leave') {
        mappedEvents[user][date] = { leave: event.leave_type }
      } else if (key === 'holiday') {
        mappedEvents[user][date] = {
          holiday: event.holiday,
          description: event.description,
          weekly_off: event.weekly_off,
        }
      } else {
        mappedEvents[user][date] = []
      }
    }

    if (!key && Array.isArray(mappedEvents[user][date])) {
      mappedEvents[user][date].push(event)
    }
  }
}

const getUserTaskCount = (userName) => {
  const dateString = props.selectedDay.format('YYYY-MM-DD')
  const dayData = events.data?.[userName]?.[dateString]

  if (!dayData) return 0

  // Handle new structure with tasks/holiday/leave
  if (dayData.tasks && Array.isArray(dayData.tasks)) {
    return dayData.tasks.length
  }

  // Handle old structure (plain array)
  if (Array.isArray(dayData)) {
    return dayData.length
  }

  return 0
}

const getLeaveForDay = (userName) => {
  const dateString = props.selectedDay.format('YYYY-MM-DD')
  const dayData = events.data?.[userName]?.[dateString]

  if (dayData?.leave) {
    return dayData.leave
  }
  return null
}

const getHolidayForDay = (userName) => {
  const dateString = props.selectedDay.format('YYYY-MM-DD')
  const dayData = events.data?.[userName]?.[dateString]

  if (dayData?.holiday) {
    return dayData.holiday
  }
  return null
}

const getTasksForHour = (userName, hour) => {
  const dateString = props.selectedDay.format('YYYY-MM-DD')
  const dayData = events.data?.[userName]?.[dateString]

  let userTasks = []

  // Handle new structure with tasks/holiday/leave
  if (dayData?.tasks && Array.isArray(dayData.tasks)) {
    userTasks = dayData.tasks
  } else if (Array.isArray(dayData)) {
    // Handle old structure (plain array)
    userTasks = dayData
  }

  if (!userTasks.length) {
    return []
  }

  return userTasks.filter((task) => {
    if (!task.start_time || !task.end_time) {
      // If no time specified, show in first hour (00)
      return hour === '00'
    }

    const currentDate = props.selectedDay.format('YYYY-MM-DD')
    const isStartDay = task.start_date === currentDate
    const isEndDay = task.end_date === currentDate
    const isMultiDay = task.start_date !== task.end_date

    // For multi-day tasks on intermediate days, show in first hour (all day)
    if (isMultiDay && !isStartDay && !isEndDay) {
      return hour === '00'
    }

    const [startHour, startMinute] = task.start_time.split(':').map(Number)
    const [endHour, endMinute] = task.end_time.split(':').map(Number)
    const currentHour = parseInt(hour)

    // For multi-day tasks: only apply time constraints on start/end days
    if (isMultiDay) {
      if (isStartDay) {
        // On start day: show from start_time until end of day
        return startHour <= currentHour
      }
      if (isEndDay) {
        // On end day: show from start of day until end_time
        return endHour > currentHour || (endHour === currentHour && endMinute > 0)
      }
    }

    // Single-day task or fallback: use both start and end time
    const taskStartsBeforeOrDuringThisHour = startHour <= currentHour
    const taskEndsAfterThisHourStarts =
      endHour > currentHour || (endHour === currentHour && endMinute > 0)

    return taskStartsBeforeOrDuringThisHour && taskEndsAfterThisHourStarts
  })
}

defineExpose({ events })
</script>

<style lang="scss" scoped>
.table-container {
  &::-webkit-scrollbar {
    width: 5px;
    height: 5px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: #d1d5db;
    border-radius: 2.5px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: #9ca3af;
  }
}
</style>
