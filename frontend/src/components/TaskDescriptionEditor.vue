<template>
  <div
    class="w-full rounded-4 border border-outline-gray-2 bg-surface-gray-2 px-2 py-1.5 transition-colors focus-within:border-outline-gray-4 focus-within:bg-surface-base"
  >
    <Editor
      v-model="description"
      :extensions="extensions"
      :upload-function="uploadDescriptionFile"
      placeholder="This task is about..."
    >
      <EditorBubbleMenu :items="articleToolbar" />
      <EditorContent class="min-h-[80px] text-sm" aria-label="Description" />
    </Editor>
  </div>
</template>

<script setup>
import { upload } from 'frappe-ui'
import {
  Editor,
  EditorBubbleMenu,
  EditorContent,
  RichTextKit,
  articleToolbar,
} from 'frappe-ui/editor'

const description = defineModel({ default: '' })
const extensions = [RichTextKit]

function uploadDescriptionFile(file, options) {
  return upload(file, { ...options, private: true })
}
</script>
