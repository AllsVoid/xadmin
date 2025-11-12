/**
 * 测试计划 YAML API
 */
import httpClient from '@/utils/http'

export interface UploadResponse {
  code: number
  message: string
  data: {
    id: number
    file_name: string
    basic_info: {
      plan_name?: string
      description?: string
      test_type?: string
      cpu?: string
      gpu?: string
      gpu_version?: string
      os?: string
      kernel?: string
      driver?: string
    }
    is_valid: boolean
    compatible_count: number
    incompatible_count: number
    warning_count: number
    error_count: number
  }
}

export interface AnalysisResponse {
  code: number
  message: string
  data: {
    id: number
    file_name: string
    file_size: number
    basic_info: {
      plan_name?: string
      test_type?: string
      cpu?: string
      gpu?: string
      os?: string
      kernel?: string
    }
    validation_status: string
    compatible_machines: any[]
    incompatible_machines: any[]
    compatible_count: number
    incompatible_count: number
    warnings: string[]
    errors: string[]
    warning_count: number
    error_count: number
    create_time: string
  }
}

export interface ComparisonResponse {
  code: number
  message: string
  data: {
    id: number
    file_name: string
    user_yaml: string
    template_yaml: string
    comparison: {
      missing_fields: string[]
      type_errors: any[]
      has_issues: boolean
    }
    missing_fields: string[]
    type_errors: any[]
  }
}

export interface ListResponse {
  code: number
  message: string
  data: {
    list: any[]
    total: number
    page: number
    page_size: number
    total_pages: number
  }
}

export const testPlanYamlApi = {
  /**
   * 上传 YAML 文件
   */
  upload(formData: FormData): Promise<UploadResponse> {
    return httpClient.post('/system/test/plan/yaml/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 获取分析结果
   */
  getAnalysis(id: number): Promise<AnalysisResponse> {
    return httpClient.get(`/system/test/plan/yaml/${id}/analysis`)
  },

  /**
   * 获取对比结果
   */
  getComparison(id: number): Promise<ComparisonResponse> {
    return httpClient.get(`/system/test/plan/yaml/${id}/comparison`)
  },

  /**
   * 获取 YAML 列表
   */
  list(params: { page?: number; page_size?: number }): Promise<ListResponse> {
    return httpClient.get('/system/test/plan/yaml/list', { params })
  },

  /**
   * 删除 YAML 记录
   */
  delete(id: number): Promise<{ code: number; message: string; data: null }> {
    return httpClient.delete(`/system/test/plan/yaml/${id}`)
  }
}

