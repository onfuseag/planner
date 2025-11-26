<template>
  <div class="flex items-center justify-between sticky top-0 bg-white z-10">
    <div class="flex items-center space-x-2">
      <!-- Previous Day Button -->
      <div class="flex items-center bg-gray-50 rounded-md space-x-0.5">
        <Button
          icon="chevron-left"
          variant="ghost"
          @click="emit('addToDay', -1)"
        />
        <span class="w-48 text-center font-medium text-base">
          {{ selectedDay?.format('dddd, MMMM DD, YYYY') }}
        </span>
        <Button
          icon="chevron-right"
          variant="ghost"
          @click="emit('addToDay', 1)"
        />
      </div>
      <!-- Date Picker -->
      <DatePicker
        v-model="pickerDate"
        placeholder="Select Date"
        :formatter="(value) => dayjs(value).format('YYYY-MM-DD')"
      />
    </div>
    <!-- Filters -->
    <div class="ml-auto space-x-2.5 flex">
      <div
        v-for="[key, value] of Object.entries(filters)"
        :key="key"
        class="max-w-36 w-36"
      >
        <Link
          v-if="key === 'project'"
          doctype="Project"
          v-model="filters.project.model"
          placeholder="Select Project"
          :show-description="true"
          :update-filters="true"
          class="overflow-hidden"
        />
        <FormControl
          v-else
          type="select"
          :placeholder="toTitleCase(key)"
          :options="value.options"
          v-model="value.model"
          :disabled="!value.options.length"
        />
      </div>
      <Button
        icon="x"
        @click="
          Object.keys(filters).forEach((d) => {
            filters[d].model = null
          })
        "
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch, ref } from 'vue'
import { FormControl, DatePicker } from 'frappe-ui'
import { Dayjs } from 'dayjs'
import { dayjs } from '../utils'
import { priority, status } from '../data'
import Link from './Link.vue'

export type FilterField = 'status' | 'priority' | 'project'

const props = defineProps({
  selectedDay: Dayjs,
})

const emit = defineEmits<{
  (e: 'addToDay', change: number): void
  (e: 'updateFilters', newFilters: { [K in FilterField]: string }): void
  (e: 'updateSelectedDay', newDay: Dayjs): void
}>()

const pickerDate = ref(props.selectedDay?.format('YYYY-MM-DD'))

watch(pickerDate, (newDate) => {
  if (newDate) {
    emit('updateSelectedDay', dayjs(newDate))
  }
})

watch(() => props.selectedDay, (newDay) => {
  if (newDay) {
    pickerDate.value = newDay.format('YYYY-MM-DD')
  }
})

const filters: {
  [K in FilterField]: {
    options?: string[]
    model?: { value: string } | string | null
  }
} = reactive({
  project: { model: null },
  status: { options: status, model: null },
  priority: { options: priority, model: null },
})

watch(filters, (val) => {
  const newFilters = {
    status: val.status.model || '',
    priority: val.priority.model || '',
    project: val?.project?.model || '',
  }
  emit('updateFilters', newFilters)
})

const toTitleCase = (str: string) =>
  str
    .split('_')
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join(' ')
</script>
