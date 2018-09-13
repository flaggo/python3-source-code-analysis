# Unix（包括 Linux） 环境下编译 Python

在 Unix 环境下编译 Python 较为简单，主要分为两个步骤：Python 所依赖的必要环境，以及执行编译、安装命令。

## 环境准备

编译 Python 前通常需要在系统上安装以下库：

- `gcc` // 编译工具
- `zlib` // 压缩、解压相关库
- `libffi` // Python 所以来的用于支持 C 扩展的库
- `openssl` // 安全套接字层密码库，Linux 中通常已具备

不同的发行版，安装方式和包名称也不尽相同。

对于 `Debian/Ubuntu`，执行：

```console
sudo apt install -y zlib1g zlib1g-dev libffi-dev openssl libssl-dev
```

对于 `RedHat/CentOS/Fedora` 系统，执行：

```console
yum install -y zlib zlib-devel libffi-devel openssl openssl-devel
```

## 编译、安装

进入 Python 源码根目录，执行以下命令：

```console
./configure
make
make install
```

Python 将会被编译，并安装在默认目录中。若您希望将 Python 安装在特定目录，则需要在一开始修改 `configure` 命令为：

```console
./configure –-prefix=<Python要安装到的目录（绝对路径）>
```

在指定目录中:

- **bin 目录** 存放的是可执行文件
- **include 目录** 存放的是 Python 源码的头文件
- **lib 目录** 存放的是 Python 标准库
  - **lib/python3.7/config-3.7m-{platform} 目录** 存放的是 libpython3.7m.a，该静态库用于使用 C 语言进行扩展。`{platform}` 代表平台，比如在 Mac OS 上为 “darwin”，在 Linux 上为 “x86_64-linux-gnu”
- **share 目录** 存放的是帮助等文件

默认情况下，编译的 Python 是静态链接（libpython3.7m.a）。如果希望编译的 Python 是动态链接（libpython3.7m.so），则需要在一开始修改`configure` 命令为：

```console
./configure --enable-shared
```

如需重新编译，请首先执行：

```console
make clean
```

再执行本节开头处的命令即可。
