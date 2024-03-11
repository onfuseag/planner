<template>
    <div class="flex min-h-full flex-col justify-center px-6 py-12 lg:px-8">
        <div class="sm:mx-auto sm:w-full sm:max-w-sm">
            <!-- <img class="mx-auto h-10 w-auto" src="https://tailwindui.com/img/logos/mark.svg?color=indigo&shade=600"
                alt="Your Company"> -->
            <h2 class="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">Sign in to your account
            </h2>
        </div>

        <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
            <form class="space-y-6" @submit.prevent="onSignIn">
                <div class="mb-3">
                    <FormControl :type="'email'" size="md" variant="outline" :disabled="false" label="Email"
                        v-model="email" />
                </div>

                <div class="mb-3">
                    <FormControl :type="'password'" size="md" variant="outline" :disabled="false" label="Password"
                        v-model="password" />
                </div>

                <div>
                    <Button :variant="'solid'" theme="gray" size="md" label="Login" :loadingText="null" :disabled="false"
                        :link="null" iconRight="log-in" :loading="false" class="w-full" type="submit">
                    </Button>
                </div>
            </form>
        </div>
    </div>
</template>
<script setup>
import { ref } from 'vue'
import { FormControl, createResource } from 'frappe-ui'
import { useRouter } from 'vue-router';

const router = useRouter();

let showEmailLogin = ref(false);
let email = ref('admin@planner.com');
let password = ref('adminplanner');

const onSignIn = () => {
    router.push({
        name: 'Dashboard'
    });
}

</script>