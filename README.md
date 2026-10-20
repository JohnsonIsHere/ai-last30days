# ai-last30days

Monthly AI briefings. Each issue gathers what people actually said on Reddit, X, Hacker News, GitHub and YouTube over a rolling thirty-day window, then writes it up as one readable page.

Built with the [`last30days`](https://github.com/mvanhorn/last30days-skill) research skill.

- **Front page: <https://johnsonishere.github.io/ai-last30days/>** — always the current issue
- **Archive: <https://johnsonishere.github.io/ai-last30days/issues/>** — every issue, permanent links

## Issues

| Window | Issue | Covering |
|---|---|---|
| 20 Sep to 20 Oct 2026 | [Frontier on Hold](https://johnsonishere.github.io/ai-last30days/issues/2026-10-frontier-on-hold.html) | Model updates, AI engineering, AI safety, Europe AI |

## Layout

```
src/<slug>.html       issue source, as published to a Claude artifact
issues.json           manifest: slug, title, date, window, topics, summary
build.py              generates the site from the two above
index.html            generated — a copy of the newest issue
issues/<slug>.html    generated — the permanent link for each issue
issues/index.html     generated — the archive listing
```

Everything outside `src/` and `issues.json` is generated. Do not hand-edit it.

A file in `src/` is an **artifact body**: it carries its own `<title>` and `<style>` but no `<!doctype>`, `<head>` or `<body>`, because the Claude artifact platform supplies those at publish time. GitHub Pages does not, so `build.py` adds them, and also injects the archive nav that would not resolve inside an artifact. That is why the same source can produce both.

## Adding next month's issue

1. Save the new artifact body to `src/YYYY-MM-slug.html`
2. Add an entry to the **top** of the `issues` array in `issues.json` (newest first)
3. `python3 build.py`
4. Commit and push; GitHub Pages redeploys in a minute or two

The front page moves to the new issue automatically. Previous issues keep their URLs forever.

## Which link to share

Share the **dated issue link** when you are describing that specific issue, since it will never change under your readers. Share the **front page** when you want people to land on whatever is current.
