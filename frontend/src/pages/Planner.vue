<template>
    <Layout :breadcrumbs="breadcrumbs">
        <div class="mx-auto px-4 lg:px-8 max-w-[1800px]">
            <div class="flex justify-between items-center gap-x-2 mb-3">
                <!-- <Button :variant="'solid'" theme="gray" size="md" label="Button" @click="goToPrevWeek">
                    Prev
                </Button> -->
                <div class="bg-white py-1 px-3 rounded">
                    KW{{ weekNumber }}
                </div>
                <div class="bg-white py-1 px-3 rounded">
                    {{ department }}
                </div>
                <!-- <Button :variant="'solid'" theme="gray" size="md" label="Button" @click="goToNextWeek">
                    Next
                </Button> -->
            </div>
            <div class="flex flex-col lg:flex-row justify-between items-start gap-6">
                <div class="w-full lg:w-9/12">
                    <div class="bg-white rounded p-2">

                        <div ref="timeline"></div>

                    </div>
                </div>
                <div class="w-full lg:w-3/12">
                    <div class="bg-white rounded p-3">
                        <template v-if="!isTaskFormActive">
                            <p class="text-lg mb-3">Backlog</p>
                            <div class="grid grid-rows gap-3 mb-3">
                                <div class="flex flex-col bg-gray-300 p-3 rounded gap-2 cursor-grab select-none"
                                    v-for="task in backLog" :key="task.id" @click="openTaskDetail" draggable="true"
                                    @dragstart="dragBackLog($event, task)">
                                    <div class="flex justify-between items-center">
                                        <p class="text-sm">{{ task.title }}</p>
                                        <p class="text-xs">{{ task.duration }}</p>
                                    </div>
                                    <div class="flex justify-start items-center">
                                        <p class="text-sm font-semibold">{{ task.project_name }}</p>
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <div class="mb-3 flex justify-between items-center">
                                <p class="text-lg">Edit Task</p>
                                <Button :variant="'solid'" theme="gray" size="sm" label="Button" :loadingText="null"
                                    :disabled="false" :link="null" icon="arrow-left" :loading="false"
                                    @click="backToBackLog">
                                </Button>
                            </div>
                            <TaskForm />
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </Layout>
</template>

<script setup>
import Layout from "@/pages/shared/Layout.vue";
import { computed, ref, onMounted, watchEffect } from "vue";
import TaskForm from "@/components/Task/TaskForm.vue";
import { Timeline, DataSet } from 'vis-timeline/standalone';
import { useRoute } from 'vue-router';
import { createResource } from 'frappe-ui'
import { getURL } from '../getURL.js' 

//const { employees } = EmployeesStore();


const route = useRoute(); // Access to the current route

var employees = {}

// Get which dashboard we are supposed to load
const dashboardName = route.params.dashboardName;
const department = route.params.department;

let breadcrumbs = [
    {
        label: 'Dashboard',
        route: {
            name: 'Dashboard',
        },
    },
    {
        label: dashboardName,
        route: {
            name: 'Planner'
        }
    },
];

let currentDate = ref(new Date());
let isTaskFormActive = ref(false);
let weekNumber = ref(0);

const timeline = ref();
const backLog = ref([
    {
        name: '1ddffffff-a',
        title: "P-ANL-20222024-01-Montage",
        duration: "6 Tage",
        project_name: "Hofnerstrasse 4, Haus B, 8888 Unterageri",
        type: 1 // Enum 1 = work 
    },
]);

const openTaskDetail = () => {
    isTaskFormActive.value = true;
};

const dragEndBackLog = () => {}

const dragBackLog = (event, task) => {

    event.dataTransfer.effectAllowed = 'move';
    let item = {
        id: new Date(),
        type: 'range',
        content: task
    };

    event.target.id = new Date(item.id).toISOString();

    let startDateTime = new Date(currentDate.value);
    startDateTime.setHours(0, 0, 0, 0);
    item.content.startDate = startDateTime.toLocaleDateString('en-CA'); 

    let endDateTime = new Date(currentDate.value.setDate(currentDate.value.getDate() + 1));
    endDateTime.setHours(0, 0, 0, 0);
    item.content.endDate = endDateTime.toLocaleDateString('en-CA'); 

    event.dataTransfer.setData('text', JSON.stringify(item));
    event.target.addEventListener('dragend', dragEndBackLog.bind(this), false);
};

const backToBackLog = () => {
    isTaskFormActive.value = false;
    let selectedItem = timeline.value?.querySelector('.vis-item.vis-range.vis-selected');
    if (selectedItem) {
        selectedItem.classList.remove('vis-selected');
    }
};

const getWeekNumber = (d) => {
    d = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    let date = d;
    date.setHours(0, 0, 0, 0);
    date.setDate(date.getDate() + 3 - (date.getDay() + 6) % 7);
    let week1 = new Date(date.getFullYear(), 0, 4);
    return 1 + Math.round(((date.getTime() - week1.getTime()) / 86400000 - 3 + (week1.getDay() + 6) % 7) / 7);
}

const initTimeLine = () => {
    var groups = new DataSet()
    for (var i = 0; i < employees.length; i++) {
        groups.add({
            id: employees[i].name,
            content: {
                name: employees[i].employee_name,
                image: employees[i].image
            }
        })
    }

    var items = new DataSet();

    employees.forEach(employee => {
        employee.tasks.forEach(task => {
            items.add({
                id: task.name,
                group: employee.name,
                content: {
                    title: task.title,
                    project_name: task.project_name,
                    type: task.type
                },
                start: task.startDate,
                end: task.endDate,
                editable : task.type == 1
            });
        });
    });

    var currentDay = new Date(currentDate.value);
    var startOfWeek = new Date(currentDay.setDate(currentDay.getDate() - currentDay.getDay() + (currentDay.getDay() == 0 ? -6 : 1)));
    var endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(endOfWeek.getDate() + 6);
    endOfWeek.setHours(23, 59, 59, 999);

    var options = {
        stack: true,
        start: startOfWeek,
        end: endOfWeek,
        zoomable: false,
        editable: {
            add: false, // Disable adding items on double click
            updateTime: true, // Items can be moved horizontally
            updateGroup: true, // Items can be moved from one group to another
            remove: false, // Items can be deleted by selecting and pressing the delete key
        },
        orientation: 'top',
        horizontalScroll: true,
        showWeekScale: true,
        itemsAlwaysDraggable: {
            item: true,
            range: true
        },
        margin: {
            axis: 5,  
        },
        template: function (item, element, data) {
            element.classList.add('task-card');
            element.parentNode.parentNode.setAttribute('task-type', item.content.type);
            return '<p class="text-xs">' + item.content.title + '</p>' + '<p class="text-xs">' + item.content.project_name + '</p>';
        },
        groupTemplate: function (group, element) {
            element.classList.add('employee');
            return '<div class="employee">' +
                '<img class="employee-avatar" src="' + getURL() + group.content.image + '" alt="Avatar">' +
                '<p class="employee-name">' + group.content.name + '</p>' + '</div>';
        },
        snap: function (date, scale, step) {
            date.setHours(0);
            date.setMinutes(0);
            date.setSeconds(0);
            date.setMilliseconds(0);
            return date;
        },
    };

    // create a Timeline
    var container = timeline.value;
    timeline.value = new Timeline(container, items, groups, options);

    timeline.value.on('select', function (properties) {
        if(properties.items.length > 0) {
            isTaskFormActive.value = true;
        } else {
            isTaskFormActive.value = false;
        }
    });

    timeline.value.on('rangechanged', function (properties) {
        var startOfWeek = properties.start;
        weekNumber.value = getWeekNumber(startOfWeek);
    });
}

onMounted(() => {

    const resource = createResource({
        url: 'planner.api.get_planner_tasks', 
        params : {
            department: department
        }, 
        auto: true,
        onSuccess: (data) => {
            employees = resource.data
            initTimeLine()
        }
    });

    
    weekNumber.value = getWeekNumber(new Date(currentDate.value));
});


</script>

<style scoped></style>
