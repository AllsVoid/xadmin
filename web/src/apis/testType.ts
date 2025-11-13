import http from '@/utils/http'

/**
 * 选项接口
 */
export interface OptionItem {
  label: string
  value: string
}

/**
 * 测试类型接口
 */
export interface TestType {
  id: number
  typeName: string
  createdAt?: string
  updatedAt?: string
}

/**
 * 测试组件接口
 */
export interface TestComponent {
  id: number
  testTypeId: number
  componentCategory?: string
  componentName: string
}

/**
 * 测试用例接口
 */
export interface TestCase {
  id: number
  testComponentId: number
  caseName: string
  caseConfig?: any
  createdAt?: string
  updatedAt?: string
}

/**
 * 获取测试类型选项列表（用于下拉框）
 */
export async function getTestTypeOptions(): Promise<OptionItem[]> {
  const res = await http.get<OptionItem[]>('/tp/api/test-type/options')
  return res.data || []
}

/**
 * 获取测试类型列表
 */
export async function getTestTypes(): Promise<TestType[]> {
  const res = await http.get<TestType[]>('/tp/api/test-type/list')
  return res.data || []
}

/**
 * 获取指定测试类型的测试组件列表
 * @param testTypeId 测试类型 ID
 */
export async function getTestComponents(testTypeId: number): Promise<TestComponent[]> {
  const res = await http.get<TestComponent[]>('/tp/api/test-component/list', { test_type_id: testTypeId })
  return res.data || []
}

/**
 * 获取指定测试组件的测试用例列表
 * @param testComponentId 测试组件 ID
 */
export async function getTestCases(testComponentId: number): Promise<TestCase[]> {
  const res = await http.get<any>('/tp/api/test-case/list', { test_component_id: testComponentId, page: 1, size: 1000 })
  return res.data?.list || []
}

/**
 * 搜索所有测试用例（不限制组件）
 * @param keyword 搜索关键词
 */
export async function searchAllTestCases(keyword: string): Promise<TestCase[]> {
  const res = await http.get<any>('/tp/api/test-case/list', { page: 1, size: 1000 })
  const allCases = res.data?.list || []
  
  if (!keyword || !keyword.trim()) {
    return allCases
  }
  
  // 前端过滤（如果后端不支持搜索参数）
  const lowerKeyword = keyword.toLowerCase()
  return allCases.filter((testCase: TestCase) =>
    testCase.caseName.toLowerCase().includes(lowerKeyword)
  )
}

