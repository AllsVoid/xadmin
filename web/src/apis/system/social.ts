/**
 * 社交账号相关 API
 * 注意: 当前后端未实现此功能，这里提供空实现以避免构建错误
 */

/**
 * 绑定社交账号
 * @param source 社交平台来源
 * @param params 绑定参数
 */
export function bindSocialAccount(source: string, params: Record<string, any>) {
  console.warn('社交账号绑定功能未实现')
  return Promise.reject(new Error('社交账号绑定功能未实现'))
}

/**
 * 获取用户社交账号列表
 */
export function listUserSocial() {
  console.warn('获取用户社交账号列表功能未实现')
  return Promise.resolve({ data: [] })
}

/**
 * 社交账号授权
 * @param source 社交平台来源
 */
export function socialAuth(source: string) {
  console.warn('社交账号授权功能未实现')
  return Promise.reject(new Error('社交账号授权功能未实现'))
}

/**
 * 解绑社交账号
 * @param id 社交账号ID
 */
export function unbindSocialAccount(id: string | number) {
  console.warn('解绑社交账号功能未实现')
  return Promise.reject(new Error('解绑社交账号功能未实现'))
}

