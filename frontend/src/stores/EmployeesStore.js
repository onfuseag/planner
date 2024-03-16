import { defineStore } from 'pinia'
import axios from 'axios'
import { ref, computed, reactive } from 'vue'

export const EmployeesStore = defineStore('EmployeesStore', () => {

    const dataEmployees = ref();

    const getEmployees = async () => {
        try {
            // just change the API URL to your own
            const response = await axios.get('https://api.npoint.io/0db4abe440e814678410');
            dataEmployees.value = response.data;
        } catch (error) {
            console.error(error);
        }
    };

    // const addEmployess = async (id) => {
    //     try {
    //         const response = await axios.post(`/api/`);
    //         return response;
    //     } catch (error) {
    //         console.error(error);
    //     }
    // };

    return { dataEmployees, getEmployees }

});