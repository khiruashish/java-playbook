# Deployment Guide: from ZIP to a live website (Java handbook)

Step-by-step notes for taking the downloaded `java-playbook.zip`, running it on your computer, pushing it to your own GitHub repository, and publishing it as a website on GitHub Pages.

Written for **macOS** (Terminal / zsh). Windows differences are noted where they matter.

**Final result:** your site is live at `https://<your-username>.github.io/java-playbook/`

---

## Contents

1. [What you need](#1-what-you-need)
2. [Unzip and open the folder](#2-unzip-and-open-the-folder)
3. [Run the site on your computer](#3-run-the-site-on-your-computer)
4. [Create the GitHub repository](#4-create-the-github-repository)
5. [Push the code to GitHub](#5-push-the-code-to-github)
6. [Publish the website (GitHub Pages)](#6-publish-the-website-github-pages)
7. [Making changes later](#7-making-changes-later)
8. [Troubleshooting](#8-troubleshooting)
9. [Command cheat sheet](#9-command-cheat-sheet)

---

## 1. What you need

| Tool | Check it's installed | Install |
|---|---|---|
| **Python 3.9+** | `python3 --version` | https://www.python.org/downloads/ or `brew install python` |
| **JDK 21+** (only for the code checks and examples) | `java -version` | https://adoptium.net |
| **Git** | `git --version` | `xcode-select --install` (macOS) or https://git-scm.com |
| **GitHub account** | — | https://github.com/signup |
| **GitHub CLI** (optional, makes login easy) | `gh --version` | `brew install gh` |

---

## 2. Unzip and open the folder

1. Double-click `java-playbook.zip` in Finder (or run `unzip java-playbook.zip`).
2. Open Terminal and go into the folder:

    ```bash
    cd ~/Downloads/java-playbook
    ```

3. Check you're in the right place:

    ```bash
    ls
    ```

    You should see:

    ```text
    DEPLOYMENT.md   MASTER_PROMPT.md   README.md   _source   chapter-prompt.md   code   docs
    java-handbook-master-plan.md   mkdocs.yml   requirements.txt   scaffold-handbook.sh   tools
    ```

    > **Tip:** If you see another `java-playbook` folder instead, the zip unpacked one level deeper. Run `cd java-playbook` again.

> **Run a Java example without installing anything else:** with JDK 21+, `java code/examples/java8/J8_01_Lambdas.java`.

---

## 3. Run the site on your computer

### 3.1 Create a virtual environment (one time only)

A virtual environment keeps this project's Python packages separate from everything else on your Mac.

```bash
python3 -m venv .venv
```

This creates a hidden `.venv` folder. You only do this **once** per folder.

### 3.2 Activate it (every new Terminal window)

```bash
source .venv/bin/activate
```

Your prompt now starts with `(.venv)`.

| OS | Activate command |
|---|---|
| macOS / Linux | `source .venv/bin/activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |

### 3.3 Install the dependencies (one time only)

```bash
pip install -r requirements.txt
```

Note the file name: **`requirements.txt`**, with an **s**.

### 3.4 Preview the site

```bash
mkdocs serve
```

Open **http://127.0.0.1:8000** in your browser. The page reloads automatically when you edit a file. Press Ctrl+C in Terminal to stop it.

### 3.5 Build check (optional, recommended before deploying)

```bash
mkdocs build --strict
```

It should end with `Documentation built in X seconds` and show no `WARNING` lines. The output goes to a `site/` folder, which is ignored by git.

---

## 4. Create the GitHub repository

1. Go to **https://github.com/new**
2. **Repository name:** `java-playbook`
3. Choose **Public** (GitHub Pages on a private repo needs a paid plan).
4. ⚠️ **Do not** tick *Add a README*, *Add .gitignore* or *Choose a license*. The repository must be **empty**.
5. Click **Create repository**.

### 4.1 Update the site config

Open `mkdocs.yml` and change these two lines to point at your new repository:

```yaml
repo_url: https://github.com/<your-username>/java-playbook
edit_uri: edit/main/docs/
```

Optionally also set the site's public address, which improves links and search:

```yaml
site_url: https://<your-username>.github.io/java-playbook/
```

---

## 5. Push the code to GitHub

### 5.1 Log in to GitHub from Terminal (one time only)

GitHub doesn't accept your account password for `git push`. The easiest way to log in is the GitHub CLI:

```bash
gh auth login
```

Answer the prompts: **GitHub.com** → **HTTPS** → **Yes** (authenticate Git) → **Login with a web browser**, then paste the code shown into the browser.

<details>
<summary>No GitHub CLI? Use a personal access token instead</summary>

1. Go to https://github.com/settings/tokens → **Generate new token (classic)**.
2. Tick the **`repo`** and **`workflow`** scopes, then generate.
3. Copy the token. When `git push` asks for a password, paste the token.
4. To avoid typing it every time on macOS: `git config --global credential.helper osxkeychain`

</details>

### 5.2 Tell git who you are (one time only)

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 5.3 Create the local repository and push

Run these from inside the `java-playbook` folder:

```bash
git init
git add .
git commit -m "Initial commit: Web UI Frontend Playbook"
git branch -M main
git remote add origin https://github.com/<your-username>/java-playbook.git
git push -u origin main
```

Refresh your repository page on GitHub: all the files should be there.

> **What doesn't get uploaded:** `.gitignore` already excludes `.venv/`, `site/`, `__pycache__/` and `.cache/`, so only the source files are pushed.

---

## 6. Publish the website (GitHub Pages)

Pick **one** of the two methods.

### Method A: automatic deploy on every push (recommended)

The zip already contains the workflow file **`.github/workflows/deploy.yml`**. It builds and publishes the site every time you push to `main`.

1. On GitHub, open your repository → **Settings** → **Pages**.
2. Under **Build and deployment → Source**, choose **GitHub Actions**.
3. Open the **Actions** tab. A run called **"Deploy site"** starts automatically after your push.
    - If nothing is running, click **Deploy site** → **Run workflow**.
4. When it shows a green ✔ (about 1–2 minutes), open:
    **`https://<your-username>.github.io/java-playbook/`**

From now on, **every `git push` updates the website automatically.**

<details>
<summary>What's in `.github/workflows/deploy.yml`</summary>

```yaml
name: Deploy site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: mkdocs build --strict
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

</details>

### Method B: deploy manually from your computer

1. With the virtual environment active:

    ```bash
    source .venv/bin/activate
    mkdocs gh-deploy --force
    ```

    This builds the site and pushes it to a branch called **`gh-pages`**.

2. On GitHub: **Settings** → **Pages** → **Source: Deploy from a branch** → Branch **`gh-pages`**, folder **`/ (root)`** → **Save**.
3. After 1–2 minutes, open `https://<your-username>.github.io/java-playbook/`.

Run `mkdocs gh-deploy --force` again each time you want to update the site.

> ⚠️ **Don't mix the methods.** If you use Method B, set Pages to "Deploy from a branch". If you use Method A, set it to "GitHub Actions". If you only use Method B, delete `.github/workflows/deploy.yml` so the Actions run doesn't fail.

---

## 7. Making changes later

```bash
cd ~/Downloads/java-playbook
source .venv/bin/activate        # every new Terminal window
mkdocs serve                     # preview while you edit
```

When you're happy:

```bash
mkdocs build --strict            # optional check
git add .
git commit -m "Describe what you changed"
git push                         # Method A: site updates automatically
# mkdocs gh-deploy --force       # Method B: run this as well
```

### Generated pages: edit the source, not the page

| Page | Edit this | Then run |
|---|---|---|
| `docs/07-examples/*.md` | `code/examples/**/*.java` (and `tools/build-examples.py` for page text) | `python3 tools/run-examples.py && python3 tools/build-examples.py` |
| Appendix B, Part 2 | Section 9 of Ch 06–10 | See `java-handbook-master-plan.md` §8 |
| Appendix C | Section 9 of Ch 24–33 | `python3 tools/build-interview-bank.py …` (see §8) |
| Appendix E | Each chapter's cheat sheet | `python3 tools/build-cheat-sheets.py` |
| Appendix F, JEP index | Appendix A | `python3 tools/build-glossary.py` |

### Checks before you push

```bash
mkdocs build --strict                 # no WARNING lines
python3 tools/check-code-blocks.py    # needs a JDK; expect DEFECT 0
python3 tools/check-references.py     # expect findings: 0
```

### Adding a new page

1. Create the file, e.g. `docs/03-collections/24-my-topic.md` (use `chapter-prompt.md` to write it).
2. Add it to the `nav:` section of `mkdocs.yml`:

    ```yaml
    - Collections:
        - "24 · My Topic": 03-collections/24-my-topic.md
    ```

3. Preview with `mkdocs serve`, then commit and push.

---

## 8. Troubleshooting

### Local setup

| Error / symptom | Cause | Fix |
|---|---|---|
| `Could not open requirements file: … 'requirement.txt'` | Typo | The file is **`requirements.txt`** (with an **s**) |
| `source: no such file or directory: .venv/bin/activate` | The virtual environment hasn't been created in this folder | `python3 -m venv .venv`, then `source .venv/bin/activate` |
| `command not found: mkdocs` | Venv not active, or packages not installed | `source .venv/bin/activate` then `pip install -r requirements.txt`. Or run `python -m mkdocs serve` |
| Prompt shows `(base)` and things act strangely | A conda environment is active | Run `conda deactivate`, then activate `.venv`. Or skip the venv and use `pip install -r requirements.txt` + `python -m mkdocs serve` |
| `ls` doesn't show `mkdocs.yml` | You're in the wrong folder | `cd` into the folder that contains `mkdocs.yml` |
| `[Errno 48] Address already in use` | Another `mkdocs serve` is running | Stop it with Ctrl+C, or use `mkdocs serve -a 127.0.0.1:8001` |
| Pip notice "A new release of pip is available" | Just a suggestion | Ignore it, or run `pip install --upgrade pip` |
| Diagrams don't render | You're offline | Mermaid loads from the internet; everything else works offline |
| `check-code-blocks.py` fails immediately | No JDK installed | Install JDK 21+ (or skip it; it's a check, not part of the build) |

### Git and GitHub

| Error / symptom | Cause | Fix |
|---|---|---|
| `Support for password authentication was removed` | GitHub needs a token, not your password | `gh auth login`, or use a personal access token (section 5.1) |
| `! [rejected] main -> main (fetch first)` | The GitHub repo wasn't empty (README added) | `git pull origin main --allow-unrelated-histories`, then `git push`. Or delete and recreate the repo empty |
| `remote origin already exists` | `git remote add` was run twice | `git remote set-url origin https://github.com/<you>/java-playbook.git` |
| `fatal: not a git repository` | `git init` wasn't run in this folder | `git init` (section 5.3) |
| `refusing to allow … to create or update workflow` | Your token lacks the `workflow` scope | Use `gh auth login`, or create a token with `repo` **and** `workflow` |
| `.venv` or `site` appear on GitHub | They were committed before `.gitignore` | `git rm -r --cached .venv site`, then commit and push |

### GitHub Pages

| Error / symptom | Cause | Fix |
|---|---|---|
| 404 at the site address | Pages not set up yet, or still building | Check **Settings → Pages**; wait 2 minutes; check the **Actions** tab |
| Actions run fails at the **deploy** job | Pages source isn't "GitHub Actions" | **Settings → Pages → Source: GitHub Actions**, then re-run |
| Actions run fails at `mkdocs build --strict` | A broken link or missing page in `nav` | Run `mkdocs build --strict` locally; fix each `WARNING` |
| Site loads but looks unstyled | Wrong address | Use the full address ending in `/java-playbook/` |
| Changes don't show up | Browser cache, or deploy still running | Hard refresh (Cmd+Shift+R); check the Actions run finished |
| Private repo: Pages option missing | Free plan limitation | Make the repo public, or upgrade the plan |

---

## 9. Command cheat sheet

```bash
# ---- one-time setup ----
cd ~/Downloads/java-playbook
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
gh auth login                                   # or use a personal access token
git init
git add .
git commit -m "Initial commit: Web UI Frontend Playbook"
git branch -M main
git remote add origin https://github.com/<your-username>/java-playbook.git
git push -u origin main
# then: GitHub → Settings → Pages → Source: GitHub Actions

# ---- every time you work on it ----
source .venv/bin/activate
mkdocs serve                                    # http://127.0.0.1:8000
mkdocs build --strict                           # check before pushing
git add . && git commit -m "Update" && git push  # site redeploys automatically

# ---- manual deploy (Method B only) ----
mkdocs gh-deploy --force
```
