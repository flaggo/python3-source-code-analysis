# 介绍

本项目致力于对 Python 3.7 的源码分析，深度参考陈儒大大的《Python 源码剖析》，编写 Python 3 的版本。

希望各位 Python 爱好者能参与其中，一起探索 Python 魔法背后的奥秘！

# 使用

您可以直接访问 [在线版](https://flaggo.github.io/python3-source-code-analysis/)，或者根据以下步骤访问本地版。

本项目使用 [VitePress](https://vitepress.dev/) 构建。

## 前置条件

您的系统上需要安装好 Node.js 18 及以上版本（会自带 npm）。

## 安装依赖

```console
npm install
```

## 本地预览

启动本地开发服务器（支持热更新）：

```console
npm run dev
```

然后访问 http://localhost:5173/python3-source-code-analysis/ 即可查看本书内容。

> 也可以使用 `make serve`，等价于 `npm run dev`。

## 构建静态页面

```console
npm run build
```

构建产物输出到 `.vitepress/dist`，可用如下命令在本地预览构建结果：

```console
npm run preview
```

# Roadmap

大体按照《Python 源码剖析》中的目录结构进行编写。依次介绍 Python 源码基本信息、内建对象和虚拟机。

- [x] 章节
    - [x] 序章
    - [x] 前言
    - [x] Python 源代码的组织
    - [x] Windows 环境下编译 Python
    - [x] UNIX/Linux 环境下编译 Python
    - [x] 修改 Python 源码
- [ ] Python 内建对象
    - [x] Python 对象初探
    - [x] Python 整数对象
    - [ ] Python 字符串 对象
    - [x] Python List 对象
    - [x] Python Dict 对象
    - [x] Python Set 对象
    - [ ] 实现简版 Python
- [ ] Python 虚拟机
    - [ ] Python 编译结果
    - [ ] Python 虚拟机框架
    - [ ] 虚拟机一般表达式
    - [ ] Python 虚拟机控制流
    - [ ] Python 虚拟机函数机制
    - [ ] Python 运行环境初始化
    - [ ] Python 模块加载机制
    - [ ] Python 多线程机制
    - [ ] Python 内存管理机制

