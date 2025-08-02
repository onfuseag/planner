<template>
  <div class="px-12 py-8 overflow-y-scroll flex flex-col gap-8">
    <!-- Top Section Above Header -->
    <div class="flex items-center">
      <FeatherIcon name="calendar" class="h-7 w-7 text-gray-500 mr-2.5" />
      <span class="font-semibold text-2xl text-gray-500 mr-2"
        >Task Manager:</span
      >
      <span class="font-semibold text-2xl">Week View</span>
      <div class="ml-auto space-x-2.5">
        <Button
          label="Create Task"
          variant="solid"
          iconLeft="plus"
          @click="showTaskCreationDialog = true"
        />
        <Button
          label="Assign a Task"
          iconLeft="user-plus"
          @click="showTaskAssignmentDialog = true"
        />
      </div>
    </div>
    <WeekViewHeader
      :firstOfWeek="firstOfWeek"
      @updateFilters="updateFilters"
      @addToWeek="addToWeek"
    />
    <WeekViewTable
      ref="weekViewTable"
      :firstOfWeek="firstOfWeek"
      :employees="employees.data || []"
      :task-filters="taskFilters"
    />
    <TaskCreationDialog
      v-model="showTaskCreationDialog"
      v-if="showTaskCreationDialog"
      :employees="employees.data"
      @create="
        () => {
          showTaskCreationDialog = false
          $refs.weekViewTable.events.reload()
        }
      "
    />
    <TaskAssignmentDialog
      v-if="showTaskAssignmentDialog"
      :employees="employees.data"
      v-model="showTaskAssignmentDialog"
    />
  </div>
</template>

<script setup>
import { Button, FeatherIcon, createListResource } from 'frappe-ui'
import { reactive, ref } from 'vue'
import WeekViewHeader from '../components/WeekViewHeader.vue'
import WeekViewTable from '../components/WeekViewTable.vue'
import TaskAssignmentDialog from '../components/TaskAssignmentDialog.vue'
import TaskCreationDialog from '../components/TaskCreationDialog.vue'
import { dayjs, raiseToast } from '../utils'

const firstOfWeek = ref(dayjs().startOf('week'))
const employeeFilters = reactive({
  status: 'Active',
})
const showTaskCreationDialog = ref(false)
const showTaskAssignmentDialog = ref(false)

const weekViewTable = ref(null)

const addToWeek = (change) => {
  firstOfWeek.value = firstOfWeek.value.add(change, 'week')
}

const isCompanySelected = ref(false)
const taskFilters = reactive({
  status: null,
  priority: null,
  project: '',
})
const updateFilters = (newFilters) => {
  isCompanySelected.value = !!newFilters.company
  if (!isCompanySelected.value) return //here company toast
  let employeeUpdated = false
  Object.entries(newFilters).forEach(([key, value]) => {
    if (['status', 'priority', 'project'].includes(key)) {
      if (value) taskFilters[key] = value
      else delete taskFilters[key]
      return
    }

    if (value) employeeFilters[key] = value
    else delete employeeFilters[key]
    employeeUpdated = true
  })
  if (employeeUpdated) employees.fetch()
}

const employees = createListResource({
  doctype: 'Employee',
  fields: ['name', 'employee_name', 'designation', 'image'],
  cache: ['Employee'],
  filters: employeeFilters,
  pageLength: 99999,
  auto: true,
  onError(error) {
    console.log(error)
    raiseToast('error', error)
  },
})
</script>

<style lang="scss" scoped></style>
