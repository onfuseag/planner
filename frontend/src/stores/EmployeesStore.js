import { defineStore } from 'pinia'
import axios from 'axios'
import { ref, computed, reactive } from 'vue'
import { createResource } from 'frappe-ui'

export const EmployeesStore = defineStore('employees-tasks', () => {

    
    const employeesTasks = createResource({
        url: 'planner.api.get_planner_tasks', 
        params : {
            department: "Operations"
        }, 
        auto: true
    });
    console.log(response)
    dataEmployees.value = response.data;
        
   

    const employees = computed(() => employeesTasks.data || [])


    return { employees }

});