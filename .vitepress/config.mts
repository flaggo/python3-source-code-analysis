import { defineConfig } from 'vitepress'
import taskLists from 'markdown-it-task-lists'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  lang: 'zh-Hans',
  title: 'Python 3 源码分析',
  description: '致力于分析 Python 3.7.0 的源码实现',

  // 部署在 https://flaggo.github.io/python3-source-code-analysis/
  base: '/python3-source-code-analysis/',

  // 用仓库根目录作为内容源；首页为 index.md（背景 + Roadmap）
  srcDir: '.',
  // 不作为页面渲染的文件：README 仅供 GitHub 仓库使用，不进站点
  srcExclude: ['README.md', 'SUMMARY.md', '_book/**', '**/node_modules/**'],

  lastUpdated: true,
  cleanUrls: true,
  ignoreDeadLinks: true,

  markdown: {
    lineNumbers: true,
    config: (md) => {
      md.use(taskLists)
    }
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
          { text: 'Python 列表对象', link: '/objects/list-object/' },
          { text: 'Python 字典对象', link: '/objects/dict-object/' },
          { text: 'Python 集合对象', link: '/objects/set-object/' },
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
