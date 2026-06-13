# budgood-perimeter

[English](README.md) · **中文**

> 给"**所有读取你知识库的东西**"建一份可审计的清单,在这份清单变化时收到提醒,别让它悄悄烂掉。零依赖,约 600 行,Apache-2.0。

[![tests](https://img.shields.io/badge/tests-12%20passing-brightgreen)](docs/validation.md) [![python](https://img.shields.io/badge/python-%E2%89%A53.8-blue)]() [![dependencies](https://img.shields.io/badge/dependencies-0-lightgrey)]() [![license](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

---

## 60 秒看懂

你维护着一个**知识库**——可能是一份 JSONL 知识图谱、一个你的 RAG 应用在查的向量索引、一个 agent 的长期记忆、一张代码智能图。是哪种都行。

第一天,有两个脚本读它。半年后——经过几十次提交、几个同事、也许还有一两个 agent——**现在到底有多少东西在读这个知识库?**

你不知道。没人知道。根本没有这么一份清单。而且有三件事正在悄悄出错:

- **新的读取者冒出来,没人注意。** 一个夜间任务、一个新接口、一份 vendored 副本——每一个现在都依赖你的数据,却没人登记。
- **有些读取者悄悄把元数据丢了。** 你的记录是带"等级"的——`confidence: low`、`status: candidate`、`tier: T5`(未核实的猜测)。忠实的读取者会把它带下去;马虎的读取者只返回正文,于是下游代码把一个**猜测当成了既定事实**。
- **看板用"沉默"撒谎。** "覆盖率 95%"一直绿着,因为根本没人在核对"谁在碰什么"这张地图还对不对。它在沉默中腐烂。

**budgood-perimeter** 是一个小工具,专治这个"**不知道**"。它给每一个读取你 store 的**通道**(脚本/服务/导出)维护一份可审计、append-only 的清单,并:

| 命令 | 告诉你什么 |
|---|---|
| `scan` | 自上次核对以来,哪些读取者是**新增**、**消失**、或**变了** |
| `labels` | 哪些读取者**把元数据丢了**(泄漏) vs 把它带下去了 |
| `staleness` | 太久没人重新核对时,提醒你一次(只一次) |
| `status` | 一个诚实看板:只报**新鲜度**,永远拒绝说"已完备" |
| `attest` | 给每次核对留痕,于是"上一次真正去看是什么时候、看到了什么"有了答案 |

**它从不读你的数据。** 它只盯着那些"**门**"——引用了 store 的文件。把它想成:每个知识库都有一个盲区,就是你忘了它存在的那些门,而这是那个盲区的烟雾探测器。

## 2 分钟走一遍

假设你的知识库是 `kb.jsonl`,读取者都调一个 `open_kb()`。

**1. 告诉它去哪看**(`perimeter.toml`):

```toml
project_root = "."
[paths]
manifest = "channels.jsonl"
attestations = "attestations.jsonl"
```

**2. 种下清单**(`channels.jsonl`)——store、怎么**认出**一个读取者(即"谓词 predicate")、以及你已经知道的通道:

```jsonl
{"id":"STORE","type":"store","status":"active","canonical_files":["kb.jsonl"]}
{"id":"PRED-1","type":"predicate","status":"active","version":"v1","include_globs":["**/*.py"],"access_pattern":"open_kb|kb\\.jsonl"}
{"id":"CH-1","type":"channel","status":"active","path":"api/search.py","role":"reader","label_preserving":true,"found_under_predicate":"v1"}
```

**3. 扫一下——它抓出了一个没人登记的读取者:**

```text
$ budgood-perimeter scan --config perimeter.toml
=== perimeter survey · mechanical (predicate v1) ===
live 2 · registered 1
[born  unregistered] 1
  + jobs/nightly_export.py      <- 一个没人在追的、新读你 KB 的脚本
[died  registered-but-gone] 0
[changed] 0
--- judgement segment (not automatable; the live act) ---
Part I  复检谓词 ...   Part II  逐条判 unowned 边界 ...
```

**4. 你打开 `nightly_export.py`,判定它是个真读取者、而且丢了等级,登记它、并给这次核对留痕**(这是人来做的那一步——工具从不替你决定):

```text
$ budgood-perimeter attest --config perimeter.toml --by alice \
    --predicate-review "nightly_export 是真通道;它返回裸记录 -> 登记为泄漏"
```

**5. 现在 `labels` 列出了你刚发现的那个泄漏:**

```text
$ budgood-perimeter labels --config perimeter.toml
[LEAK  drops the grade] 1
  jobs/nightly_export.py  (reader) -> False
```

整个闭环就是这样:*工具发现变化、列出泄漏;你来拍板;记录替你记住。*

## 这是给谁的

- 你维护着一个**知识图谱 / RAG 索引 / agent 记忆 / 代码图**,有不止一个东西在读它,而读取者的清单早已超出你脑子能记的范围。
- 你在意:别让 **低置信 / candidate / 未核实** 的记录在经过读取者时被洗成"事实"。
- 你想要一条**审计线索**:"谁在读我们的数据,以及我们上一次核对这份清单是什么时候。"

**不适合你,如果:** 你要的是 eval 框架、检索器、路由器、或 agent 循环。budgood-perimeter 只治理一件事——*那组读取者*——并刻意止步于此。

## 它**故意不做**的事

- 它**从不改动**你的代码或数据——只列举、只留痕,不替你修。
- 它**从不自动登记**一个新读取者、也不自动判定泄漏——这些由你作为判断来做。
- 它**从不强制**你按表勘察。它可以**提醒**(staleness),但"给判断设 deadline"恰恰是它拒绝施加的(原因见"背后的思路")。

---

## 安装

零依赖;**Python ≥ 3.8**。(TOML 解析在 3.11+ 用标准库 `tomllib`,有 `tomli` 则用之,否则走内置兜底——所以它在任何环境直接跑,无需安装任何东西。)

```bash
git clone https://github.com/budgood/budgood-perimeter && cd budgood-perimeter
pip install -e .            # 装好 `budgood-perimeter` 命令
# (PyPI 发布待定:pip install budgood-perimeter)
```

不装也能试:`python -m budgood_perimeter scan --config perimeter.toml`。

## 命令速查

```bash
budgood-perimeter scan      --config perimeter.toml   # 相对清单:新增/消失/漂移的读取者
budgood-perimeter status    --config perimeter.toml   # 诚实看板(新鲜度,永不 "complete")
budgood-perimeter staleness --config perimeter.toml   # 仅当勘察过期时输出一行
budgood-perimeter labels    --config perimeter.toml   # 哪些读取者剥掉了 store 的元数据
budgood-perimeter attest    --config perimeter.toml --predicate-review "..." --by 你
```

## 一次勘察怎么跑(模型)

三段,刻意如此:

1. **机械段(免费、自动)。** 引擎按**谓词**(一条版本化规则,如"import 了 `open_kb` 或提到 `kb.jsonl`")扫你的文件树,把这个活集合与你登记的清单做差 → **born / died / changed**。
2. **慧段(你来,不可自动化)。** 你看变化、做判断:这是个真通道吗?谓词需要捕捉新形态吗?它丢等级吗?工具把问题摆给你([`docs/checklist.md`](docs/checklist.md)),但从不替你回答。
3. **留痕(attestation)。** 你这次勘察被追加成一条不可变记录。一次什么都没找到、也没判任何东西的勘察,会被自动标 `thin`——一次便宜得可疑的"看一眼"。

一切都是 **append-only**:你从不改记录,而是追加一条同 id 新版本;当前生效视图 = "同 id 最后一条且 status==active",随时可重生。**谓词本身就是一条版本化记录**,现实超出它时你就升版。**看板永不声称完备**——只报上次勘察有多新鲜。

## 写一个适配器(用到你自己的 store 上)

一个适配器无非是:一份 `perimeter.toml`(项目根 + 文件路径)+ 一份种了一条 `store` 记录和一条 active `predicate` 的 `channels.jsonl`。就这些——引擎核心里**没有一行领域代码**。一个完整、真实、高风险的适配器(一张学术知识图谱)在 [`examples/buddhist-kg/`](examples/buddhist-kg/),它被用来在真实数据上验证引擎。

## 真实数据验证过

通用引擎经示例适配器在一个**运行中的知识图谱**上跑,**逐个数字复现**了那个项目手写的审计结果,随后一次真自勘把它收敛到 `born/died/changed = 0`,`labels` 列出了 **3 个真实元数据泄漏**。12 个单元测试零依赖通过。完整简报:[`docs/validation.md`](docs/validation.md)。

---

## 背后的思路(可选阅读)

budgood-perimeter 是作者称为 **缘起工程 / Condition Engineering** 的一套小设计学派里的第一个工具。一个念头贯穿全部:

> **永远不让"基底"成为一个决策的亲因。** 数据、表、代码、乃至这个工具本身,都可以**辅助**一个判断;但它们不可以**做**这个判断。判断永远留在"此刻正在看的那个人(或 agent)的现行"里。

由此落出三条不变量,而工具对自己也强制执行:

1. **append-only + provenance(来源谱系)**——"谁读什么"这份记录不可变、可重生,于是它无法漂移成"自信却错"的状态。(这也是它为何能抵御知识层版本的*模型坍缩*:真实、有据的事实始终锚住,不被自生的漂移淹没。)
2. **照明,而非控制**——引擎让问题**可见**,但从不替你处理。一个工具一旦开始自动修它发现的东西,它的规则表就变成会腐烂的东西。
3. **增上缘,非亲因**——引擎从不强制自己重勘。一个能强迫你重核它自己边界的系统,就是在自定义自身的 scope——然后它就能悄悄认定"我完备了"。所以顶点那一下始终不被强制;工具只保证:你永远无法**悄悄相信**自己的清单是对的。

给从 agent 工具来的人一个更大的说法:**闭环只是一个旋钮的某一档,而非目标。** agent 的"循环工程"问的是"怎么把循环闭合、让它收敛?";这套工具问的是"**判断被允许活在哪里,以及我怎么让每一处我停止观察的地方都无法被遗忘?**"只有当你有一个又硬又便宜的 oracle、且动作可逆时,闭环才是对的那一档;其余一切,你治理边界、把判断留活。完整论述见 [`docs/framework.md`](docs/framework.md)。

## 术语

| 术语 | 大白话 |
|---|---|
| store | 你的知识库;引擎从不打开它 |
| channel | 读取 store 的一个文件/服务 |
| predicate | "什么算一个读取者"的版本化规则 |
| born / died / changed | 自上次勘察以来 新增的 / 消失的 / 漂移的读取者 |
| owned / unowned | 你能 instrument 的边界 vs 不能的(人、外部工具、LLM 的上下文) |
| attestation | 一条不可变记录:某次勘察发生过——diff、你的复检、日期 |
| thin | 一次什么都没做的 attestation——本身被标记照亮 |
| label-preserving | 一个读取者有没有把 store 的元数据(等级)带过它的边界 |
| leak（泄漏) | 一个读取者返回 store 内容时把等级剥掉了 |

## 联系作者

有问题、想法,或想交流知识库治理的经验?欢迎加我(**释则生**)微信:

<img src="docs/assets/wechat-shizesheng.png" alt="微信:释则生" width="240">

## License

[Apache-2.0](LICENSE)。
