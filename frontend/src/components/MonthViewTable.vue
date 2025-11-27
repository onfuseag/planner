<template>
  <div
    ref="tableContainer"
    class="rounded-lg border max-h-[90%] max-w-[100%] overflow-scroll table-container"
    :class="loading && 'animate-pulse pointer-events-none'"
  >
    <table class="border-separate border-spacing-0">
      <!-- first row -->
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

          <!-- Day/Date Row -->
          <th
            v-for="(day, idx) in daysOfMonth"
            :key="idx"
            class="font-medium border-b min-w-32"
            :class="{ 'border-l': idx }"
          >
            {{ day.dayName }} {{ dayjs(day.date).format('DD') }}
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

          <!-- Tasks -->
          <td
            v-if="
              !userSearch?.length ||
              userSearch?.some((item) => item.value === user?.name)
            "
            v-for="(day, colIdx) in daysOfMonth"
            :key="colIdx"
            class="p-1.5 z-[1] border-t"
            :class="{
              'border-l': rowIdx + 1,
              'align-top': events.data?.[user.name]?.[day.date],
              'bg-yellow-50': getHolidayForDay(user.name, day.date),
              'bg-orange-50': getLeaveForDay(user.name, day.date),
              'bg-gray-50':
                dropCell.user === user.name &&
                dropCell.date === day.date &&
                !(getHolidayForDay(user.name, day.date) || getLeaveForDay(user.name, day.date)),
            }"
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
            <!-- Holiday -->
            <div
              v-if="getHolidayForDay(user.name, day.date)"
              class="text-xs px-2 py-1 bg-yellow-100 border border-yellow-300 rounded text-center mb-2"
            >
              <div class="font-semibold text-yellow-800">
                {{ getHolidayForDay(user.name, day.date).description || 'Holiday' }}
              </div>
              <div
                v-if="getHolidayForDay(user.name, day.date).weekly_off"
                class="text-yellow-700"
              >
                (Weekly Off)
              </div>
            </div>

            <!-- Leave -->
            <div
              v-if="getLeaveForDay(user.name, day.date)"
              class="text-xs px-2 py-1 bg-orange-100 border border-orange-300 rounded text-center mb-2"
            >
              <div class="font-semibold text-orange-800">
                On Leave
              </div>
              <div class="text-orange-700">
                {{ getLeaveForDay(user.name, day.date).leave_type }}
              </div>
            </div>

            <!-- Tasks -->
            <div
              class="flex flex-col space-y-1.5 translate-x-0 translate-y-0 max-w-40 min-w-36"
            >
              <div
                v-for="task in getTasksForDay(user.name, day.date)"
                @mouseenter="
                  onTaskMouseEnter(task, user.name, day.date, $event)
                "
                @mouseleave="onTaskMouseLeave()"
                class="rounded border-2 p-2 cursor-pointer space-y-1.5"
                :class="[
                  dropCell.user === user.name &&
                    dropCell.date === day.date &&
                    dropCell.task === task.name &&
                    'scale-105',
                  hoveredCell.user === user.name &&
                    hoveredCell.date === day.date &&
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
              >
                <div class="text-xs pointer-events-none truncate">
                  {{ task['subject'] }}
                </div>
                <!-- <div class="truncate pointer-events-none text-xs">
                  {{ task['project'] }}
                </div> -->
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

              <!-- Add Task -->
              <Button
                variant="outline"
                icon="plus"
                class="border-2 active:bg-white w-full"
                :class="
                  hoveredCell.user === user.name &&
                  hoveredCell.date === day.date &&
                  !dropCell.user
                    ? 'visible'
                    : 'invisible'
                "
                @click="
                  () => {
                    selectedTask.task = ''
                    selectedTask.subject = ''
                    selectedTask.user = {
                      label: `${user.name}: ${user.full_name}`,
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
    for (const user in data) {
      mapEventsToDates(data, mappedEvents, user)
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
  hoveredCell.value.color = ''
}

const getUserTaskCount = (userName) => {
  const userEvents = events.data?.[userName]
  if (!userEvents) return 0

  let count = 0
  for (const dateKey in userEvents) {
    const dayData = userEvents[dateKey]
    // Handle new structure with tasks array
    if (dayData?.tasks && Array.isArray(dayData.tasks)) {
      count += dayData.tasks.length
    } else if (Array.isArray(dayData)) {
      // Handle old structure (plain array)
      count += dayData.length
    }
  }
  return count
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
  if (
    dayjs(event.start_date).isSameOrBefore(date) &&
    (dayjs(event.end_date).isSameOrAfter(date) || !event.end_date)
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
      color: event.color.toLowerCase() || 'blue',
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
