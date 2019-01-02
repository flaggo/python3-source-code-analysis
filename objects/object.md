# Python 对象初探

在Python的世界一切皆对象，不论是整数，还是字符串，甚至连类型、函数等都是一种对象。

## 对象的分类

以下是Python对象的大致的一个分类

- Fundamental 对象: 类型对象
- Numeric 对象: 数值对象
- Sequence 对象: 容纳其他对象的序列集合对象
- Mapping 对象: 类似 C++中的 map 的关联对象
- Internal 对象: Python 虚拟机在运行时内部使用的对象

![object category](object_category.jpg)

## 对象机制的基石 PyObject

对于初学者来说这么多类型的对象怎么学？别着急，我们后续章节会解答。

在开始我们的学习之旅之前，我们要先认识一个结构体**PyObject**，可以说Python的对象机制就是基于**PyObject**拓展开来的，所以我们先看看**PyObject** 到底长什么样。

`源文件：`[Include/object.h](https://github.com/python/cpython/blob/v3.7.0/Include/object.h#L106)

```c
// Include/object.h
#define _PyObject_HEAD_EXTRA            \
    struct _object *_ob_next;           \
    struct _object *_ob_prev;

typedef struct _object {
    _PyObject_HEAD_EXTRA    // 双向链表 垃圾回收 需要用到
    Py_ssize_t ob_refcnt;   // 引用计数
    struct _typeobject *ob_type;    // 指向类型对象的指针，决定了对象的类型
} PyObject;
```

Python中的所有对象都拥有一些相同的内容，而这些内容就定义在**PyObject**中，

**PyObject** 包含 一个用于垃圾回收的双向链表，一个引用计数变量 `ob_refcnt` 和 一个类型对象指针`ob_type`

![PyObject](PyObject.jpg)

## 定长对象与变长对象

Python对象除了前面提到的那种分类方法外，还可以分为定长对象和变长对象这两种形式。

变长对象都拥有一个相同的内容 **PyVarObject**，而 **PyVarObject**也是基于**PyObject**扩展的。

从代码中可以看出**PyVarObject**比**PyObject**多出了一个用于存储元素个数的变量*ob_size*。

`源文件：`[Include/object.h](https://github.com/python/cpython/blob/v3.7.0/Include/object.h#L106)

```c
// Include/object.h
typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;
    struct _typeobject *ob_type;
} PyObject;

typedef struct {
    PyObject ob_base;
    Py_ssize_t ob_size; /* Number of items in variable part */
} PyVarObject;
```


![PyVarObject](PyVarObject.jpg)

## 类型对象

前面我们提到了**PyObject** 的 对象类型指针`struct _typeobject *ob_type`，它指向的类型对象就决定了一个对象是什么类型的。

这是一个非常重要的结构体，它不仅仅决定了一个对象的类型，还包含大量的`元信息`，
包括创建对象需要分配多少内存，对象都支持哪些操作等等。

接下来我们看一下`struct _typeobject`代码

在 **PyTypeObject** 的定义中包含许多信息，主要分类以下几类:
- 类型名, tp_name, 主要用于 Python 内部调试用
- 创建该类型对象时分配的空间大小信息，即 `tp_basicsize` 和 `tp_itemsize`
- 与该类型对象相关的操作信息(如 `tp_print` 这样的函数指针)
- 一些对象属性

`源文件：`[Include/object.h](https://github.com/python/cpython/blob/v3.7.0/Include/object.h#L346)

```c
// Include/object.h
typedef struct _typeobject {
    PyObject_VAR_HEAD
    const char *tp_name; /* For printing, in format "<module>.<name>" */ // 类型名
    Py_ssize_t tp_basicsize, tp_itemsize; /* For allocation */
    // 创建该类型对象分配的内存空间大小

    // 一堆方法定义，函数和指针
    /* Methods to implement standard operations */
    destructor tp_dealloc;
    printfunc tp_print;
    getattrfunc tp_getattr;
    setattrfunc tp_setattr;
    PyAsyncMethods *tp_as_async; /* formerly known as tp_compare (Python 2)
                                    or tp_reserved (Python 3) */
    reprfunc tp_repr;

    /* Method suites for standard classes */
    // 标准类方法集
    PyNumberMethods *tp_as_number;  // 数值对象操作
    PySequenceMethods *tp_as_sequence;  // 序列对象操作
    PyMappingMethods *tp_as_mapping;  // 字典对象操作

    // 更多标准操作
    /* More standard operations (here for binary compatibility) */
    hashfunc tp_hash;
    ternaryfunc tp_call;
    reprfunc tp_str;
    getattrofunc tp_getattro;
    setattrofunc tp_setattro;

    ......

} PyTypeObject;
```


## 类型的类型

在 **PyTypeObjet** 定义开始有一个宏`PyOject_VAR_HEAD`，查看源码可知 **PyTypeObjet** 是一个变长对象

`源文件：`[Include/object.h](https://github.com/python/cpython/blob/v3.7.0/Include/object.h#L98)

```c
// Include/object.h
#define PyObject_VAR_HEAD      PyVarObject ob_base;
```

对象的类型是由该对象指向的 类型对象 决定的，那么类型对象的类型是由谁决定的呢？
对于其他对象，可以通过与其关联的类型对象确定其类型，那么通过什么来确定一个对象是类型对象呢？
答案就是 `PyType_Type`

`源文件：`[Objects/typeobject.c](https://github.com/python/cpython/blob/v3.7.0/Objects/typeobject.c#L3540)

```c
// Objects/typeobject.c
PyTypeObject PyType_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "type",                                     /* tp_name */
    sizeof(PyHeapTypeObject),                   /* tp_basicsize */
    sizeof(PyMemberDef),                        /* tp_itemsize */

    ......
};
```

`PyType_Type` 在类型机制中至关重要，所有用户自定义 `class` 所
对应的 `PyTypeObject` 对象都是通过 `PyType_Type`创建的


接下来我们看 `PyLong_Type` 是怎么与 `PyType_Type` 建立联系的。
前面提到，在Python中，每一个对象都将自己的引用计数、类型信息保存在开始的部分中。
为了方便对这部分内存初始化，Python中提供了几个有用的宏:

`源文件：`[Include/object.h](https://github.com/python/cpython/blob/v3.7.0/Include/object.h#L69)

```c
// Include/object.h
#ifdef Py_TRACE_REFS
    #define _PyObject_EXTRA_INIT 0, 0,
#else
    #define _PyObject_EXTRA_INIT
#endif

#define PyObject_HEAD_INIT(type)        \
    { _PyObject_EXTRA_INIT              \
    1, type },
```

这些宏在各种内建类型对象的初始化中被大量使用。
以`PyLong_Type`为例，可以清晰的看到一般的类型对象和`PyType_Type`之间的关系

`源文件：`[Objects/longobject.c](https://github.com/python/cpython/blob/v3.7.0/Objects/longobject.c#L5379)

```c
// Objects/longobject.c

PyTypeObject PyLong_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "int",                                      /* tp_name */
    offsetof(PyLongObject, ob_digit),           /* tp_basicsize */
    sizeof(digit),                              /* tp_itemsize */

    ......
};
```

下图是对象运行时的图像表现

![](object_runtime_relation.jpg)


## 对象的创建

Python创建对象有两种方式

### 范型API 或称为 AOL (Abstract Object Layer)

这类API通常形如`PyObject_XXX`这样的形式。可以应用在任何Python对象上，
如`PyObject_Print`。创建一个整数对象的方式

```c
PyObject* longobj = PyObject_New(Pyobject, &PyLong_Type);
```

### 与类型相关的API 或称为 COL (Concrete Object Layer)

这类API 通常只能作用于某一种类型的对象上，对于每一种内建对象
Python都提供了这样一组API。例如整数对象，我们可以利用如下的API创建
```c
PyObject *longObj = PyLong_FromLong(10);
```

## 对象的行为

在 **PyTypeObject** 中定义了大量的函数指针。这些函数指针可以视为类型对象中
所定义的操作，这些操作直接决定着一个对象在运行时所表现出的行为，比如 **PyTypeObject** 中的 `tp_hash` 指明了该类型对象如何生成其`hash`值。

在**PyTypeObject**的代码中，我们还可以看到非常重要的三组操作族
- `PyNumberMethods *tp_as_number`
- `PySequenceMethods *tp_as_sequence`
- `PyMappingMethods *tp_as_mapping`


**PySequenceMethods** 的代码如下

`源文件：`[Include/object.h](https://github.com/python/cpython/blob/v3.7.0/Include/object.h#L240)

```c
// Include/object.h
typedef PyObject * (*binaryfunc)(PyObject *, PyObject *);

typedef struct {
    binaryfunc nb_matrix_multiply;
    binaryfunc nb_inplace_matrix_multiply;

    ......
} PyNumberMethods;
```

**PyNumberMethods** 定义了一个数值对象该支持的操作。一个数值对象如 整数对象，那么它的类型对象 `PyLong_Type`中`tp_as_number.nb_add`
就指定了它进行加法操作时的具体行为。

在以下代码中可以看出`PyLong_Type`中的`tp_as_number`项指向的是`long_as_number`

`源文件：`[Objects/longobject.h](https://github.com/python/cpython/blob/v3.7.0/Objects/longobject.c#L5342)

```c
// Objects/longobject.c
static PyNumberMethods long_as_number = {
    (binaryfunc)long_add,       /*nb_add*/
    (binaryfunc)long_sub,       /*nb_subtract*/
    (binaryfunc)long_mul,       /*nb_multiply*/

    ......
};

PyTypeObject PyLong_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "int",                                      /* tp_name */
    offsetof(PyLongObject, ob_digit),           /* tp_basicsize */
    sizeof(digit),                              /* tp_itemsize */
    long_dealloc,                               /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_reserved */
    long_to_decimal_string,                     /* tp_repr */
    &long_as_number,                            /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */

    ......
};
```

`PySequenceMethods *tp_as_sequence` 和 `PyMappingMethods *tp_as_mapping`的分析与`PyNumberMethods *tp_as_number` 相同，大家可以自行查阅源码


## 对象的多态性

Python创建一个对象比如 **PyLongObject** 时，会分配内存进行初始化，然后
Python内部会用 `PyObject*` 变量来维护这个对象，其他对象也与此类似

所以在 Python 内部各个函数之间传递的都是一种范型指针 `PyObject*`
我们不知道这个指针所指的对象是什么类型，只能通过所指对象的 `ob_type` 域
动态进行判断，而Python正是通过 `ob_type` 实现了多态机制

考虑以下的 py_hash 函数

```c
Py_hash_t
calc_hash(PyObject* object)
{
    Py_hash_t hash = object->ob_type->tp_hash(object);
    return hash;
}
```

如果传递给 calc_hash 函数的指针是一个 `PyLongObject*`，那么它会调用 PyLongObject 对象对应的类型对象中定义的 hash操作`tp_hash`，`tp_hash`可以在**PyTypeObject中找到，
而具体赋值绑定我们可以在 `PyLong_Type` 初始化代码中看到绑定的是`long_hash`函数

`源文件：`[Objects/longobject.c](https://github.com/python/cpython/blob/v3.7.0/Objects/longobject.c#L5379)

```c
// Objects/longobject.c
PyTypeObject PyLong_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "int",                                      /* tp_name */
    ...

    (hashfunc)long_hash,                        /* tp_hash */

    ...
};
```

如果指针是一个 `PyUnicodeObject*`，那么就会调用 PyUnicodeObject 对象对应的类型对象中定义的输出操作，查看源码可以看到 实际绑定的是 `unicode_hash`函数

`源文件：`[Objects/unicodeobject.c](https://github.com/python/cpython/blob/v3.7.0/Objects/unicodeobject.c#L15066)

```c
// Objects/unicodeobject.c
PyTypeObject PyUnicode_Type = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    "str",              /* tp_name */

    ...

    (hashfunc) unicode_hash,        /* tp_hash*/

    ...
};
```


## 引用计数

Python 通过引用计数来管理维护对象在内存中的存在与否

Python 中的每个东西都是一个对象， 都有`ob_refcnt` 变量，这个变量维护对象的引用计数，从而最终决定该对象的创建与销毁

在Python中，主要通过 `Py_INCREF(op)`与`Py_DECREF(op)` 这两个宏
来增加和减少对一个对象的引用计数。当一个对象的引用计数减少到0之后，
`Py_DECREF`将调用该对象的`tp_dealloc`来释放对象所占用的内存和系统资源；

但这并不意味着最终一定会调用 `free` 释放内存空间。因为频繁的申请、释放内存会大大降低Python的执行效率。因此Python中大量采用了内存对象池的技术，使得对象释放的空间归还给内存池而不是直接`free`，后续使用可先从对象池中获取

`源文件：`[Include/object.h](https://github.com/python/cpython/blob/v3.7.0/Include/object.h#L777)

```c
// Include/object.h
#define _Py_NewReference(op) (                          \
    _Py_INC_TPALLOCS(op) _Py_COUNT_ALLOCS_COMMA         \
    _Py_INC_REFTOTAL  _Py_REF_DEBUG_COMMA               \
    Py_REFCNT(op) = 1)

#define Py_INCREF(op) (                         \
    _Py_INC_REFTOTAL  _Py_REF_DEBUG_COMMA       \
    ((PyObject *)(op))->ob_refcnt++)

#define Py_DECREF(op)                                   \
    do {                                                \
        PyObject *_py_decref_tmp = (PyObject *)(op);    \
        if (_Py_DEC_REFTOTAL  _Py_REF_DEBUG_COMMA       \
        --(_py_decref_tmp)->ob_refcnt != 0)             \
            _Py_CHECK_REFCNT(_py_decref_tmp)            \
        else                                            \
            _Py_Dealloc(_py_decref_tmp);                \
    } while (0)
```
