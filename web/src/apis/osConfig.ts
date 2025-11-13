import http from '@/utils/http'

/**
 * 选项接口
 */
export interface OptionItem {
  label: string
  value: string
}

/**
 * OS 配置接口
 */
export interface OsConfig {
  id: number
  label: string
  value: string
  osFamily?: string
  version?: string
}

/**
 * 获取 OS 配置选项列表
 */
export async function getOsOptions(): Promise<OsConfig[]> {
  const res = await http.get<OsConfig[]>('/tp/api/os-config/options')
  return res.data || []
}

/**
 * 获取指定 OS 的内核版本列表
 * @param osConfigId OS 配置的 ID
 */
export async function getOsKernels(osConfigId: number): Promise<OptionItem[]> {
  const res = await http.get<OptionItem[]>(`/tp/api/os-config/${osConfigId}/kernels`)
  return res.data || []
}

/**
 * 获取所有内核类型（去重）
 */
export async function getAllKernelTypes(): Promise<OptionItem[]> {
  const res = await http.get<OptionItem[]>('/tp/api/os-config/kernels/all')
  return res.data || []
}

