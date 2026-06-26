import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import MiniVM from './MiniVM.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('MiniVM', MiniVM)
  }
} satisfies Theme
