<template>
  <div class="flex items-center justify-between">
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
        class="w-40"
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
            if (d !== 'company') {
              filters[d].model = null
            }
          })
        "
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { FormControl, createResource, createListResource } from 'frappe-ui'
import { raiseToast } from '../utils'
import { Dayjs } from 'dayjs'
import { priority, status } from '../data'
import Link from './Link.vue'
import { ref } from 'vue'
export type FilterField =
  | 'company'
  | 'department'
  | 'branch'
  | 'designation'
  | 'status'
  | 'priority'
  | 'project'

const props = defineProps({
  firstOfMonth: Dayjs,
})

const emit = defineEmits<{
  (e: 'addToMonth', change: number): void
  (e: 'updateFilters', newFilters: { [K in FilterField]: string }): void
}>()

const filters: {
  [K in FilterField]: {
    options: string[]
    model?: { value: string } | null
  }
} = reactive({
  company: { options: [], model: null },
  project: { model: null },
  department: { options: [], model: null },
  branch: { options: [], model: null },
  designation: { options: [], model: null },
  status: { options: status, model: null },
  priority: { options: priority, model: null },
})

// company changes update department options
const projectFilters = ref({})
watch(
  () => filters.company.model,
  (val) => {
    if (val?.value) {
      getFilterOptions('department', { company: val.value })
      projectFilters.value = { company: val?.value }
    } else {
      filters.department.model = null
      filters.department.options = []
    }
  },
)

watch(filters, (val) => {
  const newFilters = {
    company: val.company.model?.value || '',
    department: val.department.model?.value || '',
    branch: val.branch.model?.value || '',
    designation: val.designation.model?.value || '',
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

// RESOURCES

const defaultCompany = createResource({
  url: 'planner.api.tasks.get_default_company',
  auto: true,
  onSuccess: () => {
    ;['company', 'branch', 'designation'].forEach((field) =>
      getFilterOptions(field as FilterField),
    )
  },
})

const getFilterOptions = (
  field: FilterField,
  listFilters: { company?: string } = {},
) => {
  createListResource({
    doctype: toTitleCase(field),
    fields: ['name'],
    filters: listFilters,
    pageLength: 100,
    auto: true,
    onSuccess: (data: { name: string }[]) => {
      const value = field === 'company' ? defaultCompany.data : ''
      filters[field].model = { value }
      filters[field].options = data.map((item) => item.name)
    },
    onError(error: { messages: string[] }) {
      raiseToast('error', error.messages[0])
    },
  })
}
</script>
