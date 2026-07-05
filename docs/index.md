# Dimjournal

**Dimjournal** is a Python tool that creates and maintains a local backup of your Midjourney image generations.

## What it does

- Downloads your Midjourney job history (metadata: prompts, IDs, timestamps)
- Downloads upscaled images and organises them into `Year/Month/` folders
- Embeds prompt, author, and creation-time metadata directly into PNG files
- Resumes interrupted downloads — only fetches new or missing items
- Persists login session cookies to avoid repeated manual logins

## Quick start

```bash
pip install dimjournal
dimjournal
```

The first run opens a Chrome window. Log in to Midjourney manually; subsequent runs reuse saved session cookies.

## Disclaimer

Midjourney's Terms of Service may restrict automation. Use at your own risk.

## Links

- [Installation](installation.md)
- [Usage](usage.md)
- [API Reference](api.md)
- [Source on GitHub](https://github.com/twardoch/dimjournal)
