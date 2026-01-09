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
        <Button
          icon="refresh-cw"
          @click="refreshView"
          :loading="isRefreshing"
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
          $refs.weekViewTable.events.reload()
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
import { Button, FeatherIcon, createListResource } from 'frappe-ui'
import { reactive, ref } from 'vue'
import WeekViewHeader from '../components/WeekViewHeader.vue'
import WeekViewTable from '../components/WeekViewTable.vue'
import TaskAssignmentDialog from '../components/TaskAssignmentDialog.vue'
import TaskCreationDialog from '../components/TaskCreationDialog.vue'
import { dayjs, raiseToast } from '../utils'

const firstOfWeek = ref(dayjs().startOf('week'))
const showTaskCreationDialog = ref(false)
const showTaskAssignmentDialog = ref(false)
const isRefreshing = ref(false)

const weekViewTable = ref(null)

const addToWeek = (change) => {
  firstOfWeek.value = firstOfWeek.value.add(change, 'week')
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

const refreshView = async () => {
  isRefreshing.value = true
  try {
    await users.reload()
    if (weekViewTable.value) {
      await weekViewTable.value.events.reload()
    }
  } catch (error) {
    console.error(error)
    raiseToast('error', 'Failed to refresh view')
  } finally {
    isRefreshing.value = false
  }
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
