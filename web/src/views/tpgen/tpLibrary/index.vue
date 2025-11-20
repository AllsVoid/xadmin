<template>
  <div class="table-page">
    <a-row justify="space-between" align="center" class="header page_header">
      <a-space wrap>
        <div class="title">Test Plan Library</div>
      </a-space>
    </a-row>

    <a-row class="h-full page_content">
      <a-col :span="24" class="h-full ov-hidden">
        <LibraryTable
          v-model:query-form="queryForm"
          v-model:selected-keys="selectedKeys"
          :data-list="dataList"
          :loading="loading"
          :pagination="pagination"
          @refresh="search"
          @search="search"
          @reset="reset"
          @batch-delete="onBatchDelete"
          @preview="onPreview"
          @copy="onCopy"
          @update="onUpdate"
          @delete="onDelete"
        />
      </a-col>
    </a-row>

    <!-- 预览抽屉 -->
    <PlanPreviewDrawer
      v-model="previewDrawerVisible"
      :record="currentRecord"
    />
  </div>
</template>

<script setup lang="ts">
import LibraryTable from './components/LibraryTable.vue'
import PlanPreviewDrawer from '../myTP/components/PlanPreviewDrawer.vue'
import { usePlanCopy, usePlanData, usePlanDelete, usePlanEdit, usePlanPreview } from './composables/usePlanData'
import { useResetReactive } from '@/hooks'

defineOptions({ name: 'TpgenTpLibrary' })

// 查询表单
const [queryForm, resetForm] = useResetReactive({
  sort: ['createTime,desc'],
})

// 数据管理 - 只显示公共测试计划（status=2）
const { loading, dataList, pagination, selectedKeys, search, refresh } = usePlanData(queryForm)

// 重置
const reset = () => {
  resetForm()
  search()
}

// 预览功能
const { previewDrawerVisible, currentRecord, onPreview } = usePlanPreview()

// 复制功能
const { onCopy } = usePlanCopy(refresh)

// 编辑功能（仅管理员）
const { onUpdate } = usePlanEdit(search)

// 删除功能（仅管理员）
const { onDelete, onBatchDelete } = usePlanDelete(refresh, selectedKeys)

// 初始化
onMounted(() => {
  search()
})
</script>

<style scoped lang="scss">
@import './index.scss';
</style>

