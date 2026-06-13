# Validation brief · 实际测试简报

*English first, 中文在后。*

---

## English

### Verdict
The generic engine is **decoupled** (zero domain code), **runs zero-dependency** on Python 3.8+,
and was **validated against a real, live knowledge graph**: it reproduced the domain-native audit
exactly, a real survey converged it, and the optional label-preservation capability surfaced real
leaks and demonstrated a working remediation. **12/12 unit tests pass.**

### Environment & method
- Python 3.10 (no `tomllib`, no network) → exercised the built-in TOML fallback and zero-dep path.
- Engine run as `python -m budgood_perimeter <cmd> --config <toml>`.
- Real store: a live knowledge-graph checkout (`buddhist-corpus/_indexes/v0_3`), driven only by
  the `examples/buddhist-kg` adapter config — **no engine code changed for the domain.**

### 1 · Zero-dependency unit tests — 12 passing
`manifest` (append-only latest-by-id-active), `survey` (scan / attest / thin-detection / honest
status / staleness / manual-channel-not-died), `labels` (leak detection), `taint` (grade
extraction / attach / preserve). All pass with **no third-party dependency**.

### 2 · Decoupling proof — synthetic fixture, zero domain content
The survey tests run against `tests/fixtures/fakeproj` (a tiny fake store + reader_a/b/c, no domain
content). The engine correctly reports `born=[reader_b.py]`, flags the registered leaking reader,
and never claims completeness — proving the core needs nothing domain-specific.

### 3 · Real-data validation — the adapter reproduces the native audit, then converges
| step | result |
|---|---|
| generic engine `scan` on the live KG (via adapter) | `live 26 · registered 6 · born 22 · died 2 · changed 4` |
| cross-check vs domain-native script | **identical numbers** ✅ |
| optional `open_store` adapter (chokepoint) reads the real KG | `concept_nodes = 412` ✅ |
| a real survey (exclude `loader.py` as store-definition + a vendored copy; register 20 channels; flag 2 predicate-blind channels as `manual`) | converged to **`born/died/changed = 0`** ✅ |

The "changed 4" correctly reflected the predicate version bump (v1.1 → v1.2) flagging prior
confirmations for re-check. The 2 predicate-blind channels (a subprocess-indirection writer; an
ASDB reader referencing the store by a non-matched path form) were honestly carried as `manual`
rather than chased by widening the predicate (which would inflate noise) — and a small engine
refinement discovered here (manual channels are excluded from `died`) keeps them from polluting the diff.

### 4 · Label-preservation — leaks surfaced mechanically
`labels` on the surveyed KG: **3 LEAK** (BM25 `build_index`, vector `build_vec_index`, spectral
`encode` — all drop the grade), **1 TRANSFORM** (ASDB flattens everything to one tier),
**5 preserving**, **0 undeclared** (the 7 initially-undeclared readers were each judged — 3
preserving, 1 leak, 2 reclassified as drivers, 1 as a re-export). A label leak is now a thing the
engine *lists*, not a comment.

### 5 · Taint remediation — leak → self-labelled value
The reference primitive `budgood_perimeter.taint` makes a leaking reader's output self-labelled:
```
BEFORE (leak):      ['…']
AFTER (preserving): [Labeled('…', grade={'tier': 'T5', 'confidence': 'low'})]
```
Applying it at a channel flips its manifest `label_preserving` to `true`.

### Reproduce
```bash
PYTHONPATH=. python3 -m unittest discover -s tests        # 12 tests
PYTHONPATH=. python3 -m budgood_perimeter scan   --config examples/buddhist-kg/perimeter.toml
PYTHONPATH=. python3 -m budgood_perimeter labels --config examples/buddhist-kg/perimeter.toml
```
(Point `project_root` in the adapter toml at your own store checkout.)

### Honest caveats
- Two channel classifications (`detect_text` preserving; `encode` leak) were judged from access
  signals and are noted in the manifest as pending a deeper read — a live-act judgement, recorded with its basis.
- The 3 real leaks are *listed*, not fixed; remediation (applying `taint`) edits the domain's own
  reader code and is left to the maintainer.

---

## 中文

### 结论
通用引擎已**解耦**（核心零领域代码）、在 Python 3.8+ 上**零依赖运行**，并在**一个真实、运行中的知识图谱**上**通过验证**：它逐项复现了领域原生审计结果，一次真自勘把它收敛，可选的 label 保全能力列出了真实泄漏并演示了可用的修法。**12/12 单元测试通过。**

### 环境与方法
- Python 3.10（无 `tomllib`、无网络）→ 正好走通内置 TOML 兜底与零依赖路径。
- 引擎以 `python -m budgood_perimeter <命令> --config <toml>` 运行。
- 真实 store：一个运行中的知识图谱（`buddhist-corpus/_indexes/v0_3`），仅由 `examples/buddhist-kg` 适配器配置驱动——**未为该领域改动任何引擎代码。**

### 1 · 零依赖单元测试——12 通过
覆盖 `manifest`（append-only 同 id 最后一条 active）、`survey`（scan / attest / thin 检测 / 诚实 status / staleness / manual 通道不计 died）、`labels`（泄漏检测）、`taint`（等级抽取 / attach / preserve）。全部在**无任何第三方依赖**下通过。

### 2 · 解耦证明——合成 fixture，零领域内容
survey 测试跑在 `tests/fixtures/fakeproj`（一个极小的假 store + reader_a/b/c，零领域内容）。引擎正确报出 `born=[reader_b.py]`、标出那个登记在册的泄漏 reader、且永不声称完备——证明核心不需要任何领域专属物。

### 3 · 真实数据验证——适配器复现原生审计，随后收敛
| 步骤 | 结果 |
|---|---|
| 通用引擎在真实 KG 上 `scan`（经适配器） | `live 26 · registered 6 · born 22 · died 2 · changed 4` |
| 与领域原生脚本交叉核对 | **数字逐项一致** ✅ |
| 可选 `open_store` 适配器（chokepoint）读真实 KG | `concept_nodes = 412` ✅ |
| 一次真自勘（排除 `loader.py`=store 定义 + 一个 vendored 副本；收编 20 通道；2 个谓词盲通道标 `manual`） | 收敛到 **`born/died/changed = 0`** ✅ |

"changed 4" 正确反映了谓词升版（v1.1 → v1.2）把旧确认标为待复核。2 个谓词盲通道（一个经 subprocess 间接写、一个 ASDB reader 以非匹配路径形式引用 store）被诚实地以 `manual` 手动登记，而非靠放宽谓词去追（那会灌进噪声）——本次还发现并加入一个引擎小改进（manual 通道不计入 `died`），免得它们污染 diff。

### 4 · label 保全——泄漏被机械列出
在勘过的 KG 上跑 `labels`：**3 LEAK**（BM25 `build_index`、向量 `build_vec_index`、频谱 `encode`——都丢等级）、**1 TRANSFORM**（ASDB 一律压平成某一档）、**5 preserving**、**0 undeclared**（最初 7 个未声明 reader 已逐个判定——3 preserving、1 leak、2 改判为 driver、1 为 re-export）。一个 label 泄漏，现在是引擎能**列举**的东西，不再是一句注释。

### 5 · taint 修法——泄漏 → 自照值
参考原语 `budgood_perimeter.taint` 让泄漏 reader 的输出自带标签：
```
BEFORE (泄漏):     ['…']
AFTER (保全):      [Labeled('…', grade={'tier': 'T5', 'confidence': 'low'})]
```
在某个通道上应用它，会把其清单里的 `label_preserving` 翻转为 `true`。

### 复现
```bash
PYTHONPATH=. python3 -m unittest discover -s tests        # 12 个测试
PYTHONPATH=. python3 -m budgood_perimeter scan   --config examples/buddhist-kg/perimeter.toml
PYTHONPATH=. python3 -m budgood_perimeter labels --config examples/buddhist-kg/perimeter.toml
```
（把适配器 toml 里的 `project_root` 指向你自己的 store checkout。）

### 诚实标注
- 两条通道分类（`detect_text` 判 preserving；`encode` 判 leak）是据访问信号判定的，清单里已注明"待深读确认"——活的判断，连同其依据一并留痕。
- 3 个真实泄漏目前只是被**列出**、未被修；修法（应用 `taint`）会改到领域自己的 reader 代码，留给维护者定夺。
