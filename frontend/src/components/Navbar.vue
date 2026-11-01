<template>
  <div
    class="h-12 bg-white border-b px-4 sm:px-8 lg:px-12 flex items-center gap-4 sm:gap-6"
  >
    <div class="flex items-center">
      <a
        href="/desk/planner"
        class="text-gray-600 hover:text-gray-700 flex items-center"
      >
        Planner
      </a>
    </div>
    <nav aria-label="Planner navigation" class="flex h-full items-center gap-4">
      <RouterLink
        :to="{ name: 'Home' }"
        class="inline-flex h-full items-center border-b-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
        :class="
          route.name === 'Home'
            ? 'border-gray-900 font-medium text-gray-900'
            : 'border-transparent text-gray-600 hover:text-gray-900'
        "
        :aria-current="route.name === 'Home' ? 'page' : undefined"
      >
        Tasks
      </RouterLink>
      <RouterLink
        :to="{ name: 'Checklists' }"
        class="inline-flex h-full items-center border-b-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
        :class="
          route.name === 'Checklists'
            ? 'border-gray-900 font-medium text-gray-900'
            : 'border-transparent text-gray-600 hover:text-gray-900'
        "
        :aria-current="route.name === 'Checklists' ? 'page' : undefined"
      >
        Checklists
      </RouterLink>
    </nav>
    <!-- Dropdown renders no root element of its own, so the spacing lives on a wrapper -->
    <div class="ml-auto">
      <Dropdown
        align="end"
        :options="[
          {
            label: 'Switch to Desk',
            onClick: () => goTo('/app'),
          },
          {
            label: 'Open Tasks',
            onClick: () => goTo('/app/task'),
          },
          {
            label: 'Log Out',
            onClick: logoutUser,
          },
        ]"
      >
        <Avatar
          :label="props.user?.full_name"
          :image="props.user?.user_image"
          size="xl"
          class="cursor-pointer"
        />
      </Dropdown>
    </div>
  </div>
</template>

<script setup>
import { Dropdown, Avatar, createResource } from 'frappe-ui'
import { useRoute } from 'vue-router'

import { goTo, raiseToast } from '../utils'

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
  beforeLogout: Function,
})

const emit = defineEmits(['logout-failed'])
const route = useRoute()

async function logoutUser() {
  if ((await props.beforeLogout?.()) === false) return
  try {
    await logout.submit()
  } catch {
    emit('logout-failed')
  }
}

// RESOURCES

const logout = createResource({
  url: 'logout',
  onSuccess() {
    goTo('/login')
  },
  onError(error) {
    raiseToast('error', error.messages[0])
  },
})
</script>
