<template>
  <div class="tpgen-container">

    <div class="tpgen-main">
      <a-tabs v-model:active-key="activeTab" type="rounded" class="tpgen-tabs" destroy-on-hide>
        <a-tab-pane key="custom" title="自定义测试计划">
          <template #title>
            <icon-settings />
            Generate Test Plan
          </template>
          <!-- <CustomPlan @progress-change="handleProgressChange" /> -->
          <CustomPlan />
        </a-tab-pane>

        
        <a-tab-pane key="upload" title="上传测试计划">
          <template #title>
            <icon-upload />
            Upload Test Plan
          </template>
          <UploadPlan />
        </a-tab-pane>




      </a-tabs>


    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import UploadPlan from './components/UploadPlan.vue'
import CustomPlan from './components/CustomPlan.vue'
import { useTpgenStore } from '@/stores'

defineOptions({ name: 'TPGenOnline' })

const tpgenStore = useTpgenStore()
// const activeTab = ref('upload')
const activeTab = ref('custom')
// const progress = ref(0)

// const handleProgressChange = (val: number) => {
//   progress.value = val
// }

// 如果是编辑模式，自动切换到 Generate Test Plan tab
onMounted(() => {
  if (tpgenStore.editMode) {
    activeTab.value = 'custom'
  }
})
</script>

<style scoped lang="scss">
@import './index.scss';
</style>
