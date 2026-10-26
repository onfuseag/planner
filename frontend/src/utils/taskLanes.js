// Lays tasks out as continuous bars across a row of day (or hour) columns, stacking
// overlapping tasks into lanes (first lane that is free on the start column).
import dayjs from './dayjs'

const dayjsOf = (value) => (value ? dayjs(value) : null)

// unique tasks for one user out of the per-day event map built by the views
export function collectUserTasks(userEvents) {
  const tasks = new Map()
  for (const dayData of Object.values(userEvents || {})) {
    const dayTasks = Array.isArray(dayData) ? dayData : dayData?.tasks || []
    for (const task of dayTasks) tasks.set(task.name, task)
  }
  return [...tasks.values()]
}

// days: [{ date: 'YYYY-MM-DD' }] in column order
export function layoutTaskBars(tasks, days) {
  if (!days.length) return { bars: [], laneCount: 0 }
  const index = new Map(days.map((d, i) => [d.date, i]))
  const first = days[0].date
  const last = days[days.length - 1].date

  const bars = []
  for (const task of tasks) {
    const start = String(task.start_date || '').slice(0, 10)
    const end = String(task.end_date || task.start_date || '').slice(0, 10)
    if (!start || end < first || start > last) continue
    bars.push({
      task,
      startIdx: start < first ? 0 : index.get(start),
      endIdx: end > last ? days.length - 1 : index.get(end),
      clippedStart: start < first,
      clippedEnd: end > last,
    })
  }

  return packLanes(bars)
}

// hour columns ('00'..'23') for one day: a bar from the start hour to the last hour
// the task touches. Tasks with no time set (00:00 to 00:00) are all-day, matching the
// month and week views, which count both the start and the end date.
export function layoutHourBars(tasks, day, hourCount = 24) {
  const dayStart = day.startOf('day')
  const dayEnd = dayStart.add(1, 'day')
  const lastHour = hourCount - 1
  const bars = []
  for (const task of tasks) {
    const start = dayjsOf(task.start_date)
    const end = dayjsOf(task.end_date || task.start_date)
    if (!start || !start.isBefore(dayEnd)) continue
    const allDay =
      start.hour() === 0 && start.minute() === 0 && end.hour() === 0 && end.minute() === 0
    if (allDay) {
      if (end.isBefore(dayStart, 'day') || start.isAfter(dayStart, 'day')) continue
      bars.push({
        task,
        startIdx: 0,
        endIdx: lastHour,
        clippedStart: start.isBefore(dayStart, 'day'),
        clippedEnd: end.isAfter(dayStart, 'day'),
      })
      continue
    }
    if (!end.isAfter(dayStart) && !start.isSame(dayStart, 'day')) continue
    const clippedStart = start.isBefore(dayStart)
    const clippedEnd = !end.isBefore(dayEnd)
    const startIdx = clippedStart ? 0 : start.hour()
    // the end hour counts only if the task runs into it (10:30 -> 10, 10:00 -> 9)
    let endIdx = clippedEnd ? lastHour : end.minute() > 0 ? end.hour() : end.hour() - 1
    if (endIdx < startIdx) endIdx = startIdx // zero-length or same-hour task: one hour slot
    bars.push({ task, startIdx, endIdx, clippedStart, clippedEnd })
  }
  return packLanes(bars)
}

// longer bars first on the same start column, so short ones fill the gaps after them
export function packLanes(bars) {
  bars.sort((a, b) => a.startIdx - b.startIdx || b.endIdx - a.endIdx || a.task.name.localeCompare(b.task.name))
  const laneEnds = []
  for (const bar of bars) {
    let lane = laneEnds.findIndex((end) => end < bar.startIdx)
    if (lane === -1) lane = laneEnds.length
    laneEnds[lane] = bar.endIdx
    bar.lane = lane
  }
  return { bars, laneCount: laneEnds.length }
}

// row geometry shared by the month and week tables (px)
export const DAY_LABEL_HEIGHT = 22 // weekly off / holiday / leave label line at the top of a day cell
export const LANE_HEIGHT = 48 // one stacked bar, including the gap below it
export const ADD_BUTTON_HEIGHT = 30 // strip at the bottom of a row for the hover add-task button

export function dayLabel(holiday, leave) {
  if (leave) return { text: 'On leave', title: `On leave · ${leave.leave_type}`, cls: 'text-orange-700 font-medium' }
  if (holiday?.weekly_off) return { text: 'Weekly off', cls: 'text-gray-600' }
  if (holiday) return { text: holiday.description || 'Holiday', cls: 'text-gray-700 font-medium' }
  return null
}

// measured header cells -> column edges relative to the first day column
export function measureEdges(cells) {
  const ths = cells.filter(Boolean)
  if (!ths.length) return []
  const base = ths[0].getBoundingClientRect().left
  return ths.map((th) => {
    const r = th.getBoundingClientRect()
    return { left: r.left - base, width: r.width }
  })
}

// index of the header cell under a viewport x position, or -1
export function columnAt(cells, x) {
  return cells.findIndex((th) => {
    if (!th) return false
    const r = th.getBoundingClientRect()
    return x >= r.left && x < r.right
  })
}

// columns a user's bars cover, for placing the add-task button out of their way
export function coveredColumns(bars) {
  const cols = new Set()
  for (const bar of bars) for (let i = bar.startIdx; i <= bar.endIdx; i++) cols.add(i)
  return cols
}
