<template>
    <Combobox v-model="selectedValue"
    nullable
    >
        <div class="relative">
            <ComboboxInput @change="onInputChange"
        :value="query" :placeholder="props.placeholder"
                class="text-base rounded h-7 py-1.5 pl-2 pr-2 border border-gray-100 bg-gray-100 placeholder-gray-500 hover:border-gray-200 hover:bg-gray-200 focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors w-full" />
            <Button :variant="'outline'" type="button" theme="gray" size="sm" label="Button" icon="arrow-right"
                class="button-field absolute right-0">
            </Button>
        </div>
        <div class="relative mt-1 rounded-lg bg-white text-base shadow-2xl">
            <ComboboxOptions class="max-h-[15rem] overflow-y-auto px-1.5 pb-1.5 pt-1.5">
                <div v-for="group in groups" :key="group.key" v-show="group.items.length > 0">
                    <div v-if="group.group && !group.hideLabel"
                        class="sticky top-10 truncate bg-white px-2.5 py-1.5 text-sm font-medium text-gray-600">
                        {{ group.group }}
                    </div>
                    <ComboboxOption as="template" v-for="(option, idx) in group.items.slice(0, 50)" :key="idx"
                        :value="option" v-slot="{ active, selected }" :disabled="option.disabled"
                        :class="{
                            'opacity-50' : option.disabled,
                            'cursor-not-allowed' : option.disabled,
                            'cursor-pointer' : !option.disabled,
                        }"
                        >
                        <li :class="[
                            'flex items-center justify-between rounded px-2.5 py-1.5 text-base',
                            { 'bg-gray-100': active },
                        ]">
                            <div class="flex flex-1 gap-2 overflow-hidden">
                                <div class="flex flex-col">
                                    <span class="text-base">{{ option[props.valueBy] }}</span>
                                    <span class="text-sm text-gray-500">{{ option[props.labelBy] }}</span>
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
    valueBy: {
        type: String,
        default: 'value',
    },
    labelBy: {
        type: String,
        default: 'label',
    },
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
    const value = isOptionOrValue(option) === 'value' ? option : option[props.valueBy]
    return allOptions.value?.find((o) => o[props.valueBy] === value)
};

// const getLabel = (option) => {
//     if (isOptionOrValue(option) === 'value') return option
//     return option[props.labelBy] || option[props.valueBy] || 'No label'
// }

const onInputChange = (e) => {
    query.value = e.target.value;
};

const selectedValue = computed({
    get() {
        const option = findOption(props.modelValue);
        return option ? option[props.valueBy] : null;
    },
    set(val) {
        if (val) showOptions.value = false
        const option = findOption(val);
        const value = option ? option[props.valueBy] : null;
        
        emits('update:modelValue', value);
        query.value = value;

        return
    },
});

const queryResult = computed(() => {
    const option = findOption(selectedValue.value);
    return option ? option[props.valueBy] : null;
});

const filterOptions = (options) => {
    if (!query.value) return options;
    const filteredOptions = options.filter((option) => {
        return (
            option[props.labelBy].toLowerCase().includes(query.value.toLowerCase()) ||
            option[props.valueBy].toLowerCase().includes(query.value.toLowerCase())
        );
    });
    return filteredOptions.length > 0 ? filteredOptions : [];
};
</script>