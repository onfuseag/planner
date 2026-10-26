<template>
  <div
    ref="tableContainer"
    class="rounded-lg border w-full overflow-scroll table-container"
    style="max-height: calc(100vh - 250px)"
    :class="loading && 'animate-pulse pointer-events-none'"
  >
    <table
      ref="tableEl"
      class="border-separate border-spacing-0 table-fixed"
      :style="{ width: `${288 + hours.length * 128}px` }"
    >
      <!-- Header Row -->
      <thead>
        <tr class="bg-white">
          <!-- User Search -->
          <th
            class="p-2 border-b border-r min-w-72 max-w-72 w-72 sticky top-0 left-0 z-20 bg-surface-white"
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
            v-for="(hour, idx) in hours"
            :key="hour"
            :ref="(el) => (headerCells[idx] = el)"
            class="font-medium border-b w-32 sticky top-0 z-10 bg-white"
            :class="{ 'border-l': true }"
          >
            {{ hour }}:00
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(user, rowIdx) in users"
          :key="user.name"
          @mouseleave="addCell = { user: '', col: -1 }"
        >
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

          <!-- Hour cells: the day's label on the first one, then the user's task bars (drawn once, from the first cell) -->
          <td
            v-if="
              !userSearch?.length ||
              userSearch?.some((item) => item.value === user?.name)
            "
            v-for="(hour, colIdx) in hours"
            :key="hour"
            class="relative p-0 border-t border-l align-top"
            :class="{
              'bg-orange-50': getLeaveForDay(user.name),
              'bg-gray-50':
                !getLeaveForDay(user.name) &&
                (getHolidayForDay(user.name) || (dropCell.user === user.name && dropCell.hour === hour)),
            }"
            :style="{ height: `${rowHeight(user.name)}px` }"
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
            @mousemove="(e) => trackAddCell(user.name, colIdx, e)"
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
            <div
              class="flex items-center gap-1 px-1.5"
              :style="{ height: `${DAY_LABEL_HEIGHT}px` }"
            >
              <span
                v-if="colIdx === 0 && cellLabel(user.name)"
                class="truncate text-[11px] leading-4"
                :class="cellLabel(user.name).cls"
                :title="cellLabel(user.name).title || cellLabel(user.name).text"
              >
                {{ cellLabel(user.name).text }}
              </span>
            </div>

            <!-- Add Task: centred in an empty cell; under the bars (in the strip kept free of them) when the cell has tasks -->
            <button
              type="button"
              class="absolute left-1/2 z-[3] flex h-6 w-6 -translate-x-1/2 items-center justify-center rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300 hover:text-gray-900"
              :class="[
                addCell.user === user.name && addCell.col === colIdx ? 'visible' : 'invisible',
                cellHasTasks(user.name, colIdx) ? 'bottom-1' : 'top-1/2 -translate-y-1/2',
              ]"
              title="Add task"
              @click="openNewTask(user)"
            >
              <FeatherIcon name="plus" class="h-3.5 w-3.5" />
            </button>

            <TaskBarLayer
              v-if="colIdx === 0"
              :bars="userLayouts[user.name]?.bars || []"
              :edges="hourEdges"
              :day-kinds="dayKinds(user.name)"
              :top="DAY_LABEL_HEIGHT"
              :lane-height="LANE_HEIGHT"
              :subtitle="barSubtitle"
              @open="openTask"
              @enter="(task, e) => onTaskMouseEnter(task, user.name, hours[0], e)"
              @leave="onTaskMouseLeave"
            />
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
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import colors from 'tailwindcss/colors'
import { Avatar, Autocomplete, createResource, FeatherIcon } from 'frappe-ui'
import { dateFormat, dayjs, raiseToast } from '../utils'
import TaskAssignmentDialog from '../components/TaskAssignmentDialog.vue'
import TaskHoverPopover from '../components/TaskHoverPopover.vue'
import TaskBarLayer from '../components/TaskBarLayer.vue'
import {
  layoutHourBars,
  dayLabel,
  measureEdges,
  DAY_LABEL_HEIGHT,
  LANE_HEIGHT,
  ADD_BUTTON_HEIGHT,
  columnAt,
  coveredColumns,
} from '../utils/taskLanes'

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
        // Use 'day' granularity to compare dates only, ignoring time component
        // Use isSameOrBefore/isSameOrAfter pattern (same as Weekly/Monthly views)
        if (
          dayjs(task.start_date).isSameOrBefore(dateString, 'day') &&
          (dayjs(task.end_date).isSameOrAfter(dateString, 'day') || !task.end_date)
        ) {
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
  hoveredCell.value.project_name = task.project_name
  hoveredCell.value.dates = taskTimeRange(task)
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
  hoveredCell.value.project_name = ''
  hoveredCell.value.dates = ''
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

  // Use 'day' granularity to compare dates only, ignoring time component
  // Use isSameOrBefore/isSameOrAfter pattern (same as Weekly/Monthly views)
  if (
    startDate.isSameOrBefore(date, 'day') &&
    (endDate.isSameOrAfter(date, 'day') || !endDate.isValid())
  ) {
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

const tasksForDay = (userName) => {
  const dayData = events.data?.[userName]?.[props.selectedDay.format('YYYY-MM-DD')]
  return Array.isArray(dayData) ? dayData : dayData?.tasks || []
}

// one continuous bar per task across the hours it covers, stacked into lanes per user
const userLayouts = computed(() => {
  const layouts = {}
  if (!props.selectedDay) return layouts
  for (const user of props.users) {
    layouts[user.name] = layoutHourBars(tasksForDay(user.name), props.selectedDay, hours.length)
  }
  return layouts
})

const busyColumns = computed(() => {
  const busy = {}
  for (const [user, layout] of Object.entries(userLayouts.value)) busy[user] = coveredColumns(layout.bars)
  return busy
})
const cellHasTasks = (userName, colIdx) => !!busyColumns.value[userName]?.has(colIdx)

const rowHeight = (userName) =>
  DAY_LABEL_HEIGHT +
  Math.max(userLayouts.value[userName]?.laneCount || 0, 1) * LANE_HEIGHT +
  ADD_BUTTON_HEIGHT

// a holiday or leave covers the whole day, so every hour of it is marked
const dayKinds = (userName) => {
  const kind = getLeaveForDay(userName) ? 'leave' : getHolidayForDay(userName) ? 'off' : null
  return hours.map(() => kind)
}

const cellLabel = (userName) =>
  dayLabel(getHolidayForDay(userName), getLeaveForDay(userName))

const isAllDay = (start, end) =>
  start.hour() === 0 && start.minute() === 0 && end.hour() === 0 && end.minute() === 0

// time first: in a day view the hours matter more than the project
function taskTimeRange(task) {
  const start = dayjs(task.start_date)
  const end = dayjs(task.end_date || task.start_date)
  if (isAllDay(start, end)) {
    return start.isSame(end, 'day') ? 'All day' : `${start.format('D MMM')} → ${end.format('D MMM')}`
  }
  if (start.isSame(end, 'day')) return `${start.format('HH:mm')}–${end.format('HH:mm')}`
  return `${start.format('D MMM HH:mm')} → ${end.format('D MMM HH:mm')}`
}

const barSubtitle = (task) =>
  [taskTimeRange(task), task.project_name, task.status].filter(Boolean).join(' · ')

function openTask(task) {
  selectedTask.value.task = task.name
  selectedTask.value.subject = task.subject
  showTaskAssignmentDialog.value = true
}

function openNewTask(user) {
  selectedTask.value.task = ''
  selectedTask.value.subject = ''
  selectedTask.value.user = {
    label: user.full_name,
    value: user.name,
  }
  showTaskAssignmentDialog.value = true
}

// hour column edges, measured from the header so bars line up at any width
const tableEl = ref(null)
const headerCells = [] // filled by the header :ref callbacks; not reactive on purpose
const hourEdges = ref([])
const remeasure = () => (hourEdges.value = measureEdges(headerCells))
// which cell shows the add-task button: the one under the pointer, also when the
// pointer is over a bar (bars live inside the row's first cell)
const addCell = ref({ user: '', col: -1 })
function trackAddCell(userName, colIdx, e) {
  const col = e.target.closest?.('.task-bar') ? columnAt(headerCells, e.clientX) : colIdx
  if (addCell.value.user !== userName || addCell.value.col !== col) {
    addCell.value = { user: userName, col }
  }
}
let resizeObserver
onMounted(() => {
  remeasure()
  resizeObserver = new ResizeObserver(remeasure)
  if (tableEl.value) resizeObserver.observe(tableEl.value)
})
onBeforeUnmount(() => resizeObserver?.disconnect())
watch(
  () => props.selectedDay?.format('YYYY-MM-DD'),
  () => nextTick(remeasure),
)

const getUserTaskCount = (userName) => {
  const dateString = props.selectedDay.format('YYYY-MM-DD')
  const dayData = events.data?.[userName]?.[dateString]

  if (!dayData) return 0

  // Use a Set to count unique tasks by their name
  const uniqueTaskNames = new Set()

  // Handle new structure with tasks/holiday/leave
  if (dayData.tasks && Array.isArray(dayData.tasks)) {
    dayData.tasks.forEach((task) => uniqueTaskNames.add(task.name))
  } else if (Array.isArray(dayData)) {
    // Handle old structure (plain array)
    dayData.forEach((task) => uniqueTaskNames.add(task.name))
  }

  return uniqueTaskNames.size
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
