<template>
  <div v-if="user.data" class="min-h-screen">
    <Navbar :user="user.data" />
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
import { views } from '../data'
import { ref, computed, watch, provide } from 'vue'
// RESOURCES

const currentView = ref('month')
// read and changed by the ViewSwitcher in each view's toolbar
provide('currentView', currentView)

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
