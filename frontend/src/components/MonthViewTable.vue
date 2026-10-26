<template>
  <div
    ref="tableContainer"
    class="rounded-lg border w-full overflow-scroll table-container" style="max-height: calc(100vh - 250px)"
    :class="loading && 'animate-pulse pointer-events-none'"
  >
    <table
      ref="tableEl"
      class="border-separate border-spacing-0 table-fixed"
      :style="{ width: `${288 + daysOfMonth.length * 128}px` }"
    >
      <!-- first row -->
      <thead>
        <tr class="bg-white">
          <!-- User Search -->
          <th
            class="p-2 border-b border-r w-72 sticky top-0 left-0 z-20 bg-surface-white"
          >
            <Autocomplete
              :options="userSearchOptions"
              v-model="userSearch"
              placeholder="Search User"
              :multiple="true"
            />
          </th>

          <!-- Day/Date Row -->
          <th
            v-for="(day, idx) in daysOfMonth"
            :key="idx"
            :ref="(el) => (headerCells[idx] = el)"
            class="font-medium border-b w-32 sticky top-0 z-10 bg-white"
            :class="{
              'border-l': idx,
              'shadow-[inset_0_0_0_1.5px_#1e3a5f,0_0_6px_1px_rgba(30,58,95,0.25)]': day.date === dayjs().format('YYYY-MM-DD'),
            }"
          >
            {{ day.dayName }} {{ dayjs(day.date).format('DD') }}
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

          <!-- Day cells: a label line, then the user's task bars (drawn once, from the first cell) -->
          <td
            v-if="
              !userSearch?.length ||
              userSearch?.some((item) => item.value === user?.name)
            "
            v-for="(day, colIdx) in daysOfMonth"
            :key="colIdx"
            class="relative p-0 border-t align-top"
            :class="{
              'border-l': rowIdx + 1,
              'bg-gray-50': getHolidayForDay(user.name, day.date) || (dropCell.user === user.name && dropCell.date === day.date && !getLeaveForDay(user.name, day.date)),
              'bg-orange-50': getLeaveForDay(user.name, day.date),
            }"
            :style="{ height: `${rowHeight(user.name)}px` }"
            @mouseenter="
              () => {
                hoveredCell.user = user.name
                hoveredCell.date = day.date
              }
            "
            @mouseleave="
              () => {
                hoveredCell.user = ''
                hoveredCell.date = ''
              }
            "
            @mousemove="(e) => trackAddCell(user.name, colIdx, e)"
            @dragover.prevent
            @dragenter="
              () => {
                dropCell.user = user.name
                dropCell.date = day.date
              }
            "
            @drop="
              () => {
                if (!isHolidayOrLeave(user.name, day.date)) {
                  loading = true
                  swapShift.submit()
                }
              }
            "
          >
            <div
              class="flex items-center gap-1 px-1.5"
              :style="{ height: `${DAY_LABEL_HEIGHT}px` }"
            >
              <span
                v-if="cellLabel(user.name, day.date)"
                class="truncate text-[11px] leading-4"
                :class="cellLabel(user.name, day.date).cls"
                :title="cellLabel(user.name, day.date).title || cellLabel(user.name, day.date).text"
              >
                {{ cellLabel(user.name, day.date).text }}
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
              :edges="dayEdges"
              :day-kinds="dayKinds(user.name)"
              :top="DAY_LABEL_HEIGHT"
              :lane-height="LANE_HEIGHT"
              @open="openTask"
              @enter="(task, e) => onTaskMouseEnter(task, user.name, task.start_date, e)"
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
  collectUserTasks,
  layoutTaskBars,
  dayLabel,
  measureEdges,
  DAY_LABEL_HEIGHT,
  LANE_HEIGHT,
  ADD_BUTTON_HEIGHT,
  columnAt,
  coveredColumns,
} from '../utils/taskLanes'

const props = defineProps({
  firstOfMonth: {
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
const daysOfMonth = computed(() => {
  const daysOfMonth = []
  for (let i = 1; i <= props.firstOfMonth.daysInMonth(); i++) {
    const date = props.firstOfMonth.date(i)
    daysOfMonth.push({
      dayName: date.format('ddd'),
      date: date.format('YYYY-MM-DD'),
    })
  }
  return daysOfMonth
})

const hoveredCell = ref({
  user: '',
  user_display: '',
  date: '',
  task: '',
  subject: '',
  shift_status: '',
  priority: '',
  project: '',
  project_name: '',
  color: '',
})

const selectedTask = ref({
  task: '',
  subject: '',
  user: null,
})

const dropCell = ref({ user: '', date: '', task: '' })
const loading = ref(false)
const isHolidayOrLeave = (user, day) =>
  events.data?.[user]?.[day]?.holiday ||
  events.data?.[user]?.[day]?.leave

const events = createResource({
  url: 'planner.api.tasks.get_events',
  auto: true,
  makeParams() {
    return {
      month_start: props.firstOfMonth.format('YYYY-MM-DD'),
      month_end: props.firstOfMonth.endOf('month').format('YYYY-MM-DD'),
      //   employee_filters: props.employeeFilters,
      task_filters: props.taskFilters,
    }
  },
  onSuccess() {
    loading.value = false
  },
  onError(error) {
    raiseToast('error', error)
  },
  transform: (data) => {
    const mappedEvents = {}

    // Handle new response structure with separate tasks, holidays, leaves
    const tasks = data.tasks || data
    const holidays = data.holidays || {}
    const leaves = data.leaves || {}

    // Get all dates in the month
    const monthStart = props.firstOfMonth.startOf('month')
    const monthEnd = props.firstOfMonth.endOf('month')
    const daysInMonth = monthEnd.diff(monthStart, 'day') + 1

    // Process tasks
    for (const user in tasks) {
      if (!mappedEvents[user]) {
        mappedEvents[user] = {}
      }

      for (let d = 0; d < daysInMonth; d++) {
        const date = monthStart.add(d, 'day')
        const key = date.format('YYYY-MM-DD')

        // Add tasks for this user on this date
        for (const task of tasks[user]) {
          // Use 'day' granularity to compare dates only, ignoring time component
          if (
            dayjs(task.start_date).isSameOrBefore(date, 'day') &&
            (dayjs(task.end_date).isSameOrAfter(date, 'day') || !task.end_date)
          ) {
            if (!Array.isArray(mappedEvents[user][key])) {
              mappedEvents[user][key] = []
            }
            mappedEvents[user][key].push({
              name: task.name,
              subject: task.subject,
              project: task.project,
              project_name: task.project_name,
              priority: task.priority,
              status: task.status,
              color: task.color?.toLowerCase() || 'blue',
              start_date: task.start_date,
              end_date: task.end_date,
              completed_on: task.status === 'Completed' ? task.completed_on : null,
            })
          }
        }
      }
    }

    // Process holidays
    for (const user in holidays) {
      if (!mappedEvents[user]) {
        mappedEvents[user] = {}
      }
      for (let d = 0; d < daysInMonth; d++) {
        const date = monthStart.add(d, 'day')
        const key = date.format('YYYY-MM-DD')

        if (holidays[user][key]) {
          if (!mappedEvents[user][key]) {
            mappedEvents[user][key] = {
              tasks: [],
              holiday: holidays[user][key]
            }
          } else if (Array.isArray(mappedEvents[user][key])) {
            mappedEvents[user][key] = {
              tasks: mappedEvents[user][key],
              holiday: holidays[user][key]
            }
          } else {
            mappedEvents[user][key].holiday = holidays[user][key]
          }
        }
      }
    }

    // Process leaves
    for (const user in leaves) {
      if (!mappedEvents[user]) {
        mappedEvents[user] = {}
      }
      for (let d = 0; d < daysInMonth; d++) {
        const date = monthStart.add(d, 'day')
        const key = date.format('YYYY-MM-DD')

        if (leaves[user][key]) {
          if (!mappedEvents[user][key]) {
            mappedEvents[user][key] = {
              tasks: [],
              leave: leaves[user][key]
            }
          } else if (Array.isArray(mappedEvents[user][key])) {
            mappedEvents[user][key] = {
              tasks: mappedEvents[user][key],
              leave: leaves[user][key]
            }
          } else {
            mappedEvents[user][key].leave = leaves[user][key]
          }
        }
      }
    }

    return mappedEvents
  },
})

const hoverPosition = ref({ top: 0, left: 0 })
const tableContainer = ref(null)

function onTaskMouseEnter(task, userName, date, event) {
  hoveredCell.value.task = task.name
  hoveredCell.value.subject = task.subject
  hoveredCell.value.shift_status = task.status
  hoveredCell.value.priority = task.priority || ''
  hoveredCell.value.project = task.project || ''
  hoveredCell.value.project_name = task.project_name || ''
  hoveredCell.value.color = task.color || colors[task.color][50]
  hoveredCell.value.user = userName
  hoveredCell.value.user_display =
    props.users.find((u) => u.name === userName)?.full_name ||
    userName
  hoveredCell.value.date = date
  hoveredCell.value.dates = formatRange(task)

  const rect = event.currentTarget.getBoundingClientRect()
  hoverPosition.value = {
    x: rect.left + rect.width / 2 + window.scrollX,
    y: rect.top + window.scrollY,
  }
}

function formatRange(task) {
  const start = dayjs(task.start_date)
  const end = dayjs(task.end_date || task.start_date)
  const fmt = (d) => d.format(dateFormat.value)
  return start.isSame(end, 'day') ? fmt(start) : `${fmt(start)} → ${fmt(end)}`
}

function onTaskMouseLeave() {
  hoveredCell.value.task = ''
  hoveredCell.value.dates = ''
  hoveredCell.value.subject = ''
  hoveredCell.value.shift_status = ''
  hoveredCell.value.priority = ''
  hoveredCell.value.project = ''
  hoveredCell.value.color = ''
}

// one continuous bar per task, stacked into lanes per user
const userLayouts = computed(() => {
  const layouts = {}
  for (const user of props.users) {
    layouts[user.name] = layoutTaskBars(
      collectUserTasks(events.data?.[user.name]),
      daysOfMonth.value,
    )
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

const dayKinds = (userName) =>
  daysOfMonth.value.map((d) =>
    getLeaveForDay(userName, d.date)
      ? 'leave'
      : getHolidayForDay(userName, d.date)
        ? 'off'
        : null,
  )

const cellLabel = (userName, day) =>
  dayLabel(getHolidayForDay(userName, day), getLeaveForDay(userName, day))

function openTask(task) {
  selectedTask.value.task = task.name
  selectedTask.value.subject = task.subject
  showTaskAssignmentDialog.value = true
}

function openNewTask(user) {
  selectedTask.value.task = ''
  selectedTask.value.subject = ''
  selectedTask.value.user = {
    label: `${user.name}: ${user.full_name}`,
    value: user.name,
  }
  showTaskAssignmentDialog.value = true
}

// day column edges, measured from the header so bars line up at any width
const tableEl = ref(null)
const headerCells = [] // filled by the header :ref callbacks; not reactive on purpose
const dayEdges = ref([])
const remeasure = () => (dayEdges.value = measureEdges(headerCells))
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
watch(daysOfMonth, () => nextTick(remeasure))

const getUserTaskCount = (userName) => {
  const userEvents = events.data?.[userName]
  if (!userEvents) return 0

  // Use a Set to count unique tasks by their name
  const uniqueTaskNames = new Set()
  for (const dateKey in userEvents) {
    const dayData = userEvents[dateKey]
    // Handle new structure with tasks array
    if (dayData?.tasks && Array.isArray(dayData.tasks)) {
      dayData.tasks.forEach((task) => uniqueTaskNames.add(task.name))
    } else if (Array.isArray(dayData)) {
      // Handle old structure (plain array)
      dayData.forEach((task) => uniqueTaskNames.add(task.name))
    }
  }
  return uniqueTaskNames.size
}

const getLeaveForDay = (userName, day) => {
  const dayData = events.data?.[userName]?.[day]
  return dayData?.leave || null
}

const getHolidayForDay = (userName, day) => {
  const dayData = events.data?.[userName]?.[day]
  return dayData?.holiday || null
}

const getTasksForDay = (userName, day) => {
  const dayData = events.data?.[userName]?.[day]

  // Handle new structure with tasks/holiday/leave
  if (dayData?.tasks && Array.isArray(dayData.tasks)) {
    return dayData.tasks
  }

  // Handle old structure (plain array)
  if (Array.isArray(dayData)) {
    return dayData
  }

  return []
}

const mapEventsToDates = (data, mappedEvents, user) => {
  mappedEvents[user] = {}
  for (let d = 1; d <= props.firstOfMonth.daysInMonth(); d++) {
    const date = props.firstOfMonth.date(d)
    const key = date.format('YYYY-MM-DD')

    for (const event of Object.values(data[user])) {
      let result
      if ('holiday' in event) {
        result = handleHoliday(event, date)
        if (result) {
          mappedEvents[user][key] = result
          break
        }
      } else if ('leave' in event) {
        result = handleLeave(event, date)
        if (result) {
          mappedEvents[user][key] = result
          break
        }
      } else {
        handleShifts(event, date, mappedEvents, user, key)
      }
    }
  }
}

const handleShifts = (event, date, mappedEvents, user, key) => {
  // Use 'day' granularity to compare dates only, ignoring time component
  if (
    dayjs(event.start_date).isSameOrBefore(date, 'day') &&
    (dayjs(event.end_date).isSameOrAfter(date, 'day') || !event.end_date)
  ) {
    if (!Array.isArray(mappedEvents[user][key]))
      mappedEvents[user][key] = []
    mappedEvents[user][key].push({
      name: event.name,
      subject: event.subject,
      project: event.project,
      project_name: event.project_name,
      priority: event.priority,
      status: event.status,
      color: event.color?.toLowerCase() || 'blue',
      start_date: event.start_date,
      end_date: event.end_date,
      completed_on: event.status === 'Completed' ? event.completed_on : null,
    })
  }
}

const handleLeave = (event, date) => {
  if (
    dayjs(event.from_date).isSameOrBefore(date) &&
    dayjs(event.to_date).isSameOrAfter(date)
  )
    return {
      leave: event.leave,
      leave_type: event.leave_type,
    }
}

const handleHoliday = (event, date) => {
  if (date.isSame(event.holiday_date)) {
    return {
      holiday: event.holiday,
      description: event.description,
      weekly_off: event.weekly_off,
    }
  }
}

watch(
  () => [props.firstOfMonth, props.taskFilters],
  () => {
    loading.value = true
    events.fetch()
  },
  { deep: true },
)

defineExpose({
  events,
})
</script>

<style scoped>
.blocked-cell {
  @apply text-sm text-gray-500 text-center p-2;
}
</style>

<!-- .table-container {
  -ms-overflow-style: none; /* IE and Edge */
}

.table-container::-webkit-scrollbar {
  display: none;
} -->
