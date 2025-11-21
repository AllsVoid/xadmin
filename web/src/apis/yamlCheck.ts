import http from '@/utils/http'

/**
 * 验证响应接口
 */
export interface ValidationResponse {
  success: boolean
  error?: {
    code: string
    message: string
    key?: string
    lineNumber?: number
  }
}

/**
 * YAML 兼容性验证
 * @param yamlData YAML 数据对象
 * @param yamlText 原始 YAML 文本（可选，用于准确的行号查找）
 * @returns ValidationResponse 验证结果
 */
export async function validateYaml(yamlData: any, yamlText?: string): Promise<ValidationResponse> {
  const response = await http.post<ValidationResponse>('/system/yaml/validate', { 
    yamlData,
    yamlText 
  })
  return response.data // ← 关键：提取 data 字段
}
