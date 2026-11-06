# 芽芽镇的咕噜邮车

为约4岁孩子设计的连续英语情景对话绘本：原创可爱角色、好笑的小麻烦、生活中的自然对话，以及能接着读下去的新发现。

本仓库的可复用 Skill 位于 [`skills/storybook-english-series`](skills/storybook-english-series/SKILL.md)。默认每集8页、3个新目标词，第6和12集安排复习；逐步整理人教版小学英语词汇，具体书系、版次和完整词表仍需核实。文本出现过不等于孩子已掌握。

## 安装与使用

将 `skills/storybook-english-series` 整个文件夹（包括 assets、references 和 scripts）复制到 Codex 的个人 Skills 目录，通常是 `~/.codex/skills/`，或你配置的 `$CODEX_HOME/skills/`。保留原文件夹名。

在 Codex 中输入：

> 使用 $storybook-english-series，为4岁孩子写《芽芽镇的咕噜邮车》第一集，制作可以直接打印的绘本。

续写时提供家庭项目的存档和上一集。家庭阅读状态、孩子反馈与每集成品保存在自己的项目里，不提交到公共 Skill。

## 固定人物母版

团团、米米和咕噜邮车复用同一张获认可的 [v1人物母版](skills/storybook-english-series/assets/characters/characters-v1.png)。[清单](skills/storybook-english-series/assets/characters/manifest.json) 记录版本、SHA256和固定来源；出图前运行 `scripts/ensure_character_master.py`，核验实际图片并将其作为每次图像生成的参考。缺失时恢复相同版本，校验失败则停止出图，不自动重画或更换母版。只有明确要求改版时才建立新版本并保留旧版。

## 可以直接打印的成品

默认交付 A4 PDF 与每页带字 PNG。每页同时排好英语对话和中文陪读，留出打印安全边距，不需要家长另外配字。仅请求规划、故事或分镜时，不自动生成整套图片。

Skill 中附有系列设定、第一季规划、第一集写作样例、家庭存档模板，以及词汇和母版核验脚本。
