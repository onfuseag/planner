<template>
  <component
    :is="multiple ? MultiSelect : Combobox"
    v-model="selectedValue"
    v-model:open="showOptions"
    v-model:query="query"
    :options="normalizedOptions"
    v-bind="multiple ? {} : { trigger: 'button' }"
    :label="label"
    :placeholder="placeholder"
    :loading="loading"
    :hide-search="hideSearch"
    :side="side"
    :align="align"
    :class="['w-full', buttonClasses]"
  >
    <template v-if="$slots.target" #trigger="{ open, setOpen, close }">
      <slot
        name="target"
        :open="() => setOpen(true)"
        :close="close"
        :toggle-popover="() => setOpen(!open)"
        :is-open="open"
      />
    </template>
    <template v-if="$slots.prefix" #prefix>
      <slot name="prefix" />
    </template>
    <template v-if="$slots.suffix" #suffix>
      <slot name="suffix" />
    </template>
    <template v-if="$slots['item-prefix']" #item-prefix="{ item, selected }">
      <slot name="item-prefix" :option="item" :selected="selected" />
    </template>
    <template v-if="$slots['item-suffix']" #item-suffix="{ item, selected }">
      <slot name="item-suffix" :option="item" :selected="selected" />
    </template>
    <template v-if="$slots.footer || (!multiple && showFooter)" #footer>
      <slot name="footer" :toggle-popover="togglePopover">
        <Button label="Clear" @click="selectedValue = null" />
      </slot>
    </template>
  </component>
</template>

<script setup>
import { Button, Combobox, MultiSelect } from 'frappe-ui'
import { computed, ref, watch } from 'vue'

const props = defineProps({
  label: String,
  modelValue: [String, Number, Object, Array],
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: String,
  multiple: Boolean,
  loading: Boolean,
  hideSearch: Boolean,
  placement: String,
  showFooter: Boolean,
  buttonClasses: [String, Array, Object],
})
const emit = defineEmits(['update:modelValue', 'update:query', 'change'])
const query = ref('')
const showOptions = ref(false)
const side = computed(() => props.placement?.split('-')[0] || 'bottom')
const align = computed(() => props.placement?.split('-')[1] || 'start')

function sanitizeOption(option) {
  return typeof option === 'object'
    ? option
    : { label: String(option), value: option }
}

const normalizedOptions = computed(() => {
  const options = (props.options || []).map((option) => {
    if (!option.group) return sanitizeOption(option)
    const { items, ...group } = option
    return {
      ...group,
      options: (group.options || items || []).map(sanitizeOption),
    }
  })
  const values = new Set(
    options.flatMap((option) => option.options || [option]).map(getValue),
  )
  const selected = Array.isArray(props.modelValue)
    ? props.modelValue
    : [props.modelValue]
  for (const option of selected) {
    if (option == null || option === '' || values.has(getValue(option))) continue
    options.push(sanitizeOption(option))
    values.add(getValue(option))
  }
  return options
})
const allOptions = computed(() =>
  normalizedOptions.value.flatMap((option) => option.options || [option]),
)

function getValue(option) {
  return option && typeof option === 'object' ? option.value : option
}

function findOption(value) {
  const current = Array.isArray(props.modelValue)
    ? props.modelValue
    : [props.modelValue]
  const option = [...allOptions.value, ...current].find(
    (option) => option != null && getValue(option) === value,
  )
  return sanitizeOption(option ?? value)
}

const selectedValue = computed({
  get() {
    if (props.multiple) {
      return Array.isArray(props.modelValue)
        ? props.modelValue.map(getValue)
        : []
    }
    return getValue(props.modelValue) ?? null
  },
  set(value) {
    const selection = props.multiple
      ? (value || []).map(findOption)
      : value == null
        ? null
        : findOption(value)
    emit('update:modelValue', selection)
  },
})

function togglePopover(open) {
  showOptions.value = open ?? !showOptions.value
}

watch(query, (value) => emit('update:query', value))
watch(showOptions, (open) => {
  if (!open) query.value = ''
})

defineExpose({ togglePopover })
</script>
