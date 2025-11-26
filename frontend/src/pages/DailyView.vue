<template>
  <div class="px-12 py-8 overflow-y-scroll flex flex-col gap-8">
    <!-- Top Section Above Header -->
    <div class="flex items-center">
      <FeatherIcon name="calendar" class="h-7 w-7 text-gray-500 mr-2.5" />
      <span class="font-semibold text-2xl text-gray-500 mr-2">Planner:</span>

      <span class="font-semibold text-2xl">Daily View</span>
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
    <DailyViewHeader
      :selected-day="selectedDay"
      @updateFilters="updateFilters"
      @addToDay="addToDay"
      @updateSelectedDay="updateSelectedDay"
    />
    <DailyViewTable
      ref="dailyViewTable"
      :selected-day="selectedDay"
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
          $refs.dailyViewTable.events.reload()
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
import { FeatherIcon, createListResource, Button } from 'frappe-ui'
import { dayjs, raiseToast } from '../utils'
import DailyViewHeader from '../components/DailyViewHeader.vue'
import DailyViewTable from '../components/DailyViewTable.vue'
import TaskCreationDialog from '../components/TaskCreationDialog.vue'
import TaskAssignmentDialog from '../components/TaskAssignmentDialog.vue'

const selectedDay = ref(dayjs().startOf('D'))
const showTaskCreationDialog = ref(false)
const showTaskAssignmentDialog = ref(false)

const dailyViewTable = ref(null)

const addToDay = (change) => {
  selectedDay.value = selectedDay.value.add(change, 'D')
}

const updateSelectedDay = (newDay) => {
  selectedDay.value = newDay.startOf('D')
}

const taskFilters = reactive({
  status: null,
  priority: null,
  project: '',
})

const updateFilters = (newFilters) => {
  Object.entries(newFilters).forEach(([key, value]) => {
    if (['status', 'priority', 'project'].includes(key)) {
      if (value) taskFilters[key] = value
      else delete taskFilters[key]
    }
  })
}

const users = createListResource({
  doctype: 'User',
  fields: ['name', 'full_name', 'user_image'],
  cache: ['User'],
  filters: {
    enabled: 1,
    user_type: 'System User',
  },
  pageLength: 99999,
  auto: true,
  onError(error) {
    console.log(error)
    raiseToast('error', error)
  },
})
</script>

<style lang="scss" scoped></style>
