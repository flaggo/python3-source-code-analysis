<script setup>
import { ref, shallowRef, computed, onUnmounted } from 'vue'
import TOY_SRC from '../../docs/practice/mini-vm/minivm.py?raw'
import { getPyodide } from './pyodide'

const EXAMPLES = {
  '算术表达式': 'a = 5\nb = 3\nc = a + b * 2\nprint(c)',
  'if / else': 'x = 7\nif x % 2 == 0:\n    print(0)\nelse:\n    print(1)',
  'while 累加': 's = 0\ni = 1\nwhile i <= 5:\n    s = s + i\n    i = i + 1\nprint(s)',
  '递归阶乘': 'def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n\nprint(fact(5))',
  '递归 Fibonacci': 'def fib(n):\n    if n < 2:\n        return n\n    return fib(n - 1) + fib(n - 2)\n\nprint(fib(6))',
}

const code = ref(EXAMPLES['递归阶乘'])
const status = ref('idle')        // idle | loading | ready | error
const statusMsg = ref('')
const pyodide = shallowRef(null)
const pyMod = shallowRef(null)
const trace = shallowRef([])
const codes = shallowRef({})
const step = ref(0)
const errorMsg = ref('')
let timer = null

const hasTrace = computed(() => trace.value.length > 0)
const cur = computed(() => trace.value[step.value] || null)
const activeFrame = computed(() => {
  const c = cur.value
  if (!c || !c.frames.length) return null
  return c.frames[c.frames.length - 1]
})
const activeListing = computed(() => {
  const f = activeFrame.value
  if (!f) return []
  return (codes.value[f.code_id] || {}).listing || []
})
const revStack = computed(() => {
  const f = activeFrame.value
  if (!f) return []
  return f.stack.slice().reverse()    // 栈顶显示在最上面
})

async function ensurePyodide() {
  if (pyMod.value) return pyMod.value
  status.value = 'loading'
  statusMsg.value = '正在加载 Python 运行环境（Pyodide，首次约数 MB，请稍候）…'
  const py = await getPyodide()
  // 把「迷你虚拟机」写进文件系统，当模块 import（这样它的 __main__ REPL 不会被触发）
  py.FS.writeFile('minivm_demo.py', TOY_SRC)
  pyMod.value = py.pyimport('minivm_demo')
  pyodide.value = py
  status.value = 'ready'
  statusMsg.value = ''
  return pyMod.value
}

async function runCode() {
  stopAuto()
  errorMsg.value = ''
  try {
    const mod = await ensurePyodide()
    const out = mod.run_trace(code.value)   // 在 WASM-Python 里编译并带轨迹执行，返回 JSON 字符串
    const data = JSON.parse(out)
    codes.value = data.codes || {}
    trace.value = data.trace || []
    step.value = 0
    if (!data.ok) {
      errorMsg.value = data.error
      status.value = 'error'
    } else {
      status.value = 'ready'
    }
  } catch (e) {
    errorMsg.value = String(e)
    status.value = 'error'
  }
}

function next() { if (step.value < trace.value.length - 1) step.value++; else stopAuto() }
function prev() { if (step.value > 0) step.value-- }
function reset() { stopAuto(); step.value = 0 }
function stopAuto() { if (timer) { clearInterval(timer); timer = null } }
function auto() {
  if (timer) { stopAuto(); return }
  timer = setInterval(next, 320)
}
onUnmounted(stopAuto)

function pickExample(e) {
  code.value = EXAMPLES[e.target.value]
  trace.value = []
  step.value = 0
  errorMsg.value = ''
}
</script>

<template>
  <div class="minivm">
    <div class="mv-editor">
      <div class="mv-toolbar">
        <select class="mv-select" @change="pickExample" title="选择示例">
          <option v-for="(_, name) in EXAMPLES" :key="name" :value="name"
                  :selected="EXAMPLES[name] === code">{{ name }}</option>
        </select>
        <span class="mv-spacer" />
        <span v-if="status === 'loading'" class="mv-hint">{{ statusMsg }}</span>
      </div>
      <textarea v-model="code" class="mv-code" spellcheck="false" rows="7"></textarea>
      <div class="mv-controls">
        <button class="mv-btn mv-run" :disabled="status === 'loading'" @click="runCode">
          {{ status === 'loading' ? '加载中…' : '▶ 编译并运行' }}
        </button>
        <template v-if="hasTrace">
          <button class="mv-btn" @click="reset" title="回到开头">⟲ 重置</button>
          <button class="mv-btn" :disabled="step === 0" @click="prev">◀ 上一步</button>
          <button class="mv-btn" :disabled="step >= trace.length - 1" @click="next">下一步 ▶</button>
          <button class="mv-btn" @click="auto">{{ timer ? '⏸ 暂停' : '⏵ 自动' }}</button>
          <span class="mv-step">第 {{ step + 1 }} / {{ trace.length }} 步</span>
        </template>
      </div>
      <div v-if="errorMsg" class="mv-error">⚠ {{ errorMsg }}</div>
    </div>

    <div v-if="hasTrace" class="mv-stage">
      <!-- 字节码 + 指令指针 -->
      <div class="mv-panel mv-bytecode">
        <div class="mv-title">字节码 · {{ activeFrame ? activeFrame.name : '' }}</div>
        <ol class="mv-instrs">
          <li v-for="(ins, i) in activeListing" :key="i"
              :class="{ active: activeFrame && i === activeFrame.pc }">
            <span class="mv-ptr">{{ activeFrame && i === activeFrame.pc ? '▶' : '' }}</span>
            <span class="mv-off">{{ i }}</span>
            <span class="mv-ins">{{ ins }}</span>
          </li>
        </ol>
      </div>

      <!-- 求值栈 -->
      <div class="mv-panel mv-stack">
        <div class="mv-title">求值栈</div>
        <div class="mv-cells">
          <div v-if="!revStack.length" class="mv-empty">（空）</div>
          <div v-for="(v, i) in revStack" :key="i" class="mv-cell" :class="{ top: i === 0 }">
            {{ v }}<span v-if="i === 0" class="mv-tag">栈顶</span>
          </div>
        </div>
      </div>

      <!-- 局部变量 -->
      <div class="mv-panel mv-locals">
        <div class="mv-title">局部变量</div>
        <div class="mv-cells">
          <div v-if="!activeFrame || !activeFrame.locals.length" class="mv-empty">（空）</div>
          <div v-for="(kv, i) in (activeFrame ? activeFrame.locals : [])" :key="i" class="mv-kv">
            <span class="mv-k">{{ kv[0] }}</span><span class="mv-eq">=</span><span class="mv-v">{{ kv[1] }}</span>
          </div>
        </div>
      </div>

      <!-- 调用栈 / 帧栈 -->
      <div class="mv-panel mv-frames">
        <div class="mv-title">调用栈（帧栈）</div>
        <div class="mv-framelist">
          <div v-for="(fr, i) in cur.frames" :key="i" class="mv-frame"
               :class="{ active: i === cur.frames.length - 1 }">
            <span class="mv-fname">{{ fr.name }}</span>
            <span class="mv-fpc">pc={{ fr.pc }}</span>
            <span v-if="i === cur.frames.length - 1" class="mv-tag">活动</span>
          </div>
        </div>
      </div>

      <!-- 输出 -->
      <div class="mv-panel mv-output">
        <div class="mv-title">输出{{ cur.done ? ' · ✓ 执行结束' : '' }}</div>
        <pre class="mv-out">{{ cur.output || '（暂无输出）' }}</pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.minivm {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 14px;
  margin: 18px 0;
  background: var(--vp-c-bg-soft);
  font-size: 13px;
}
.mv-toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.mv-spacer { flex: 1; }
.mv-hint { color: var(--vp-c-text-2); font-size: 12px; }
.mv-select {
  padding: 4px 8px; border-radius: 6px;
  border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
}
.mv-code {
  width: 100%; box-sizing: border-box;
  font-family: var(--vp-font-family-mono, 'SF Mono', monospace);
  font-size: 13px; line-height: 1.5;
  padding: 10px; border-radius: 8px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg); color: var(--vp-c-text-1);
  resize: vertical;
}
.mv-controls { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-top: 10px; }
.mv-btn {
  padding: 5px 12px; border-radius: 6px; cursor: pointer;
  border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg);
  color: var(--vp-c-text-1); font-size: 12.5px;
}
.mv-btn:hover:not(:disabled) { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }
.mv-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.mv-run { background: var(--vp-c-brand-1); color: #fff; border-color: var(--vp-c-brand-1); font-weight: 600; }
.mv-run:hover:not(:disabled) { background: var(--vp-c-brand-2); color: #fff; }
.mv-step { color: var(--vp-c-text-2); font-size: 12px; margin-left: 4px; }
.mv-error {
  margin-top: 10px; padding: 8px 12px; border-radius: 6px;
  background: var(--vp-c-danger-soft); color: var(--vp-c-danger-1); font-size: 12.5px;
}
.mv-stage {
  display: grid; gap: 10px; margin-top: 14px;
  grid-template-columns: 1.4fr 1fr 1fr;
  grid-template-areas: 'bytecode stack locals' 'bytecode frames output';
}
.mv-bytecode { grid-area: bytecode; }
.mv-stack { grid-area: stack; }
.mv-locals { grid-area: locals; }
.mv-frames { grid-area: frames; }
.mv-output { grid-area: output; }
.mv-panel {
  border: 1px solid var(--vp-c-divider); border-radius: 8px;
  background: var(--vp-c-bg); padding: 8px 10px; overflow: auto;
}
.mv-title { font-weight: 600; font-size: 12px; color: var(--vp-c-text-2); margin-bottom: 6px; }
.mv-instrs { list-style: none; margin: 0; padding: 0; font-family: var(--vp-font-family-mono, monospace); font-size: 12.5px; }
.mv-instrs li { display: flex; align-items: center; gap: 6px; padding: 1px 4px; border-radius: 4px; white-space: nowrap; }
.mv-instrs li.active { background: var(--vp-c-brand-soft); }
.mv-ptr { width: 12px; color: var(--vp-c-brand-1); }
.mv-off { width: 20px; text-align: right; color: var(--vp-c-text-3); }
.mv-ins { color: var(--vp-c-text-1); }
.mv-cells { display: flex; flex-direction: column; gap: 4px; }
.mv-cell {
  font-family: var(--vp-font-family-mono, monospace); font-size: 12.5px;
  padding: 4px 8px; border-radius: 5px; border: 1px solid var(--vp-c-divider);
  display: flex; justify-content: space-between; align-items: center;
}
.mv-cell.top { border-color: var(--vp-c-brand-1); background: var(--vp-c-brand-soft); }
.mv-tag { font-size: 10px; color: var(--vp-c-brand-1); margin-left: 6px; }
.mv-empty { color: var(--vp-c-text-3); font-size: 12px; padding: 2px; }
.mv-kv { font-family: var(--vp-font-family-mono, monospace); font-size: 12.5px; padding: 2px 0; }
.mv-k { color: var(--vp-c-brand-1); }
.mv-eq { color: var(--vp-c-text-3); margin: 0 5px; }
.mv-v { color: var(--vp-c-text-1); }
.mv-framelist { display: flex; flex-direction: column-reverse; gap: 4px; }
.mv-frame {
  font-family: var(--vp-font-family-mono, monospace); font-size: 12px;
  padding: 4px 8px; border-radius: 5px; border: 1px solid var(--vp-c-divider);
  display: flex; align-items: center; gap: 8px;
}
.mv-frame.active { border-color: var(--vp-c-brand-1); background: var(--vp-c-brand-soft); }
.mv-fname { color: var(--vp-c-text-1); font-weight: 600; }
.mv-fpc { color: var(--vp-c-text-3); }
.mv-out { margin: 0; font-family: var(--vp-font-family-mono, monospace); font-size: 12.5px; color: var(--vp-c-text-1); white-space: pre-wrap; }
@media (max-width: 720px) {
  .mv-stage { grid-template-columns: 1fr; grid-template-areas: 'bytecode' 'frames' 'stack' 'locals' 'output'; }
}
</style>
