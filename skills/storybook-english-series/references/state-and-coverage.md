# 项目存档与覆盖统计

## 建立家庭自己的项目

复制本Skill的 `assets/starter-series/` 到用户指定项目目录。不要将阅读进度写回Skill安装目录。项目最少包含 `vocabulary.csv`、`state.json`；写正文时创建 `episodes/`。模板预排12集，正文尚未采用，图片尚未生成；所有词条均为待核候选。

## vocabulary.csv

必填列：`id,headword,meaning,forms,edition,book,unit,source_status,source`。

- id稳定且唯一，包含不同义项时分开，例如 `v-orange-fruit` 与 `v-orange-colour`。不能因为字母相同就自动两项都覆盖。
- headword与meaning保留所选词表原条目和该义项。forms是明确认可的词形或拼写变体，用 `|` 分隔；不做词干推断。短语保持完整，不拆开后冒充短语已出现。变体是否归并依目标词表，不统一强行合并。
- verified表示已对所选来源逐项核对；provisional表示候选。verified须有确切edition、book、unit和source。来源可为用户确认的目标词表，报告需说明，不冒称官方。原词重复出现于多个单元时保留一稳定ID，在source登记所有位置。
- 暂定词、教学额外词、角色名不自动计入冻结分母。后续核对发现候选词不在该版教材，可继续当故事补充词，单列统计。

## state.json

模板即最小可用实例，字段含义：

- `schema_version: 1`。
- `curriculum`：范围名称、edition_status=pending/confirmed、corpus_frozen布尔值、books_expected八册、books_verified已核对册名、editions_by_book各册版次（可暂为null）。仅写标签不会令数据变为完整官方词表。
- `episodes`按实际故事顺序排列；每集包含id、status、artifact相对路径、new_targets、review_targets。status为planned/text_ready/illustrated。planned可没有正文文件，不能计入已引入；写好后更新同一条记录，不追加重复id。
- `continuity`：上一集结尾、当前位置、物品及归属、已解决事项、未决钩子、下集任务。
- `visual`：人物参考文件、固定外观变更、image_status与实际image_files。图片状态用none/prompts_only/partial/complete；仅在真实图片齐全时记complete，正文同时可标illustrated。
- `review_due`：词条id、建议复现集号、已实际出现的集号，依据新写正文刷新。
- `parent_observations`：仅记录用户实际反馈与日期，如“能指认box，未要求开口”。不要凭生成结果推断掌握。
- `next_episode`：下一集编号。仅改集纲不前进此编号。

每次修改正文后复核并更新存档；返回最终文件路径。跨聊天交接时携带整个项目（尤其已写正文），不只贴一个百分比。

## 每集正文JSON

默认路径 `episodes/S01E01.json`；完整示例在 `assets/example-S01E01.json`，该示例未计入初始项目状态。

```json
{
  "id": "S01E01",
  "title": "会咕噜叫的盒子",
  "sense_confirmed": ["v-door", "v-open", "v-box"],
  "pages": [
    {
      "page": 1,
      "english": ["Look! A box!"],
      "chinese": "米米指向门外的盒子：看，一个盒子！",
      "art_prompt": "角色参考图+画面主体、动作与构图；暂无真实图片"
    }
  ]
}
```

这是结构片段；完整集默认8页。english只放真正印在绘本里的英文，不放说话者标签、词汇清单或统计说明。中文和绘图提示分栏。可以附加speaker等字段，但审核脚本只读english。标题页和给家长的词表页不要混进pages。

`sense_confirmed`是编辑逐项检查后的人工标记，确认匹配到的词在本集确实承担所选义项，不能自动把所有ID填进去。若同形词在一集出现多种义项，字符串工具不能可靠分配；先人工核对，必要时另用可独立复核的集安排对应义项，避免两条同时套用全部出现次数。

## 审核命令与口径

```bash
python3 /absolute/path/to/storybook-english-series/scripts/audit_series.py /absolute/path/to/series-project
```

脚本标准库即可运行，输出JSON。退出0表示记录有效，**不代表词表覆盖完成**；1表示记录矛盾，2表示输入不可读。

统计条件：只读text_ready/illustrated集的english。新目标词在本集至少3次出现且有sense_confirmed才算正文达标；复现词在后续集至少1次有意义出现并有语义标记即可计该集复现。某词在一集出现十次仍只是1集。review_targets必须此前已在真实正文中成功引入，不能拿planned词冒充旧词。

输出区分已核实词条、候选词条、计划集数、正文引入数、跨至少3集出现数、证据不足词和未安排词。只计明确指定的目标与复现词，未登记的偶然支架词不默认为正式覆盖。

完整覆盖标志要求：记录有效、词表冻结、版次确认、八册核对集合一致、有非空核实词条且实际册次齐全、每个核实词条已正式引入且出现在至少3集。脚本不证明原词表完整、来源官方、词义自然、插图存在或孩子学会；这些需对应的人或工具核对。

未冻结时的报告示例：

> 当前为人教PEP三起候选编排，完整词表未冻结。本项目已正式引入X个候选目标词，其中Z个已在至少3集正文中出现；教材全集覆盖率暂不计算。图片：仅提示词。

冻结后：

> 按已确认的[版本/八册]词表，共Y个去重词条，正文已引入X个，其中Z个已跨至少3集复现。此为故事覆盖统计，孩子理解与表达另依家长反馈。
