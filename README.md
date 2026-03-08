# FiveM Script Template (ZAWAPPS)

Professional template for FiveM resources with automated CI/CD, versioning, and branch synchronization. Optimized for **FiveM Escrow** distribution.

---

## ⚠️ Important: GitHub Free Tier Limitations

If you are using this template with a **GitHub Free** account and a **Private** repository, please note:

- **Recursive Workflow Triggers:** On GitHub Free, pushes made with the default `GITHUB_TOKEN` **do not** trigger subsequent workflows. To ensure that merging `main` into `staging` or `develop` triggers the required builds/validations, you **must** configure a `GH_PAT` (Personal Access Token) with `repo` and `workflow` scopes.
- **Branch Protection:** GitHub does not enforce branch protection (like "Require PR") on free private repos. You must manually ensure your PRs are validated and have a "Green Check" before merging.

---

## 🚀 Starting a New Script

**1. Create the repository**
- Go to this template on GitHub -> **Use this template** -> **Create a new repository**.
- Set visibility to **Private**.

**2. Initialize the repo**
```bash
git clone https://github.com/YOUR-ORG/your-repo.git
cd your-repo
bash .github/scripts/setup-new-repo.sh
```
*The script will prompt you for:*
- **SCRIPT_NAME**: Used for folder naming and `fxmanifest.lua`.
- **Description & Author**: Internal metadata.
- **Discord Webhooks**: For automated staging and production notifications.
- **GH_PAT**: To enable automated branch synchronization.

---

## 🛠 CI/CD Safety & Integrity

This template includes several automated checks to prevent breaking production:

- **Luacheck:** Validates Lua syntax and global definitions (including FiveM natives).
- **Config Sync Check:** Ensures that every `Config.Key` used in your code exists in `shared/config.dist.lua`.
- **NUI Validation:** Automatically runs `npm ci` and `npm run build` to verify the UI.
- **Version Validation:** Prevents merging to `main` if the version is not higher than the current production release.

---

## 📦 Configuration Strategy

This template uses a **Dist/Local** pattern to prevent overwriting customer settings during updates:

1.  **`shared/config.dist.lua`**: Contains default values. **This file is shipped to customers.**
2.  **`shared/config.lua`**: Contains user-specific overrides. **This file is ignored by Git.**
3.  **Deployment**: The build pipeline ensures `config.dist.lua` is always present in the release. *Warning: Never delete `.dist.lua` files, as they serve as the blueprint for your configuration.*

---

## 🚀 Release Workflow

### 1. Development (Internal)
1.  Work on `develop` or a feature branch.
2.  Open PR to `develop`. **Requirement:** PR Body must have a `## Changelog` section.

### 2. Staging (Testing)
1.  Open PR: `develop` -> `staging`.
2.  The `staging-build` workflow creates a `.zip` for testing and notifies Discord.
3.  *Note:* Staging builds use the current date/time as a version suffix (e.g., `1.0.0-staging-20231027`).

### 3. Production (Customer Release)
1.  Open PR: `staging` -> `main`.
2.  **Requirement:** You **MUST** include `VERSION: X.Y.Z` in the PR body. 
    - *Warning:* Failure to specify a version will trigger a fallback logic that may default to `1.0.0` or a previous version, potentially breaking update notifications.
3.  **Result:**
    - `fxmanifest.lua` and `CHANGELOG.md` are updated.
    - A GitHub Release is created with the production `.zip`.
    - **Automated Sync:** `main` is merged back to `develop` and `staging` using your `GH_PAT`.

---

## 🔄 Branch Synchronization & Conflicts

When a release or hotfix happens on `main`, the system tries to merge those changes back to `develop` and `staging` automatically.

- **Success:** Changes flow back silently.
- **Conflict:** If `develop` has moved too far ahead, the pipeline will **automatically open a Sync PR**. 
  - *Action Required:* Open the PR, resolve the conflict in the GitHub UI, and merge it manually.

---

## 📝 Changelog Guidelines

Your PR body MUST contain a changelog. The `release_engine.py` will automatically aggregate these into the final `CHANGELOG.md`. Use these categories:
- `Added`: New features
- `Fixed`: Bug fixes
- `Changed`: Logic updates
- `Config`: New or updated configuration options
