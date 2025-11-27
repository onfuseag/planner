<template>
  <div
    v-if="visible"
    class="absolute z-50 pointer-events-none max-w-xs text-xs bg-white shadow-lg rounded p-2 space-y-1"
    :style="popoverStyle"
  >
    <div class="font-medium truncate" :title="data.subject">
      {{ data.subject }}
    </div>
    <div v-if="data.project_name" class="truncate">
      <span class="font-semibold">Project:</span> {{ data.project_name }}
    </div>
    <div v-if="data.user_display" class="truncate">
      <span class="font-semibold">Assigned to:</span>
      {{ data.user_display }}
    </div>
    <div class="truncate">
      <span class="font-semibold">Status:</span> {{ data.shift_status }}
    </div>
    <div v-if="data.priority" class="truncate">
      <span class="font-semibold">Priority:</span> {{ data.priority }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
  position: {
    type: Object,
    required: true,
  },
})

const visible = computed(() => props.data && props.data.task)

// Handle both position formats: {x, y} for Daily view and {top, left} for Month/Week views
const popoverStyle = computed(() => {
  // Check if it's Daily view format (x, y)
  if ('x' in props.position && 'y' in props.position) {
    // Daily view format
    return {
      top: props.position.y + 'px',
      left: props.position.x + 'px',
      transform: 'translate(20%, calc(-100% + 185px))',
    }
  } else {
    // Month/Week view format (top, left)
    return {
      top: props.position.top + 'px',
      left: props.position.left + 'px',
      transform: 'translate(-50%, -100%)',
      marginTop: '-8px',
    }
  }
})
</script>

<style scoped></style>
