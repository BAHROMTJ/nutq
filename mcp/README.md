# nutq-mcp

An [MCP](https://modelcontextprotocol.io) server that gives AI assistants (Claude, and any other MCP client) reliable tools for **Tajik, Persian, Dari and Uzbek** text, built on [nutq](https://github.com/BAHROMTJ/nutq).

Language models often misspell Tajik in Perso-Arabic script, mix up Uzbek oʻ/gʻ, or get number words wrong. With this server, the assistant calls tested code instead of guessing.

## Tools

| Tool | What it does | Example |
|---|---|---|
| `convert_script` | Changes the writing system | `Забони тоҷикӣ` → `زبان تاجیکی`; `O'zbekiston` → `Ўзбекистон` |
| `normalize_text` | Spells out numbers, dates, times, money, %, phone numbers, units and abbreviations for TTS | `Нархи 25 $ аст` → `Нархи бисту панҷ доллар аст` |
| `number_to_words` | Writes a single number in words (cardinal or ordinal, any script) | `4, uz, ordinal, Cyrl` → `тўртинчи` |
| `clean_text` | Fixes characters only (look-alike letters, ي/ك, apostrophes, ZWNJ) | `o'zbek` → `oʻzbek` |
| `list_languages` | Lists languages, scripts and status | `tg`, `fa`, `fa-AF`, `uz` |

All tools are read-only and work offline.

## Install

Requires Python 3.10+. With [uv](https://docs.astral.sh/uv/), there is nothing to install by hand.

**Claude Code**

```bash
claude mcp add nutq -- uvx nutq-mcp
```

**Claude Desktop** — add this to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nutq": {
      "command": "uvx",
      "args": ["nutq-mcp"]
    }
  }
}
```

Without uv: `pip install nutq-mcp`, then use `"command": "nutq-mcp"`.

Then ask, for example: *"Write «Забони тоҷикӣ ширинтар аз шакар» in Persian script"* or *"Prepare this Uzbek text for speech synthesis: 2026-yil 12-mart, 15% chegirma"*.

## Development

```bash
pip install -e ../ -e .
python -m unittest discover -s tests
```

The tests start the server in-process through a real MCP client, and also as a subprocess over stdio.

MIT license.
