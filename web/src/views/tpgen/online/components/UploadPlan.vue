<template>
  <div class="upload-plan">
    <a-card class="form-section" :bordered="false">
      <template #title>
        <div class="section-title" style="display: none;">
          <icon-file-add />
          Upload Your Test Plan
        </div>
      </template>

      <div
        class="upload-area"
        :class="{ dragover: isDragOver }"
        @click="handleClickUpload"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleDrop"
      >
        <icon-cloud-upload :size="48" />
        <h3>Upload YAML Test Plan</h3>
        <p>Drag & drop your YAML file here or click to browse</p>
        <input
          ref="fileInputRef"
          type="file"
          accept=".yaml,.yml"
          style="display: none"
          @change="handleFileChange"
        >
      </div>

      <div v-if="uploadedFile" class="file-info">
        <div class="success-message">
          <div class="success-header">
            <icon-check-circle />
            <strong>{{ uploadedFile.name }} Uploaded Successfully!</strong>
          </div>
          <div class="success-details">
            Size: {{ formatFileSize(uploadedFile.size) }}
          </div>
        </div>
      </div>

      <div v-if="validationResults.length > 0" class="validation-results">
        <h3>Test Plan Analysis Result</h3>
        
        <!-- Error Summary (Collapsible) -->
        <div v-if="errorSummary.length > 0" class="error-summary">
          <a-collapse
            :default-active-key="[]"
            expand-icon-position="right"
            :bordered="false"
          >
            <a-collapse-item key="errors" class="error-collapse-item">
              <template #header>
                <div class="error-header">
                  <icon-close-circle />
                  <strong>YAML Syntax Error: YAML validation failed ({{ errorSummary.length }} errors detected)</strong>
                </div>
              </template>
              <ul class="error-list">
                <li v-for="(error, index) in errorSummary" :key="index">
                  Line {{ error.line }} [ERROR] --- {{ error.message }}
                </li>
              </ul>
            </a-collapse-item>
          </a-collapse>
        </div>

        <!-- File Content with Error Highlighting -->
        <div v-if="fileContent.length > 0" class="file-content-section">
          <a-collapse
            :default-active-key="['file-content']"
            expand-icon-position="right"
            :bordered="false"
          >
            <a-collapse-item key="file-content" class="file-content-collapse-item">
              <template #header>
                <div class="file-content-header-wrapper">
                  <div class="file-content-title">
                    <icon-file />
                    <strong>File Content (errors highlighted in red):</strong>
                  </div>
                  <a-button
                    type="text"
                    size="small"
                    class="copy-button"
                    @click.stop="handleCopyFileContent"
                  >
                    <template #icon><icon-copy /></template>
                    Copy
                  </a-button>
                </div>
              </template>
              <div class="file-content-box">
                <div
                  v-for="(line, index) in fileContent"
                  :key="index"
                  class="code-line"
                  :class="{ 
                    'error-line': errorLines.includes(index + 1),
                    'comment-line': line.trim().startsWith('#')
                  }"
                >
                  <span class="line-number">{{ index + 1 }}</span>
                  <pre class="line-content">{{ line || ' ' }}<span v-if="getErrorMessage(index + 1)" class="error-comment">{{ getErrorMessage(index + 1) }}</span></pre>
                </div>
              </div>
            </a-collapse-item>
          </a-collapse>
        </div>
        
        <div
          v-for="(result, index) in validationResults"
          v-show="result.title || result.message"
          :key="index"
          class="validation-item"
          :class="result.type"
        >
          <component :is="getResultIcon(result.type)" />
          <div>
            <strong>{{ result.title }}</strong>
            <p v-if="result.message">{{ result.message }}</p>
            <ul v-if="result.items && result.items.length > 0">
              <li v-for="(item, idx) in result.items" :key="idx">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="actions">
        <a-button
          type="primary"
          :disabled="!uploadedFile"
          :loading="analyzing"
          @click="handleAnalyze"
        >
          <template #icon><icon-search /></template>
          Analyze Test Plan
        </a-button>
        <a-button
          v-if="errorSummary.length > 0"
          type="outline"
          @click="handleDownloadYaml"
        >
          <template #icon><icon-download /></template>
          Download YAML
        </a-button>
      </div>
    </a-card>

    <!-- 分析结果详情 -->
    <a-card v-if="analysisResult" class="form-section analysis-output" :bordered="false">
      <template #title>
        <div class="section-title">
          <icon-bar-chart />
          Analysis Results
        </div>
      </template>

      <!-- 兼容的机器 -->
      <div v-if="analysisResult.compatibleMachines.length > 0" class="analysis-section">
        <div class="machine-section-wrapper">
          <a-collapse
            :default-active-key="['compatible']"
            expand-icon-position="right"
            :bordered="false"
          >
            <a-collapse-item key="compatible" class="compatible-collapse-item">
              <template #header>
                <div class="section-header">
                  <icon-check-circle />
                  <strong>Compatible Machines ({{ analysisResult.compatibleMachines.length }})</strong>
                </div>
              </template>
              <div class="section-description">
                The following machines match your test plan requirements:
              </div>
              <div class="machine-grid">
                <div
                  v-for="machine in analysisResult.compatibleMachines"
                  :key="machine.id"
                  class="machine-card compatible"
                >
                  <h4>{{ machine.name }}</h4>
                  <p><strong>Motherboard:</strong> {{ machine.motherboard }}</p>
                  <p><strong>GPU:</strong> {{ machine.gpu }}</p>
                  <p><strong>CPU:</strong> {{ machine.cpu }}</p>
                  <a-tag color="green">Compatible</a-tag>
                </div>
              </div>
            </a-collapse-item>
          </a-collapse>
        </div>
      </div>

      <!-- 不兼容的机器 -->
      <div v-if="analysisResult.incompatibleMachines.length > 0" class="analysis-section">
        <div class="machine-section-wrapper">
          <a-collapse
            :default-active-key="['incompatible']"
            expand-icon-position="right"
            :bordered="false"
          >
            <a-collapse-item key="incompatible" class="incompatible-collapse-item">
              <template #header>
                <div class="section-header">
                  <icon-exclamation-circle />
                  <strong>Incompatible Machines ({{ analysisResult.incompatibleMachines.length }})</strong>
                </div>
              </template>
              <div class="section-description">
                The following machines do not match your test plan requirements:
              </div>
              <div class="machine-grid">
                <div
                  v-for="item in analysisResult.incompatibleMachines"
                  :key="item.machine.id"
                  class="machine-card incompatible"
                >
                  <h4>{{ item.machine.name }}</h4>
                  <p><strong>Motherboard:</strong> {{ item.machine.motherboard }}</p>
                  <p><strong>GPU:</strong> {{ item.machine.gpu }}</p>
                  <p><strong>CPU:</strong> {{ item.machine.cpu }}</p>
                  <a-tag color="red">Incompatible</a-tag>
                  <ul class="reasons">
                    <li v-for="(reason, idx) in item.reasons" :key="idx">{{ reason }}</li>
                  </ul>
                </div>
              </div>
            </a-collapse-item>
          </a-collapse>
        </div>
      </div>

      <!-- 缺失配置 -->
      <div v-if="analysisResult.missingConfigurations.length > 0" class="analysis-section">
        <a-alert type="error">
          <template #icon><icon-close-circle /></template>
          <div>
            <strong>Missing Configurations</strong>
            <ul>
              <li v-for="(config, idx) in analysisResult.missingConfigurations" :key="idx">
                {{ config }}
              </li>
            </ul>
          </div>
        </a-alert>
      </div>

      <!-- 警告 -->
      <div v-if="analysisResult.warnings.length > 0" class="analysis-section">
        <a-alert type="warning">
          <template #icon><icon-exclamation-circle /></template>
          <div>
            <strong>Configuration Warnings</strong>
            <ul>
              <li v-for="(warning, idx) in analysisResult.warnings" :key="idx">
                {{ warning }}
              </li>
            </ul>
          </div>
        </a-alert>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import type { AnalysisResult, Machine } from '../types'
import { Message } from '@arco-design/web-vue'

defineOptions({ name: 'UploadPlan' })

// Mock 机器数据 (实际项目中应该从 API 获取)
const mockMachines: Machine[] = [
  { id: 1, name: 'Machine A', motherboard: 'ASUS Pro WS X570-ACE', gpu: 'Radeon RX 7900 Series', cpu: 'Ryzen Threadripper', status: 'Available' },
  { id: 2, name: 'Machine B', motherboard: 'Gigabyte B550 AORUS', gpu: 'Radeon RX 7900 Series', cpu: 'Ryzen Threadripper', status: 'Available' },
  { id: 3, name: 'Machine C', motherboard: 'ASRock X570 Taichi', gpu: 'Radeon RX 6800 Series', cpu: 'Ryzen 7', status: 'Available' },
  { id: 4, name: 'Machine D', motherboard: 'MSI MEG X570 GODLIKE', gpu: 'Radeon Pro W7800', cpu: 'EPYC', status: 'Available' },
  { id: 5, name: 'Machine E', motherboard: 'ASUS Pro WS X570-ACE', gpu: 'Radeon Pro W6800', cpu: 'Ryzen Threadripper', status: 'Available' },
]

const fileInputRef = ref<HTMLInputElement>()
const isDragOver = ref(false)
const uploadedFile = ref<File | null>(null)
const analyzing = ref(false)
const validationResults = ref<Array<{ type: string; title: string; message?: string; items?: string[] }>>([])
const analysisResult = ref<AnalysisResult | null>(null)
const errorSummary = ref<Array<{ line: number; column: number; message: string }>>([])
const fileContent = ref<string[]>([])
const errorLines = ref<number[]>([])

const handleClickUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFile(target.files[0])
  }
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    handleFile(event.dataTransfer.files[0])
  }
}

const handleFile = (file: File) => {
  if (!file.name.endsWith('.yaml') && !file.name.endsWith('.yml')) {
    Message.error('Please upload a YAML file')
    return
  }

  uploadedFile.value = file
  validationResults.value = []
  analysisResult.value = null
  errorSummary.value = []
  fileContent.value = []
  errorLines.value = []
  Message.success('File uploaded successfully')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0)
    return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Number.parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`
}

const handleAnalyze = async () => {
  if (!uploadedFile.value)
    return

  analyzing.value = true
  try {
    // 第一步：调用后端 API 进行严格的 YAML 语法验证
    const formData = new FormData()
    formData.append('file', uploadedFile.value)

    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    const response = await fetch('/api/system/test/plan/yaml/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    })

    const backendResult = await response.json()

    // 如果后端验证失败，显示详细错误信息
    if (!response.ok || backendResult.code !== 200) {
      const errorDetails = backendResult.data?.errors || []
      const lines = backendResult.data?.lines || []
      
      // 设置文件内容
      fileContent.value = lines
      
      // 设置错误摘要和错误行
      errorSummary.value = errorDetails
      errorLines.value = errorDetails
        .map((err: any) => err.line)
        .filter((line: number) => line > 0)

      // 只设置一个标记，让错误摘要区域显示
      validationResults.value = [
        {
          type: 'error',
          title: '', // 空标题，因为错误已在上面的 error-summary 中显示
          message: '',
        },
      ]

      return
    }

    // 第二步：后端验证通过，继续前端分析
    const text = await uploadedFile.value.text()
    const yamlData = parseYaml(text)

    // 验证和分析
    const result = validateYamlConfig(yamlData)
    analysisResult.value = result

    validationResults.value = [
      {
        type: 'success',
        title: 'YAML File Parsed Successfully',
        message: '',
      },
    ]

    // 滚动到分析结果
    setTimeout(() => {
      document.querySelector('.analysis-output')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }
  catch (error: any) {
    validationResults.value = [
      {
        type: 'error',
        title: 'Error parsing YAML file',
        message: error.message,
      },
    ]
  }
  finally {
    analyzing.value = false
  }
}

// 简单的 YAML 解析器
function parseYaml(yamlContent: string): any {
  const lines = yamlContent.split('\n')
  const result: any = {}
  let currentSection: string | null = null

  for (const line of lines) {
    const trimmed = line.trim()

    if (!trimmed || trimmed.startsWith('#'))
      continue

    if (trimmed.endsWith(':')) {
      currentSection = trimmed.slice(0, -1).trim()
      result[currentSection] = {}
    }
    else if (trimmed.includes(':')) {
      const [key, value] = trimmed.split(':').map(s => s.trim())
      if (currentSection) {
        result[currentSection][key] = value
      }
      else {
        result[key] = value
      }
    }
  }

  return result
}

// 验证 YAML 配置
function validateYamlConfig(yamlData: any): AnalysisResult {
  const result: AnalysisResult = {
    compatibleMachines: [],
    incompatibleMachines: [],
    missingConfigurations: [],
    warnings: [],
  }

  const requiredCPU = yamlData.hardware?.cpu
  const requiredGPU = yamlData.hardware?.gpu

  if (!requiredCPU || !requiredGPU) {
    result.missingConfigurations.push('Hardware configuration (CPU/GPU) is missing in the YAML file')
  }

  // 检查机器兼容性
  mockMachines.forEach((machine) => {
    const cpuMatch = !requiredCPU || machine.cpu === requiredCPU
    const gpuMatch = !requiredGPU || machine.gpu === requiredGPU

    if (cpuMatch && gpuMatch) {
      result.compatibleMachines.push(machine)
    }
    else {
      result.incompatibleMachines.push({
        machine,
        reasons: [
          ...(!cpuMatch ? [`CPU mismatch: required ${requiredCPU}, found ${machine.cpu}`] : []),
          ...(!gpuMatch ? [`GPU mismatch: required ${requiredGPU}, found ${machine.gpu}`] : []),
        ],
      })
    }
  })

  // 检查其他配置
  if (!yamlData.environment?.os) {
    result.warnings.push('OS configuration is not specified')
  }

  if (!yamlData.environment?.kernel) {
    result.warnings.push('Kernel configuration is not specified')
  }

  if (!yamlData.firmware?.gpu_version) {
    result.warnings.push('GPU firmware version is not specified')
  }

  return result
}

const getResultIcon = (type: string) => {
  const icons: Record<string, any> = {
    success: 'icon-check-circle',
    warning: 'icon-exclamation-circle',
    error: 'icon-close-circle',
  }
  return icons[type] || 'icon-info-circle'
}

const getErrorMessage = (lineNum: number): string => {
  // 查找该行的错误信息
  const error = errorSummary.value.find(err => err.line === lineNum)
  if (error) {
    return `    # ${error.message}`
  }
  return ''
}

const handleDownloadYaml = () => {
  if (!uploadedFile.value || fileContent.value.length === 0)
    return

  // 从 fileContent 重新组合完整内容，并添加错误注释
  const contentWithComments = fileContent.value.map((line, index) => {
    const lineNumber = index + 1
    const errorMessage = getErrorMessage(lineNumber)
    // 如果该行有错误注释，将注释添加到行尾
    return errorMessage ? `${line}${errorMessage}` : line
  }).join('\n')
  
  // 创建 Blob 并下载
  const blob = new Blob([contentWithComments], { type: 'text/yaml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = uploadedFile.value.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  Message.success(`Downloaded: ${uploadedFile.value.name}`)
}

const handleCopyFileContent = async () => {
  if (fileContent.value.length === 0) {
    Message.warning('No content to copy')
    return
  }

  try {
    // 组合文件内容，包含错误注释
    const contentWithComments = fileContent.value.map((line, index) => {
      const lineNumber = index + 1
      const errorMessage = getErrorMessage(lineNumber)
      // 如果该行有错误注释，将注释添加到行尾
      return errorMessage ? `${line}${errorMessage}` : line
    }).join('\n')

    // 使用 Clipboard API 复制到剪贴板
    await navigator.clipboard.writeText(contentWithComments)
    Message.success('Copy File Content Success.')
  }
  catch (error) {
    // 如果 Clipboard API 失败，使用传统方法
    try {
      const textarea = document.createElement('textarea')
      const contentWithComments = fileContent.value.map((line, index) => {
        const lineNumber = index + 1
        const errorMessage = getErrorMessage(lineNumber)
        return errorMessage ? `${line}${errorMessage}` : line
      }).join('\n')
      
      textarea.value = contentWithComments
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      Message.success('Copy File Content Success.')
    }
    catch (fallbackError) {
      Message.error('Failed to copy file content')
      console.error('Copy failed:', fallbackError)
    }
  }
}
</script>

<style scoped lang="scss">
.upload-plan {
  .form-section {
    background: white;
    border-radius: 12px;
    margin-bottom: 15px;
    margin-top: 5px;  // ✅ 添加这行，设置上边距为0（或负值如 -10px）
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    border-left: 5px solid #3498db;

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

  .upload-area {
    border: 3px dashed #e1e5eb;
    border-radius: 12px;
    padding: 60px 30px;
    text-align: center;
    transition: all 0.3s ease;
    background: #f8f9fa;
    cursor: pointer;
    margin-bottom: 20px;

    &:hover,
    &.dragover {
      border-color: #3498db;
      background: rgba(52, 152, 219, 0.05);
    }

    .arco-icon {
      font-size: 3rem;
      color: #3498db;
      margin-bottom: 15px;
    }

    h3 {
      margin: 0 0 10px 0;
      color: #2c3e50;
    }

    p {
      margin: 0;
      color: #6c757d;
    }
  }

  .file-info {
    margin-bottom: 15px;

    .success-message {
      background: rgba(39, 174, 96, 0.1);
      border-left: 4px solid #27ae60;
      border-radius: 8px;
      padding: 15px 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;

      .success-header {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #27ae60;

        .arco-icon {
          font-size: 1.5rem;
          flex-shrink: 0;
          width: 24px;
          height: 24px;
        }

        strong {
          color: #2c3e50;
          font-size: 1rem;
        }
      }

      .success-details {
        margin: 0;
        margin-left: 36px; // 图标宽度 24px + gap 12px = 36px，精确对齐
        font-size: 1rem;
        line-height: 1.6;
        color: #2c3e50;
        font-weight: 600;
      }
    }
  }

  .validation-results {
    margin-top: 15px;

    h3 {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 15px;
      color: #2c3e50;
    }

    .error-summary {
      margin-bottom: 20px;

      :deep(.arco-collapse) {
        background: transparent;
        border: none;
      }

      :deep(.error-collapse-item) {
        background: rgba(231, 76, 60, 0.1);
        border-left: 4px solid #e74c3c;
        border-radius: 8px;
        margin-bottom: 0;

        .arco-collapse-item-header {
          padding: 15px 20px;
          background: transparent;
          border: none;

          .error-header {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #e74c3c;

            .arco-icon {
              font-size: 1.5rem;
            }

            strong {
              color: #2c3e50;
            }
          }
        }

        .arco-collapse-item-content {
          padding: 0 20px 15px 20px;
          border: none;
        }
      }

      .error-list {
        margin: 0;
        padding: 0 0 0 20px;
        list-style: none;

        li {
          margin: 8px 0;
          padding-left: 0;
          font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
          font-size: 0.95rem;
          line-height: 1.6;
          color: #555;
        }
      }
    }

    .file-content-section {
      margin: 20px 0;
      border: 2px solid #e1e5eb;
      border-radius: 8px;
      overflow: hidden;
      background: #2d2d2d;

      :deep(.arco-collapse) {
        background: transparent;
        border: none;
      }

      :deep(.file-content-collapse-item) {
        background: transparent;
        border: none;
        margin-bottom: 0;

        .arco-collapse-item-header {
          padding: 12px 15px;
          background: #1e1e1e;
          border: none;
          border-bottom: 1px solid #3d3d3d;

          .file-content-header-wrapper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            gap: 15px;

            .file-content-title {
              display: flex;
              align-items: center;
              gap: 10px;
              color: #fff;
              flex: 1;

              .arco-icon {
                font-size: 1.2rem;
              }
            }

            .copy-button {
              color: #3498db;
              padding: 4px 12px;
              transition: all 0.3s;

              &:hover {
                color: #2980b9;
                background: rgba(52, 152, 219, 0.1);
              }

              .arco-icon {
                font-size: 1rem;
              }
            }
          }
        }

        .arco-collapse-item-content {
          padding: 0;
          border: none;
          background: #2d2d2d;
        }
      }

      .file-content-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 15px;
        background: #1e1e1e;
        color: #fff;
        border-bottom: 1px solid #3d3d3d;
      }

      .file-content-box {
        max-height: 1000px;
        overflow-y: auto;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.5;

        .code-line {
          display: flex;
          align-items: stretch;
          min-height: 20px;
          transition: background-color 0.2s;

          &:hover {
            background: #3d3d3d;
          }

          &.comment-line {
            .line-content {
              color: #6a9955;
              font-style: italic;
            }
          }

          &.error-line {
            background: rgba(231, 76, 60, 0.2);
            border-left: 4px solid #e74c3c;

            .line-number {
              background: #e74c3c;
              color: #fff;
              font-weight: bold;
            }

            .line-content {
              color: #ff6b6b;
            }
          }

          .line-number {
            display: inline-block;
            width: 50px;
            text-align: right;
            padding: 0 10px;
            background: #252525;
            color: #858585;
            user-select: none;
            flex-shrink: 0;
          }

          .line-content {
            flex: 1;
            padding: 0 10px;
            color: #d4d4d4;
            white-space: pre;
            margin: 0;

            .error-comment {
              color: #ff6b6b;
              font-style: normal;
              font-family: inherit;
              font-size: inherit;
              font-weight: inherit;
            }
          }
        }
      }
    }

    .validation-item {
      padding: 15px 20px;
      border-radius: 8px;
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      gap: 12px;

      .arco-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
        width: 24px;
        height: 24px;
      }

      &.success {
        background: rgba(39, 174, 96, 0.1);
        border-left: 4px solid #27ae60;

        .arco-icon {
          color: #27ae60;
        }
      }

      &.warning {
        background: rgba(243, 156, 18, 0.1);
        border-left: 4px solid #f39c12;

        .arco-icon {
          color: #f39c12;
        }
      }

      &.error {
        background: rgba(231, 76, 60, 0.1);
        border-left: 4px solid #e74c3c;

        .arco-icon {
          color: #e74c3c;
        }
      }

      strong {
        display: block;
        margin-bottom: 5px;
        font-size: 1rem;
        font-weight: 600;
        color: #2c3e50;
      }

      p {
        margin: 5px 0;
      }

      ul {
        margin: 10px 0 0 20px;
        padding: 0;

        li {
          margin: 5px 0;
        }
      }
    }
  }

  .actions {
    margin-top: 20px;
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .analysis-output {
    .analysis-section {
      margin-bottom: 25px;

      &:last-child {
        margin-bottom: 0;
      }

      .machine-section-wrapper {
        :deep(.arco-collapse) {
          background: transparent;
          border: none;
        }

        :deep(.compatible-collapse-item) {
          background: rgba(39, 174, 96, 0.1);
          border-left: 4px solid #27ae60;
          border-radius: 8px;
          margin-bottom: 0;

          .arco-collapse-item-header {
            padding: 15px 20px;
            background: transparent;
            border: none;

            .section-header {
              display: flex;
              align-items: center;
              gap: 12px;
              color: #27ae60;

              .arco-icon {
                font-size: 1.5rem;
              }

              strong {
                color: #2c3e50;
              }
            }
          }

          .arco-collapse-item-content {
            padding: 0 20px 15px 20px;
            border: none;
          }
        }

        :deep(.incompatible-collapse-item) {
          background: rgba(243, 156, 18, 0.1);
          border-left: 4px solid #f39c12;
          border-radius: 8px;
          margin-bottom: 0;

          .arco-collapse-item-header {
            padding: 15px 20px;
            background: transparent;
            border: none;

            .section-header {
              display: flex;
              align-items: center;
              gap: 12px;
              color: #f39c12;

              .arco-icon {
                font-size: 1.5rem;
              }

              strong {
                color: #2c3e50;
              }
            }
          }

          .arco-collapse-item-content {
            padding: 0 20px 15px 20px;
            border: none;
          }
        }

        .section-description {
          margin: 0 0 15px 0;
          padding: 0;
          font-size: 0.95rem;
          line-height: 1.6;
          color: #2c3e50;
        }
      }

      .machine-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 20px;
        margin-top: 0;

        .machine-card {
          border: 2px solid #e1e5eb;
          border-radius: 12px;
          padding: 20px;
          background: white;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;

          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            transition: all 0.3s ease;
          }

          &:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
          }

          &.compatible {
            &::before {
              background: #27ae60;
            }

            &:hover {
              border-color: #27ae60;
            }
          }

          &.incompatible {
            opacity: 0.8;

            &::before {
              background: #e74c3c;
            }

            &:hover {
              border-color: #e74c3c;
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

          .reasons {
            margin: 10px 0 0 20px;
            padding: 0;
            font-size: 0.9rem;
            color: #666;

            li {
              margin: 5px 0;
            }
          }
        }
      }

      ul {
        margin: 10px 0 0 20px;
        padding: 0;

        li {
          margin: 5px 0;
        }
      }

      // 为 Missing Configurations 和 Configuration Warnings 添加圆角
      :deep(.arco-alert) {
        border-radius: 8px;
      }
    }
  }
}
</style>

