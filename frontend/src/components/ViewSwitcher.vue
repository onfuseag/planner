<template>
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
</template>

<script setup lang="ts">
import { inject, Ref } from 'vue'
import { views } from '../data'

// Home.vue owns the selected view; each view page renders this switcher in its toolbar
const currentView = inject<Ref<string>>('currentView')
</script>
