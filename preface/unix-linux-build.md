# Unix（包括 Linux） 环境下编译 Python

在 Unix 环境编译 Python 较为简单，执行以下命令：

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
  - **lib/python3.7/config-3.7m-{platform} 目录** 存放的是 libpython3.7m.a，该静态库用于使用 C 语言进行扩展。{platform}代表平台，比如在 Mac OS 上 {platform}为“darwin”
- **share 目录** 存放的是帮助等文件
