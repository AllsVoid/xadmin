import picocolors from 'picocolors'
import type { Plugin } from 'vite'

export default function appInfo(): Plugin {
  return {
    name: 'appInfo',
    apply: 'serve',
    async buildStart() {
      const { bold, green, cyan } = picocolors
      // eslint-disable-next-line no-console
      console.log('\n' + bold(green('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')))
      // eslint-disable-next-line no-console
      console.log(bold(green('  XAdmin v1.0.0')))
      // eslint-disable-next-line no-console
      // console.log(cyan('  在线文档：') + 'https://continew.top')
      // eslint-disable-next-line no-console
      // console.log(cyan('  常见问题：') + 'https://continew.top/faq.html')
      // eslint-disable-next-line no-console
      // console.log(cyan('  持续迭代优化的前后端分离中后台管理系统框架。'))
      // eslint-disable-next-line no-console
      console.log(bold(green('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')) + '\n')
    },
  }
}
