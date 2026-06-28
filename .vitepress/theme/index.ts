import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import MiniVM from './MiniVM.vue'
import MiniVMPlayground from './MiniVMPlayground.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('MiniVM', MiniVM)
    app.component('MiniVMPlayground', MiniVMPlayground)
  }
} satisfies Theme
