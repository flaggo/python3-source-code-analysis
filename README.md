# 介绍

本项目致力于对 Python 3.7 的源码分析，深度参考陈儒大大的《Python 源码剖析》，编写 Python 3 的版本。

希望各位 Python 爱好者能参与其中，一起探索 Python 魔法背后的奥秘！

# 使用

您可以直接访问 [在线版](https://flaggo.github.io/python3-source-code-analysis/)，或者根据以下步骤访问本地版。

## 前置条件

您的系统上需要安装好 node。

## 使用 make 命令

若您可使用 make 命令，简单执行如下命令进行初始化：

```console
make init
```

执行如下命令运行服务端：

```console
make run
```

## 使用 gitbook 命令

若您不能使用 make 命令，或想直接使用 gitbook 命令，执行如下命令进行初始化：

```console
npm i -g gitbook-cli #可能需要sudo
gitbook install
```

执行如下命令运行服务端：

```console
gitbook serve
```

## 访问

直接访问 http://localhost:4000 即可查看本书内容。

# 计划

大体按照《Python 源码剖析》中的目录结构进行编写。依次介绍 Python 源码基本信息、内建对象和虚拟机。
