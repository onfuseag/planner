<template>
  <FrappeUIProvider>
    <div class="min-h-screen">
      <router-view />
    </div>
  </FrappeUIProvider>
</template>

<script setup>
import { FrappeUIProvider } from 'frappe-ui'
</script>
