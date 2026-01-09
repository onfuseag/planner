<template>
  <div v-if="user.data" class="min-h-screen">
    <Navbar :user="user.data" />
    <div class="px-12 py-4 flex justify-end space-x-2">
      <Button
        label="Daily"
        :variant="currentView === 'daily' ? 'solid' : 'ghost'"
        @click="currentView = 'daily'"
      />
      <Button
        label="Week"
        :variant="currentView === 'week' ? 'solid' : 'ghost'"
        @click="currentView = 'week'"
      />
      <Button
        label="Month"
        :variant="currentView === 'month' ? 'solid' : 'ghost'"
        @click="currentView = 'month'"
      />
    </div>
    <DailyView v-if="currentView === 'daily'" />
    <Weekview v-else-if="currentView === 'week'" />
    <MonthView v-else />
    <Toasts />
  </div>
</template>

<script setup lang="ts">
import { Toasts, createResource, Button } from 'frappe-ui'

import Navbar from '../components/Navbar.vue'
import MonthView from './MonthView.vue'
import Weekview from './Weekview.vue'
import DailyView from './DailyView.vue'
import { dateFormat } from '../utils'
import { ref } from 'vue'
// RESOURCES

const currentView = ref('month')

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
