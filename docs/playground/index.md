---
layout: page
title: Playground
description: 在线改造并运行迷你 Python 虚拟机
sidebar: false
aside: false
---

<div class="pg-page">

# 迷你 Python 虚拟机 · Playground

左边是这台用 Python 写成的迷你虚拟机的**完整源码**，可以直接编辑；右边是一个**终端式 REPL**——直接在里面输入代码、回车执行，用你**改过的**虚拟机来跑，立刻看到效果。配套讲解见[实战章节：动手写一个迷你 Python 虚拟机](/practice/mini-vm/)。

<ClientOnly>
  <MiniVMPlayground />
</ClientOnly>

</div>

<style>
.pg-page { max-width: 1180px; margin: 0 auto; padding: 32px 24px 64px; }
.pg-page h1 { font-size: 1.6rem; font-weight: 700; margin-bottom: 12px; }
.pg-page > p { color: var(--vp-c-text-2); line-height: 1.7; margin-bottom: 8px; }
.pg-page a { color: var(--vp-c-brand-1); font-weight: 500; }
</style>
