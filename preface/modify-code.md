# 修改 Python 源码

## 在源代码中 Print

在接下来研究源码的过程中，我们可能会对某些语句的逻辑感到好奇，需要输出中间结果。
这就需要借助 Python C API 中打印对象的接口：

`源文件：`[Objects/object.c](https://github.com/python/cpython/blob/v3.7.0/Objects/object.c#L339)

```c
int
PyObject_Print(PyObject *op, FILE *fp, int flags)
```

比如，我们希望在解释器交互界面中打印整数值的时候输出一段字符串，则我们可以修改如下函数：

`源文件：`[Objects/longobject.c](https://github.com/python/cpython/blob/v3.7.0/Objects/longobject.c#L1762)

```c
static PyObject *
long_to_decimal_string(PyObject *aa)
{
    PyObject *str = PyUnicode_FromString("I am always before int");
    PyObject_Print(str, stdout, 0);
    printf("\n");

    PyObject *v;
    if (long_to_decimal_string_internal(aa, &v, NULL, NULL, NULL) == -1)
        return NULL;
    return v;
}
```

其中，函数实现中的前 3 行为我们加入的代码。`PyUnicode_FromString` 用于把 C 中的原生字符数组
转换为出 Python 中的字符串（Unicode）对象；而 `PyObject_Print` 则将转换好的字符串对象打印至
我们指定的标准输出（`stdout`）。

对 Python 重新进行编译，在 Unix 上可执行：

```console
make && make bininstall
```

运行编译后的 Python，输入 print 语句即可看到我们希望的结果：

```python
>>> print(1)
'I am always before int'
1
```
