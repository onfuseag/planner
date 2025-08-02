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
          <!-- Employee Search -->
          <th
            class="p-2 border-b border-r min-w-72 max-w-72 sticky left-0 bg-surface-white"
          >
            <Autocomplete
              :options="employeeSearchOptions"
              v-model="employeeSearch"
              placeholder="Search Employee"
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
        <tr v-for="(employee, rowIdx) in employees" :key="employee.name">
          <!-- Employees List -->
          <td
            v-if="
              !employeeSearch?.length ||
              employeeSearch?.some((item) => item.value === employee?.name)
            "
            class="px-2 py-7 z-[5] border-r min-w-72 max-w-72 sticky left-0 bg-surface-white"
            :class="{ 'border-t': rowIdx }"
          >
            <div class="flex" :class="!employee.designation && 'items-center'">
              <Avatar
                :label="employee.employee_name"
                :image="employee.image"
                size="2xl"
              />
              <div class="flex flex-col ml-2 my-0.5 truncate">
                <div class="truncate text-base font-medium">
                  {{ employee.employee_name }}
                </div>
                <div class="mt-auto text-xs text-gray-500 truncate">
                  {{ employee.designation }}
                </div>
              </div>
            </div>
          </td>

          <!-- Tasks -->
          <td
            v-if="
              !employeeSearch?.length ||
              employeeSearch?.some((item) => item.value === employee?.name)
            "
            v-for="(day, colIdx) in daysOfMonth"
            :key="colIdx"
            class="p-1.5 z-[1] border-t"
            :class="{
              'border-l': rowIdx + 1,
              'align-top': events.data?.[employee.name]?.[day.date],
              'align-middle bg-gray-50':
                events.data?.[employee.name]?.[day.date]?.holiday,
              'align-middle bg-pink-50':
                events.data?.[employee.name]?.[day.date]?.leave,
              'bg-gray-50':
                dropCell.employee === employee.name &&
                dropCell.date === day.date &&
                !isHolidayOrLeave(employee.name, day.date),
            }"
            @mouseenter="
              () => {
                hoveredCell.employee = employee.name
                hoveredCell.date = day.date
              }
            "
            @mouseleave="
              () => {
                hoveredCell.employee = ''
                hoveredCell.date = ''
              }
            "
            @dragover.prevent
            @dragenter="
              () => {
                dropCell.employee = employee.name
                dropCell.date = day.date
              }
            "
            @drop="
              () => {
                if (!isHolidayOrLeave(employee.name, day.date)) {
                  loading = true
                  swapShift.submit()
                }
              }
            "
          >
            <!-- Holiday -->
            <div
              v-if="events.data?.[employee.name]?.[day.date]?.holiday"
              class="blocked-cell"
            >
              <div
                class="w-32"
                v-html="
                  events.data[employee.name][day.date].weekly_off
                    ? '<strong>WO</strong>'
                    : events.data[employee.name][day.date].description
                "
              ></div>
            </div>

            <!-- Leave -->
            <div
              v-else-if="events.data?.[employee.name]?.[day.date]?.leave"
              class="blocked-cell"
            >
              {{ events.data[employee.name][day.date].leave_type }}
            </div>

            <!-- Tasks -->
            <div
              v-else
              class="flex flex-col space-y-1.5 translate-x-0 translate-y-0 max-w-40 min-w-36"
            >
              <div
                v-for="task in events.data?.[employee.name]?.[day.date]"
                @mouseenter="
                  onTaskMouseEnter(task, employee.name, day.date, $event)
                "
                @mouseleave="onTaskMouseLeave()"
                class="rounded border-2 p-2 cursor-pointer space-y-1.5"
                :class="[
                  dropCell.employee === employee.name &&
                    dropCell.date === day.date &&
                    dropCell.task === task.name &&
                    'scale-105',
                  hoveredCell.employee === employee.name &&
                    hoveredCell.date === day.date &&
                    hoveredCell.task === task.name &&
                    dropCell.employee &&
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

              <!-- Add Shift -->
              <Button
                variant="outline"
                icon="plus"
                class="border-2 active:bg-white w-full"
                :class="
                  hoveredCell.employee === employee.name &&
                  hoveredCell.date === day.date &&
                  !dropCell.employee
                    ? 'visible'
                    : 'invisible'
                "
                @click="
                  () => {
                    selectedTask.task = ''
                    selectedTask.subject = ''
                    selectedTask.employee = {
                      label: `${employee.name}: ${employee.employee_name}`,
                      value: employee.name,
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
    :employees="props.employees"
    :task-name="selectedTask.task"
    :task-subject="selectedTask.subject"
    :selected-employee="selectedTask.employee"
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
  employees: {
    required: true,
  },
  taskFilters: {
    required: true,
  },
})

const showTaskAssignmentDialog = ref(false)

const employeeSearch = ref()
const employeeSearchOptions = computed(() => {
  return props.employees.map((employee) => ({
    value: employee.name,
    label: `${employee.name}: ${employee.employee_name}`,
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
  employee: '',
  employee_display: '',
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
  employee: null,
})

const dropCell = ref({ employee: '', date: '', task: '' })
const loading = ref(false)
const isHolidayOrLeave = (employee, day) =>
  events.data?.[employee]?.[day]?.holiday ||
  events.data?.[employee]?.[day]?.leave

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
    for (const employee in data) {
      mapEventsToDates(data, mappedEvents, employee)
    }
    return mappedEvents
  },
})

const hoverPosition = ref({ top: 0, left: 0 })
const tableContainer = ref(null)

function onTaskMouseEnter(task, employeeName, date, event) {
  hoveredCell.value.task = task.name
  hoveredCell.value.subject = task.subject
  hoveredCell.value.shift_status = task.status
  hoveredCell.value.priority = task.priority || ''
  hoveredCell.value.project = task.project || ''
  hoveredCell.value.project_name = task.project_name || ''
  hoveredCell.value.color = task.color || colors[task.color][50]
  hoveredCell.value.employee = employeeName
  hoveredCell.value.employee_display =
    props.employees.find((emp) => emp.name === employeeName)?.employee_name ||
    employeeName
  hoveredCell.value.date = date

  const rect = event.currentTarget.getBoundingClientRect()
  const containerRect = tableContainer.value.getBoundingClientRect()
  hoverPosition.value = {
    top: rect.bottom - containerRect.top,
    left:
      rect.left -
      containerRect.left +
      rect.width / 2 +
      tableContainer.value.scrollLeft,
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

const mapEventsToDates = (data, mappedEvents, employee) => {
  mappedEvents[employee] = {}
  for (let d = 1; d <= props.firstOfMonth.daysInMonth(); d++) {
    const date = props.firstOfMonth.date(d)
    const key = date.format('YYYY-MM-DD')

    for (const event of Object.values(data[employee])) {
      let result
      if ('holiday' in event) {
        result = handleHoliday(event, date)
        if (result) {
          mappedEvents[employee][key] = result
          break
        }
      } else if ('leave' in event) {
        result = handleLeave(event, date)
        if (result) {
          mappedEvents[employee][key] = result
          break
        }
      } else {
        handleShifts(event, date, mappedEvents, employee, key)
      }
    }
  }
}

const handleShifts = (event, date, mappedEvents, employee, key) => {
  if (
    dayjs(event.start_date).isSameOrBefore(date) &&
    (dayjs(event.end_date).isSameOrAfter(date) || !event.end_date)
  ) {
    if (!Array.isArray(mappedEvents[employee][key]))
      mappedEvents[employee][key] = []
    mappedEvents[employee][key].push({
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
  () => [props.firstOfMonth, props.employeeFilters, props.taskFilters],
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
