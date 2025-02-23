<template>
  <div v-if="user.data" class="min-h-screen">
    <Navbar :user="user.data" />
    <MonthView />
    <Toasts />
  </div>
</template>

<script setup lang="ts">
import { Toasts, createResource } from 'frappe-ui'

import Navbar from '../components/Navbar.vue'
import MonthView from './MonthView.vue'
import { dateFormat } from '../utils'
// RESOURCES

const user = createResource({
  url: 'planner.api.get_current_user_info',
  auto: true,
  onError() {
    window.location.href = '/login?redirect-to=%2Ftask-manager'
  },
  onSuccess(data) {
    dateFormat.value = data.date_format.toUpperCase()
  },
})
</script>
