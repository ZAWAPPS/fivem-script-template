# FiveM Script Template

This is the base template for all scripts. Do not develop directly in this repo.

---

## Starting a New Script

**1. Create the repo from this template**

Go to this repo on GitHub → click **Use this template** → **Create a new repository**
- Owner: your org
- Name: `fivem-scriptname`
- Visibility: **Private**
- Click **Create repository**

**2. Clone and run setup**
```bash
git clone https://github.com/YOUR-ORG-NAME/fivem-scriptname.git
cd fivem-scriptname
bash .github/scripts/setup-new-repo.sh
```

You will be prompted to paste your two Discord webhook URLs during setup.

**3. Update placeholders**

- `fxmanifest.lua` — set `name`, `description`, `author`
- `README.md` — replace this file with your script's documentation
- `shared/config.dist.lua` — add your config options

**4. Start your first feature**
```bash
git checkout develop
git checkout -b feature/your-feature-name
```

---

## Daily Workflow

**Working on a feature:**
```bash
git checkout develop
git checkout -b feature/your-feature-name

# write your code, then when ready to open a PR:
bash .github/scripts/add-fragment.sh

git add .
git commit -m "feat: describe your change"
git push origin feature/your-feature-name
# open PR to develop on GitHub
```

**Bundling features into a release:**
```
Open PR: develop → staging
In the PR description set: VERSION: 1.2.0
Merge → changelog assembled, staging zip built, internal Discord notified
```

**Going live:**
```
Open PR: staging → main
In the PR description set: VERSION: 1.2.0
Merge → zip built, GitHub Release created, public Discord notified
Download zip from GitHub Release → upload to Keymaster
```

---

## Branch Structure

| Branch | Purpose | Triggers pipeline? |
|---|---|---|
| `feature/*` | One feature at a time, branched off develop | No |
| `develop` | Integration — features land here | No |
| `staging` | Release candidate — tested bundle of features | Staging build + internal Discord |
| `main` | Production | Full build + public Discord + GitHub Release |

---

## Changelog Fragment Types

When running `add-fragment.sh`, use these types:

| Type | Use for |
|---|---|
| `added` | New features |
| `changed` | Changes to existing behaviour |
| `fixed` | Bug fixes |
| `removed` | Removed features |
| `config` | New or changed config.lua options |