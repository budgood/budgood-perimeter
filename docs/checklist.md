# perimeter 自勘 · 慧段 checklist
### 边界谓词复检 + unowned 边界逐条判

> **这份清单是整套框架里那个不可外包的顶点现行的成文身体。**
> manifest（A）、store 网关（B）、陈旧触发（D）、诚实看板（E）都只为一件事存在：让**这一段**被跑、跑得便宜、跑完留痕。
> 但下面是一个**判断者问的问题，不是一台机器套的规则**。把它写下来不是为了自动执行，是为了让那次判断**可读、可复、便宜**——让顶点现行成为一次有纪律的二十分钟动作，而不是每次从零开始的研究。**legible ≠ automated。**

**前置（机械段已完成）。** 进入慧段前，你面前应当已经有：
- (a) 活通道集 vs manifest 的 diff：`born / died / changed`；
- (b) 当前 `channels` manifest，每条含 `found_under_predicate` 版本、`ownership`、`last_confirmed`。

慧段只在机械段之上烧判断。机械段免费，慧段才是你真正在场的理由。

---

## Part I — 谓词复检：用证伪的姿态，不是重跑的姿态

**核心纪律：** 你不是再 run 一遍谓词、看它返回什么；你是**主动去猎那条它会漏掉的访问形状**。谓词复检唯一有效的方式是试图**证伪**它。逐条问：

1. **新表面 / 新路径。** store 现在到底由哪些文件构成？把"现在算 store 的东西"重新列一遍，对照谓词匹配的路径集。有没有新出现的 index / jsonl / 派生视图，是谓词路径清单里没有的？——读它的通道，对谓词隐形。

2. **新访问形状 / 间接。** 有没有新代码把 store 内容**再服务**出去、自己却不匹配谓词？wrapper / helper 再导出、缓存层、子进程读、读一个其实 symlink 到活库的"副本"。谓词扫直接访问，间接一层就穿透它。

3. **新语言 / 新运行时。** 谓词扫 `.py`。现在有没有 `.js`、notebook、shell、编译产物、MCP server、LLM 工具在读 store？跨运行时盲区——这是最容易被一句"我们主要是 Python"放过去的一条。

4. **"store"的指称漂移了吗（最隐蔽的一条）。** store 有没有长出新表示——embedding 索引、向量库、缓存、某个 export——而下游开始把这个**派生物**当 source-of-truth 来读？一旦派生物事实上变成 store，"通道"就必须包含读派生物的人，而谓词（锚在 canonical 路径上）看不见他们。问：有没有"读缓存 / 读 export 而不读 canonical"的既成事实？

5. **ownership 越界。** 有没有原本 sealed 的 fork（unowned、读自己副本）悄悄回指了活库？——那个逐字节相同的 standalone：**只有判断把它挡在地图外**；它一旦回指就跨了 owned/unowned 线。逐个 unowned 项复核它的隔离假设是否还成立。

6. **谓词的假阳也在漂。** 对称地：谓词有没有开始把**死东西**当活的匹配进来——跑完的一次性迁移脚本、backup、`_tmp/`？过度纳入的噪音稀释注意力（就是上次手工去掉的那 ~80%）。问：谓词匹配到的里面，哪些其实冻着 / 死了、该排除——而这个排除**本身有没有被记下来**，免得下次自勘重新打同一场官司？

**Part I 产出：** 谓词裁决——**仍有效（不升版）** 或 **必须升到 vN+1**（attestation 记录什么变了、为什么）。

---

## Part II — unowned 边界逐条判：管理那个跨不过去的东西

对每一个 `ownership = unowned` 的边界（你 instrument 不了的：人脑、外部工具、LLM 上下文、你不控的 export），标签必然在它那里丢。所以逐条问的**不是"怎么跨过它"，是"怎么管理这个跨不过的东西"**：

1. **它还 unowned 吗，还是变得可拥有了？** 有时你获得了控制（外部工具出了插件 API；export 现在走你的网关）。复核：这个边界现在 instrument 得了吗？能，就 reclassify 成 owned，上 taint / 签名。**unowned 集应当被机会主义地缩小**，而不是默认永远 unowned。

2. **抵达它的东西自带灯吗？** 对一个你真跨不过的边界，唯一的防御是：让值在它之前**最后一个 owned 边界**上自带标签抵达。问：流进这个 unowned 边界的东西，在交接那一刻带着它的 `tier / candidate` 标签吗？人读 render，render 显 tier 吗？LLM 吞一个 coverage 统计，那统计带着"我汇总了 candidate 级节点"吗？——**你审的是最后那次 owned 交接，不是 unowned 边界本身。**

3. **标签在这里掉了，blast radius 多大？** 分诊。一个交接 `T0 / codified` 金料的 unowned 边界——掉了标签也没损失多少（它本就是金）。一个把 `candidate / low-confidence` 当定论交出去的——高危。按"跨过去的东西的认识论等级"给 unowned 边界排序。**危险的恰恰是：低保证内容跨进一个不可 instrument 的消费者。**

4. **有没有东西已经建在跨过去的东西上了？（exposure 维）** 不可逆性在**首个下游依赖**处结晶。对每个 unowned 边界问：有没有证据表明下游已经对跨过去的东西做了承诺（引用了、回写了、据此决策了）？有，则在这里跨过去的那个名义可逆 candidate **现在事实上不可逆**——flag 它进 promote-或-撤回 复审（回到 candidate-债 那套机器）。

5. **这个 unowned 边界本身被记下来了吗？** 把它 append 进 manifest 作 `unowned`，连同"什么跨过它"和 `last_judged` 日期——免得每次自勘从零重新发现它，也使一个**新的、你原先不知道存在的** unowned 边界，能作为对已记录集的 diff 浮现。（递归又来了：unowned 集本身是一道 perimeter，同样待遇。）

**Part II 产出：** 更新的 unowned 名册、reclassification（unowned→owned）、一张按危险度排序的"低保证内容跨进不可 instrument 消费者"清单、以及 exposure 触发的 promote / 撤回 flag。

---

## 完整性守卫（反橡皮图章）

一次**既没在谓词上找到缺口、也没 reclassify 任何东西、也没判过任何 unowned 边界**的 attestation，便宜得可疑——它自己被标 `thin` 并重新照亮。

因为活系统里几乎总有东西变了；一次"看一眼没事"的自勘，要么真没东西可勘（罕见），要么**没真看**。收尾自检：本次自勘至少做了一次对谓词的证伪尝试 + 至少一次 unowned 判断吗？没有 → `thin: true`。

---

## 反身尾：这道 checklist 自己还完整吗

最后一问，和"谓词复检自己""perimeter 自勘自己"同构：

> 自上次以来，我们撞上过哪种谓词 / 边界失效，是这张 checklist 上**没有任何一问**能逮住的？

有，就给 checklist 加一问、升它自己的版本。**这张清单也是一道高一层的 perimeter**——它同样会漏、同样会陈旧，所以它同样要在每次被使用时复检自己。退缩在这一层也被折进它自己的行为里，**不另起一座塔**。

---

## 写进 attestation 的字段（接落账段）

```
predicate_version_after      # 仍有效则不变，否则 vN+1
predicate_review             # 找到的缺口；或"已做证伪尝试、无缺口"
channel_diff                 # born / died / changed
reclassifications            # unowned → owned（及反向）
unowned_roster_after         # 更新后的 unowned 名册
hazard_ranked_crossings      # 低保证内容跨进不可 instrument 消费者，按危险度排
exposure_flags               # 已被下游依赖、需 promote/撤回复审的项
checklist_version_after      # 反身尾若加问则升版
thin                         # bool，完整性守卫判定
date / by                    # 日期 / 履行此次自勘的现行 id
```

---

## 这不是什么（诚实 coda）

- **不是自动化。** 这是判断者问的问题，不是机器套的规则。写下来让它可读、可复、便宜——不让它自执行。
- **不是 deadline。** staleness 触发只照亮"过期了"；它不规定你何时**必须**自勘。定 deadline = 对判断立法 = 宪法所禁的原罪。
- **不保证 perimeter 正确（不可达）。** 它保证的只有一件事：**系统无法再悄悄相信自己 perimeter 正确**——把"忘了存在的门"这个 unknown-unknown，转成"距上次清点 N 久、且清点的定义本身带版本号"这个 known / dated / aging 的债。

这就是顶点处能拿到的全部：你废不掉那个顶点现行，但你能让它的**荒废变吵、履行变廉、自我定义可审计**。
