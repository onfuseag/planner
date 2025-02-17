<template>
  <div class="px-12 py-8 space-y-8">
    <!-- Top Section Above Header -->
    <div class="flex items-center">
      <FeatherIcon name="calendar" class="h-7 w-7 text-gray-500 mr-2.5" />
      <span class="font-semibold text-2xl text-gray-500 mr-2"
        >Planner:</span
      >
      <span class="font-semibold text-2xl">Month View</span>
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
    <MonthViewHeader
      :firstOfMonth="firstOfMonth"
      @updateFilters="updateFilters"
      @addToMonth="addToMonth"
    />
    <MonthViewTable
      ref="monthViewTable"
      :firstOfMonth="firstOfMonth"
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
          $refs.monthViewTable.events.reload()
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
import { ref, reactive } from 'vue'
import { FeatherIcon, createListResource, Button } from 'frappe-ui'
import { dayjs, raiseToast } from '../utils'
import MonthViewHeader from '../components/MonthViewHeader.vue'
import MonthViewTable from '../components/MonthViewTable.vue'
import TaskCreationDialog from '../components/TaskCreationDialog.vue'
import TaskAssignmentDialog from '../components/TaskAssignmentDialog.vue'

const firstOfMonth = ref(dayjs().date(1).startOf('D'))
const employeeFilters = reactive({
  status: 'Active',
})
const showTaskCreationDialog = ref(false)
const showTaskAssignmentDialog = ref(false)

const monthViewTable = ref(null)

const addToMonth = (change) => {
  firstOfMonth.value = firstOfMonth.value.add(change, 'M')
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
