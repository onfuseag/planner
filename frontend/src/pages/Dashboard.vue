<template>
    <Layout :breadcrumbs="breadcrumbs">
        <div class="mx-auto px-4 lg:px-8 max-w-[1800px]">
            <div class="flex flex-col lg:flex-row justify-between items-center my-6">
                <div>
                    <h3 class="text-3xl hidden lg:block">Planner</h3>
                </div>
                <FormControl :type="'text'" size="lg" variant="outline" placeholder="Suchen..." :disabled="false"
                    v-model="search" class="w-full lg:w-2/12">
                    <template #suffix>
                        <FeatherIcon class="w-4" name="search" />
                    </template>
                </FormControl>
            </div>
            <div class="w-6/12 lg:w-2/12">
                <router-link to="/montageansicht">
                    <div class="flex flex-col bg-white p-3 rounded gap-2 shadow-lg w-full">
                        <div class="flex justify-between items-center">
                            <p class="text-sm">Vorgang</p>
                        </div>
                        <div class="flex justify-start items-center">
                            <p class="text-base">Montageansicht</p>
                        </div>
                    </div>
                </router-link>
            </div>
        </div>
    </Layout>
</template>

<script setup>
import Layout from "@/pages/shared/Layout.vue";
import { ref } from "vue";

let breadcrumbs = [
    {
        label: 'Dashboard',
        route: {
            name: 'Dashboard',
        },
    },
];
const search = ref("");

</script>