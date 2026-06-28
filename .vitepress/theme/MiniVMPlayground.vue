<script setup>
import { ref, nextTick } from 'vue'
import TOY_SRC from '../../practice/mini-vm/minivm.py?raw'
import { getPyodide } from './pyodide'

// 注入到 Pyodide 的「驱动」：把编辑后的 VM 源码 exec 进独立命名空间，
// 并维护一个跨 REPL 输入持久的 glob。这部分固定，不随用户编辑而变。
const DRIVER = `
import json

_vm_ns = None
_vm_glob = None

def load_vm(source):
    global _vm_ns, _vm_glob
    ns = {"__name__": "minivm_playground"}   # 避免触发源码里的 __main__ REPL
    try:
        exec(source, ns)
    except Exception as e:
        return json.dumps({"ok": False, "error": "加载 VM 出错：%s" % e})
    if "execute" not in ns:
        return json.dumps({"ok": False, "error": "源码里找不到 execute() 函数"})
    _vm_ns = ns
    _vm_glob = {}
    return json.dumps({"ok": True})

def reset_session():
    global _vm_glob
    _vm_glob = {}

def repl_eval(src):
    if _vm_ns is None:
        return json.dumps({"ok": False, "error": "请先点『应用并重载 VM』"})
    s = src
    echo = _vm_ns.get("_maybe_echo")
    if echo is not None:
        try:
            s = echo(src)
        except Exception:
            s = src
    try:
        text, _ = _vm_ns["execute"](s, _vm_glob)
        return json.dumps({"ok": True, "output": text})
    except Exception as e:
        return json.dumps({"ok": False, "error": str(e)})
`

const vmSource = ref(TOY_SRC)
const vmError = ref('')
const status = ref('idle')            // idle | loading | ready | error
const py = ref(null)

// 终端式 REPL 状态
const term = ref([])                  // 已提交的行 [{kind:'in'|'out'|'err'|'muted', text}]
const pendingLines = ref([])          // 当前未执行完的块（多行 def/if/while）
const current = ref('')               // 活动输入行
const busy = ref(false)
const termRef = ref(null)
const inputRef = ref(null)
let cmdHistory = []
let histIdx = 0

async function ensureDriver() {
  if (py.value) return py.value
  status.value = 'loading'
  const p = await getPyodide()
  p.runPython(DRIVER)
  py.value = p
  status.value = 'ready'
  return p
}

async function loadVM(quiet) {
  vmError.value = ''
  const p = await ensureDriver()
  const res = JSON.parse(p.globals.get('load_vm')(vmSource.value))
  if (!res.ok) { vmError.value = res.error; status.value = 'error'; return false }
  status.value = 'ready'
  if (!quiet) {
    term.value = [{ kind: 'muted', text: '— 已应用 VM 源码，会话已重置 —' }]
    pendingLines.value = []
    current.value = ''
  }
  return true
}

async function applyVM() {
  try { await loadVM(false) } catch (e) { vmError.value = String(e); status.value = 'error' }
  await scrollDown(); focusInput()
}

function resetVM() { vmSource.value = TOY_SRC; vmError.value = '' }

async function clearSession() {
  if (py.value) py.value.runPython('reset_session()')
  term.value = []; pendingLines.value = []; current.value = ''
  focusInput()
}

async function runStatement(lines) {
  // 把输入回显进终端
  const echoed = lines.map((l, i) => ({ kind: 'in', text: (i === 0 ? '>>> ' : '... ') + l }))
  term.value = [...term.value, ...echoed]
  if (lines.length === 1 && lines[0].trim()) cmdHistory.push(lines[0])  // 仅单行进历史
  histIdx = cmdHistory.length
  busy.value = true
  await scrollDown()
  try {
    if (!py.value || py.value.globals.get('_vm_ns') == null) {
      term.value = [...term.value, { kind: 'muted', text: '（首次运行：正在加载 Python 运行环境，请稍候…）' }]
      await scrollDown()
      const ok = await loadVM(true)
      if (!ok) { term.value = [...term.value, { kind: 'err', text: vmError.value }]; busy.value = false; return }
    }
    const res = JSON.parse(py.value.globals.get('repl_eval')(lines.join('\n')))
    if (res.ok) {
      if (res.output) term.value = [...term.value, { kind: 'out', text: res.output }]
    } else {
      term.value = [...term.value, { kind: 'err', text: res.error }]
    }
  } catch (e) {
    term.value = [...term.value, { kind: 'err', text: String(e) }]
  }
  busy.value = false
  await scrollDown(); focusInput()
}

function onKeydown(e) {
  if (e.isComposing) return                 // 输入法组合中，别误触发
  if (e.key === 'Enter') {
    e.preventDefault()
    if (busy.value) return
    const line = current.value
    current.value = ''
    const starting = pendingLines.value.length === 0
    if (starting && line.trim() === '') return
    if (starting && !line.trim().endsWith(':')) {
      runStatement([line])
    } else if (starting) {                  // 以冒号结尾 → 进入续行
      pendingLines.value = [line]
    } else if (line.trim() === '') {        // 块中空行 → 执行整块
      const blk = pendingLines.value.slice()
      pendingLines.value = []
      runStatement(blk)
    } else {
      pendingLines.value = [...pendingLines.value, line]
    }
    scrollDown()
  } else if (e.key === 'ArrowUp') {
    if (pendingLines.value.length === 0 && cmdHistory.length) {
      e.preventDefault()
      histIdx = Math.max(0, histIdx - 1)
      current.value = cmdHistory[histIdx] ?? ''
    }
  } else if (e.key === 'ArrowDown') {
    if (pendingLines.value.length === 0 && cmdHistory.length) {
      e.preventDefault()
      histIdx = Math.min(cmdHistory.length, histIdx + 1)
      current.value = cmdHistory[histIdx] ?? ''
    }
  }
}

function focusInput() { nextTick(() => inputRef.value && inputRef.value.focus()) }
async function scrollDown() {
  await nextTick()
  const el = termRef.value
  if (el) el.scrollTop = el.scrollHeight
}
</script>

<template>
  <div class="pg">
    <div class="pg-cols">
      <!-- 左：可编辑的 VM 源码 -->
      <div class="pg-col">
        <div class="pg-head">
          <span class="pg-title">虚拟机源码 · minivm.py（可编辑）</span>
          <span class="pg-spacer" />
          <button class="pg-btn" @click="resetVM" title="还原成默认源码">还原默认</button>
          <button class="pg-btn pg-apply" :disabled="status === 'loading'" @click="applyVM">
            {{ status === 'loading' ? '加载中…' : '应用并重载 VM' }}
          </button>
        </div>
        <textarea v-model="vmSource" class="pg-src" spellcheck="false"></textarea>
        <div v-if="vmError" class="pg-error">⚠ {{ vmError }}</div>
      </div>

      <!-- 右：终端式 REPL（直接输入） -->
      <div class="pg-col">
        <div class="pg-head">
          <span class="pg-title">交互式 REPL（用你改过的 VM 执行）</span>
          <span class="pg-spacer" />
          <button class="pg-btn" @click="clearSession" title="清空历史并重置变量">清空会话</button>
        </div>
        <div ref="termRef" class="pg-term" @click="focusInput">
          <div v-if="!term.length && !pendingLines.length" class="pg-muted">
            直接在这里输入，回车执行——就像一个 Python REPL。<br />
            支持赋值、算术 / 比较、if / while、def / return（含递归）、print；纯表达式回显结果。
          </div>
          <div v-for="(h, i) in term" :key="i" class="pg-line" :class="'pg-' + h.kind">{{ h.text }}</div>
          <div v-for="(l, i) in pendingLines" :key="'p' + i" class="pg-line pg-in">{{ (i === 0 ? '>>> ' : '... ') + l }}</div>
          <div class="pg-active">
            <span class="pg-prompt">{{ pendingLines.length ? '... ' : '>>> ' }}</span>
            <input ref="inputRef" v-model="current" class="pg-cmd" spellcheck="false"
                   autocomplete="off" autocapitalize="off" :disabled="busy" @keydown="onKeydown" />
          </div>
        </div>
      </div>
    </div>
    <div class="pg-tip">
      💡 试试改造虚拟机：在左侧给 <code>_binop</code> 加一个新运算符、或新增一条指令，点「应用并重载 VM」，
      再到右侧 REPL 里直接敲代码验证。改坏了点「还原默认」即可。
    </div>
  </div>
</template>

<style scoped>
.pg {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 14px;
  margin: 18px auto;
  max-width: 1100px;
  background: var(--vp-c-bg-soft);
  font-size: 13px;
}
.pg-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.pg-col { display: flex; flex-direction: column; min-width: 0; }
.pg-head { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.pg-title { font-weight: 600; font-size: 12px; color: var(--vp-c-text-2); }
.pg-spacer { flex: 1; }
.pg-btn {
  padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 12px;
  border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg); color: var(--vp-c-text-1);
}
.pg-btn:hover:not(:disabled) { border-color: var(--vp-c-brand-1); color: var(--vp-c-brand-1); }
.pg-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.pg-apply { background: var(--vp-c-brand-1); color: #fff; border-color: var(--vp-c-brand-1); font-weight: 600; }
.pg-apply:hover:not(:disabled) { background: var(--vp-c-brand-2); color: #fff; }
.pg-src {
  width: 100%; box-sizing: border-box; height: 420px; resize: vertical;
  font-family: var(--vp-font-family-mono, monospace); font-size: 12px; line-height: 1.5;
  padding: 10px; border-radius: 8px; border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg); color: var(--vp-c-text-1); white-space: pre; overflow: auto;
}
.pg-term {
  height: 420px; box-sizing: border-box; overflow: auto; cursor: text;
  padding: 10px 12px; border-radius: 8px; border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg); color: var(--vp-c-text-1);
  font-family: var(--vp-font-family-mono, monospace); font-size: 12.5px; line-height: 1.6;
}
.pg-line { white-space: pre-wrap; word-break: break-word; }
.pg-in { color: var(--vp-c-text-1); }
.pg-out { color: var(--vp-c-brand-1); }
.pg-err { color: var(--vp-c-danger-1); white-space: pre-wrap; }
.pg-muted { color: var(--vp-c-text-3); }
.pg-active { display: flex; align-items: baseline; }
.pg-prompt { color: var(--vp-c-text-3); white-space: pre; flex: none; }
.pg-cmd {
  flex: 1; min-width: 0; border: none; outline: none; background: transparent;
  font-family: inherit; font-size: inherit; line-height: inherit;
  color: var(--vp-c-text-1); caret-color: var(--vp-c-brand-1); padding: 0;
}
.pg-cmd:disabled { color: var(--vp-c-text-3); }
.pg-error {
  margin-top: 8px; padding: 8px 12px; border-radius: 6px;
  background: var(--vp-c-danger-soft); color: var(--vp-c-danger-1); font-size: 12.5px; white-space: pre-wrap;
}
.pg-tip {
  margin-top: 12px; padding: 8px 12px; border-radius: 8px;
  background: var(--vp-c-bg); border: 1px dashed var(--vp-c-divider);
  color: var(--vp-c-text-2); font-size: 12px; line-height: 1.6;
}
.pg-tip code, .pg-muted code { font-family: var(--vp-font-family-mono, monospace); color: var(--vp-c-brand-1); }
@media (max-width: 720px) {
  .pg-cols { grid-template-columns: 1fr; }
  .pg-src, .pg-term { height: 280px; }
}
</style>
