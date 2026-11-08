# tg-markdown

把 Markdown 安全地转成 Telegram 消息格式（`parse_mode="HTML"`）。单文件、零依赖、Python 3.8+。

Convert Markdown to Telegram-safe HTML. Single file, zero dependencies.

## 为什么需要它

用 Telegram 机器人推送报告时，正文往往是 Markdown（尤其是大模型写的）。直接发出去，用户看到的是 `**`、`#`、`|` 原文；
改用 Telegram 自带的 `MarkdownV2`，又要求把 `_ * [ ] ( ) . !` 等十几种符号全部转义，漏一个整条消息就会被拒（HTTP 400）。

这个小工具改走 HTML 模式（只需要转义 `& < >`），把常见 Markdown 转成 Telegram 支持的标签：

| Markdown | 显示效果 |
|---|---|
| `**粗体**` `__粗体__` | 粗体 |
| `` `代码` `` / ```` ``` 代码块 ``` ```` | 等宽 |
| `[文字](https://...)` | 可点链接（只放行 http/https） |
| `# 标题` | 粗体标题 |
| `- 列表` | • 列表（保留缩进） |
| `> 引用` | 引用块 |
| 表格 | 卡片式列表：两列 →「• 左：右」；三列以上 → 首列作标题、其余「列名：内容」逐行列出 |

另外两个函数：

- `to_plain(md)`：去掉 Markdown 符号的纯文本，用作 HTML 仍被拒时的兜底。
- `split_html_safe(md, limit=3800)`：按行切分长消息，保证每块转换后不超过上限，且不会把标签、表格、代码块从中间切断。

> **v1.1**：表格从等宽对齐改为卡片式。Telegram 手机端的等宽字体不含中文，中文会回落到系统字体，宽度约为英文的 1.6–1.8 倍且各端不同，按字宽补空格的方案在手机上必然错位。

## 用法

```python
import tg_markdown

html = tg_markdown.to_html(markdown_text)
# sendMessage(chat_id=..., text=html, parse_mode="HTML")
```

完整的发送示例（含分块和纯文本兜底）见 [`example_send.py`](example_send.py)。

## 测试

```bash
python3 -m unittest discover -s tests
```

## 许可

MIT
