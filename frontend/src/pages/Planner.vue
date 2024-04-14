<template>
    <Layout :breadcrumbs="breadcrumbs">
        <div class="mx-auto px-4 lg:px-8 max-w-[1800px]">
            <div class="flex justify-between items-center mb-3 sticky top-0" ref="timelineInfoRef">
                <div class="flex gap-x-2">
                    <Button :variant="'solid'" theme="gray" size="md" label="Button" id="buttonPrev">
                        Prev
                    </Button>
                    <div class="bg-white py-1 px-3 rounded">
                        KW{{ weekNumber }}
                    </div>
                    <Button :variant="'solid'" theme="gray" size="md" label="Button" id="buttonNext">
                        Next
                    </Button>
                </div>
                <div class="flex gap-x-2">
                    <Button :variant="'solid'" theme="gray" size="md" label="Button" :loadingText="null"
                        :disabled="false" :link="null" icon="refresh-cw" :loading="false"
                        @click="getEmployeeTasks(); getBacklogTasks();">
                    </Button>
                    <div class="bg-white py-1 px-3 rounded">     
                        {{ department }}
                    </div>
                </div>
            </div>
            <div class="flex flex-col lg:flex-row justify-between items-start gap-6">
                <div class="w-full lg:w-9/12">
                    <div class="bg-white rounded p-2">

                        <div ref="timeline" id="timeline"></div>

                    </div>
                </div>
                <div class="w-full lg:w-3/12 sticky top-16">
                    <div class="bg-white rounded p-3">
                        <template v-if="!isTaskFormActive">
                            <div class="p-0">
                                <TextInput class="p-1" type="text" placeholder="Search ..." v-model="searchText" @keyup.enter="getBacklogTasks">
                                    <template #suffix>
                                    <FeatherIcon
                                        class="w-4"
                                        name="search"
                                        @click="getBacklogTasks"
                                    />
                                    </template>
                                </TextInput>

                                <TextInput class="p-1" type="text" placeholder="Project ..." v-model="projectText" @keyup.enter="getBacklogTasks">
                                    <template #suffix>
                                    <FeatherIcon
                                        class="w-4"
                                        name="search"
                                        @click="getBacklogTasks"
                                    />
                                    </template>
                                </TextInput>
                            </div>
                            <br>
                            <p class="text-lg mb-3">Backlog</p>
                            <div class="grid grid-rows gap-3 mb-3">
                                <div class="flex flex-col bg-gray-200 p-3 rounded gap-2 cursor-grab select-none"
                                    v-for="task in backlog" :key="task.name" @click="openTaskDetail(task.name)" draggable="true"
                                    @dragstart="dragBackLog($event, task)" :style="{ backgroundColor: task.color }">
                                    <div :id="task.name" class="flex justify-between items-center" >
                                        <div>
                                            <p v-if="task.project" class="leading-4 text-xs">{{ task.project }}</p>
                                            <p class="leading-4 text-sm font-bold">{{ task.subject }}</p>
                                            <p class="leading-4 text-sm">{{ task.expected_time }} h</p>
                                            <p class="leading-4 text-sm">{{ task.project_name }}</p>
                                        </div>

                                        <div class="text-right">
                                            <p class="text-xs">{{ task.priority }}</p>
                                            <p class="text-xs font-semibold">{{ task.exp_start_date }}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <div class="mb-3 flex justify-between items-center">
                                <a target=”_blank” :href="getURL() + '/app/task/' + activeTask" class="text-blue-700">{{ activeTask }}</a>
                                <Button :variant="'solid'" theme="gray" size="sm" label="Button" :loadingText="null"
                                    :disabled="false" :link="null" icon="arrow-left" :loading="false"
                                    @click="backToBackLog">
                                </Button>
                            </div>
                            <TaskForm :task='activeTask' :department='department' />
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </Layout>
</template>

<script setup>
import Layout from "@/pages/shared/Layout.vue";
import { computed, ref, onMounted, watchEffect, reactive  } from "vue";
import TaskForm from "@/components/Task/TaskForm.vue";
import { Timeline, DataSet } from 'vis-timeline/standalone';
import { useRoute } from 'vue-router';
import { createResource, createListResource, Avatar } from 'frappe-ui'
import { getURL } from '../getURL.js' 


const route = useRoute(); // Access to the current route
const searchText = defineModel('searchText')
const projectText = defineModel('projectText')

// The employees with all tasks
var employees = {}

// All the tasks in backlog
var backlog = reactive([]);

const getBacklogTasks = () => {
    const resp = createResource({
        url: 'planner.api.planner_get_backlog', 
        params : {
            searchtext: searchText.value, 
            projectText: projectText.value
        }, 
        auto: true,
        onSuccess:(data) => {
            // Clear backlog array
            backlog.splice(0);

            // Push new items into the backlog array
            data.forEach(task => {
                backlog.push(task);
            });
        }
    });

}

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
let activeTask = ref("");
let weekNumber = ref(0);

const timeline = ref();

const openTaskDetail = (taskName) => {
    activeTask = taskName // Ensure to set the current task first
    isTaskFormActive.value = true;
};

const dragEndBackLog = (val) => {
    console.log("drop")
    console.log(val)
}

const dragBackLog = (event, task) => {

    event.dataTransfer.effectAllowed = 'move';

    var tasktitle = "" 

    if (task.project) {
        tasktitle = task.project + ' - ' + task.subject
    } else {
        tasktitle = task.subject
    }

    let item = {
        id: task.name,
        name: task.name,
        type: 'range',
        content: {
            name: task.name,
            title: tasktitle, 
            project_name: task.project_name, 
            type: task.type
        }
    };

    console.log("Task: ", task)

    event.target.id = item.id; 
    console.log("Task:0")

    let startDateTime = new Date(currentDate.value);
    startDateTime.setHours(0, 0, 0, 0);
    item.content.startDate = startDateTime.toLocaleDateString('de-DE'); 

    console.log("Task:2")

    let endDateTime = new Date(currentDate.value.setDate(currentDate.value.getDate() + 2));

    endDateTime.setHours(0, 0, 0, 0);
    item.content.endDate = endDateTime.toLocaleDateString('de-DE'); 

    console.log("Task:3")
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

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const formattedDate = date.toISOString().split('T')[0];
  return formattedDate;
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
    // Get the div element by its ref attribute
    const timelineDiv = document.getElementById('timeline');

    // Check if the div element exists
    if (timelineDiv) {
        // Empty the div by setting its innerHTML to an empty string
        timelineDiv.innerHTML = '';
    } else {
        console.error('Div element with ref "timeline" not found.');
    }

    var groups = new DataSet()
    for (var i = 0; i < employees.length; i++) {

        groups.add({
            id: employees[i].user_id,
            content: {
                name: employees[i].employee_name,
                image: employees[i].image === null ? null : getURL() + employees[i].image
            }
        })
    }

    var items = new DataSet();

    employees.forEach(employee => {
        employee.tasks.forEach(task => {
            items.add({
                id: task.name + "!" + Math.random().toString(16).slice(2), // need to make this random
                name: task.name,
                group: employee.user_id,
                content: {
                    title: task.title,
                    project_name: task.project_name,
                    type: task.type, 
                    owner: employee.user_id
                },
                start: task.startDate,
                end: task.endDate,
                editable : task.type == 1, 
                style: "background-color: " + task.color + ";" // Make sure it is colored right
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
            add: true,         // add new items by double tapping
            updateTime: true,  // drag items horizontally
            updateGroup: false, // drag items from one group to another
            remove: true,       // delete an item by tapping the delete button top right
            overrideItems: false  // allow these options to override item.editable
        },
        orientation: 'top',
        horizontalScroll: true,
        showWeekScale: true,
        itemsAlwaysDraggable: {
            item: true,
            range: true
        },
        format: {
            majorLabels: function (date, scale, step) {
                let dateObj = new Date(date);
                let monthName = dateObj.toLocaleString('default', { month: 'long' });
                return monthName + ' ' + 'KW' + getWeekNumber(dateObj);
            }
        },
        margin: {
            axis: 5,  
        },
        onMove: function (item, callback) {

            // If the user moves it to another user
            if (item.content.owner != item.group) {
                callback(null); // cancel updating the item
                console.log("Dragged into another timeline")
                return;
            }
            
            var start_date = new Date(item.start)
            start_date.setDate(start_date.getDate() + 1) // Add one because the format option counts wrong

            createResource({
                url: 'planner.api.planner_change_date_task', 
                params: {
                    task : item.name, 
                    exp_start_date: formatDate(start_date), 
                    exp_end_date: formatDate(new Date(item.end))
                }, 
                auto: true,
                onSuccess: () =>  {
                    callback(item); // send back adjusted item
                }, 
                onError: () =>  {
                    callback(null); // cancel updating the item
                }
            })
        },
        onAdd: function (item, callback) {
            var assignees = [item.group]

            createResource({
                url: 'frappe.desk.form.assign_to.add', 
                params: {
                    doctype: "Task", 
                    name: item.content.name, 
                    description: item.content.subject, 
                    assign_to: assignees, 
                    bulk_assign: false
                }, 
                auto: true,
                onSuccess: () =>  {
                    // So we can change the length afterwards
                    item.content.owner = item.group;
                    
                    callback(item); // send back adjusted item
                    // We now need to update the item to accept the new dates

                    var start_date = new Date(item.start)
                    start_date.setDate(start_date.getDate() + 1) // Add one because the format option counts wrong

                    var end_date = new Date(item.start)
                    end_date.setDate(end_date.getDate() + 2) // Add two for visibility

                    createResource({
                        url: 'planner.api.planner_change_date_task', 
                        params: {
                            task : item.content.name, 
                            exp_start_date: formatDate(start_date), 
                            exp_end_date: formatDate(end_date)
                        }, 
                        auto: true,
                        onSuccess: () =>  {
                            console.log("Success")
                        }
                    })
                }, 
                onError: () =>  {
                    callback(null); // cancel updating the item
                }
            })
            
        },
        template: function (item, element, data) {
            element.classList.add('task-card');
            element.parentNode.parentNode.setAttribute('task-type', item.content.type);
            return '<p class="text-xs">' + item.content.title + '</p>' + '<p class="text-xs">' + item.content.project_name + '</p>';
        },
        groupTemplate: function (group, element) {
            element.classList.add('employee');
            var templateimage = ""
            if (group.content.image) {
                templateimage = '<img class="employee-avatar" src="' + group.content.image + '" alt="Avatar">'
            }
            return '<div class="employee">' +
                templateimage +
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
    var container = document.getElementById('timeline');
    var timeline = new Timeline(container, items, groups, options);

    timeline.on('select', function (properties) {
        if(properties.items.length > 0) {
            activeTask = properties.items[0].substring(0,properties.items[0].indexOf("!"))
            isTaskFormActive.value = true;
            
        } else {
            isTaskFormActive.value = false;
        }
    });

    timeline.on('rangechanged', function (properties) {
        var startOfWeek = properties.start;
        weekNumber.value = getWeekNumber(startOfWeek);
        setTimeout(function () {
            var element = document.querySelector(".vis-panel.vis-top");
            if (element && element.classList.contains('scroll')) {
                element.style.top = (window.scrollY - 135) + 'px';
            }
        }, 100);
    });

    document.getElementById('buttonNext').onclick = function () {
        var currentStart = timeline.getWindow().start;
        var nextWeekStart = new Date(currentStart);
        nextWeekStart.setDate(nextWeekStart.getDate() + 7);
        var nextWeekEnd = new Date(nextWeekStart);
        nextWeekEnd.setDate(nextWeekEnd.getDate() + 6);
        timeline.setWindow(nextWeekStart, nextWeekEnd);
    };

    document.getElementById('buttonPrev').onclick = function () {
        var currentStart = timeline.getWindow().start;
        var prevWeekStart = new Date(currentStart);
        prevWeekStart.setDate(prevWeekStart.getDate() - 7);
        var prevWeekEnd = new Date(prevWeekStart);
        prevWeekEnd.setDate(prevWeekEnd.getDate() + 6);
        timeline.setWindow(prevWeekStart, prevWeekEnd);
    };

}

const getEmployeeTasks = () => {
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

}

const timelineInfoRef = ref();

onMounted(() => {

    searchText.value ="";
    projectText.value ="";

    getEmployeeTasks();

    getBacklogTasks();
    
    weekNumber.value = getWeekNumber(new Date(currentDate.value));
    var element = document.querySelector(".vis-panel.vis-top");
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            timelineInfoRef.value.classList.add('scrolled');
        } else {
            timelineInfoRef.value.classList.remove('scrolled');
        }
        if (window.scrollY > 200) {
            if (element) {
                element.classList.add('scroll');
                element.style.top = (window.scrollY - 135) + 'px';
            }
        } else {
            if (element) {
                element.classList.remove('scroll');
                element.style.top = '0px';
            }
        }
    });
});


</script>

<style scoped>
.scrolled {
    background-color: #fff;
    z-index: 999;
    padding: 0.5rem 1rem;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    border-radius: 0 0 0.5rem 0.5rem;
    transition: all 0.3s ease;
}
</style>
