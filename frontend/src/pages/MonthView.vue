<template>
  <div class="px-12 py-8 overflow-y-scroll flex flex-col gap-8">
    <!-- Top Section Above Header -->
    <div class="flex items-center">
      <FeatherIcon name="calendar" class="h-7 w-7 text-gray-500 mr-2.5" />
      <span class="font-semibold text-2xl text-gray-500 mr-2">Planner:</span>

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
        <Button
          icon="refresh-cw"
          @click="refreshView"
          :loading="isRefreshing"
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
      :users="users.data || []"
      :task-filters="taskFilters"
    />
    <TaskCreationDialog
      v-model="showTaskCreationDialog"
      v-if="showTaskCreationDialog"
      :users="users.data"
      @create="
        () => {
          showTaskCreationDialog = false
          $refs.monthViewTable.events.reload()
        }
      "
    />
    <TaskAssignmentDialog
      v-if="showTaskAssignmentDialog"
      :users="users.data"
      v-model="showTaskAssignmentDialog"
    />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { FeatherIcon, createResource, Button } from 'frappe-ui'
import { dayjs, raiseToast } from '../utils'
import MonthViewHeader from '../components/MonthViewHeader.vue'
import MonthViewTable from '../components/MonthViewTable.vue'
import TaskCreationDialog from '../components/TaskCreationDialog.vue'
import TaskAssignmentDialog from '../components/TaskAssignmentDialog.vue'

const firstOfMonth = ref(dayjs().date(1).startOf('D'))
const showTaskCreationDialog = ref(false)
const showTaskAssignmentDialog = ref(false)
const isRefreshing = ref(false)

const monthViewTable = ref(null)

const addToMonth = (change) => {
  firstOfMonth.value = firstOfMonth.value.add(change, 'M')
}

const taskFilters = reactive({
  status: null,
  priority: null,
  project: '',
  department: '',
})

const updateFilters = (newFilters) => {
  Object.entries(newFilters).forEach(([key, value]) => {
    if (['status', 'priority', 'project'].includes(key)) {
      if (value) taskFilters[key] = value
      else delete taskFilters[key]
    }
    // Handle department filter separately (filters users, not tasks)
    if (key === 'department') {
      taskFilters.department = value || ''
      users.submit({ department: value || null })
    }
  })
}

const refreshView = async () => {
  isRefreshing.value = true
  try {
    await users.submit({ department: taskFilters.department || null })
    if (monthViewTable.value) {
      await monthViewTable.value.events.reload()
    }
  } catch (error) {
    console.error(error)
    raiseToast('error', 'Failed to refresh view')
  } finally {
    isRefreshing.value = false
  }
}

const users = createResource({
  url: 'planner.api.tasks.get_users_for_planner',
  auto: true,
  onError(error) {
    console.log(error)
    raiseToast('error', error)
  },
})
</script>

<style lang="scss" scoped></style>
