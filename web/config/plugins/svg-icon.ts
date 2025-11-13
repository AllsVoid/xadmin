import { fileURLToPath } from 'node:url'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'

export default function createSvgIcon(isBuild) {
  return createSvgIconsPlugin({
    // 指定需要缓存的图标文件夹（使用 ESM 语法）
    iconDirs: [fileURLToPath(new URL('../../src/assets/icons', import.meta.url))],
    // 指定 symbolId 格式
    symbolId: 'icon-[dir]-[name]',
    svgoOptions: isBuild,
  })
}
