<template>
  <div v-if="loading" role="status" class="py-16 text-center text-gray-500">
    Loading checklist…
  </div>
  <div
    v-else-if="loadError"
    role="alert"
    class="rounded-6 border border-red-200 bg-red-50 p-5"
  >
    <p class="text-sm text-red-700">{{ loadError }}</p>
    <Button class="mt-3" @click="loadChecklist(name)">Try again</Button>
  </div>
  <div v-else-if="draft" class="mx-auto max-w-6xl space-y-5">
    <div
      class="sticky top-0 z-20 -mx-1 flex flex-wrap items-center justify-between gap-3 bg-gray-50 px-1 py-3"
    >
      <div>
        <h1 class="text-2xl-semibold text-gray-900">
          {{ isNew ? 'New checklist' : draft.type }}
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          {{ draft.project_name || draft.project || 'Project checklist' }}
          <span aria-live="polite">
            ·
            {{
              saving
                ? 'Saving…'
                : dirty
                  ? 'Unsaved changes'
                  : isNew
                    ? 'Not saved yet'
                    : 'Saved'
            }}</span
          >
        </p>
      </div>
      <div class="flex items-center gap-2">
        <a
          v-if="!isNew"
          :href="deskUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="rounded-4 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 focus-visible:ring-2 focus-visible:ring-gray-500"
          >Open in Desk</a
        >
        <Button
          variant="solid"
          :loading="saving"
          :disabled="saving || pendingUploads > 0 || (!dirty && !isNew)"
          @click="saveChecklist"
        >
          Save checklist
        </Button>
      </div>
    </div>

    <p
      v-if="isNew && template"
      class="rounded-6 border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-800"
    >
      Started from a template. Save to create your new checklist.
    </p>

    <div
      v-if="saveError"
      role="alert"
      class="rounded-6 border border-red-200 bg-red-50 p-4 text-sm text-red-700"
    >
      <p>{{ saveError }}</p>
      <Button v-if="conflict" class="mt-3" @click="reloadChecklist"
        >Reload saved version</Button
      >
    </div>

    <fieldset
      :disabled="saving"
      :inert="saving || undefined"
      class="min-w-0 space-y-5"
    >
      <div
        class="grid gap-4 rounded-7 border border-gray-200 bg-white p-5 sm:grid-cols-2 lg:grid-cols-4"
      >
        <Link
          v-model="draft.type"
          doctype="Project Checklist Type"
          label="Checklist type *"
          placeholder="Choose a type"
        />
        <Link
          v-model="draft.project"
          doctype="Project"
          label="Project"
          placeholder="Choose a project"
        />
        <FormControl v-model="draft.date" type="date" label="Date" />
        <FormControl
          v-model="draft.status"
          type="select"
          label="Checklist status"
          :options="checklistStatuses"
        />
        <details class="sm:col-span-2 lg:col-span-4">
          <summary class="cursor-pointer text-sm text-gray-600">
            Customer and report details
          </summary>
          <div class="mt-4 grid gap-4 sm:grid-cols-2">
            <FormControl v-model="draft.customer" label="Customer" />
            <FormControl
              v-model="draft.customer_mail"
              label="Customer email"
              type="email"
            />
            <FormControl v-model="draft.position" label="Position" />
            <Link
              v-model="draft.user"
              doctype="User"
              label="Contact person"
              placeholder="Choose a user"
            />
            <FormControl
              v-model="draft.pretext"
              type="textarea"
              label="Introduction"
            />
            <FormControl
              v-model="draft.posttext"
              type="textarea"
              label="Closing text"
            />
          </div>
        </details>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 class="text-base-semibold text-gray-900">Checklist items</h2>
          <p class="mt-1 text-sm text-gray-500">{{ itemSummary }}</p>
        </div>
        <Button icon-left="lucide-plus" @click="openCategoryDialog()"
          >Add category</Button
        >
      </div>

      <div
        v-if="removedRow"
        role="status"
        class="flex items-center justify-between rounded-6 bg-gray-100 px-4 py-2 text-sm text-gray-700"
      >
        <span>Item removed.</span>
        <Button variant="ghost" @click="undoRemove">Undo</Button>
      </div>

      <div
        v-if="!groups.length"
        class="rounded-7 border border-dashed border-gray-300 bg-white px-6 py-12 text-center"
      >
        <h3 class="font-medium text-gray-900">Start with a category</h3>
        <p class="mx-auto mt-2 max-w-md text-sm text-gray-500">
          Give your first group a name, then add its checklist items. New lines
          automatically belong to that category.
        </p>
        <Button class="mt-5" icon-left="lucide-plus" @click="openCategoryDialog()"
          >Add category</Button
        >
      </div>

      <section
        v-for="group in groups"
        :key="group.category"
        class="overflow-hidden rounded-7 border border-gray-200 bg-white"
      >
        <div
          class="flex flex-wrap items-center gap-2 bg-gray-50 px-4 py-3 sm:px-5"
        >
          <h3 class="min-w-0 flex-1">
            <button
              type="button"
              class="flex w-full items-center gap-2 rounded-4 text-left focus-visible:ring-2 focus-visible:ring-gray-500"
              :aria-expanded="!collapsed.has(group.category)"
              :aria-controls="groupId(group.category)"
              @click="toggleCategory(group.category)"
            >
              <span
                :class="
                  collapsed.has(group.category)
                    ? 'lucide-chevron-right'
                    : 'lucide-chevron-down'
                "
                class="h-4 w-4 shrink-0 text-gray-500"
                aria-hidden="true"
              />
              <span class="break-words text-sm-semibold text-gray-800">{{
                group.category || 'Uncategorized'
              }}</span>
              <span class="shrink-0 text-xs text-gray-500"
                >{{ group.rows.length }}
                {{ group.rows.length === 1 ? 'item' : 'items' }}</span
              >
            </button>
          </h3>
          <Button
            variant="ghost"
            :label="`Rename category: ${group.category || 'Uncategorized'}`"
            :disabled="pendingUploads > 0"
            @click="openCategoryDialog(group.category)"
            >Rename</Button
          >
        </div>
        <div
          v-show="!collapsed.has(group.category)"
          :id="groupId(group.category)"
        >
          <ChecklistPointRow
            v-for="row in group.rows"
            :key="rowId(row)"
            :id="rowId(row)"
            :row="row"
            :document-name="draft.name || ''"
            :disabled="saving"
            @remove="removeRow(row)"
            @uploading="pendingUploads += $event ? 1 : -1"
          />
          <div class="border-t border-gray-100 px-4 py-2 sm:px-5">
            <Button
              variant="ghost"
              icon-left="lucide-plus"
              :label="`Add line to ${group.category || 'Uncategorized'}`"
              @click="addLine(group.category)"
              >Add line</Button
            >
          </div>
        </div>
      </section>

      <div class="flex flex-wrap items-center justify-between gap-3 pb-8">
        <Button variant="ghost" icon-left="lucide-plus" @click="addLine('')"
          >Add uncategorized line</Button
        >
        <p v-if="isNew" class="text-sm text-gray-500">
          Save the checklist before adding photos.
        </p>
        <p
          v-else-if="pendingUploads"
          role="status"
          class="text-sm text-gray-500"
        >
          Wait for photo uploads before saving.
        </p>
      </div>
    </fieldset>
  </div>

  <Dialog
    v-model:open="categoryDialog"
    :title="renamingCategory === null ? 'Add category' : 'Rename category'"
    size="sm"
  >
    <template #default>
      <form
        id="checklist-category-form"
        class="space-y-3"
        @submit.prevent="commitCategory"
      >
        <FormControl
          v-model="categoryText"
          label="Category name"
          placeholder="For example, Safety checks"
          :autofocus="true"
        />
        <p class="text-sm text-gray-500">
          {{
            renamingCategory === null
              ? 'Your first line will be added under this heading.'
              : 'This updates the category text on every item in this group.'
          }}
        </p>
        <p v-if="categoryWillMerge" class="text-sm text-amber-700">
          This category already exists. Its items will be grouped together.
        </p>
      </form>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button @click="categoryDialog = false">Cancel</Button>
        <Button
          variant="solid"
          type="submit"
          form="checklist-category-form"
          :disabled="!categoryText.trim()"
          >{{
            renamingCategory === null ? 'Add category' : 'Rename category'
          }}</Button
        >
      </div>
    </template>
  </Dialog>

  <Dialog
    v-model:open="leaveDialog"
    title="Discard unsaved changes?"
    size="sm"
    @update:open="cancelDismissedLeave"
  >
    <template #default
      ><p class="text-sm text-gray-600">
        Your checklist has changes that have not been saved.
      </p></template
    >
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button @click="resolveLeave(false)">Keep editing</Button>
        <Button theme="red" variant="solid" @click="resolveLeave(true)"
          >Discard changes</Button
        >
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, toRaw, watch } from 'vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import {
  Button,
  Dialog,
  FormControl,
  createResource,
} from 'frappe-ui'
import Link from './Link.vue'
import ChecklistPointRow from './ChecklistPointRow.vue'
import {
  addChecklistRow,
  createChecklistFromTemplate,
  groupChecklistRows,
  prepareChecklistForSave,
  renameChecklistCategory,
} from '../utils/checklists.mjs'

const props = defineProps({
  name: { type: String, required: true },
  project: { type: String, default: '' },
  template: { type: String, default: '' },
})
const emit = defineEmits(['saved'])
const draft = ref(null)
const baseline = ref('')
const loading = ref(false)
const saving = ref(false)
const loadError = ref('')
const saveError = ref('')
const conflict = ref(false)
const pendingUploads = ref(0)
const collapsed = ref(new Set())
const removedRow = ref(null)
const categoryDialog = ref(false)
const categoryText = ref('')
const renamingCategory = ref(null)
const leaveDialog = ref(false)
let leaveResolver = null
let allowUnload = false
let loadSequence = 0
let nextId = 0
const rowIds = new WeakMap()
const groupIds = new Map()

const getDocument = createResource({ url: 'frappe.client.get' })
const saveDocument = createResource({ url: 'frappe.client.save' })
const insertDocument = createResource({ url: 'frappe.client.insert' })
const insertFromTemplate = createResource({
  url: 'planner.api.checklists.create_from_template',
})
const isNew = computed(() => !draft.value?.name)
const dirty = computed(
  () => draft.value && JSON.stringify(draft.value) !== baseline.value,
)
const groups = computed(() => groupChecklistRows(draft.value?.checklist || []))
const deskUrl = computed(
  () => `/app/project-checklist/${encodeURIComponent(draft.value?.name || '')}`,
)
const checklistStatuses = [
  'Open',
  'Pending Review',
  'Template',
  'Completed',
  'Cancelled',
].map((value) => ({ label: value, value }))
const itemSummary = computed(() => {
  const rows = draft.value?.checklist || []
  const counts = ['Open', 'Done', 'Not applicable', 'Data']
    .map((status) => {
      const count = rows.filter((row) => row.status === status).length
      return count ? `${count} ${status.toLowerCase()}` : ''
    })
    .filter(Boolean)
  const unclassified = rows.filter((row) => !row.status).length
  if (unclassified) counts.push(`${unclassified} without status`)
  return rows.length
    ? `${rows.length} ${rows.length === 1 ? 'item' : 'items'} · ${counts.join(' · ')}`
    : 'No items yet'
})
const categoryWillMerge = computed(() => {
  const category = categoryText.value.trim()
  return (
    category !== renamingCategory.value &&
    groups.value.some((group) => group.category === category)
  )
})

function rowId(row) {
  const identity = toRaw(row)
  if (!rowIds.has(identity)) rowIds.set(identity, `checklist-row-${++nextId}`)
  return rowIds.get(identity)
}

function groupId(category) {
  if (!groupIds.has(category))
    groupIds.set(category, `checklist-group-${++nextId}`)
  return groupIds.get(category)
}

function errorMessage(error) {
  return String(
    error?.messages?.join(' ') ||
      error?.message ||
      'The request failed. Please try again.',
  ).replace(/<[^>]*>/g, '')
}

function setDocument(document) {
  draft.value = JSON.parse(JSON.stringify(document))
  draft.value.checklist ||= []
  baseline.value = JSON.stringify(draft.value)
  removedRow.value = null
}

function today() {
  const date = new Date()
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

async function loadChecklist(name) {
  const sequence = ++loadSequence
  loadError.value = ''
  saveError.value = ''
  conflict.value = false
  collapsed.value = new Set()
  if (name === 'new' && !props.template) {
    setDocument({
      doctype: 'Project Checklist',
      project: props.project,
      type: '',
      date: today(),
      status: 'Open',
      checklist: [],
    })
    loading.value = false
    return
  }
  loading.value = true
  draft.value = null
  try {
    const doc = await getDocument.submit({
      doctype: 'Project Checklist',
      name: name === 'new' ? props.template : name,
    })
    if (sequence === loadSequence) {
      setDocument(
        name === 'new'
          ? createChecklistFromTemplate(doc, {
              date: today(),
              project: props.project,
            })
          : doc,
      )
    }
  } catch (error) {
    if (sequence === loadSequence) loadError.value = errorMessage(error)
  } finally {
    if (sequence === loadSequence) loading.value = false
  }
}

async function focusRow(row) {
  await nextTick()
  document.getElementById(rowId(row))?.querySelector('input')?.focus()
}

function addLine(category) {
  collapsed.value.delete(category)
  const row = addChecklistRow(draft.value.checklist, category)
  focusRow(row)
}

function toggleCategory(category) {
  if (collapsed.value.has(category)) collapsed.value.delete(category)
  else collapsed.value.add(category)
}

function openCategoryDialog(category = null) {
  renamingCategory.value = category
  categoryText.value = category || ''
  categoryDialog.value = true
}

function commitCategory() {
  if (pendingUploads.value && renamingCategory.value !== null) return
  const category = categoryText.value.trim()
  if (!category) return
  if (renamingCategory.value === null) {
    addLine(category)
  } else {
    renameChecklistCategory(
      draft.value.checklist,
      renamingCategory.value,
      category,
    )
    collapsed.value.delete(category)
    collapsed.value.delete(renamingCategory.value)
  }
  categoryDialog.value = false
}

function removeRow(row) {
  const index = draft.value.checklist.indexOf(row)
  if (index < 0) return
  removedRow.value = { row, index }
  draft.value.checklist.splice(index, 1)
}

function undoRemove() {
  if (!removedRow.value) return
  draft.value.checklist.splice(removedRow.value.index, 0, removedRow.value.row)
  collapsed.value.delete(removedRow.value.row.category || '')
  removedRow.value = null
}

async function saveChecklist() {
  if (saving.value || pendingUploads.value) return
  saveError.value = ''
  conflict.value = false
  if (!draft.value.type) {
    saveError.value = 'Choose a checklist type before saving.'
    return
  }
  const emptyRow = draft.value.checklist.find(
    (row) => !row.name && !row.task?.trim() && !row.data?.trim() && !row.image,
  )
  if (emptyRow) {
    saveError.value = `Fill in or remove the empty new item in ${emptyRow.category || 'Uncategorized'} before saving.`
    collapsed.value.delete(emptyRow.category || '')
    focusRow(emptyRow)
    return
  }
  saving.value = true
  try {
    // Submit every row, including collapsed groups, with its original name and
    // the parent's modified timestamp for Frappe's normal conflict checks.
    const doc = prepareChecklistForSave(draft.value)
    const fromTemplate = isNew.value && props.template
    const resource = isNew.value
      ? fromTemplate
        ? insertFromTemplate
        : insertDocument
      : saveDocument
    const saved = await resource.submit({
      doc,
      ...(fromTemplate ? { template: props.template } : {}),
    })
    setDocument(saved)
    saving.value = false
    emit('saved', saved)
  } catch (error) {
    conflict.value = error?.exc_type === 'TimestampMismatchError'
    saveError.value = conflict.value
      ? 'This checklist was changed elsewhere. Your edits are still here. Copy any changes you need before reloading the saved version.'
      : errorMessage(error)
  } finally {
    saving.value = false
  }
}

function confirmLeave() {
  if (saving.value || pendingUploads.value) {
    saveError.value =
      'Wait for saving and photo uploads to finish before leaving.'
    return false
  }
  if (!dirty.value) return true
  leaveDialog.value = true
  return new Promise((resolve) => {
    leaveResolver = resolve
  })
}

function resolveLeave(discard) {
  const resolve = leaveResolver
  leaveResolver = null
  leaveDialog.value = false
  resolve?.(discard)
}

function cancelDismissedLeave(open) {
  if (!open && leaveResolver) resolveLeave(false)
}

async function reloadChecklist() {
  if (await confirmLeave()) loadChecklist(props.name)
}

function beforeUnload(event) {
  if (allowUnload) return
  if (!dirty.value && !saving.value && !pendingUploads.value) return
  event.preventDefault()
  event.returnValue = ''
}

async function prepareLogout() {
  const allowed = await confirmLeave()
  allowUnload = allowed
  return allowed
}

function resumeEditing() {
  allowUnload = false
}

defineExpose({ prepareLogout, resumeEditing })

onBeforeRouteLeave(confirmLeave)
onBeforeRouteUpdate((to, from) =>
  to.params.name === from.params.name &&
  to.query.template === from.query.template
    ? true
    : confirmLeave(),
)
window.addEventListener('beforeunload', beforeUnload)
onBeforeUnmount(() => {
  window.removeEventListener('beforeunload', beforeUnload)
  leaveResolver?.(false)
})
watch(
  () => draft.value?.project,
  (project, previous) => {
    if (draft.value && previous !== undefined && project !== previous) {
      draft.value.project_name = ''
    }
  },
  { flush: 'sync' },
)
watch(
  () => draft.value?.user,
  (user, previous) => {
    if (draft.value && previous !== undefined && user !== previous) {
      draft.value.user_name = ''
    }
  },
  { flush: 'sync' },
)
watch(
  [() => props.name, () => props.template],
  ([name]) => {
    if (name === draft.value?.name) return
    loadChecklist(name)
  },
  { immediate: true },
)
</script>
