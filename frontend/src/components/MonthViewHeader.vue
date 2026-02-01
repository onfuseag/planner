<template>
  <div class="flex items-center justify-between sticky top-0 bg-white z-10">
    <div class="flex items-center bg-gray-50 rounded-md space-x-0.5">
      <Button
        icon="chevron-left"
        variant="ghost"
        @click="emit('addToMonth', -1)"
      />
      <span class="w-32 text-center font-medium text-base">
        {{ firstOfMonth?.format('MMMM') }},
        {{ firstOfMonth?.format('YYYY') }}
      </span>
      <Button
        icon="chevron-right"
        variant="ghost"
        @click="emit('addToMonth', 1)"
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
          v-if="key === 'department'"
          type="autocomplete"
          placeholder="Department"
          :options="value.options"
          v-model="value.model"
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
import { reactive, watch, onMounted } from 'vue'
import { FormControl } from 'frappe-ui'
import { Dayjs } from 'dayjs'
import { priority, status, departments } from '../data'
import Link from './Link.vue'

export type FilterField = 'status' | 'priority' | 'project' | 'department'

const props = defineProps({
  firstOfMonth: Dayjs,
})

const emit = defineEmits<{
  (e: 'addToMonth', change: number): void
  (e: 'updateFilters', newFilters: { [K in FilterField]: string }): void
}>()

const filters: {
  [K in FilterField]: {
    options?: any[]
    model?: { value: string } | string | null
  }
} = reactive({
  department: { options: [], model: null },
  project: { model: null },
  status: { options: status, model: null },
  priority: { options: priority, model: null },
})

onMounted(() => {
  departments.fetch().then(() => {
    filters.department.options = departments.data || []
  })
})

watch(filters, (val) => {
  const newFilters = {
    status: val.status.model || '',
    priority: val.priority.model || '',
    project: val?.project?.model || '',
    department: val?.department?.model?.value || '',
  }
  emit('updateFilters', newFilters)
})

const toTitleCase = (str: string) =>
  str
    .split('_')
    .map((s) => s.charAt(0).toUpperCase() + s.slice(1))
    .join(' ')
</script>
