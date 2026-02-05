---
description: Process for releasing a new version of the application using Semantic Versioning
---

# Release Process & Versioning Strategy

## 1. Understanding Semantic Versioning (SemVer)
We use the **Semantic Versioning 2.0.0** standard (Major.Minor.Patch).
Format: `vX.Y.Z` (e.g., `v1.2.0`)

| Segment | Type | When to increment? | Example |
| :--- | :--- | :--- | :--- |
| **MAJOR** (X) | **Breaking Changes** | Incompatible API changes, architecture rewrites. | `1.0.0` → `2.0.0` |
| **MINOR** (Y) | **New Features** | Adding functionality in a backwards-compatible manner. | `1.2.0` → `1.3.0` |
| **PATCH** (Z) | **Bug Fixes** | Backwards-compatible bug fixes or minor tweaks. | `1.2.0` → `1.2.1` |

> **Note**: For pre-release (development), we are currently in `0.X.Y`. Breaking changes are allowed in `0.x`, but stability typically starts at `1.0.0`.

---

## 2. Release Workflow Steps

### Step 1: Verification
Ensure the current branch (`main`) is passing all tests.
```bash
python -m pytest tests/
```

### Step 2: Determine Next Version
Based on the changes since the last tag, decide if this is a Patch, Minor, or Major release.
*   **Patch**: Did you fix a bug?
*   **Minor**: Did you add a new skill, tool, or feature?
*   **Major**: Did you change the entire architecture or break existing `.ledger` formats?

### Step 3: Create Release Tag
We use Git Tags to mark releases.

**Option A: Lightweight Tag (Simple)**
```bash
git tag v1.0.0
```

**Option B: Annotated Tag (Recommended for Releases)**
It stores the tagger name, email, and date.
```bash
git tag -a v1.0.0 -m "Release v1.0.0: Features X, Y, Z"
```

### Step 4: Push Tags to GitHub
Tags are not pushed by default with `git push`. You must push them explicitly.
```bash
git push origin v1.0.0
```
*Or push all tags:*
```bash
git push origin --tags
```

### Step 5: (Optional) GitHub Release
1. Go to GitHub > Releases.
2. "Draft a new release".
3. Choose the tag `v1.0.0`.
4. Generate release notes (GitHub can auto-generate this from Pull Requests).
5. Publish.

---

## 3. Recommended Project Version Management
To keep the version in sync with the code, it is recommended to have a `__version__` variable in the standard location:
*   File: `src/agent_telegram/__init__.py`
*   Content: `__version__ = "0.1.0"`

When releasing, update this file first, commit it ("chore: bump version to 0.1.0"), and then Tag.
