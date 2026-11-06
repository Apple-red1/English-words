# 写作、分镜与插画

开工前按SKILL入口读取同目录可选的 `local-preferences.json`，沿用其私有 `output_root` 与 `series_project`；用户本轮明确路径优先。该文件与实际家庭目录不得进入公开GitHub或可分享Skill包。

## 正文结构

第一轮默认8页正文，不计封面与给家长的词汇页。每页写一段能连续朗读的故事：中文承担起因、动作和笑点，在角色真正需要请求、回应和协商时，自然嵌入1—2句完整英语对白。约40—80个英文词是初始创作参考，不必为凑字数扩写。

| 页 | 作用 | 画面与对白 |
|---|---|---|
| 1 | 熟悉场景里出现小惊喜 | 从具体动作开始，不用设定说明开场 |
| 2 | 主角想做一件事 | 一句可模仿的请求或选择 |
| 3 | 好笑的第一次尝试 | 表情与动作给笑点，不嘲笑角色 |
| 4 | 伙伴回应，改变办法 | 回扣目标词，英语有对话对象 |
| 5 | 孩子可预测的重复与变化 | 可停一下让孩子指认、接一个词 |
| 6 | 合作把麻烦解决 | 关键动作可见，词汇参与结果 |
| 7 | 温暖或好笑的回报 | 对方真实回应，避免老师总结知识 |
| 8 | 本集收好，出现小钩子 | 可是新邀请、新声音、新道具；轻松而安全 |

允许为情节调整页序。不要每页都塞进全部目标词；每词3—5次的出现分散在需要它的地方。检查“the door?”这种重复是否有真实指向或确认意图；没有就重写。

采用单一的自然混合语流，例如：

> 团团抱着空盘子，朝米米眨眨眼：“Open the door, please.”他猜，盒子里一定有块会打嗝的大饼干！

英语就是角色当时说的话；后面继续推进动作和情节，不再接“请把门打开”重译一遍。禁止独立英语块加逐句中文翻译，也不提供中英文各一套正文。英语保持完整自然的话语，不把box、door等单词硬塞进中文句子。画面和动作帮助理解，不靠翻译打断朗读。人物名不算目标词，拟声词不自动计入教材词汇；不使用汉字谐音标注英语发音，用户需要时用可核对音标或可用朗读工具。

## 每集交付模板

1. 集号、标题、接前集一句话；3个目标词及本集词义、最多2个句框。
2. 8页表格：页码 / 画面 / 连续朗读正文。最后一栏是中文叙事中嵌入完整英语人物对白，朗读时只读这一栏，不把英语与中文另列成两份。正文不插入教学统计。
3. 一个不考查的亲子游戏，例如把玩具藏在盒子里，一人请求、一人打开；孩子可以只做动作。
4. 下集预告一句，不提前宣告词汇表。
5. 给家长：新目标词、复现词、支架语、尚未解决的线索、可选阅读反馈；写入状态前逐项核对。
6. 请求出图时按下节核验固定母版，传入真实参考图并完成全页A4插画内的中英排版，交付PDF与每页自带字PNG；只请求故事时不自动批量出图。

保存每页时用 `read_aloud` 记录这份最终连续正文。若保留 `english` 数组作目标词审计，必须与 `read_aloud` 内的英语对白一致；旧式 `chinese` 字段只作历史来源，不能再渲染为重复的中文译文。排版和交付始终使用唯一的 `read_aloud`，不要把内部审计字段直接拼成“英语块＋翻译块”。

## 人物与画风连续

先读取 series-bible 中的角色锚点、家庭 `state.json` 中已锁定的 `character_master` 和前集成图。**已有获认可的v1人物母版，不再重新生成“第一张设定图”。** 每次出图前运行本Skill的 `scripts/ensure_character_master.py`，已有项目用 `--expected-version` 与 `--expected-sha256` 传入锁定值。脚本成功返回实际文件路径后查看图片；每次调用图像工具都显式传入这张母版文件，前集成图可作为额外参考。若工具不能接收实际参考图，明确说明限制，不把纯文字提示当作角色一致性保障。

清单 `assets/characters/manifest.json` 记录版本、SHA256、仓库文件位置与官方 `raw_url`。脚本先核对捆绑文件，再核对缓存；缺失或损坏时只能下载同一已登记版本并校验，不能临时重绘替代。网络或校验失败时停止出图并报告原因。支持 `--cache-dir` 覆盖缓存根目录；不在Skill中写当前用户的绝对路径。记录本次实际使用的版本、SHA256和路径到家庭状态及本集出图元数据，跨聊天沿用该锁定信息。

若用户明确要求人物改版，建立v2图片及清单，旧图和旧清单归档保留；已有故事继续使用原版本，除非用户明确要求迁移。`--manifest` 可选择保留的旧版清单，预期版本/哈希不一致时不能跳过检查。改装、换衣、帽子、临时道具登记起止集号，临时造型不覆盖固定母版。

基础提示词（按当前画面补全，不作为已生成图片）：

> Original cute children's picture-book illustration, rounded shapes, soft gouache with subtle crayon outlines, warm cream paper texture, gentle bright colours, expressive faces, uncluttered setting, one clear action. Tuan: a cream-brown round-eared bear in butter-yellow overalls, a leaf pocket on the left chest. Mimi: a white lop-eared rabbit with a pale grey left ear tip, a short mint scarf and a small orange crossbody bag. Gulu: a cornflower-blue bread-shaped little mail van, cream roof, two warm-yellow round headlights and a white leaf emblem on the door. Keep proportions and clothing consistent with the supplied reference image. [Scene, action, target objects, camera angle, composition.] A4 portrait composition, 210:297 aspect ratio, one continuous illustration covering the entire page. Reserve a natural light-coloured area within the scene for one continuous story paragraph combining Chinese narration with embedded English character dialogue; optional speech bubbles must follow the same reading flow. Do not create separate Chinese and English panels. Keep text areas, faces and target objects inside a 12–15 mm print-safe zone. No separate white caption strip or top-image/bottom-text layout. No baked-in text or watermark.

默认完整成品采用 **A4竖版（210 × 297 mm）的全页插画PDF，以及按页导出的自带字PNG**；用户明确指定其他尺寸时从其选择。整页从上到下、从左到右都是同一场景的插画背景，连续朗读正文直接融入画内统一的叙事文字块，或在同一阅读顺序中融入人物气泡；可利用浅色墙面、天空或地面留白，不把中文与英语分成两套。禁止默认采用“上图下文”的底部白色文字栏，也不把方形插图贴在A4上再用一块文字区补足空白。让目标物体清楚可指认，不为漂亮而缩到背景；不把无字插图当最终成品，不要求家长添加文本。

先按A4竖版比例设计人物、动作和画内文字的空间。若原图是方形或比例不合，不能沿单一方向强拉伸；用图像生成工具在固定母版参考下扩展或重构场景到A4比例，只有不影响人物、目标物与文字留白的边缘才可少量等比裁切。不要以大片白底或装饰画框代替需要补画的背景。

插画生成时可以无字，再用文档或图像排版工具，把唯一的 `read_aloud` 连续正文放进预留的画内区域；英语对白可适度强调，但不能另起一套翻译版面，也不能重复中文译文。文字层叠加不等于另开页外文字栏。用可用中文字体，PDF嵌入字体，PNG呈现同一份带字排版。正文建议英语至少22 pt、中文至少16 pt，以连续顺读为先；文本过多时精简叙事或重构画面，不硬塞长段落。背景铺满A4画布，文字、页码、人物脸部和核心目标物距纸边保留12—15 mm打印安全区。

导出后逐页渲染检查：A4整页插画背景连续、角色没有因拉伸变形、正文能按中文叙事与嵌入的英语对白顺读、没有重复汉译或独立中英文两套区域、英文准确、中文无缺字、中英文字均在画内且不遮挡动作、没有底部白色文字栏、打印安全区足够、PDF与PNG内容和页序一致。检查通过后交付可直接打印的PDF和每页自带字PNG，原始无字插画只作为可选附属资产。仅交付分镜或提示词时明确尚未完成图像与成品排版。

先检查一两页实际效果再继续整集，减少角色漂移；每次调用仍传入同一母版。检查耳朵、口袋、围巾、邮车颜色、角色比例、道具位置，以及画面能否支持对白中的数量、动作和词义。发现偏离时用同一母版修改当页，不另造新母版。

## 反馈如何影响下一集

- “太难 / 听不完”：先减英语长度，增加熟悉场景，允许0—2个新词；不因原定3词而强推。
- “喜欢同一页反复读”：保留那种笑点与句框，下一集变化情境，避免原封不动重写。
- “愿意主动说”：增加角色轮换与选择，不立刻把词数翻倍。
- 用户没提供反馈：保持当前密度；只把已写文本记为引入，不替孩子登记掌握程度。
