<template>
  <div
    v-if="visible"
    ref="popover"
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
import { computed, ref, watch, nextTick } from 'vue'

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

const popover = ref(null)
const adjustedPosition = ref({ top: 0, left: 0 })

const visible = computed(() => props.data && props.data.task)

const popoverStyle = computed(() => {
  return {
    top: adjustedPosition.value.top + 'px',
    left: adjustedPosition.value.left + 'px',
    transform: 'translate(-50%, -100%)',
    marginTop: '-8px',
  }
})

watch(
  () => props.position,
  async (newPosition) => {
    if (!newPosition || !visible.value) return

    // Start with the base position
    adjustedPosition.value = { ...newPosition }

    // Wait for DOM update
    await nextTick()

    if (!popover.value) return

    const rect = popover.value.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight

    let { top, left } = newPosition

    // Adjust horizontal position if going off screen
    if (rect.right > viewportWidth) {
      left = viewportWidth - rect.width / 2 - 20
    } else if (rect.left < 0) {
      left = rect.width / 2 + 20
    }

    // Adjust vertical position if going off top
    if (rect.top < 0) {
      top = rect.height + 20
    }

    adjustedPosition.value = { top, left }
  },
  { immediate: true, deep: true }
)
</script>

<style scoped></style>
