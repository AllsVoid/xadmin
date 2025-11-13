<template>
  <div class="gi_page">
    <BasicInfo />
  </div>
</template>

<script setup lang="ts">
import BasicInfo from './BasicInfo.vue'

defineOptions({ name: 'SettingProfile' })
</script>

<style scoped lang="scss">
// 使用项目默认的 gi_page 样式，不需要额外设置背景色
</style>
