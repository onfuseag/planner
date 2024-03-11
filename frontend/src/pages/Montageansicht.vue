<template>
    <Layout :breadcrumbs="breadcrumbs">
        <div class="mx-auto px-4 lg:px-8 max-w-[1800px]">
            <div class="flex justify-start items-center gap-x-2 mb-6">
                <!-- <Button :variant="'solid'" theme="gray" size="md" label="Button" @click="goToPrevWeek">
                    Prev
                </Button> -->
                <div class="bg-white py-1 px-3 rounded">
                    KW{{ weekNumber }}
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
                                        <p class="text-sm font-semibold">{{ task.address }}</p>
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <div class="mb-3 flex justify-between items-center">
                                <p class="text-lg">Task 40031</p>
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

let breadcrumbs = [
    {
        label: 'Dashboard',
        route: {
            name: 'Dashboard',
        },
    },
    {
        label: 'Montageansicht',
        route: {
            name: 'Montageansicht',
        },
    },
];
let currentDate = ref(new Date());
let isTaskFormActive = ref(false);
let weekNumber = ref(0);

const timeline = ref();

const employees = ref([
    {
        id: 1,
        name: "Muhammad Darwis Arifin",
        avatar: "https://i.pravatar.cc/400?img=70",
        tasks: [
            {
                id: '1-a',
                title: "P-ANL-20222024-01-Montage",
                duration: "6 Tage",
                address: "Hofnerstrasse 4, Haus B, 8888 Unterageri",
                startDate: "2024-02-27",
                endDate: "2024-02-29",
            },
        ],
    },
    {
        id: 2,
        name: "Christoph Diethelm",
        avatar: "https://i.pravatar.cc/400?img=69",
        tasks: [],
    },
    {
        id: 3,
        name: "John Doe",
        avatar: "https://i.pravatar.cc/400?img=68",
        tasks: [
            {
                id: '1-b',
                title: "P-ANL-20222024-01-Montage",
                duration: "6 Tage",
                address: "Hofnerstrasse 4, Haus B, 8888 Unterageri",
                startDate: "2024-02-28",
                endDate: "2024-03-01",
            },
            {
                id: '1-ft6667b',
                title: "P-ANL-20222024-01-Montage",
                duration: "6 Tage",
                address: "Hofnerstrasse 4, Haus B, 8888 Unterageri",
                startDate: "2024-02-26",
                endDate: "2024-02-29",
            },
        ],
    },
    {
        id: 4,
        name: "Marco Simeone",
        avatar: "https://i.pravatar.cc/400?img=64",
        tasks: [
        ],
    },
    {
        id: 5,
        name: "Joao Schmid",
        avatar: "https://i.pravatar.cc/400?img=61",
        tasks: [
            {
                id: '1-ff',
                title: "P-ANL-20222024-01-Montage",
                duration: "6 Tage",
                address: "Hofnerstrasse 4, Haus B, 8888 Unterageri",
                startDate: "2024-02-28",
                endDate: "2024-02-29",
            },
        ],
    },
    {
        id: 6,
        name: "Lucas Aeneas",
        avatar: "https://i.pravatar.cc/400?img=56",
        tasks: [],
    },
    {
        id: 7,
        name: "Arjen Robben",
        avatar: "https://i.pravatar.cc/400?img=55",
        tasks: [
            {
                id: '1-6666f',
                title: "P-ANL-20222024-01-Montage",
                duration: "6 Tage",
                address: "Hofnerstrasse 4, Haus B, 8888 Unterageri",
                startDate: "2024-02-24",
                endDate: "2024-02-26",
            },
        ],
    },
    {
        id: 8,
        name: "Anthony",
        avatar: "https://i.pravatar.cc/400?img=54",
        tasks: [
            {
                id: '1-66eeeeeeeeee66f',
                title: "P-ANL-20222024-01-Montage",
                duration: "6 Tage",
                address: "Hofnerstrasse 4, Haus B, 8888 Unterageri",
                startDate: "2024-02-23",
                endDate: "2024-02-26",
            },
        ],
    },
]);

const backLog = ref([
    {
        id: '1ddffffff-a',
        title: "P-ANL-20222024-01-Montage",
        duration: "6 Tage",
        address: "Hofnerstrasse 4, Haus B, 8888 Unterageri",
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
    for (var i = 0; i < employees.value.length; i++) {
        groups.add({
            id: employees.value[i].id,
            content: {
                name: employees.value[i].name,
                avatar: employees.value[i].avatar
            }
        })
    }

    var items = new DataSet();

    employees.value.forEach(employee => {
        employee.tasks.forEach(task => {
            items.add({
                id: task.id,
                group: employee.id,
                content: {
                    title: task.title,
                    address: task.address,
                },
                start: task.startDate,
                end: task.endDate
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
        editable: true,
        orientation: 'top',
        horizontalScroll: true,
        showWeekScale: true,
        itemsAlwaysDraggable: {
            item: true,
            range: true
        },
        template: function (item, element, data) {
            element.classList.add('task-card');

            return '<p class="text-xs">' + item.content.title + '</p>' + '<p class="text-xs">' + item.content.address + '</p>';
        },
        groupTemplate: function (group, element) {
            element.classList.add('employee');
            return '<div class="employee">' +
                '<img class="employee-avatar" src="' + group.content.avatar + '" alt="Avatar">' +
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
        isTaskFormActive.value = true;
    });

    timeline.value.on('rangechanged', function (properties) {
        var startOfWeek = properties.start;
        weekNumber.value = getWeekNumber(startOfWeek);
    });
}

onMounted(() => {
    initTimeLine();
    weekNumber.value = getWeekNumber(new Date(currentDate.value));
});


</script>

<style scoped></style>
