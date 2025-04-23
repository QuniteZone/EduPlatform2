import { defineStore } from 'pinia';

export const useContentStore = defineStore('content', {
    state: () => ({
        previewContent: '', // 存储预览内容
    }),
    actions: {
        setPreviewContent(content) {
            this.previewContent = content;
        },
    },
});