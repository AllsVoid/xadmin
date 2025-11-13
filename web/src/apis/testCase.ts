import http from '@/utils/http'

export interface TestCase {
  id: number
  caseName: string
  componentId: number
  componentName: string
  category: string
  testTypeId: number | null
  testTypeName: string
}

/**
 * 搜索所有 test cases（用于搜索框自动完成）
 */
export const searchTestCases = (keyword: string): Promise<TestCase[]> => {
  return http({
    url: '/tp/api/test-case/search',  // ✅ 修正路径：test-case 不是 test-cases
    method: 'get',
    params: { keyword }
  }).then((res: any) => {
    if (res.code === 200) {
      return res.data || []
    }
    return []
  })
}

