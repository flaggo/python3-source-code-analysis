# 前言

本项目致力于对 Python 3.7 的源码分析，深度参考陈儒大大的《Python 源码剖析》，编写 Python 3 的版本。

希望各位 Python 爱好者能参与其中，一起探索 Python 魔法背后的奥秘！

## Roadmap

在《Python 源码剖析》的基础上，按更贴合 CPython 3.7 的结构重新编排，分为六个部分：准备、对象与类型系统、编译、虚拟机、运行时、内存管理。

- [x] 第 1 部分：准备
    - [x] 前言
    - [x] Python 源代码的组织
    - [x] Windows 环境下编译 Python
    - [x] UNIX/Linux 环境下编译 Python
    - [x] 修改 Python 源码
- [x] 第 2 部分：对象与类型系统
    - [x] Python 对象初探
    - [x] Python 整数对象
    - [x] Python 浮点数对象
    - [x] Python 字符串对象
    - [x] Python bytes 与 bytearray 对象
    - [x] Python 列表对象
    - [x] Python 元组对象
    - [x] Python 字典对象
    - [x] Python 集合对象
    - [x] Python 布尔与 None 对象
    - [x] Python 类型对象与自定义类
- [ ] 第 3 部分：编译
    - [ ] 从源码到字节码（编译过程）
    - [ ] 编译的产物：code object 与 pyc
- [ ] 第 4 部分：虚拟机
    - [ ] Python 虚拟机框架（帧对象与求值循环）
    - [ ] 一般表达式与名字空间
    - [ ] 控制流：跳转、循环与迭代器
    - [ ] 异常机制：block 栈与栈展开
    - [ ] 函数机制：调用、参数与闭包
    - [ ] 生成器与协程
- [ ] 第 5 部分：运行时
    - [ ] Python 运行环境初始化
    - [ ] 模块与 import 机制
    - [ ] 多线程与 GIL
- [ ] 第 6 部分：内存管理
    - [ ] 内存分配与引用计数（pymalloc）
    - [ ] 循环垃圾回收（分代 GC）
