<template>
  <div
    v-if="visible"
    class="absolute z-50 pointer-events-none max-w-xs text-xs bg-white shadow-lg rounded p-2 space-y-1"
    :style="{
      top: position.top + 'px',
      left: position.left + 'px',
      transform: 'translate(20%, calc(-100% + 185px))',
    }"
  >
    <div class="font-medium truncate" :title="data.subject">
      {{ data.subject }}
    </div>
    <div v-if="data.project_name" class="truncate">
      <span class="font-semibold">Project:</span> {{ data.project_name }}
    </div>
    <div v-if="data.employee_display" class="truncate">
      <span class="font-semibold">Assigned to:</span>
      {{ data.employee_display }}
    </div>
    <div class="flex justify-between">
      <span>{{ data.status }}</span>
      <span v-if="data.priority"
        ><span class="font-semibold">Priority:</span> {{ data.priority }}</span
      >
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
</script>

<style scoped></style>
