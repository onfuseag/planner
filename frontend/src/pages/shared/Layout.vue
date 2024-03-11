<template>
    <div class="wrapper">
        <nav class="bg-white border-b">
            <div class="mx-auto px-4 lg:px-8 max-w-[1800px]">
                <div class="flex justify-end items-center h-12">
                    <Button :variant="'solid'" theme="red" size="md" label="Button" :loadingText="null" :disabled="false"
                        :link="null" icon="log-out" :loading="false" @click="onSignOut">
                    </Button>
                </div>
            </div>
        </nav>
    </div>
    <div class="p-1 bg-white mb-8">
        <div class="mx-auto px-4 lg:px-8 max-w-[1800px]">
            <Breadcrumbs :items="props.breadcrumbs" />
        </div>
    </div>
    <div class="content-wrapper">
        <slot />
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
const props = defineProps({
    breadcrumbs: {
        type: Array,
    },
});

const onSignOut = () => {
    router.push({ name: 'SignIn' });
}
</script>

<style scoped></style>