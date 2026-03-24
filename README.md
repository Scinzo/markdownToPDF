# markdownToPDF

Convert Markdown to beautifully styled PDFs with [WeasyPrint](https://weasyprint.org/).

## Setup

```bash
brew install pango   # macOS (required by WeasyPrint)
uv sync
```

## Usage

```bash
uv run converter.py sample.md                        # outputs sample.pdf
uv run converter.py sample.md -o out.pdf              # custom output path
uv run converter.py sample.md --title "My Document"   # cover page with title
uv run converter.py sample.md --no-title               # skip cover page
uv run converter.py sample.md --css custom.css         # custom stylesheet
```

## Features

- Full Markdown Extra support (tables, fenced code, footnotes, definition lists, `[TOC]`, etc.)
- Syntax highlighting via Pygments
- Wide tables (>6 columns) auto-render on landscape pages
- Local fonts — works offline
