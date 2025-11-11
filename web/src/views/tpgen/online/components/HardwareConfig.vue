<template>
  <a-card class="form-section" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-cpu />
        Hardware Platform Configuration
      </div>
    </template>

    <!-- <a-form-item label="CPU Model" field="cpu">
      <a-select v-model="localCpu" placeholder="Select CPU" @change="handleUpdate">
        <a-option v-for="option in cpuOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </a-option>
      </a-select>
    </a-form-item> -->

    <a-form-item label="AMD GPU Product Line" field="gpu">
      <a-select 
        v-model="localGpu" 
        placeholder="Select GPU" 
        :loading="gpuLoading"
        @change="handleUpdate"
      >
        <a-option 
          v-for="option in gpuOptions" 
          :key="option.value" 
          :value="option.value"
        >
          {{ option.label }}
        </a-option>
      </a-select>
    </a-form-item>




    <a-form-item label="Available Test Machines">
      <div v-if="filteredMachines.length === 0" class="no-machines">
        <a-empty description="No machines match the selected criteria" />
      </div>
      <div v-else class="machine-list">
        <div
          v-for="machine in filteredMachines"
          :key="machine.id"
          class="machine-card"
          :class="{ selected: localSelectedMachines.includes(machine.id) }"
          @click="toggleMachine(machine.id)"
        >
          <h4>{{ machine.name }}</h4>
          <p><strong>Motherboard:</strong> {{ machine.motherboard }}</p>
          <p><strong>GPU:</strong> {{ machine.gpu }}</p>
          <p><strong>CPU:</strong> {{ machine.cpu }}</p>
          <a-tag :color="machine.status === 'Available' ? 'green' : 'red'">
            {{ machine.status }}
          </a-tag>
        </div>
      </div>
    </a-form-item>
  </a-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { getGpuOptions } from '@/apis/sutDevice'
import { Message } from '@arco-design/web-vue'

defineOptions({ name: 'HardwareConfig' })

const props = defineProps<{
  cpu: string
  gpu: string
  selectedMachines: number[]
}>()

const emit = defineEmits<{
  'update:cpu': [value: string]
  'update:gpu': [value: string]
  'update:selectedMachines': [value: number[]]
  'update': []
}>()

// CPU 选项（静态数据）
const cpuOptions = ref([
  { label: 'Ryzen Threadripper', value: 'Ryzen Threadripper' },
  { label: 'Intel Xeon', value: 'Intel Xeon' },
  { label: 'AMD EPYC', value: 'AMD EPYC' },
])

// GPU 选项改为响应式数据
const gpuOptions = ref<Array<{label: string, value: string}>>([])
const gpuLoading = ref(false)

// Mock machines 数据（临时使用，后续可以改为API获取）
const mockMachines = ref<Array<{
  id: number
  name: string
  motherboard: string
  gpu: string
  cpu: string
  status: string
}>>([
  {
    id: 1,
    name: 'Test Machine 1',
    motherboard: 'ASUS X670E',
    gpu: 'Radeon RX 7900 Series',
    cpu: 'Ryzen Threadripper',
    status: 'Available'
  },
  {
    id: 2,
    name: 'Test Machine 2',
    motherboard: 'MSI B550',
    gpu: 'Radeon RX 6800',
    cpu: 'Ryzen Threadripper',
    status: 'Available'
  },
])


const localCpu = computed({
  get: () => props.cpu,
  set: val => emit('update:cpu', val),
})

const localGpu = computed({
  get: () => props.gpu,
  set: val => emit('update:gpu', val),
})

const localSelectedMachines = computed({
  get: () => props.selectedMachines,
  set: val => emit('update:selectedMachines', val),
})

// 新增：加载 GPU 选项的函数
const loadGpuOptions = async () => {
  gpuLoading.value = true
  try {
    const options = await getGpuOptions()
    gpuOptions.value = options
    console.log('[HardwareConfig] GPU 选项加载成功:', options)
    
    // 如果当前没有选中值，或者当前值不在新的选项列表中，自动选择第一个
    if (options.length > 0) {
      const currentValueExists = options.some(opt => opt.value === localGpu.value)
      if (!localGpu.value || !currentValueExists) {
        localGpu.value = options[0].value
        console.log('[HardwareConfig] 自动选择第一个 GPU 选项:', options[0].value)
      }
    }
  } catch (error) {
    console.error('[HardwareConfig] 加载 GPU 选项失败:', error)
    Message.error('加载 GPU 选项失败')
    gpuOptions.value = []
  } finally {
    gpuLoading.value = false
  }
}


// 根据 CPU 和 GPU 过滤机器
const filteredMachines = computed(() => {
  return mockMachines.value.filter((machine) => {
    const cpuMatch = !localCpu.value || machine.cpu === localCpu.value
    const gpuMatch = !localGpu.value || machine.gpu === localGpu.value
    return cpuMatch && gpuMatch
  })
})

// 切换机器选择
const toggleMachine = (id: number) => {
  const index = localSelectedMachines.value.indexOf(id)
  if (index === -1) {
    localSelectedMachines.value = [...localSelectedMachines.value, id]
  }
  else {
    localSelectedMachines.value = localSelectedMachines.value.filter(mid => mid !== id)
  }
  handleUpdate()
}

const handleUpdate = () => {
  emit('update')
}
// 组件挂载时加载 GPU 选项
onMounted(() => {
  loadGpuOptions()
})
// 监听 CPU/GPU 变化，重新过滤选中的机器
watch([localCpu, localGpu], () => {
  const validMachineIds = filteredMachines.value.map(m => m.id)
  localSelectedMachines.value = localSelectedMachines.value.filter(id => validMachineIds.includes(id))
})
</script>

<style scoped lang="scss">
.form-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  border-left: 5px solid #3498db;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;

    .arco-icon {
      color: #3498db;
      background: #f8f9fa;
      padding: 8px;
      border-radius: 8px;
    }
  }
}

.no-machines {
  padding: 40px;
  text-align: center;
}

.machine-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 15px;

  .machine-card {
    border: 2px solid #e1e5eb;
    border-radius: 12px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: white;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: #3498db;
      transform: scaleX(0);
      transition: all 0.3s ease;
    }

    &:hover {
      border-color: #3498db;
      transform: translateY(-5px);
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);

      &::before {
        transform: scaleX(1);
      }
    }

    &.selected {
      border-color: #3498db;
      background: rgba(52, 152, 219, 0.05);
      box-shadow: 0 5px 15px rgba(52, 152, 219, 0.2);

      &::before {
        transform: scaleX(1);
        background: #27ae60;
      }
    }

    h4 {
      margin: 0 0 10px 0;
      color: #2c3e50;
      font-size: 1.3rem;
    }

    p {
      margin: 8px 0;
      color: #555;
      font-size: 0.9rem;
    }
  }
}

@media (max-width: 768px) {
  .machine-list {
    grid-template-columns: 1fr;
  }
}
</style>

