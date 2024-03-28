<template>
    <form>
        <div class="flex flex-col">
            <div class="mb-3">

                <label class="block text-xs text-gray-600 mb-2">Assigned to</label>

                <div class="flex justify-start items-center">
                    


                    <Avatar :shape="'circle'" :label="assignee.owner" :image="assignee.image" size="2xl"
                        v-for="assignee in docinfo.assignments" :key="assignee.owner" v-if="docinfo" />
                    <Button :variant="'subtle'" theme="gray" size="lg" label="Button" :loading="false"
                        :loadingText="null" :disabled="false" :link="null" icon="user-plus" class="rounded-full"
                        type="button" @click="addAssigneePopup = true">
                    </Button>


                    <Dialog v-model="addAssigneePopup">
                        <template #body-title>
                            <p class="text-base">Assigned to</p>
                        </template>
                        <template #body-content>
                            <Autocomplete :options="employeesList" v-model="employees" placeholder="Select people"
                                :multiple="false" class="mb-5" @update:modelValue="onSelectEmployee" />
                            <div class="flex flex-col gap-3">
                                <div class="flex justify-between items-center"
                                    v-for="assignee in docinfo.assignments">
                                    <div class="flex justify-start items-center gap-3">
                                        <Avatar :shape="'circle'" :image="assignee.image" :label="assignee.owner" size="2xl" />
                                        <span>{{ assignee.fullname }}</span>
                                    </div>
                                    <Button :variant="'outline'" theme="gray" size="sm" label="Button" icon="x"
                                        @click="unselectEmployee(assignee.owner)">
                                    </Button>
                                </div>
                            </div>
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
                    <label class="block text-xs text-gray-600 mb-2">Project</label>
                    <TextInputAutocomplete v-model="project" placeholder="Project" :options="projectOptions" />
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Elevator</label>
                    <TextInputAutocomplete v-model="elevator" placeholder="Elevator" :options="elevatorOptions" value-by="elevator" label-by="name" />
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Type</label>
                    <TextInputAutocomplete v-model="type" placeholder="Type" :options="typeOptions" />
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Status</label>
                    <Select :options="['Open', 'Working', 'Pending Review', 'Overdue', 'Completed', 'Cancelled']"
                        v-model="status" />
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Priority</label>
                    <Select :options="['Low', 'Medium', 'High']" v-model="priority" />
                </div>
                <div class="mb-3">
                    <label class="block text-xs text-gray-600 mb-2">Parent Task</label>
                    <TextInputAutocomplete v-model="parent_task" placeholder="Parent Task" :options="parentTaskOptions" value-by="parent_name" label-by="name" />
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
import { useRoute } from 'vue-router';
import TextInputAutocomplete from '@/components/TextInputAutocomplete.vue';

// Props to be taken
const props = defineProps({
    task: String, 
    department: String
});

let dataTask = ref();

const schema = toTypedSchema(
    object({
        subject: string().required(),
        project: string(),
        elevator: string(),
        type: string(),
        parent_task: string(),
        status: string().required(),
        priority: string().required(),
        exp_start_date: string().required(),
        exp_end_date: string().required(),
        expected_time: string().required(),
        actual_time: string().required(),
    })
);

let employees = ref();

let employeesList = ref([]);

// get selected employees from API
let selectedEmployees = ref([{
    label: 'Muhammad Darwis Arifin',
    value: 'Muhammad-Darwis-Arifin',
    image: 'https://i.pravatar.cc/400?img=70',
},
{
    label: 'Christoph Diethelm',
    value: 'Christoph-Diethelm',
    image: 'https://i.pravatar.cc/400?img=69',
},]);

// filter out selected employees from employees list automatically
const unselectedEmployees = computed(() => {
    return employeesList;
});

// event when remove selected employee
const unselectEmployee = (assignedperson) => {

    const resp = createResource({
        url: 'frappe.desk.form.assign_to.remove',
        params: {
            doctype: "Task",
            name: props.task,
            assign_to: assignedperson
        },
        auto: true, 
        onSuccess: () => {

            for (let index in docinfo.assignments) {
                const assignee = docinfo.assignments[index];
                if (assignedperson === assignee.owner) {
                    // Remove the assignee at this index
                    docinfo.assignments.splice(index, 1);
                }
            }
        }
    });
};
// event when select employee
const onSelectEmployee = (employee) => {

    // have to put this in an array for the api to work
    const assign_to_array = [employee.value]

    const resp = createResource({
        url: 'frappe.desk.form.assign_to.add', 
        params: {
            doctype: "Task", 
            name: props.task, 
            description: props.task, 
            assign_to: assign_to_array, 
            bulk_assign: false
        }, 
        auto: true,
        onSuccess: () =>  {
            docinfo.assignments.push({
                owner: employee.value, 
                fullname: employee.label
            })
            selectedEmployees.value.push(employee);
        }
    })
};


// default options structure
let projectOptions = ref([
    {
        "label": "TASK-2024-00004",
        "value": "PROJ-0001",
    },
    {
        "label": "TASK-2024-00005",
        "value": "PROJ-0006"
    },
    {
        "label": "TASK-2024-00008",
        "value": "PROJ-0008"
    }]);

// you can define which property to be used as label and value, don't forget to add value-by and label-by on the component
let elevatorOptions = ref([
    {
        "name": "Elevator 1",
        "elevator": "Elevator 1 value",
    },
    {
        "name": "Elevator 2",
        "elevator": "Elevator 2 value"
    },
    {
        "name": "Elevator 3",
        "elevator": "Elevator 3 value"
    }]);

let typeOptions = ref([
    {
        "label": "Task",
        "value": "Task",
    },
    {
        "label": "Bug",
        "value": "Bug"
    },
    {
        "label": "Feature",
        "value": "Feature"
    }]);

let parentTaskOptions = ref([
    {
        "name": "TASK-2024-00004",
        "parent_name": "TASK-2024-00004 value",
    },
    {
        "name": "TASK-2024-00005",
        "parent_name": "TASK-2024-00005 value"
    },
    {
        "name": "TASK-2024-00008",
        "parent_name": "TASK-2024-00008 value"
    }]);

const { values, errors, defineField, handleSubmit, setError } = useForm({
    validationSchema: schema
});

const [subject] = defineField('subject');
const [project] = defineField('project');
const [elevator] = defineField('elevator');
const [type] = defineField('type');
const [parent_task] = defineField('parent_task');
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
        if (dataTask.value.subject !== values.subject){
            updateValue("subject", values.subject)
            dataTask.value.subject = values.subject
        }

        if (dataTask.value.project !== values.project) {
            updateValue("project", values.project)
            dataTask.value.project = values.project
        }
        if (dataTask.value.status !== values.status) {
            updateValue("status", values.status)
            dataTask.value.status = values.status
        }
        if (dataTask.value.priority !== values.priority) {
            updateValue("priority", values.priority)
            dataTask.value.priority = values.priority
        }
        if (dataTask.value.exp_start_date !== values.exp_start_date) {
            setError({"exp_start_date": 'Error message'});
            updateValue("exp_start_date", values.exp_start_date)
            dataTask.value.exp_start_date = values.exp_start_date

            
        }
        if (dataTask.value.exp_end_date !== values.exp_end_date) {
            updateValue("exp_end_date", values.exp_end_date)
            dataTask.value.exp_end_date = values.exp_end_date
        }
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
        if (docinfo.user_info[docinfo.assignments[i].owner].image) {
            docinfo.assignments[i].image = getURL() + docinfo.user_info[docinfo.assignments[i].owner].image
        }

        // Assign the user readable name always
        docinfo.assignments[i].fullname = docinfo.user_info[docinfo.assignments[i].owner].fullname
    }
}

const updateValue = (field, value) => {

    const resp = createResource({
        url: 'frappe.client.set_value',
        params: {
            doctype: "Task",
            name: props.task,
            fieldname: field,
            value: value
        },
        auto: true
    });
}


onMounted(() => {

    const resp = createResource({
        url: 'frappe.desk.search.search_link',
        params: {
            doctype: "User",
            txt:"",
            filters: {
                user_type: "System User", 
                enabled: 1
            }
        },
        auto: true, 
        onSuccess: (data) => {
            var users = []
            for (var i = 0; i < data.length; i++) {
                console.log(data[i])
                var user = {}
                
                user.value = data[i].value;
                user.label = data[i].description;

                users.push(user)
            }
            employeesList = users;
        }
    });

    const response = createResource({
        url: 'frappe.desk.form.load.getdoc',
        params: {
            doctype: "Task",
            name: props.task
        },
        auto: true,
        onSuccess: (data) => {


            if (response.data) {
                dataTask.value = response.data.docs[0];
                docinfo = response.data.docinfo;

                subject.value = dataTask.value.subject;
                project.value = dataTask.value.project;
                elevator.value = dataTask.value.elevator;
                type.value = dataTask.value.task;
                parent_task.value = dataTask.value.parent_task;
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