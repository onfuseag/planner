<template>
  <Combobox
    class="w-full"
    :model-value="selectedValue"
    v-model:open="showOptions"
    v-model:query="query"
    :options="normalizedOptions"
    trigger="button"
    :size="size === 'xl' ? 'lg' : size"
    :variant="variant"
    :placeholder="placeholder"
    :disabled="disabled"
    :filterable="filterable"
    @update:selected-option="selectOption"
  >
    <template v-if="$slots.target" #trigger="{ open, setOpen }">
      <slot
        name="target"
        :open="() => setOpen(true)"
        :toggle-popover="() => setOpen(!open)"
        :is-open="open"
      />
    </template>
    <template v-if="$slots.prefix" #prefix>
      <slot name="prefix" />
    </template>
    <template v-if="$slots['item-prefix']" #item-prefix="{ item, selected }">
      <slot name="item-prefix" :option="item" :selected="selected" />
    </template>
    <template v-if="$slots['item-label']" #item-label="{ item, selected }">
      <slot name="item-label" :option="item" :selected="selected" />
    </template>
    <template v-if="$slots.footer" #footer="{ close }">
      <slot name="footer" :value="query" :close="close" />
    </template>
  </Combobox>
</template>

<script setup>
import { Combobox } from 'frappe-ui'
import { computed, ref, useAttrs, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Object],
    default: '',
  },
  options: {
    type: Array,
    default: () => [],
  },
  size: {
    type: String,
    default: 'md',
  },
  variant: {
    type: String,
    default: 'subtle',
  },
  placeholder: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  filterable: {
    type: Boolean,
    default: true,
  },
})
const emit = defineEmits(['update:modelValue', 'update:query', 'change'])
const attrs = useAttrs()
const query = ref('')
const showOptions = ref(false)
const valuePropPassed = computed(() => 'value' in attrs)
const selectedValue = computed(() => {
  const value = valuePropPassed.value ? attrs.value : props.modelValue
  return value && typeof value === 'object' ? value.value : value || null
})

const normalizedOptions = computed(() =>
  (props.options || []).map((option) => {
    if (!option.group) return option
    const { items, ...group } = option
    return { ...group, options: group.options || items || [] }
  }),
)

function selectOption(option) {
  emit(valuePropPassed.value ? 'change' : 'update:modelValue', option)
}

watch(query, (value) => emit('update:query', value))
watch(showOptions, (open) => {
  if (!open) query.value = ''
})

defineExpose({ query })
</script>
