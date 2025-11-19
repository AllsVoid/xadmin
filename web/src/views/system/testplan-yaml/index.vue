<template>
  <div class="testplan-yaml-container">
    <!-- Upload Section -->
    <a-card title="Upload Test Plan YAML" :bordered="false" class="upload-card">
      <div class="upload-section">
        <a-upload-dragger
          name="file"
          accept=".yaml,.yml"
          :multiple="false"
          :before-upload="handleBeforeUpload"
          :custom-request="handleUpload"
          @change="handleChange"
          class="upload-dragger"
        >
          <p class="ant-upload-drag-icon">
            <CloudUploadOutlined style="font-size: 48px; color: #1890ff" />
          </p>
          <p class="ant-upload-text">Click or drag YAML file to this area to upload</p>
          <p class="ant-upload-hint">
            Support for .yaml or .yml files only. Maximum file size: 5MB
          </p>
        </a-upload-dragger>
        
        <!-- Upload Success Message -->
        <a-alert
          v-if="uploadedFile"
          :message="`${uploadedFile.name} Uploaded Successfully!`"
          :description="`File has been validated and analyzed automatically. (${(uploadedFile.size / 1024).toFixed(2)} KB)`"
          type="success"
          show-icon
          style="margin-top: 16px"
        />
        
        <a-button
          type="primary"
          size="large"
          :loading="analyzing"
          :disabled="!uploadedFile"
          @click="handleAnalyze"
          style="margin-top: 20px; width: 100%"
        >
          <FileSearchOutlined /> Analyze Test Plan
        </a-button>
      </div>
    </a-card>

    <!-- Analysis Results -->
    <a-card
      v-if="analysisResult"
      title="Analysis Results"
      :bordered="false"
      style="margin-top: 20px"
      class="analysis-card"
    >
      <!-- Basic Info -->
      <a-descriptions bordered :column="2" size="small">
        <a-descriptions-item label="File Name">
          {{ analysisResult.file_name }}
        </a-descriptions-item>
        <a-descriptions-item label="Plan Name">
          {{ analysisResult.basic_info?.plan_name || 'N/A' }}
        </a-descriptions-item>
        <a-descriptions-item label="Test Type">
          {{ analysisResult.basic_info?.test_type || 'N/A' }}
        </a-descriptions-item>
        <a-descriptions-item label="CPU">
          {{ analysisResult.basic_info?.cpu || 'N/A' }}
        </a-descriptions-item>
        <a-descriptions-item label="GPU">
          {{ analysisResult.basic_info?.gpu || 'N/A' }}
        </a-descriptions-item>
        <a-descriptions-item label="Validation Status">
          <a-tag :color="getStatusColor(analysisResult.is_valid)">
            {{ analysisResult.is_valid ? 'Valid' : 'Has Issues' }}
          </a-tag>
        </a-descriptions-item>
      </a-descriptions>

      <!-- Statistics -->
      <div class="statistics-section" style="margin-top: 20px">
        <a-row :gutter="16">
          <a-col :span="6">
            <a-statistic
              title="Compatible Machines"
              :value="analysisResult.compatible_count"
              :value-style="{ color: '#3f8600' }"
            >
              <template #prefix>
                <CheckCircleOutlined />
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="Incompatible Machines"
              :value="analysisResult.incompatible_count"
              :value-style="{ color: '#cf1322' }"
            >
              <template #prefix>
                <CloseCircleOutlined />
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="Warnings"
              :value="analysisResult.warning_count"
              :value-style="{ color: '#faad14' }"
            >
              <template #prefix>
                <ExclamationCircleOutlined />
              </template>
            </a-statistic>
          </a-col>
          <a-col :span="6">
            <a-statistic
              title="Errors"
              :value="analysisResult.error_count"
              :value-style="{ color: '#cf1322' }"
            >
              <template #prefix>
                <CloseCircleOutlined />
              </template>
            </a-statistic>
          </a-col>
        </a-row>
      </div>

      <!-- Compatible Machines Section (Always Expanded) -->
      <div style="margin-top: 20px">
        <a-card
          title="Compatible Machines"
          :bordered="false"
          :body-style="{ padding: '12px', backgroundColor: '#f6ffed' }"
        >
          <template #extra>
            <a-tag color="success">{{ compatibleMachines.length }} machine(s)</a-tag>
          </template>
          <p style="color: #666; margin-bottom: 12px">
            The following machines match your test plan requirements:
          </p>
          <a-table
            :columns="machineColumns"
            :data-source="compatibleMachines"
            :pagination="false"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'status'">
                <a-tag color="green">{{ record.status }}</a-tag>
              </template>
            </template>
          </a-table>
        </a-card>
      </div>

      <!-- Incompatible Machines Section (Collapsible, Default Collapsed) -->
      <div style="margin-top: 16px">
        <a-collapse>
          <a-collapse-panel key="incompatible">
            <template #header>
              <span style="font-weight: 600; font-size: 16px">
                <ExclamationCircleOutlined style="color: #faad14; margin-right: 8px" />
                Incompatible Machines ({{ incompatibleMachines.length }})
              </span>
            </template>
            <template #extra>
              <a-tag color="warning">{{ incompatibleMachines.length }} machine(s) do not match requirements. Click to view details.</a-tag>
            </template>
            <div style="background: #fff7e6; padding: 12px; margin-bottom: 12px; border-radius: 4px">
              <p style="margin: 0; color: #666">
                The following machines do not match your test plan requirements:
              </p>
            </div>
            <a-table
              :columns="incompatibleColumns"
              :data-source="incompatibleMachines"
              :pagination="false"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'reasons'">
                  <a-tag v-for="(reason, index) in record.incompatible_reasons" :key="index" color="red">
                    {{ reason }}
                  </a-tag>
                </template>
              </template>
            </a-table>
          </a-collapse-panel>
        </a-collapse>
      </div>

      <!-- Warnings & Errors Section -->
      <div v-if="errors.length > 0 || warnings.length > 0" style="margin-top: 16px">
        <a-card title="Warnings & Errors" :bordered="false">
          <a-alert
            v-for="(error, index) in errors"
            :key="`error-${index}`"
            :message="error"
            type="error"
            show-icon
            style="margin-bottom: 10px"
          />
          <a-alert
            v-for="(warning, index) in warnings"
            :key="`warning-${index}`"
            :message="warning"
            type="warning"
            show-icon
            style="margin-bottom: 10px"
          />
        </a-card>
      </div>

      <!-- YAML Comparison Section -->
      <div style="margin-top: 16px">
        <a-card title="YAML Comparison & Validation" :bordered="false">
          <a-button type="primary" @click="loadComparison" style="margin-bottom: 10px">
            <FileTextOutlined /> View Detailed Comparison
          </a-button>
          
          <div v-if="comparisonData" class="comparison-container">
            <a-row :gutter="16">
              <a-col :span="12">
                <h4>Standard Template</h4>
                <pre class="yaml-display">{{ comparisonData.template_yaml }}</pre>
              </a-col>
              <a-col :span="12">
                <h4>Your Uploaded YAML</h4>
                <pre class="yaml-display">{{ comparisonData.user_yaml }}</pre>
              </a-col>
            </a-row>
            
            <div v-if="comparisonData.missing_fields?.length > 0" style="margin-top: 20px">
              <a-alert
                message="Missing Fields"
                :description="comparisonData.missing_fields.join(', ')"
                type="error"
                show-icon
              />
            </div>
          </div>
        </a-card>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  CloudUploadOutlined,
  FileSearchOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  FileTextOutlined
} from '@ant-design/icons-vue'
import { testPlanYamlApi } from '@/apis/system/test-plan-yaml'

// 状态
const uploadedFile = ref<File | null>(null)
const analyzing = ref(false)
const analysisResult = ref<any>(null)
const comparisonData = ref<any>(null)
const recordId = ref<number | null>(null)

// 计算属性
const compatibleMachines = computed(() => analysisResult.value?.compatible_machines || [])
const incompatibleMachines = computed(() => analysisResult.value?.incompatible_machines || [])
const warnings = computed(() => analysisResult.value?.warnings || [])
const errors = computed(() => analysisResult.value?.errors || [])

// 表格列定义
const machineColumns = [
  { title: 'Name', dataIndex: 'name', key: 'name' },
  { title: 'Motherboard', dataIndex: 'motherboard', key: 'motherboard' },
  { title: 'CPU', dataIndex: 'cpu', key: 'cpu' },
  { title: 'GPU', dataIndex: 'gpu', key: 'gpu' },
  { title: 'Status', dataIndex: 'status', key: 'status' }
]

const incompatibleColumns = [
  { title: 'Name', dataIndex: 'name', key: 'name' },
  { title: 'Motherboard', dataIndex: 'motherboard', key: 'motherboard' },
  { title: 'CPU', dataIndex: 'cpu', key: 'cpu' },
  { title: 'GPU', dataIndex: 'gpu', key: 'gpu' },
  { title: 'Reasons', key: 'reasons' }
]

// 文件上传前的验证
const handleBeforeUpload = (file: File) => {
  const isYaml = file.name.endsWith('.yaml') || file.name.endsWith('.yml')
  if (!isYaml) {
    message.error('You can only upload YAML files!')
    return false
  }
  
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    message.error('File must be smaller than 5MB!')
    return false
  }
  
  uploadedFile.value = file
  return false // 阻止自动上传
}

// 自定义上传
const handleUpload = async (options: any) => {
  // 阻止默认上传行为
  return false
}

// 文件变化处理
const handleChange = (info: any) => {
  if (info.file.status === 'removed') {
    uploadedFile.value = null
    analysisResult.value = null
    comparisonData.value = null
    recordId.value = null
  }
}

// 分析处理
const handleAnalyze = async () => {
  if (!uploadedFile.value) {
    message.warning('Please upload a YAML file first!')
    return
  }
  
  analyzing.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    
    const response = await testPlanYamlApi.upload(formData)
    
    if (response.code === 200) {
      message.success(`${uploadedFile.value.name} analyzed successfully!`)
      recordId.value = response.data.id
      
      // 加载详细分析结果
      await loadAnalysis(response.data.id)
    } else {
      message.error(response.message || 'Analysis failed!')
    }
  } catch (error: any) {
    console.error('Analysis error:', error)
    message.error(error.message || 'Failed to analyze file')
  } finally {
    analyzing.value = false
  }
}

// 加载分析结果
const loadAnalysis = async (id: number) => {
  try {
    const response = await testPlanYamlApi.getAnalysis(id)
    
    if (response.code === 200) {
      analysisResult.value = response.data
    } else {
      message.error(response.message || 'Failed to load analysis result')
    }
  } catch (error: any) {
    console.error('Load analysis error:', error)
    message.error('Failed to load analysis result')
  }
}

// 加载对比结果
const loadComparison = async () => {
  if (!recordId.value) {
    message.warning('No record ID available')
    return
  }
  
  try {
    const response = await testPlanYamlApi.getComparison(recordId.value)
    
    if (response.code === 200) {
      comparisonData.value = response.data
      message.success('Comparison loaded successfully!')
    } else {
      message.error(response.message || 'Failed to load comparison')
    }
  } catch (error: any) {
    console.error('Load comparison error:', error)
    message.error('Failed to load comparison')
  }
}

// 获取状态颜色
const getStatusColor = (isValid: boolean) => {
  return isValid ? 'success' : 'error'
}
</script>

<style scoped lang="less">
.testplan-yaml-container {
  padding: 20px;
  
  .upload-card {
    .upload-section {
      max-width: 600px;
      margin: 0 auto;
    }
    
    .upload-dragger {
      border: 2px dashed #d9d9d9;
      border-radius: 8px;
      background: #fafafa;
      transition: all 0.3s;
      
      &:hover {
        border-color: #1890ff;
        background: #e6f7ff;
      }
    }
  }
  
  .analysis-card {
    .statistics-section {
      background: #f5f5f5;
      padding: 20px;
      border-radius: 8px;
    }
  }
  
  .comparison-container {
    .yaml-display {
      background: #f5f5f5;
      padding: 15px;
      border-radius: 4px;
      border: 1px solid #d9d9d9;
      max-height: 500px;
      overflow: auto;
      font-family: 'Courier New', monospace;
      font-size: 12px;
      line-height: 1.5;
    }
  }
}
</style>

