<template>
    <form>
        <div class="flex flex-col">
            <div class="mb-3">
                <label class="block text-xs text-gray-600 mb-2">Assigned to</label>

                <div class="flex justify-start items-center">
                    <!--<Avatar :shape="'circle'" :image="avatar" label="EY" size="2xl"
                        v-for="(avatar, index) in dataAvatars" :key="index" v-if="dataAvatars.length > 0" />
                    
                    --><Avatar :shape="'circle'" :label="assignee.owner" :image="assignee.image" size="2xl" v-for="assignee in docinfo.assignments" :key="assignee.owner" v-if="docinfo" />
                    <Button :variant="'subtle'" theme="gray" size="lg" label="Button" :loading="false"
                        :loadingText="null" :disabled="false" :link="null" icon="user-plus" class="rounded-full"
                        type="button" @click="addAssigneePopup = true">
                    </Button>
                    <Dialog v-model="addAssigneePopup">
                        <template #body-title>
                            <p class="text-base">Assigned to</p>
                        </template>
                        <template #body-content>
                            <Autocomplete :options="[
                            {
                                label: 'Muhammad Darwis Arifin',
                                value: 'Muhammad-Darwis-Arifin',
                                image: 'https://i.pravatar.cc/400?img=70',
                            },
                            {
                                label: 'Christoph Diethelm',
                                value: 'Christoph-Diethelm',
                                image: 'https://i.pravatar.cc/400?img=69',
                            },
                            {
                                label: 'John Smith',
                                value: 'john-smith',
                                image: 'https://randomuser.me/api/portraits/men/59.jpg',
                            },
                            {
                                label: 'Jane Smith',
                                value: 'jane-smith',
                                image: 'https://randomuser.me/api/portraits/women/59.jpg',
                            },
                            {
                                label: 'John Wayne',
                                value: 'john-wayne',
                                image: 'https://randomuser.me/api/portraits/men/57.jpg',
                            },
                            {
                                label: 'Jane Wayne',
                                value: 'jane-wayne',
                                image: 'https://randomuser.me/api/portraits/women/51.jpg',
                            },
                        ]" v-model="people" placeholder="Select people" :multiple="false" />
                        </template>
                        <template #actions>
                            <Button variant="solid">
                                Add
                            </Button>
                            <Button class="ml-2" @click="addAssigneePopup = false">
                                Close
                            </Button>
                        </template>
                    </Dialog>
                </div>
            </div>
            <form>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Subject</label>
                    <TextInput :type="'text'" size="sm" variant="subtle" placeholder="Subject" :disabled="false"
                        v-model="subject"
                        :class="[errors.subject ? 'border-red-400 hover:border-red-400 hover:bg-grey-200 focus:border-red-500 focus-visible:ring-red-400' : '']" />
                    <ErrorMessage v-if="errors.subject" :message="Error(errors.subject)" class="mt-1" />
                </div>

                <div class="mb-3">
                    <FormControl
                        type="text"
                        label="K">
                        <template #suffix>
                        <FeatherIcon
                            class="w-4"
                            name="search"
                        />
                        </template>
                    </FormControl>
                    <label class="block text-xs text-gray-600 mb-2">Project</label>
                    
                    <div
                        class="flex justify-between items-center text-gray-800 bg-gray-100 rounded py-2 h-7 cursor-pointer px-2">
                        <span class="text-sm">P-ANL-20022024-01</span>
                        <FeatherIcon class="w-4" name="arrow-right" />
                    </div>
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Elevator</label>
                    <div
                        class="flex justify-between items-center text-gray-800 bg-gray-100 rounded py-2 h-7 cursor-pointer px-2">
                        <span class="text-sm">ANL-20022024-01</span>
                        <FeatherIcon class="w-4" name="arrow-right" />
                    </div>
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Type</label>
                    <div
                        class="flex justify-between items-center text-gray-800 bg-gray-100 rounded py-2 h-7 cursor-pointer px-2">
                        <span class="text-sm">Bonus</span>
                        <FeatherIcon class="w-4" name="arrow-right" />
                    </div>
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Status</label>
                    <Select :options="['Open', 'Working', 'Pending Review', 'Overdue', 'Completed', 'Cancelled']" v-model="status" />
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Priority</label>
                    <Select :options="['Low','Medium','High']" v-model="priority" />
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Parent Task</label>
                    <div
                        class="flex justify-between items-center text-gray-800 bg-gray-100 rounded py-2 h-7 cursor-pointer px-2">
                        <span class="text-sm">Montageanlieferung</span>
                        <FeatherIcon class="w-4" name="arrow-right" />
                    </div>
                </div>

                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Expected Start Date</label>
                    <TextInput :type="'date'" size="sm" variant="subtle" placeholder="Expected Start Date"
                        :disabled="false" v-model="exp_start_date"
                        :class="[errors.exp_start_date ? 'border-red-400 hover:border-red-400 hover:bg-grey-200 focus:border-red-500 focus-visible:ring-red-400' : '']" />
                    <ErrorMessage v-if="errors.exp_start_date" :message="Error(errors.exp_start_date)" class="mt-1" />
                </div>

                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Expected End Date</label>
                    <TextInput :type="'date'" size="sm" variant="subtle" placeholder="Expected End Date"
                        :disabled="false" v-model="exp_end_date"
                        :class="[errors.exp_end_date ? 'border-red-400 hover:border-red-400 hover:bg-grey-200 focus:border-red-500 focus-visible:ring-red-400' : '']" />
                    <ErrorMessage v-if="errors.exp_end_date" :message="Error(errors.exp_end_date)" class="mt-1" />
                </div>

                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Expected Time</label>
                    <TextInput :type="'number'" size="sm" variant="subtle" placeholder="Expected Time" :disabled="true"
                        v-model="expected_time"
                        :class="[errors.expected_time ? 'border-red-400 hover:border-red-400 hover:bg-grey-200 focus:border-red-500 focus-visible:ring-red-400' : '']" />
                    <ErrorMessage v-if="errors.expected_time" :message="Error(errors.expected_time)" class="mt-1" />
                </div>

                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Actual Time in Hours</label>
                    <TextInput :type="'number'" size="sm" variant="subtle" placeholder="Actual Time in Hours"
                        :disabled="true" v-model="actual_time"
                        :class="[errors.actual_time ? 'border-red-400 hover:border-red-400 hover:bg-grey-200 focus:border-red-500 focus-visible:ring-red-400' : '']" />
                    <ErrorMessage v-if="errors.actual_time" :message="Error(errors.actual_time)" class="mt-1" />
                </div>
            </form>
        </div>
    </form>
</template>

<script setup>

import { ref, onMounted, inject, computed, defineProps } from "vue";
import { createResource } from "frappe-ui";
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/yup';
import { object, string, number, date, array } from 'yup';
import { watchDebounced } from '@vueuse/core';
import { getURL } from '../../getURL.js' 

// Props to be taken
const props = defineProps({
  task: String
});

let dataTask = ref();

const schema = toTypedSchema(
    object({
        subject: string().required(),
        status: string().required(),
        priority: string().required(),
        exp_start_date: string().required(),
        exp_end_date: string().required(),
        expected_time: string().required(),
        actual_time: string().required(),
    })
);

const { values, errors, defineField, handleSubmit } = useForm({
    validationSchema: schema
});

const [subject] = defineField('subject');
const [status] = defineField('status');
const [priority] = defineField('priority');
const [exp_start_date] = defineField('exp_start_date');
const [exp_end_date] = defineField('exp_end_date');
const [expected_time] = defineField('expected_time');
const [actual_time] = defineField('actual_time');

// track if any changes on the form fields, you can use this to make autosave feature
watchDebounced(
    values,
    () => {
        // let formData = new FormData();
        // formData.append('data', JSON.stringify(values));
        console.log(values)
    },
    { debounce: 1000, maxWait: 5000 },
)

// The doctype is accessible through data.doc
// Example json response from ERP sent to oyu already
// 

const addAssigneePopup = ref(false);
var docinfo = ref();

const sortDocinfo = () => {
    for (var i = 0; i < docinfo.assignments.length; i++) {
        if (docinfo.user_info[docinfo.assignments[i].owner].image){
            docinfo.assignments[i].image = getURL() + docinfo.user_info[docinfo.assignments[i].owner].image
        }
    }
}

onMounted(() => {

    const response = createResource({
        url: 'frappe.desk.form.load.getdoc', 
        params : {
            doctype: "Task", 
            name: props.task
        }, 
        auto: true,
        onSuccess: (data) => {


            if (response.data) {
                dataTask.value = response.data.docs[0];
                docinfo = response.data.docinfo;
                console.log(docinfo)
                console.log(docinfo.assignments)
                console.log(docinfo.assignments.length)


                subject.value = dataTask.value.subject;
                status.value = dataTask.value.status;
                priority.value = dataTask.value.priority;
                exp_start_date.value = dataTask.value.exp_start_date;
                exp_end_date.value = dataTask.value.exp_end_date;
                expected_time.value = dataTask.value.expected_time;
                actual_time.value = dataTask.value.actual_time;

                sortDocinfo()
            }
            
        }
    });


});

</script>