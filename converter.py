#!/usr/bin/env python3
"""mkdTOpdf — Convert Markdown files to beautiful PDFs."""

import argparse
import re
import sys
from pathlib import Path

import markdown
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

EXTENSIONS = ["extra", "codehilite", "toc", "sane_lists"]
EXTENSION_CONFIGS = {
    "codehilite": {"css_class": "highlight", "linenums": False, "guess_lang": False},
    "toc": {"title": "", "toc_depth": 3},
}

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{title}</title></head>
<body>
{title_block}
<div class="content">{body}</div>
</body>
</html>"""


def convert(
    input_path: Path,
    output_path: Path,
    css_path: Path,
    title: str | None = None,
    no_title: bool = False,
) -> None:
    md_text = input_path.read_text(encoding="utf-8")

    doc_title = title or input_path.stem.replace("-", " ").replace("_", " ").title()
    title_block = (
        f'<div class="title-block"><h1 class="doc-title">{doc_title}</h1></div>'
        if title and not no_title
        else ""
    )

    md = markdown.Markdown(extensions=EXTENSIONS, extension_configs=EXTENSION_CONFIGS)
    body = _wrap_wide_tables(md.convert(md_text))

    html = HTML_TEMPLATE.format(title=doc_title, title_block=title_block, body=body)

    font_config = FontConfiguration()
    css = CSS(
        string=css_path.read_text(encoding="utf-8"),
        font_config=font_config,
        base_url=str(css_path.parent),
    )
    HTML(string=html, base_url=str(input_path.parent) + "/").write_pdf(
        str(output_path), stylesheets=[css], font_config=font_config
    )


def _wrap_wide_tables(html: str, threshold: int = 6) -> str:
    """Wrap tables exceeding *threshold* columns for landscape pages."""
    def wrap(match: re.Match) -> str:
        table = match.group(0)
        first_row = re.search(r"<tr[^>]*>(.*?)</tr>", table, re.DOTALL | re.IGNORECASE)
        if first_row:
            cols = len(re.findall(r"<t[hd][^>]*>", first_row.group(1), re.IGNORECASE))
            if cols > threshold:
                return f'<div class="wide-table-container">{table}</div>'
        return table

    return re.sub(r"<table.*?</table>", wrap, html, flags=re.DOTALL | re.IGNORECASE)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file to a beautifully styled PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  uv run converter.py report.md\n"
               "  uv run converter.py report.md -o out.pdf --title 'My Report'\n"
               "  uv run converter.py report.md --no-title --css custom.css",
    )
    parser.add_argument("input", help="Path to the Markdown file")
    parser.add_argument("-o", "--output", help="Output PDF path (default: <input>.pdf)")
    parser.add_argument("--css", help="CSS stylesheet (default: style.css alongside this script)")
    parser.add_argument("--title", help="Title shown on the cover page (default: filename)")
    parser.add_argument("--no-title", action="store_true", help="Skip the auto-generated cover page")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    if not input_path.exists():
        print(f"error: '{input_path}' not found", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output).resolve() if args.output else input_path.with_suffix(".pdf")
    css_path = Path(args.css).resolve() if args.css else Path(__file__).parent / "style.css"
    if not css_path.exists():
        print(f"error: stylesheet '{css_path}' not found", file=sys.stderr)
        sys.exit(1)

    print(f"  {input_path.name} → {output_path.name}")
    convert(input_path, output_path, css_path, args.title, args.no_title)
    print(f"  saved: {output_path}")


if __name__ == "__main__":
    main()
