<template>
  <div class="flex items-center justify-between sticky top-0 bg-white">
    <div class="flex items-center bg-gray-50 rounded-md space-x-0.5">
      <Button
        icon="chevron-left"
        variant="ghost"
        @click="emit('addToWeek', -1)"
      />
      <span class="w-40 text-center font-medium text-base">
        Week {{ weekOfMonth }} - {{ firstOfWeek?.format('MMMM') }},
        {{ firstOfWeek?.format('YYYY') }}
      </span>
      <Button
        icon="chevron-right"
        variant="ghost"
        @click="emit('addToWeek', 1)"
      />
    </div>
    <!-- Filters -->
    <div class="ml-auto space-x-2.5 flex">
      <div
        v-for="[key, value] of Object.entries(filters)"
        :key="key"
        class="max-w-36 w-36"
      >
        <FormControl
          v-if="!['status', 'priority', 'project'].includes(key)"
          type="autocomplete"
          :placeholder="toTitleCase(key)"
          :options="value.options"
          v-model="value.model"
          :disabled="!value.options.length"
        />
        <Link
          v-else-if="key === 'project'"
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
import { Dayjs } from 'dayjs'
import { FormControl } from 'frappe-ui'
import { computed, reactive, watch } from 'vue'
import { priority, status } from '../data'
import Link from './Link.vue'
export type FilterField =
  | 'status'
  | 'priority'
  | 'project'

const props = defineProps({
  firstOfWeek: Dayjs,
})

const weekOfMonth = computed(() => {
  const start = props.firstOfWeek.startOf('month').startOf('week')
  return props.firstOfWeek.diff(start, 'week') + 1
})

const emit = defineEmits<{
  (e: 'addToWeek', change: number): void
  (e: 'updateFilters', newFilters: { [K in FilterField]: string }): void
}>()

const filters: {
  [K in FilterField]: {
    options: string[]
    model?: { value: string } | null
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
