<template>
  <div :id="id" class="border-t border-gray-100 px-4 py-4 sm:px-5">
    <div
      class="grid gap-3 md:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)_10rem_auto]"
    >
      <FormControl
        v-model="row.task"
        label="Task"
        placeholder="Describe the checklist item"
        :disabled="disabled"
      />
      <FormControl
        v-model="row.data"
        label="Data"
        placeholder="Value or notes"
        :disabled="disabled"
      />
      <FormControl
        v-model="row.status"
        type="select"
        label="Status"
        :options="statuses"
        :disabled="disabled"
      />
      <div class="flex items-end justify-end">
        <Button
          variant="ghost"
          icon="lucide-trash-2"
          :label="`Remove item${row.task ? ': ' + row.task : ''}`"
          :disabled="disabled || pending"
          @click="$emit('remove')"
        />
      </div>
    </div>

    <div class="mt-3 flex flex-wrap items-center gap-3">
      <a
        v-if="imageUrl"
        :href="imageUrl"
        target="_blank"
        rel="noopener noreferrer"
      >
        <img
          :src="imageUrl"
          :alt="`Photo for ${row.task || 'checklist item'}`"
          class="h-16 w-20 rounded-4 border border-gray-200 object-cover"
        />
      </a>
      <FileUploader
        file-types="image/*"
        :private="true"
        doctype="Project Checklist"
        :docname="documentName"
        :validate-file="validatePhoto"
        @success="photoUploaded"
        @failure="uploadFailed"
      >
        <template #default="{ openFileSelector, progress, error }">
          <Button
            variant="subtle"
            icon-left="lucide-image"
            :disabled="disabled || !documentName || pending"
            :loading="pending"
            :title="
              documentName ? '' : 'Save the checklist before adding photos'
            "
            @click="openFileSelector"
          >
            {{
              pending
                ? `Uploading ${progress}%`
                : row.image
                  ? 'Replace photo'
                  : 'Add photo'
            }}
          </Button>
          <p v-if="error" role="alert" class="mt-1 text-sm text-red-600">
            {{ error }}
          </p>
        </template>
      </FileUploader>
      <Button
        v-if="row.image"
        variant="ghost"
        :disabled="disabled || pending"
        @click="row.image = ''"
        >Remove photo</Button
      >
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Button, FileUploader, FormControl } from 'frappe-ui'

const props = defineProps({
  row: { type: Object, required: true },
  id: { type: String, required: true },
  documentName: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['remove', 'uploading'])
const pending = ref(false)
const statuses = ['Open', 'Done', 'Not applicable', 'Data'].map((value) => ({
  label: value,
  value,
}))
const imageUrl = computed(() => {
  if (!props.row.image) return ''
  try {
    const url = new URL(props.row.image, window.location.origin)
    return ['http:', 'https:'].includes(url.protocol) ? url.href : ''
  } catch {
    return ''
  }
})

function validatePhoto(file) {
  if (file.type && !file.type.startsWith('image/'))
    return 'Choose an image file.'
  pending.value = true
  emit('uploading', true)
}

function finishUpload() {
  if (!pending.value) return
  pending.value = false
  emit('uploading', false)
}

function photoUploaded(file) {
  props.row.image = file.file_url
  finishUpload()
}

function uploadFailed() {
  finishUpload()
}
</script>
