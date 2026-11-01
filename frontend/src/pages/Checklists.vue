<template>
  <div
    v-if="user.data && user.data.name !== 'Guest'"
    class="min-h-screen bg-gray-50"
  >
    <Navbar
      :user="user.data"
      :before-logout="confirmLogout"
      @logout-failed="resumeEditing"
    />
    <main class="mx-auto max-w-6xl px-4 py-6 sm:px-8 lg:px-12">
      <template v-if="checklistName">
        <RouterLink
          :to="listRoute"
          class="mb-5 inline-flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
        >
          <FeatherIcon name="arrow-left" class="h-4 w-4" />
          All checklists
        </RouterLink>
        <ChecklistEditor
          ref="editor"
          :name="checklistName"
          :project="projectFilter"
          :template="templateName"
          @saved="onSaved"
        />
      </template>
      <template v-else>
        <div class="mb-6 flex items-start justify-between gap-4">
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">
              Project checklists
            </h1>
            <p class="mt-1 text-sm text-gray-600">
              Start from a template, open a checklist, or create a new one.
            </p>
          </div>
          <RouterLink
            :to="newRoute"
            class="inline-flex shrink-0 items-center gap-1.5 rounded-md bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gray-900"
          >
            <FeatherIcon name="plus" class="h-4 w-4" />
            New checklist
          </RouterLink>
        </div>

        <section aria-labelledby="templates-heading" class="mb-8">
          <div class="mb-3">
            <h2
              id="templates-heading"
              class="text-base font-semibold text-gray-900"
            >
              Templates
            </h2>
            <p class="mt-1 text-sm text-gray-600">
              Choose a template to start a new checklist with its categories and
              lines.
            </p>
          </div>
          <div
            v-if="templatesError"
            role="alert"
            class="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
          >
            {{ templatesError }}
            <button
              class="ml-2 font-medium underline"
              @click="loadTemplates(templates.length === 0)"
            >
              Try again
            </button>
          </div>
          <div
            v-if="templatesLoading && templates.length === 0"
            role="status"
            class="rounded-lg border bg-white px-6 py-8 text-center text-sm text-gray-600"
          >
            Loading templates…
          </div>
          <div
            v-else-if="!templates.length && !templatesError"
            class="rounded-lg border border-dashed bg-white px-6 py-8 text-center text-sm text-gray-600"
          >
            No templates yet. Save a checklist with the status “Template” to
            reuse it here.
          </div>
          <ul
            v-else-if="templates.length"
            class="divide-y overflow-hidden rounded-lg border bg-white"
            aria-label="Checklist templates"
          >
            <li
              v-for="template in templates"
              :key="template.name"
              class="flex flex-wrap items-center"
            >
              <RouterLink
                :to="useTemplateRoute(template.name)"
                class="flex w-full min-w-0 items-center justify-between gap-3 px-4 py-4 hover:bg-gray-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-inset focus-visible:outline-gray-700 sm:flex-1 sm:px-5"
              >
                <div class="min-w-0">
                  <p class="font-medium text-gray-900">
                    {{ template.type || 'Checklist template' }}
                  </p>
                  <p class="mt-1 truncate text-sm text-gray-600">
                    {{
                      template.project_name ||
                      template.project ||
                      'Reusable checklist'
                    }}
                  </p>
                </div>
                <span
                  class="inline-flex shrink-0 items-center gap-1.5 text-sm font-medium text-gray-900"
                >
                  <FeatherIcon name="copy" class="h-4 w-4" />
                  Use template
                </span>
              </RouterLink>
              <RouterLink
                :to="detailRoute(template.name)"
                :aria-label="`Edit template ${template.type || template.name}`"
                class="mb-3 ml-1 mr-4 rounded-md px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 hover:text-gray-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 sm:mb-0 sm:ml-0 sm:mr-5"
              >
                Edit template
              </RouterLink>
            </li>
          </ul>
          <div
            v-if="templates.length"
            class="mt-3 flex items-center justify-between gap-3"
          >
            <p class="text-xs text-gray-500">
              {{ templates.length }} template{{
                templates.length === 1 ? '' : 's'
              }}
              loaded
            </p>
            <Button
              v-if="hasMoreTemplates"
              :loading="templatesLoading"
              @click="loadTemplates(false)"
              >Load more templates</Button
            >
          </div>
        </section>

        <h2 class="mb-3 text-base font-semibold text-gray-900">Checklists</h2>
        <div class="mb-4 flex flex-wrap items-end gap-3">
          <div class="w-full sm:w-80">
            <Link
              doctype="Project"
              label="Project"
              placeholder="All projects"
              :model-value="projectFilter"
              :show-description="true"
              @update:model-value="setProjectFilter"
            />
          </div>
          <Button
            v-if="projectFilter"
            variant="ghost"
            @click="setProjectFilter('')"
          >
            Clear filter
          </Button>
          <Button
            variant="subtle"
            :loading="loading || templatesLoading"
            @click="refreshLists"
          >
            Refresh
          </Button>
        </div>

        <div
          v-if="listError"
          role="alert"
          class="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
        >
          {{ listError }}
          <button
            class="ml-2 font-medium underline"
            @click="loadChecklists(rows.length === 0)"
          >
            Try again
          </button>
        </div>

        <div
          v-if="loading && rows.length === 0"
          role="status"
          class="rounded-lg border bg-white px-6 py-12 text-center text-sm text-gray-600"
        >
          Loading checklists…
        </div>
        <div
          v-else-if="!rows.length && !listError"
          class="rounded-lg border border-dashed bg-white px-6 py-12 text-center"
        >
          <FeatherIcon
            name="check-square"
            class="mx-auto mb-3 h-7 w-7 text-gray-400"
          />
          <h2 class="font-medium text-gray-900">No checklists yet</h2>
          <p class="mt-1 text-sm text-gray-600">
            {{
              projectFilter
                ? 'There are no checklists for this project.'
                : 'Choose a template above or create a checklist to get started.'
            }}
          </p>
        </div>
        <ul
          v-else-if="rows.length"
          class="divide-y overflow-hidden rounded-lg border bg-white"
          aria-label="Project checklists"
        >
          <li v-for="checklist in rows" :key="checklist.name">
            <RouterLink
              :to="detailRoute(checklist.name)"
              class="flex flex-wrap items-center justify-between gap-3 px-4 py-4 hover:bg-gray-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-inset focus-visible:outline-gray-700 sm:px-5"
            >
              <div class="min-w-0 flex-1">
                <p class="font-medium text-gray-900">
                  {{ checklist.type || 'Checklist' }}
                </p>
                <p class="mt-1 truncate text-sm text-gray-600">
                  {{
                    checklist.project_name || checklist.project || 'No project'
                  }}
                  <span
                    v-if="checklist.project_name && checklist.project"
                    class="text-gray-400"
                  >
                    · {{ checklist.project }}</span
                  >
                </p>
                <p class="mt-1 text-xs text-gray-400">{{ checklist.name }}</p>
              </div>
              <div class="flex shrink-0 items-center gap-3">
                <span v-if="checklist.date" class="text-xs text-gray-500">{{
                  formatDate(checklist.date)
                }}</span>
                <span
                  class="rounded px-2 py-1 text-xs"
                  :class="statusClasses(checklist.status)"
                  >{{ checklist.status || 'No status' }}</span
                >
                <FeatherIcon
                  name="chevron-right"
                  class="h-4 w-4 text-gray-400"
                />
              </div>
            </RouterLink>
          </li>
        </ul>
        <div
          v-if="rows.length"
          class="mt-4 flex items-center justify-between gap-3"
        >
          <p class="text-xs text-gray-500">
            {{ rows.length }} checklist{{ rows.length === 1 ? '' : 's' }} loaded
          </p>
          <Button
            v-if="hasMore"
            :loading="loading"
            @click="loadChecklists(false)"
            >Load more</Button
          >
        </div>
      </template>
    </main>
  </div>
  <div
    v-else
    class="flex min-h-screen items-center justify-center text-sm text-gray-600"
    role="status"
  >
    Loading Planner…
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, FeatherIcon, createResource } from 'frappe-ui'
import Navbar from '../components/Navbar.vue'
import Link from '../components/Link.vue'
import ChecklistEditor from '../components/ChecklistEditor.vue'
import { dateFormat, dayjs } from '../utils'

const route = useRoute()
const router = useRouter()
const editor = ref(null)
const pageSize = 30
const rows = ref([])
const loading = ref(false)
const listError = ref('')
const hasMore = ref(false)
let requestId = 0
const templates = ref([])
const templatesLoading = ref(false)
const templatesError = ref('')
const hasMoreTemplates = ref(false)
let templateRequestId = 0

const checklistName = computed(() =>
  typeof route.params.name === 'string' ? route.params.name : '',
)
const projectFilter = computed(() =>
  typeof route.query.project === 'string' ? route.query.project : '',
)
const templateName = computed(() =>
  typeof route.query.template === 'string' ? route.query.template : '',
)
const listRoute = computed(() => ({
  name: 'Checklists',
  params: { name: '' },
  query: projectFilter.value ? { project: projectFilter.value } : {},
}))
const newRoute = computed(() => ({
  ...listRoute.value,
  params: { name: 'new' },
}))

function login() {
  const redirect = window.location.pathname + window.location.search
  window.location.href = `/login?redirect-to=${encodeURIComponent(redirect)}`
}

const user = createResource({
  url: 'planner.api.get_current_user_info',
  auto: true,
  onError: login,
  onSuccess(data) {
    if (!data || data.name === 'Guest') {
      login()
      return
    }
    dateFormat.value = (data.date_format || 'yyyy-mm-dd').toUpperCase()
  },
})

const checklistList = createResource({ url: 'frappe.client.get_list' })
const templateList = createResource({ url: 'frappe.client.get_list' })

function detailRoute(name) {
  return { ...listRoute.value, params: { name } }
}

function useTemplateRoute(name) {
  return {
    ...newRoute.value,
    query: { ...newRoute.value.query, template: name },
  }
}

function setProjectFilter(project) {
  router.replace({ name: 'Checklists', query: project ? { project } : {} })
}

function formatDate(date) {
  return dayjs(date).format(dateFormat.value)
}

function statusClasses(status) {
  if (status === 'Completed') return 'bg-green-50 text-green-800'
  if (status === 'Open' || status === 'Pending Review')
    return 'bg-orange-50 text-orange-800'
  return 'bg-gray-100 text-gray-600'
}

function errorMessage(error) {
  const message =
    error?.messages?.[0] ||
    error?.message ||
    'Could not load checklists. Please try again.'
  return new DOMParser().parseFromString(String(message), 'text/html').body
    .textContent
}

async function loadChecklists(reset = false) {
  if (!user.data || user.data.name === 'Guest' || checklistName.value) return
  const currentRequest = ++requestId
  const start = reset ? 0 : rows.value.length
  if (reset) rows.value = []
  loading.value = true
  listError.value = ''
  try {
    const result = await checklistList.submit({
      doctype: 'Project Checklist',
      fields: ['name', 'type', 'project', 'project_name', 'date', 'status'],
      filters: {
        status: ['!=', 'Template'],
        ...(projectFilter.value ? { project: projectFilter.value } : {}),
      },
      order_by: 'modified desc, name asc',
      limit_start: start,
      limit_page_length: pageSize,
    })
    if (currentRequest !== requestId) return
    const next = result || []
    rows.value = reset
      ? next
      : [
          ...rows.value,
          ...next.filter(
            (item) => !rows.value.some((row) => row.name === item.name),
          ),
        ]
    hasMore.value = next.length === pageSize
  } catch (error) {
    if (currentRequest === requestId) listError.value = errorMessage(error)
  } finally {
    if (currentRequest === requestId) loading.value = false
  }
}

async function loadTemplates(reset = false) {
  if (!user.data || user.data.name === 'Guest' || checklistName.value) return
  const currentRequest = ++templateRequestId
  const start = reset ? 0 : templates.value.length
  if (reset) templates.value = []
  templatesLoading.value = true
  templatesError.value = ''
  try {
    const result = await templateList.submit({
      doctype: 'Project Checklist',
      fields: ['name', 'type', 'project', 'project_name', 'date', 'status'],
      filters: { status: 'Template' },
      order_by: 'modified desc, name asc',
      limit_start: start,
      limit_page_length: pageSize,
    })
    if (currentRequest !== templateRequestId) return
    const next = result || []
    templates.value = reset
      ? next
      : [
          ...templates.value,
          ...next.filter(
            (item) =>
              !templates.value.some((template) => template.name === item.name),
          ),
        ]
    hasMoreTemplates.value = next.length === pageSize
  } catch (error) {
    if (currentRequest === templateRequestId)
      templatesError.value = errorMessage(error)
  } finally {
    if (currentRequest === templateRequestId) templatesLoading.value = false
  }
}

function refreshLists() {
  loadTemplates(true)
  loadChecklists(true)
}

function onSaved(doc) {
  if (checklistName.value === 'new') router.replace(detailRoute(doc.name))
}

function confirmLogout() {
  return editor.value?.prepareLogout() ?? true
}

function resumeEditing() {
  editor.value?.resumeEditing()
}

watch(
  [() => user.data?.name, checklistName, projectFilter],
  () => {
    requestId++
    document.title =
      checklistName.value === 'new'
        ? 'Planner — New checklist'
        : 'Planner — Checklists'
    if (!checklistName.value) loadChecklists(true)
  },
  { immediate: true },
)

watch(
  [() => user.data?.name, checklistName],
  () => {
    templateRequestId++
    if (!checklistName.value) loadTemplates(true)
  },
  { immediate: true },
)
</script>
