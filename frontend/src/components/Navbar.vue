<template>
  <div class="h-12 bg-white border-b px-12 flex items-center">
    <div class="flex items-center space-x-1.5">
      <a
        href="/app"
        class="text-gray-600 hover:text-gray-700 flex items-center"
      >
        Planner
      </a>
      <FeatherIcon name="chevron-right" class="h-4 w-4" />
      <span class="font-medium">Tasks</span>
    </div>
    <Dropdown
      class="ml-auto"
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
          onClick: () => logout.submit(),
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
</template>

<script setup>
import { FeatherIcon, Dropdown, Avatar, createResource } from 'frappe-ui'

import { goTo, raiseToast } from '../utils'

const props = defineProps({
  user: {
    type: Object,
    required: true,
  },
})

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
