// 共享的 Pyodide 加载器：整个页面只下载并初始化一次，多个组件复用同一个实例。
const PYODIDE_VERSION = 'v0.26.4'
const CDN = `https://cdn.jsdelivr.net/pyodide/${PYODIDE_VERSION}/full/`

let _promise: Promise<any> | null = null

export function getPyodide(): Promise<any> {
  if (_promise) return _promise
  _promise = (async () => {
    if (!(window as any).loadPyodide) {
      await new Promise<void>((resolve, reject) => {
        const s = document.createElement('script')
        s.src = CDN + 'pyodide.js'
        s.onload = () => resolve()
        s.onerror = () => reject(new Error('加载 Pyodide 脚本失败，请检查网络'))
        document.head.appendChild(s)
      })
    }
    return await (window as any).loadPyodide({ indexURL: CDN })
  })()
  return _promise
}
