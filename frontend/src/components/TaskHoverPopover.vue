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

// Position the popover above the task with minimal gap
const popoverStyle = computed(() => {
  return {
    top: props.position.y + 'px',
    left: props.position.x + 'px',
    transform: 'translate(-50%, calc(-100% - 4px))',
  }
})
</script>

<style scoped></style>
