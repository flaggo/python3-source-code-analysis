"""minivm.py —— 一个用 Python 写成的迷你 Python 虚拟机。

流水线：源码 → AST（ast.parse）→ 玩具字节码 → 求值循环（带帧栈）。

对外只暴露 run_trace(src) -> JSON 字符串：把一段源码编译并「带轨迹地」执行，
返回每一步的帧栈快照，供浏览器里的可视化组件单步播放。

为了直观，玩具字节码把名字与常量直接内联在指令参数里
（真实 CPython 用下标去 co_consts / co_varnames 查表）。
"""
import ast
import json

_counter = 0
def _new_id():
    global _counter
    _counter += 1
    return "c%d" % _counter


# ============ 字节码：一条指令就是 (op, arg) ============

class Code:
    """一段可执行的字节码：模块体，或一个函数体。"""
    def __init__(self, name, params=()):
        self.id = _new_id()
        self.name = name
        self.params = list(params)   # 形参名
        self.instrs = []             # [[op, arg], ...]

    def emit(self, op, arg=None):
        self.instrs.append([op, arg])
        return len(self.instrs) - 1

    def listing(self):
        """生成给人看的反汇编文本。"""
        out = []
        for op, arg in self.instrs:
            if op == "MAKE_FUNCTION":
                a = arg.name
            elif arg is None:
                a = ""
            elif op == "LOAD_CONST":
                a = repr(arg)
            else:
                a = str(arg)
            out.append((op + " " + a).strip())
        return out


# ============ 编译器：AST → 玩具字节码 ============

BINOPS = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
          ast.FloorDiv: "//", ast.Mod: "%", ast.Pow: "**"}
CMPOPS = {ast.Lt: "<", ast.LtE: "<=", ast.Gt: ">", ast.GtE: ">=",
          ast.Eq: "==", ast.NotEq: "!="}


class CompileError(Exception):
    pass


def assigned_names(body):
    """收集函数体里被赋值过的名字（连同形参，就是这个函数的局部变量）。"""
    names = set()
    for stmt in body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names.add(t.id)
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name):
                names.add(node.target.id)
    return names


class Compiler:
    def __init__(self, code, scope, localnames):
        self.code = code
        self.scope = scope            # 'module' | 'function'
        self.localnames = localnames  # 函数作用域内的局部名字集合

    def compile_stmts(self, stmts):
        for s in stmts:
            self.compile_stmt(s)

    # ---- 语句 ----
    def compile_stmt(self, s):
        if isinstance(s, ast.Assign):
            if len(s.targets) != 1 or not isinstance(s.targets[0], ast.Name):
                raise CompileError("只支持 `名字 = 表达式` 形式的赋值")
            self.compile_expr(s.value)
            self.store_name(s.targets[0].id)
        elif isinstance(s, ast.AugAssign):
            if not isinstance(s.target, ast.Name):
                raise CompileError("只支持对名字做 += 这类增量赋值")
            if type(s.op) not in BINOPS:
                raise CompileError("暂不支持的运算符")
            self.load_name(s.target.id)
            self.compile_expr(s.value)
            self.code.emit("BINARY_OP", BINOPS[type(s.op)])
            self.store_name(s.target.id)
        elif isinstance(s, ast.If):
            self.compile_if(s)
        elif isinstance(s, ast.While):
            self.compile_while(s)
        elif isinstance(s, ast.Return):
            if self.scope != "function":
                raise CompileError("return 只能用在函数里")
            if s.value is None:
                self.code.emit("LOAD_CONST", None)
            else:
                self.compile_expr(s.value)
            self.code.emit("RETURN_VALUE")
        elif isinstance(s, ast.FunctionDef):
            self.compile_funcdef(s)
        elif isinstance(s, ast.Expr):
            self.compile_expr(s.value)
            self.code.emit("POP_TOP")   # 表达式语句：算完把结果丢弃
        elif isinstance(s, ast.Pass):
            pass
        else:
            raise CompileError("暂不支持的语句：%s" % type(s).__name__)

    def compile_if(self, s):
        self.compile_expr(s.test)
        jmp_else = self.code.emit("POP_JUMP_IF_FALSE", None)   # 占位，待回填
        self.compile_stmts(s.body)
        if s.orelse:
            jmp_end = self.code.emit("JUMP_ABSOLUTE", None)
            self.code.instrs[jmp_else][1] = len(self.code.instrs)   # 回填 else 落点
            self.compile_stmts(s.orelse)
            self.code.instrs[jmp_end][1] = len(self.code.instrs)    # 回填汇合点
        else:
            self.code.instrs[jmp_else][1] = len(self.code.instrs)

    def compile_while(self, s):
        start = len(self.code.instrs)
        self.compile_expr(s.test)
        jmp_end = self.code.emit("POP_JUMP_IF_FALSE", None)
        self.compile_stmts(s.body)
        self.code.emit("JUMP_ABSOLUTE", start)                  # 往回跳，形成循环
        self.code.instrs[jmp_end][1] = len(self.code.instrs)    # 回填循环出口

    def compile_funcdef(self, s):
        if self.scope != "module":
            raise CompileError("迷你版只支持在模块顶层定义函数（不支持嵌套 / 闭包）")
        a = s.args
        if (a.vararg or a.kwarg or a.kwonlyargs or a.defaults or a.kw_defaults):
            raise CompileError("函数暂只支持简单的位置参数")
        params = [arg.arg for arg in a.args]
        fcode = Code(s.name, params)
        local = set(params) | assigned_names(s.body)
        Compiler(fcode, "function", local).compile_stmts(s.body)
        fcode.emit("LOAD_CONST", None)    # 函数体跑到尽头：隐式 return None
        fcode.emit("RETURN_VALUE")
        self.code.emit("MAKE_FUNCTION", fcode)
        self.store_name(s.name)

    # ---- 表达式 ----
    def compile_expr(self, e):
        if isinstance(e, ast.Constant):
            if not isinstance(e.value, (int, float)) and e.value is not None:
                raise CompileError("迷你版只支持数字 / 布尔 / None 常量")
            self.code.emit("LOAD_CONST", e.value)
        elif isinstance(e, ast.Name):
            self.load_name(e.id)
        elif isinstance(e, ast.BinOp):
            if type(e.op) not in BINOPS:
                raise CompileError("暂不支持的运算符")
            self.compile_expr(e.left)
            self.compile_expr(e.right)
            self.code.emit("BINARY_OP", BINOPS[type(e.op)])
        elif isinstance(e, ast.UnaryOp) and isinstance(e.op, ast.USub):
            self.compile_expr(e.operand)
            self.code.emit("UNARY_NEG")
        elif isinstance(e, ast.Compare):
            if len(e.ops) != 1:
                raise CompileError("暂不支持连续比较（如 a < b < c）")
            if type(e.ops[0]) not in CMPOPS:
                raise CompileError("暂不支持的比较运算符")
            self.compile_expr(e.left)
            self.compile_expr(e.comparators[0])
            self.code.emit("COMPARE_OP", CMPOPS[type(e.ops[0])])
        elif isinstance(e, ast.Call):
            self.compile_call(e)
        else:
            raise CompileError("暂不支持的表达式：%s" % type(e).__name__)

    def compile_call(self, e):
        if e.keywords:
            raise CompileError("函数调用暂不支持关键字参数")
        if isinstance(e.func, ast.Name) and e.func.id == "print":
            if len(e.args) != 1:
                raise CompileError("迷你版的 print 只接受一个参数")
            self.compile_expr(e.args[0])
            self.code.emit("PRINT")            # 输出，并压入 None（print 返回 None）
            return
        self.compile_expr(e.func)              # 先把函数对象压栈
        for a in e.args:                       # 再依次压入实参
            self.compile_expr(a)
        self.code.emit("CALL_FUNCTION", len(e.args))

    # ---- 名字的载入 / 存储：迷你 LEGB ----
    def load_name(self, name):
        if self.scope == "function":
            if name in self.localnames:
                self.code.emit("LOAD_FAST", name)     # 局部变量
            else:
                self.code.emit("LOAD_GLOBAL", name)   # 模块级（如调用别的函数）
        else:
            self.code.emit("LOAD_NAME", name)

    def store_name(self, name):
        if self.scope == "function":
            self.code.emit("STORE_FAST", name)
        else:
            self.code.emit("STORE_NAME", name)


def compile_module(src):
    tree = ast.parse(src)
    code = Code("<module>")
    Compiler(code, "module", set()).compile_stmts(tree.body)
    return code


# ============ 虚拟机：求值循环 + 帧栈 ============

class Frame:
    """执行一段字节码的现场：求值栈、局部变量、指令指针。"""
    def __init__(self, code, local, glob, kind):
        self.code = code
        self.locals = local      # 名字 -> 值
        self.globals = glob
        self.kind = kind         # 'module' | 'function'
        self.stack = []          # 求值栈
        self.pc = 0              # 指令指针


class VMError(Exception):
    pass


MAX_STEPS = 6000
MAX_DEPTH = 60


def _disp(v):
    if isinstance(v, Code):
        return "<function %s>" % v.name
    if v is None:
        return "None"
    if v is True:
        return "True"
    if v is False:
        return "False"
    return repr(v)


def _truthy(v):
    return not (v is None or v is False or v == 0)


def _binop(op, a, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise VMError("除以零")
        return a / b
    if op == "//":
        if b == 0:
            raise VMError("除以零")
        return a // b
    if op == "%":
        return a % b
    if op == "**":
        return a ** b
    raise VMError("未知运算符 %s" % op)


def _compare(op, a, b):
    return {"<": a < b, "<=": a <= b, ">": a > b, ">=": a >= b,
            "==": a == b, "!=": a != b}[op]


def run(module_code, record):
    glob = {}
    frames = [Frame(module_code, glob, glob, "module")]
    output = []
    steps = 0

    while frames:
        f = frames[-1]

        # 当前帧跑到尽头
        if f.pc >= len(f.code.instrs):
            if f.kind == "function":         # 函数没显式 return：返回 None
                frames.pop()
                if frames:
                    frames[-1].stack.append(None)
                continue
            break                            # 模块体结束：整个程序结束

        record(frames, output)               # 记录「即将执行 f.pc 这条指令」的快照
        steps += 1
        if steps > MAX_STEPS:
            raise VMError("执行步数过多（可能是死循环）")

        op, arg = f.code.instrs[f.pc]
        f.pc += 1                            # 先前进，跳转指令会再改写

        if op == "LOAD_CONST":
            f.stack.append(arg)
        elif op == "LOAD_FAST":
            if arg not in f.locals:
                raise VMError("局部变量 %s 在赋值前被使用" % arg)
            f.stack.append(f.locals[arg])
        elif op == "STORE_FAST":
            f.locals[arg] = f.stack.pop()
        elif op == "LOAD_NAME":
            if arg not in f.locals:
                raise VMError("名字 %s 未定义" % arg)
            f.stack.append(f.locals[arg])
        elif op == "STORE_NAME":
            f.locals[arg] = f.stack.pop()
        elif op == "LOAD_GLOBAL":
            if arg not in glob:
                raise VMError("名字 %s 未定义" % arg)
            f.stack.append(glob[arg])
        elif op == "BINARY_OP":
            b = f.stack.pop()
            a = f.stack.pop()
            f.stack.append(_binop(arg, a, b))
        elif op == "UNARY_NEG":
            f.stack.append(-f.stack.pop())
        elif op == "COMPARE_OP":
            b = f.stack.pop()
            a = f.stack.pop()
            f.stack.append(_compare(arg, a, b))
        elif op == "POP_JUMP_IF_FALSE":
            if not _truthy(f.stack.pop()):
                f.pc = arg
        elif op == "JUMP_ABSOLUTE":
            f.pc = arg
        elif op == "PRINT":
            output.append(_disp(f.stack.pop()))
            f.stack.append(None)
        elif op == "POP_TOP":
            f.stack.pop()
        elif op == "MAKE_FUNCTION":
            f.stack.append(arg)              # arg 是函数体 Code，直接当函数对象
        elif op == "CALL_FUNCTION":
            argc = arg
            args = [f.stack.pop() for _ in range(argc)][::-1]
            func = f.stack.pop()
            if not isinstance(func, Code):
                raise VMError("不是可调用对象")
            if len(args) != len(func.params):
                raise VMError("%s() 需要 %d 个参数，给了 %d 个"
                              % (func.name, len(func.params), len(args)))
            if len(frames) >= MAX_DEPTH:
                raise VMError("递归过深（可能无限递归）")
            new_locals = dict(zip(func.params, args))
            frames.append(Frame(func, new_locals, glob, "function"))
        elif op == "RETURN_VALUE":
            retval = f.stack.pop()
            frames.pop()
            if frames:
                frames[-1].stack.append(retval)
        else:
            raise VMError("未知指令 %s" % op)

    record(frames, output, done=True)


# ============ 对外接口：带轨迹地跑一遍，返回 JSON ============

def _collect_codes(code, out):
    out[code.id] = {"name": code.name, "listing": code.listing()}
    for op, arg in code.instrs:
        if op == "MAKE_FUNCTION":
            _collect_codes(arg, out)


def run_trace(src):
    global _counter
    _counter = 0
    try:
        module_code = compile_module(src)
    except (SyntaxError, CompileError) as e:
        return json.dumps({"ok": False, "error": "编译错误：%s" % e})

    codes = {}
    _collect_codes(module_code, codes)
    trace = []

    def record(frames, output, done=False):
        trace.append({
            "frames": [
                {
                    "code_id": fr.code.id,
                    "name": fr.code.name,
                    "pc": fr.pc,
                    "stack": [_disp(x) for x in fr.stack],
                    "locals": [[k, _disp(v)] for k, v in fr.locals.items()],
                }
                for fr in frames
            ],
            "output": "\n".join(output),
            "done": done,
        })

    try:
        run(module_code, record)
    except Exception as e:                   # noqa: BLE001 —— 任何运行期错误都友好返回
        return json.dumps({"ok": False, "error": "运行错误：%s" % e,
                           "codes": codes, "trace": trace})

    return json.dumps({"ok": True, "codes": codes, "trace": trace})
