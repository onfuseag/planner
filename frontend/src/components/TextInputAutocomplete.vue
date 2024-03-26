<template>
    <Combobox v-model="selectedValue">
        <div class="relative">
            <ComboboxInput @change="
                      (e) => {
                        query = e.target.value
                      }
                    " :value="selectedValue?.value" :placeholder="props.placeholder"
                class="text-base rounded h-7 py-1.5 pl-2 pr-2 border border-gray-100 bg-gray-100 placeholder-gray-500 hover:border-gray-200 hover:bg-gray-200 focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors w-full" />
            <Button :variant="'outline'" type="button" theme="gray" size="sm" label="Button" icon="arrow-right"
                class="button-field absolute right-0">
            </Button>
        </div>
        <div class="relative mt-1 rounded-lg bg-white text-base shadow-2xl">
            <ComboboxOptions class="max-h-[15rem] overflow-y-auto px-1.5 pb-1.5">
                <div v-for="group in groups" :key="group.key" v-show="group.items.length > 0">
                    <div v-if="group.group && !group.hideLabel"
                        class="sticky top-10 truncate bg-white px-2.5 py-1.5 text-sm font-medium text-gray-600">
                        {{ group.group }}
                    </div>
                    <ComboboxOption as="template" v-for="(option, idx) in group.items.slice(0, 50)"
                        :key="option?.value || idx" :value="option" v-slot="{ active, selected }">
                        <li :class="[
        'flex cursor-pointer items-center justify-between rounded px-2.5 py-1.5 text-base',
        { 'bg-gray-100': active },
    ]">
                            <div class="flex flex-1 gap-2 overflow-hidden">
                                <!-- <span class="flex-1 truncate">
                                    {{ option }}
                                </span> -->
                                <div class="flex flex-col">
                                    <span class="text-base">{{ option.value }}</span>
                                    <span class="text-sm text-gray-500">{{ option.label }}</span>
                                </div>
                            </div>
                        </li>
                    </ComboboxOption>
                </div>
                <li v-if="groups.length == 0" class="rounded-md px-2.5 py-1.5 text-base text-gray-600">
                    No results found
                </li>
            </ComboboxOptions>
        </div>
    </Combobox>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
    Combobox,
    ComboboxInput,
    ComboboxOptions,
    ComboboxOption,
} from '@headlessui/vue'

const props = defineProps({
    modelValue: [String, Object],
    options: Array,
    placeholder: String,
});

const query = ref('');
const showOptions = ref(true);

const emits = defineEmits(['update:modelValue', 'update:query', 'change']);

function isOptionOrValue(optionOrValue) {
    return typeof optionOrValue === 'object' ? 'option' : 'value'
};

const sanitizeOptions = (options) => {
    if (!options) return []
    // in case the options are just values, convert them to objects
    return options.map((option) => {
        return isOptionOrValue(option) === 'option'
            ? option
            : { label: option, value: option }
    })
};

const groups = computed(() => {
    if (!props.options || props.options.length == 0) return [];

    let groups = props.options[0]?.group
        ? props.options
        : [{ group: '', items: sanitizeOptions(props.options) }];

    return groups
        .map((group, i) => {
            return {
                key: i,
                group: group.group,
                hideLabel: group.hideLabel || false,
                items: filterOptions(sanitizeOptions(group.items)),
            };
        })
        .filter((group) => group.items.length > 0);
});

const allOptions = computed(() => {
    return groups.value.flatMap((group) => group.items)
});

const findOption = (option) => {
    if (!option) return option
    const value = isOptionOrValue(option) === 'value' ? option : option.value
    return allOptions.value?.find((o) => o.value === value)
};

const getLabel = (option) => {
    if (isOptionOrValue(option) === 'value') return option
    return option?.label || option?.value || 'No label'
}

const selectedValue = computed({
    get() {
        return findOption(props.modelValue)
    },
    set(val) {
        query.value = ''
        if (val) showOptions.value = false
        emits('update:modelValue', val)
        return
    },
});

const filterOptions = (options) => {
    if (!query.value) return options
    return options.filter((option) => {
        return (
            option.label.toLowerCase().includes(query.value.toLowerCase()) ||
            option.value.toLowerCase().includes(query.value.toLowerCase())
        )
    })
};
</script>