import { defineStore } from 'pinia'
import axios from 'axios'
import { ref, computed, reactive } from 'vue'

export const AuthStore = defineStore('AuthStore', () => {

    const token = ref();
    const isAuthenticated = ref(false);

    return { token, isAuthenticated };
}, {
    persist: {
        storage: localStorage,
    }
});