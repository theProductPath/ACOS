# ACOS marketing site — gh-pages branch payload

This folder holds the public marketing and explainer site for ACOS, served at `acos.theproductpath.com`.

## How this is published

The site does **not** live on the `main` branch of the ACOS repo. It lives on an orphan `gh-pages` branch, so that anyone who clones or downloads the framework (`main`) gets zero marketing content. The framework and its marketing share one repo but never share a branch.

The contents of this folder become the **root** of the `gh-pages` branch (so `index.html` is served at the domain root). The `setup-acos-repo.sh` script at the ACOS root wires this up the first time; after that, edits to the site are committed straight to `gh-pages`.

Publishing model: GitHub Pages → Settings → Pages → **Deploy from a branch** → `gh-pages` / `(root)`. No Actions workflow needed. `.nojekyll` disables Jekyll processing; `CNAME` pins the custom domain.

## Pages

- `index.html` — home / landing page.
- `adopt.html` — the adoption guide as an HTML experience. Renders the canonical `docs/adopting-acos.md` (which lives on `main`); the markdown is the source of truth, this page is the presentation layer.
- `blueprint.html` — interactive architecture explainer.
- `cascade.html` — interactive orientation explainer (fictional client "Northwind Trades" on the tPPOS reference instance).
- `extras/` — supplementary marketing artifacts not linked in the site nav: the standalone landing page and the Squarespace embed snippet.

## Git remote (SSH host alias)

This repo's remote must use the **theProductPath** SSH host alias, not plain `github.com`:

```
git remote set-url origin git@github.com-tpp:theProductPath/ACOS.git
```

The `~/.ssh/config` defines a per-account alias (`github.com-tpp` → key `id_ed25519_tpp`, `IdentitiesOnly yes`). Plain `git@github.com` has no default key and fails with `Permission denied (publickey)`. All `theProductPath/Products/*` repos follow this convention. If git complains about a stale `.git/index.lock`, remove it with `rm .git/index.lock` (a Google Drive sync artifact).

## Editing workflow (once the repo exists)

Ask the agent, or run yourself from the ACOS repo:

```
git checkout gh-pages      # switch to the marketing branch
# edit the site files (they sit at the branch root here)
git commit -am "site: <what changed>"
git push origin gh-pages   # GitHub Pages redeploys automatically
git checkout main          # back to the framework
```

Editing the site never touches `main`; editing the framework never touches the site.

## Conventions

- Self-contained static HTML. No build step. Each page inlines its own CSS and JS.
- Brand tokens match the tPP/ACOS look: dark `#181d26`, orange `#c75c2a`, Inter. Brand changes are applied to each page's `:root` block.
- Explainer pages are anonymized for public view: no real client names, no local filesystem paths, no internal maturity/investment data.
- Keep `adopt.html` in sync with the canonical `docs/adopting-acos.md` on `main`.
