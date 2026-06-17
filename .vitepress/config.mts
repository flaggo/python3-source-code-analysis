import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  lang: 'zh-Hans',
  title: 'Python 3 源码分析',
  description: '致力于分析 Python 3.7.0 的源码实现',

  // 部署在 https://flaggo.github.io/python3-source-code-analysis/
  base: '/python3-source-code-analysis/',

  // 用仓库根目录作为内容源；README.md 作为首页
  srcDir: '.',
  rewrites: {
    'README.md': 'index.md'
  },
  // 不作为页面渲染的文件 / 旧构建产物
  srcExclude: ['SUMMARY.md', '_book/**', '**/node_modules/**'],

  lastUpdated: true,
  cleanUrls: true,
  ignoreDeadLinks: true,

  markdown: {
    lineNumbers: true
  },

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: '大纲', link: '/objects/object/' }
    ],

    sidebar: [
      {
        text: '第 1 部分：序章',
        items: [
          { text: '前言', link: '/' },
          { text: 'Python 源代码的组织', link: '/preface/code-organization/' },
          { text: 'Windows 环境下编译 Python', link: '/preface/windows-build/' },
          { text: 'UNIX/Linux 环境下编译 Python', link: '/preface/unix-linux-build/' },
          { text: '修改 Python 源码', link: '/preface/modify-code/' }
        ]
      },
      {
        text: '第 2 部分：Python 内建对象',
        items: [
          { text: 'Python 对象初探', link: '/objects/object/' },
          { text: 'Python 整数对象', link: '/objects/long-object/' },
          { text: 'Python 字符串对象', link: '/objects/str-object/' },
          { text: 'Python List 对象', link: '/objects/list-object/' },
          { text: 'Python Dict 对象', link: '/objects/dict-object/' },
          { text: 'Python Set 对象', link: '/objects/set-object/' },
          { text: '实现简版 Python', link: '/objects/simple-interpreter/' }
        ]
      },
      {
        text: '第 3 部分：Python 虚拟机',
        items: [
          { text: '（编写中…）', link: '/' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/flaggo/python3-source-code-analysis' }
    ],

    search: {
      provider: 'local'
    },

    editLink: {
      pattern: 'https://github.com/flaggo/python3-source-code-analysis/edit/master/:path',
      text: '编辑此页面'
    },

    outline: {
      label: '本页目录',
      level: [2, 3]
    },

    docFooter: {
      prev: '上一篇',
      next: '下一篇'
    },

    lastUpdated: {
      text: '最后更新于'
    },

    footer: {
      copyright: 'Copyright © FlagGo 2019-2026'
    },

    darkModeSwitchLabel: '主题',
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '菜单'
  }
})
