<template>
  <!-- Positioned inside the row's first day cell; bars span the measured day columns -->
  <div class="absolute left-0 z-[2] pointer-events-none" :style="{ top: `${top}px` }">
    <div
      v-for="bar in bars"
      :key="bar.task.name"
      :data-task="bar.task.name"
      class="task-bar absolute pointer-events-auto cursor-pointer overflow-hidden border border-black/10 hover:border-black/30"
      :class="[
        bar.clippedStart ? 'rounded-l-none border-l-0' : 'rounded-l',
        bar.clippedEnd ? 'rounded-r-none border-r-0' : 'rounded-r',
      ]"
      :style="barStyle(bar)"
      @mouseenter="(e) => emit('enter', bar.task, e)"
      @mouseleave="emit('leave')"
      @click="emit('open', bar.task)"
    >
      <!-- Days inside the task that are not working days for this person -->
      <div
        v-for="seg in offSegments(bar)"
        :key="seg.idx"
        class="absolute inset-y-0"
        :class="seg.kind === 'leave' ? 'off-leave' : 'off-day'"
        :style="{ left: `${seg.left}px`, width: `${seg.width}px` }"
      />
      <div class="relative px-2 py-1 text-xs leading-4 text-gray-900">
        <div class="truncate font-medium">{{ bar.task.subject }}</div>
        <div class="flex items-center gap-1 truncate text-gray-700">
          <FeatherIcon
            v-if="bar.task.status === 'Completed'"
            name="check"
            class="h-3 w-3 shrink-0 stroke-gray-600"
          />
          <span class="truncate">{{ (subtitle || secondLine)(bar.task) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon } from 'frappe-ui'
import { dateFormat, dayjs } from '../utils'

const props = defineProps({
  // [{ task, lane, startIdx, endIdx, clippedStart, clippedEnd }] from layoutTaskBars
  bars: { type: Array, required: true },
  // measured day columns, relative to the first one: [{ left, width }]
  edges: { type: Array, required: true },
  // per day column: null, 'off' (weekly off / holiday) or 'leave'
  dayKinds: { type: Array, required: true },
  top: { type: Number, default: 0 },
  laneHeight: { type: Number, required: true },
  // optional second line; defaults to project · status (or completion date)
  subtitle: { type: Function, default: null },
})
const emit = defineEmits(['open', 'enter', 'leave'])

const INSET = 3 // gap between a bar and its column edges

function span(bar) {
  const a = props.edges[bar.startIdx]
  const b = props.edges[bar.endIdx]
  if (!a || !b) return null
  const left = a.left + (bar.clippedStart ? 0 : INSET)
  const right = b.left + b.width - (bar.clippedEnd ? 0 : INSET)
  return { left, width: Math.max(right - left, 0) }
}

function barStyle(bar) {
  const s = span(bar)
  if (!s) return { display: 'none' }
  return {
    left: `${s.left}px`,
    width: `${s.width}px`,
    top: `${bar.lane * props.laneHeight}px`,
    height: `${props.laneHeight - 4}px`,
    backgroundColor: bar.task.color,
  }
}

function offSegments(bar) {
  const s = span(bar)
  if (!s) return []
  const segs = []
  for (let i = bar.startIdx; i <= bar.endIdx; i++) {
    const kind = props.dayKinds[i]
    const e = props.edges[i]
    if (!kind || !e) continue
    const left = Math.max(e.left - s.left, 0)
    const right = Math.min(e.left + e.width - s.left, s.width)
    // join neighbouring days of the same kind, so the stripes run on without a seam
    const prev = segs[segs.length - 1]
    if (prev && prev.kind === kind && prev.lastIdx === i - 1) {
      prev.width = right - prev.left
      prev.lastIdx = i
    } else {
      segs.push({ idx: i, lastIdx: i, kind, left, width: right - left })
    }
  }
  return segs
}

function secondLine(task) {
  const status =
    task.status === 'Completed' && task.completed_on
      ? dayjs(task.completed_on).format(dateFormat.value)
      : task.status
  return [task.project_name, status].filter(Boolean).join(' · ')
}
</script>

<style scoped>
/* Non-working days inside a task: a solid pale wash keeps the text readable on any
   task colour, and thin lines on top say why: grey for weekly off / holiday, orange
   for leave (the person is booked while away). */
.off-day {
  background:
    repeating-linear-gradient(135deg, transparent 0 7px, rgba(107, 114, 128, 0.35) 7px 8px),
    rgba(255, 255, 255, 0.72);
}
.off-leave {
  background:
    repeating-linear-gradient(135deg, transparent 0 7px, rgba(234, 88, 12, 0.7) 7px 8.5px),
    rgba(255, 255, 255, 0.72);
}
</style>
