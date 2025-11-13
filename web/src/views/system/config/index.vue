<template>
  <div class="table-page">
    <a-row justify="space-between" align="center" class="header page_header">
      <a-space wrap>
        <div class="title">系统配置</div>
      </a-space>
    </a-row>
    <!-- 简化为单个配置页面，移除多余的tab切换 -->
    <BasicSetting />
  </div>
</template>

<script setup lang="ts">
import BasicSetting from './components/BasicSetting.vue'

defineOptions({ name: 'SystemConfig' })
</script>

<style scoped lang="scss">
.table-page {
  overflow-y: auto;
}
</style>
