<template>
  <a-card class="form-section machine-test-config" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-settings />
        Test Configuration
      </div>
    </template>

    <div v-if="selectedMachines.length === 0" class="empty-tip">
      <a-alert type="info">Please select machines first</a-alert>
    </div>
    
    <div v-else class="machine-configs-wrapper">
      <a-card
        v-for="machineId in selectedMachines"
        :key="machineId"
        class="machine-config-card"
        :bordered="false"
      >
        <template #title>
          <div class="machine-header">
            <icon-desktop />
            <span>{{ getMachineName(machineId) }}</span>
          </div>
        </template>

        <!-- 该机器的所有配置 -->
        <div class="configurations-list">
          <a-collapse
            v-model:active-key="activeKeys[machineId]"
            :bordered="false"
            accordion
            class="config-collapse"
          >
            <a-collapse-item
              v-for="(config, index) in localMachineConfigs[machineId]"
              :key="config.configId"
              :name="config.configId"
              class="config-item"
            >
              <template #header>
                <div class="config-header">
                  <icon-settings />
                  <span>Configuration {{ index + 1 }}</span>
                  <a-tag
                    v-if="config.osFamily"
                    color="blue"
                    size="small"
                  >
                    {{ config.osFamily }} {{ config.osVersion }}
                  </a-tag>
                  <a-tag
                    v-if="config.testTypeName"
                    color="green"
                    size="small"
                  >
                    {{ config.testTypeName }}
                  </a-tag>
                </div>
              </template>
              
              <template #extra>
                <a-space>
                  <a-button
                    type="text"
                    size="small"
                    @click.stop="duplicateConfig(machineId, index)"
                  >
                    <template #icon>
                      <icon-copy />
                    </template>
                  </a-button>
                  <a-button
                    type="text"
                    status="danger"
                    size="small"
                    :disabled="localMachineConfigs[machineId].length <= 1"
                    @click.stop="deleteConfig(machineId, index)"
                  >
                    <template #icon>
                      <icon-delete />
                    </template>
                  </a-button>
                </a-space>
              </template>

              <!-- 配置表单 -->
              <ConfigurationForm
                :config="config"
                :machine-id="machineId"
                @update="(newConfig) => updateConfig(machineId, index, newConfig)"
              />
            </a-collapse-item>
          </a-collapse>

          <!-- 添加新配置按钮 -->
          <a-button
            type="dashed"
            long
            @click="addNewConfig(machineId)"
            class="add-config-btn"
          >
            <template #icon>
              <icon-plus />
            </template>
            Add New Configuration
          </a-button>
        </div>
      </a-card>
    </div>
  </a-card>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { Message } from '@arco-design/web-vue'
import ConfigurationForm from './ConfigurationForm.vue'
import type { MachineConfiguration } from '../types'

defineOptions({ name: 'MachineTestConfig' })

// Props & Emits
const props = defineProps<{
  selectedMachines: number[]
  machinesMap: Record<number, any>
  machineConfigurations: Record<number, MachineConfiguration[]>
}>()

const emit = defineEmits<{
  'update:machineConfigurations': [configs: Record<number, MachineConfiguration[]>]
}>()

// 本地配置数据
const localMachineConfigs = ref<Record<number, MachineConfiguration[]>>({ ...props.machineConfigurations })

// 折叠面板的激活状态
const activeKeys = ref<Record<number, string[]>>({})

// 创建默认配置
function createDefaultConfig(): MachineConfiguration {
  return {
    configId: `config-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    osId: '',
    osFamily: '',
    osVersion: '',
    deploymentMethod: 'bare_metal',
    kernelVersion: '',
    testTypeId: '',
    testTypeName: '',
    testComponents: [],
    orderedTestCases: []
  }
}

// 初始化机器配置（当选中机器变化时）
watch(() => props.selectedMachines, (newMachines) => {
  newMachines.forEach(machineId => {
    if (!localMachineConfigs.value[machineId] || localMachineConfigs.value[machineId].length === 0) {
      // 为新机器添加一个默认配置
      localMachineConfigs.value[machineId] = [createDefaultConfig()]
      // 默认展开第一个配置
      activeKeys.value[machineId] = [localMachineConfigs.value[machineId][0].configId]
    }
  })
  
  // 移除未选中机器的配置
  Object.keys(localMachineConfigs.value).forEach(machineId => {
    if (!newMachines.includes(Number(machineId))) {
      delete localMachineConfigs.value[machineId]
      delete activeKeys.value[machineId]
    }
  })
  
  emitUpdate()
}, { immediate: true })

// 添加新配置
function addNewConfig(machineId: number) {
  if (!localMachineConfigs.value[machineId]) {
    localMachineConfigs.value[machineId] = []
  }
  
  const newConfig = createDefaultConfig()
  localMachineConfigs.value[machineId].push(newConfig)
  
  // 展开新配置
  activeKeys.value[machineId] = [newConfig.configId]
  
  Message.success('Configuration added')
  emitUpdate()
}

// 复制配置
function duplicateConfig(machineId: number, index: number) {
  const original = localMachineConfigs.value[machineId][index]
  const copy: MachineConfiguration = {
    ...JSON.parse(JSON.stringify(original)),
    configId: `config-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }
  
  localMachineConfigs.value[machineId].splice(index + 1, 0, copy)
  
  // 展开复制的配置
  activeKeys.value[machineId] = [copy.configId]
  
  Message.success('Configuration duplicated')
  emitUpdate()
}

// 删除配置
function deleteConfig(machineId: number, index: number) {
  // 至少保留一个配置
  if (localMachineConfigs.value[machineId].length <= 1) {
    Message.warning('At least one configuration is required per machine')
    return
  }
  
  const deletedConfigId = localMachineConfigs.value[machineId][index].configId
  localMachineConfigs.value[machineId].splice(index, 1)
  
  // 如果删除的是当前激活的，则激活第一个
  if (activeKeys.value[machineId]?.includes(deletedConfigId)) {
    activeKeys.value[machineId] = localMachineConfigs.value[machineId].length > 0
      ? [localMachineConfigs.value[machineId][0].configId]
      : []
  }
  
  Message.success('Configuration deleted')
  emitUpdate()
}

// 更新配置
function updateConfig(machineId: number, index: number, newConfig: MachineConfiguration) {
  localMachineConfigs.value[machineId][index] = newConfig
  emitUpdate()
}

// 触发更新
function emitUpdate() {
  emit('update:machineConfigurations', { ...localMachineConfigs.value })
}

// 获取机器名称
function getMachineName(machineId: number) {
  return props.machinesMap[machineId]?.hostname || `Machine ${machineId}`
}

// 监听外部 props 变化
watch(() => props.machineConfigurations, (newConfigs) => {
  localMachineConfigs.value = { ...newConfigs }
}, { deep: true })
</script>

<style scoped lang="scss">
.machine-test-config {
  margin-top: 25px;
}

.machine-configs-wrapper {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 20px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.machine-config-card {
  background: #f7f8fa;
  border: 1px solid #e5e6eb;
  
  :deep(.arco-card-header) {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 16px 20px;
  }
  
  .machine-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    font-size: 15px;
    color: white;
  }
  
  .configurations-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    
    .config-collapse {
      background: transparent;
      
      :deep(.arco-collapse-item) {
        background: white;
        border-radius: 6px;
        border: 1px solid #e5e6eb;
        margin-bottom: 12px;
        transition: all 0.3s;
        
        &:hover {
          border-color: #165dff;
          box-shadow: 0 2px 8px rgba(22, 93, 255, 0.1);
        }
      }
      
      :deep(.arco-collapse-item-header) {
        padding: 12px 16px;
        background: #f7f8fa;
        border-radius: 6px 6px 0 0;
      }
      
      :deep(.arco-collapse-item-content) {
        padding: 20px;
      }
    }
    
    .config-header {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 500;
      color: #1d2129;
    }
    
    .add-config-btn {
      margin-top: 8px;
      border: 2px dashed #d9d9d9;
      color: #165dff;
      font-weight: 500;
      
      &:hover {
        border-color: #165dff;
        background: #f2f7ff;
      }
    }
  }
}

.empty-tip {
  padding: 40px 20px;
  text-align: center;
}
</style>

