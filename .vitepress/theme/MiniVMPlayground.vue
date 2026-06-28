<script setup>
import { ref, shallowRef, nextTick } from 'vue'
import TOY_SRC from '../../practice/mini-vm/minivm.py?raw'
import { getPyodide } from './pyodide'

// 注入到 Pyodide 的「驱动」：把编辑后的 VM 源码 exec 进独立命名空间，
// 并维护一个跨 REPL 输入持久的 glob。这部分是固定的，不随用户编辑而变。
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
const replInput = ref('1 + 2 * 3')
const history = shallowRef([])        // [{kind:'in'|'out'|'err'|'muted', text}]
const status = ref('idle')            // idle | loading | ready | error
const statusMsg = ref('')
const vmError = ref('')
const py = shallowRef(null)
const historyBox = ref(null)

async function ensureDriver() {
  if (py.value) return py.value
  status.value = 'loading'
  statusMsg.value = '正在加载 Python 运行环境（Pyodide，首次约数 MB）…'
  const p = await getPyodide()
  p.runPython(DRIVER)
  py.value = p
  status.value = 'ready'
  statusMsg.value = ''
  return p
}

async function applyVM() {
  vmError.value = ''
  try {
    const p = await ensureDriver()
    const res = JSON.parse(p.globals.get('load_vm')(vmSource.value))
    if (!res.ok) { vmError.value = res.error; status.value = 'error'; return false }
    status.value = 'ready'
    history.value = [...history.value, { kind: 'muted', text: '— 已应用 VM 源码，会话已重置 —' }]
    await scrollDown()
    return true
  } catch (e) {
    vmError.value = String(e); status.value = 'error'; return false
  }
}

async function runRepl() {
  const src = replInput.value
  if (!src.trim()) return
  // 首次运行时若还没应用过 VM，自动应用一次
  if (!py.value || py.value.globals.get('_vm_ns') == null) {
    const ok = await applyVM()
    if (!ok) return
  }
  const lines = src.split('\n')
  const shown = lines.map((l, i) => (i === 0 ? '>>> ' : '... ') + l).join('\n')
  const entries = [...history.value, { kind: 'in', text: shown }]
  try {
    const res = JSON.parse(py.value.globals.get('repl_eval')(src))
    if (res.ok) {
      if (res.output) entries.push({ kind: 'out', text: res.output })
      else entries.push({ kind: 'muted', text: '（已执行，无输出）' })
    } else {
      entries.push({ kind: 'err', text: res.error })
    }
  } catch (e) {
    entries.push({ kind: 'err', text: String(e) })
  }
  history.value = entries
  replInput.value = ''
  await scrollDown()
}

async function clearSession() {
  if (py.value) py.value.runPython('reset_session()')
  history.value = []
}

function resetVM() {
  vmSource.value = TOY_SRC
  vmError.value = ''
}

function onKey(e) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') { e.preventDefault(); runRepl() }
}

async function scrollDown() {
  await nextTick()
  const el = historyBox.value
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

      <!-- 右：REPL -->
      <div class="pg-col">
        <div class="pg-head">
          <span class="pg-title">交互式 REPL（用你改过的 VM 执行）</span>
          <span class="pg-spacer" />
          <button class="pg-btn" @click="clearSession" title="清空历史并重置变量">清空会话</button>
        </div>
        <div ref="historyBox" class="pg-history">
          <div v-if="!history.length" class="pg-muted">
            在下方输入一句代码，回车或点「运行」。支持赋值、算术/比较、if/while、def/return（含递归）、print。
            <br />纯表达式会自动回显结果（如 <code>1 + 2 * 3</code> → <code>7</code>）。
          </div>
          <div v-for="(h, i) in history" :key="i" class="pg-line" :class="'pg-' + h.kind">{{ h.text }}</div>
        </div>
        <div class="pg-replbar">
          <textarea v-model="replInput" class="pg-input" spellcheck="false" rows="2"
                    placeholder="输入代码，⌘/Ctrl + Enter 运行" @keydown="onKey"></textarea>
          <button class="pg-btn pg-run" :disabled="status === 'loading'" @click="runRepl">运行 ▶</button>
        </div>
        <div v-if="status === 'loading'" class="pg-muted">{{ statusMsg }}</div>
      </div>
    </div>
    <div class="pg-tip">
      💡 试试改造虚拟机：在左侧给 <code>BINARY_OP</code> 加一个新运算符、或新增一条指令，点「应用并重载 VM」，
      再到右侧 REPL 验证效果。改坏了点「还原默认」即可。
    </div>
  </div>
</template>

<style scoped>
.pg {
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 14px;
  margin: 18px 0;
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
.pg-apply, .pg-run { background: var(--vp-c-brand-1); color: #fff; border-color: var(--vp-c-brand-1); font-weight: 600; }
.pg-apply:hover:not(:disabled), .pg-run:hover:not(:disabled) { background: var(--vp-c-brand-2); color: #fff; }
.pg-src {
  width: 100%; box-sizing: border-box; height: 360px; resize: vertical;
  font-family: var(--vp-font-family-mono, monospace); font-size: 12px; line-height: 1.5;
  padding: 10px; border-radius: 8px; border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg); color: var(--vp-c-text-1); white-space: pre; overflow: auto;
}
.pg-history {
  height: 300px; overflow: auto; padding: 10px; border-radius: 8px;
  border: 1px solid var(--vp-c-divider); background: var(--vp-c-bg);
  font-family: var(--vp-font-family-mono, monospace); font-size: 12.5px; line-height: 1.55;
}
.pg-line { white-space: pre-wrap; }
.pg-in { color: var(--vp-c-text-1); }
.pg-out { color: var(--vp-c-brand-1); }
.pg-err { color: var(--vp-c-danger-1); }
.pg-muted { color: var(--vp-c-text-3); }
.pg-replbar { display: flex; gap: 8px; margin-top: 8px; align-items: stretch; }
.pg-input {
  flex: 1; box-sizing: border-box; resize: vertical;
  font-family: var(--vp-font-family-mono, monospace); font-size: 12.5px;
  padding: 8px 10px; border-radius: 8px; border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg); color: var(--vp-c-text-1);
}
.pg-run { align-self: stretch; white-space: nowrap; }
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
  .pg-src { height: 240px; }
}
</style>
