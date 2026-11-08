import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import tg_markdown as t


class T(unittest.TestCase):
    def test_inline(self):
        self.assertEqual(t.to_html("**加粗** 和 `a<b>` [链接](https://x.com/a?b=1&c=2)"),
                         '<b>加粗</b> 和 <code>a&lt;b&gt;</code> <a href="https://x.com/a?b=1&amp;c=2">链接</a>')

    def test_escape_and_unbalanced(self):
        self.assertEqual(t.to_html("1 < 2 & 3 > 2 **未闭合"), "1 &lt; 2 &amp; 3 &gt; 2 **未闭合")
        self.assertEqual(t.to_html("snake_case_name 和 a*b*c"), "snake_case_name 和 a*b*c")

    def test_blocks(self):
        h = t.to_html("# 标题\n- 一\n  - 二\n> 引用\n---\n|代码|名称|\n|---|---|\n|600498|烽火通信|")
        self.assertIn("<b>标题</b>", h); self.assertIn("• 一", h); self.assertIn("  • 二", h)
        self.assertIn("<blockquote>引用</blockquote>", h); self.assertIn("────────", h)
        self.assertIn("• <b>600498</b>：烽火通信", h)

    def test_javascript_link_not_linked(self):
        self.assertNotIn("<a ", t.to_html("[x](javascript:alert(1))"))

    def test_table_cards(self):
        h = t.to_html("| 代码 | 名称 | 涨跌 |\n|---|---|---|\n| **600498** | 烽火通信 | +3.2% |\n| 0700 | 腾讯 | |")
        self.assertEqual(h, "▪️ <b>600498</b>\n    名称：烽火通信\n    涨跌：+3.2%\n\n▪️ <b>0700</b>\n    名称：腾讯")
        self.assertEqual(t.to_html("| k | v |\n|---|---|\n| a | **b** |"), "• <b>a</b>：<b>b</b>")

    def test_plain(self):
        self.assertEqual(t.to_plain("# 标题\n**粗** `c` [l](https://a.b)\n- x"), "标题\n粗 c l https://a.b\n• x")

    def test_split(self):
        md = "\n".join(f"**第{i}行** " + "字" * 50 for i in range(300))
        parts = t.split_html_safe(md, 3800)
        self.assertGreater(len(parts), 1)
        self.assertTrue(all(len(t.to_html(p)) <= 3800 for p in parts))
        self.assertEqual("\n".join(parts), md)


if __name__ == "__main__":
    unittest.main()
