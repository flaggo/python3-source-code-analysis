# 大纲

## 第 1 部分：准备

- [前言](README.md)
- [Python 源代码的组织](preface/code-organization/index.md)
- [Windows 环境下编译 Python](preface/windows-build/index.md)
- [UNIX/Linux 环境下编译 Python](preface/unix-linux-build/index.md)
- [修改 Python 源码](preface/modify-code/index.md)

## 第 2 部分：对象与类型系统

- [Python 对象初探](objects/object/index.md)
- [Python 整数对象](objects/long-object/index.md)
- [Python 浮点数对象](objects/float-object/index.md)
- [Python 字符串对象](objects/str-object/index.md)
- [Python bytes 与 bytearray 对象](objects/bytes-object/index.md)
- [Python List 对象](objects/list-object/index.md)
- [Python 元组对象](objects/tuple-object/index.md)
- [Python Dict 对象](objects/dict-object/index.md)
- [Python Set 对象](objects/set-object/index.md)
- [Python 布尔与 None 对象](objects/bool-none-object/index.md)
- [Python 类型对象与自定义类](objects/type-object/index.md)

## 第 3 部分：编译

- [从源码到字节码（编译过程）](compile/source-to-bytecode/index.md)
- [编译的产物：code object 与 pyc](compile/code-object/index.md)

## 第 4 部分：虚拟机

- [Python 虚拟机框架（帧对象与求值循环）](vm/frame-and-eval-loop/index.md)
- [一般表达式与名字空间](vm/expressions-and-names/index.md)
- [控制流：跳转、循环与迭代器](vm/control-flow/index.md)
- [异常机制：block 栈与栈展开](vm/exceptions/index.md)
- [函数机制：调用、参数与闭包](vm/functions/index.md)
- [生成器与协程](vm/generators/index.md)

## 第 5 部分：运行时

- [Python 运行环境初始化](runtime/initialization/index.md)
- [模块与 import 机制](runtime/import-system/index.md)
- [多线程与 GIL](runtime/gil/index.md)

## 第 6 部分：内存管理

- [内存分配与引用计数（pymalloc）](memory/allocation-refcount/index.md)
- [循环垃圾回收（分代 GC）](memory/garbage-collection/index.md)
