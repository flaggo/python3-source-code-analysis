# Python 源代码的组织

## 源代码下载

Python 源代码可以在 GitHub 上方便的获取，执行：

```console
git clone https://github.com/python/cpython.git
git checkout v3.7.0
```

即可获取 `Python 3.7.0` 版本的代码。

## 目录结构

进入源码目录，我们可以看到该目录下主要  包含以下文件（夹）：

```console
.
├── Doc
├── Grammar
├── Include
├── LICENSE
├── Lib
├── Mac
├── Makefile.pre.in
├── Misc
├── Modules
├── Objects
├── PC
├── PCbuild
├── Parser
├── Programs
├── Python
├── README.rst
├── Tools
├── aclocal.m4
├── config.guess
├── config.sub
├── configure
├── configure.ac
├── install-sh
├── m4
├── pyconfig.h.in
└── setup.py
```

其中：

Include 目录：包含了 Python 提供的所有头文件，如果用户需要自己用 C 或 C++来编写自定义模块扩展 Python，那么就需要用到这里提供的头文件。

Lib 目录：包含了 Python 自带的所有标准库，且都是用 Python 语言编写的。

Modules 目录：包含了所有用 C 语言编写的模块，比如 math、hashlib 等。它们都是那些对速度要求非常严格的模块。而相比而言，Lib 目录下则是存放一些对速度没有太严格要求的模块，比如 os。

Parser 目录：包含了 Python 解释器中的 Scanner 和 Parser 部分，即对 Python 源代码进行词法分析和语法分析的部分。除此以外，此目录还包含了一些有用的工具，这些工具能够根据 Python 语言的语法自动生成 Python 语言的词法和语法分析器，与 YACC 非常类似。

Objects 目录：包含了所有 Python 的内建对象，包括整数、list、dict 等。同时，该目录还包括了 Python 在运行时需要的所有的内部使用对象的实现。

Python 目录：包含了 Python 解释器中的 Compiler 和执行引擎部分，是 Python 运行的核心所在。

PCBuild 目录：包含了 Visual Studio 2003 的工程文件，研究 Python 源代码就从这里开始（本书将采用 Visual Studio 2017 对 Python 进行编译）。

Programs 目录：包含了 Python 二进制可执行文件的源码。
