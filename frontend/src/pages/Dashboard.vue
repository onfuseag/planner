<template>
    <Layout :breadcrumbs="breadcrumbs">
        <div class="mx-auto px-4 lg:px-8 max-w-[1800px]">
            <div class="flex flex-col lg:flex-row justify-between items-center my-6">
                <div>
                    <h3 class="text-3xl">planner</h3>
                </div>
                <FormControl :type="'text'" size="lg" variant="outline" placeholder="Search..." :disabled="false"
                    v-model="search" class="w-full lg:w-2/12">
                    <template #suffix>
                        <FeatherIcon class="w-4" name="search" />
                    </template>
                </FormControl>
            </div>
            <div class="flex flex-wrap -m-2">
                <div class="w-3/12 lg:w-1/4 p-2" v-for="dashboard in dashboards.data" :key="dashboard.dashboard_name">
                    <router-link :to="{ name: 'Planner', params: { dashboardName: dashboard.dashboard_name, department: dashboard.department }}">
                        <div :style="{ backgroundColor: dashboard.color }" class="flex flex-col bg-white p-4 rounded gap-2 w-full" >
                            <div class="flex justify-between items-center">
                                <p class="text-xs font-semibold">{{ dashboard.dashboard_name }}</p>
                            </div>
                            <div class="flex justify-start items-center">
                                <p class="text-base">{{ dashboard.department }}</p>
                            </div>
                        </div>
                    </router-link>
                </div>
            </div>
        </div>
    </Layout>
</template>

<script setup>
import Layout from "@/pages/shared/Layout.vue";
import { ref } from "vue";
import { createListResource } from 'frappe-ui'

let breadcrumbs = [
    {
        label: 'Dashboard',
        route: {
            name: 'Dashboard',
        },
    },
];
const search = ref("");

const dashboards = createListResource({
  doctype: 'Planner Dashboard', 
  fields: ["dashboard_name", "color", "show_employee_holidays", "department"], 
  auto: true
})

console.log(dashboards)

</script>