<template>
  <div v-if="user.data" class="min-h-screen">
    <Navbar :user="user.data" />
    <div class="px-12 py-4 flex justify-end">
      <div class="inline-flex bg-gray-100 rounded-md p-1">
        <button
          v-for="view in views"
          :key="view.value"
          type="button"
          class="px-3 py-1 text-sm font-medium rounded transition-none"
          :class="
            currentView === view.value
              ? 'bg-gray-900 text-white'
              : 'text-gray-700 hover:text-gray-900'
          "
          @click="currentView = view.value"
        >
          {{ view.label }}
        </button>
      </div>
    </div>
    <KeepAlive>
      <component :is="viewComponent" />
    </KeepAlive>
  </div>
</template>

<script setup lang="ts">
import { createResource } from 'frappe-ui'

import Navbar from '../components/Navbar.vue'
import MonthView from './MonthView.vue'
import Weekview from './Weekview.vue'
import DailyView from './DailyView.vue'
import { dateFormat } from '../utils'
import { ref, computed, watch } from 'vue'
// RESOURCES

const currentView = ref('month')

const views = [
  { value: 'daily', label: 'Daily' },
  { value: 'week', label: 'Week' },
  { value: 'month', label: 'Month' },
]

const viewComponent = computed(() => {
  if (currentView.value === 'daily') return DailyView
  if (currentView.value === 'week') return Weekview
  return MonthView
})

watch(
  currentView,
  (v) => {
    const label = views.find((x) => x.value === v)?.label || ''
    document.title = `Planner — ${label} View`
  },
  { immediate: true },
)

const user = createResource({
  url: 'planner.api.get_current_user_info',
  auto: true,
  onError() {
    window.location.href = '/login?redirect-to=%2Fplanner'
  },
  onSuccess(data) {
    dateFormat.value = data.date_format.toUpperCase()
  },
})
</script>
