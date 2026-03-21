# Development Tools & Commands

Quick reference for running type checking, code formatting, and unused import removal.

---

## 🔧 Code Formatting

### Black (Auto-format code)

Format all Python files in the app directory:

```bash
black app/
```

Format a specific file:

```bash
black app/main.py
```

Check formatting without making changes (dry-run):

```bash
black --check app/
```

---

## ✅ Type Checking

### Mypy (Static type checker)

Check all Python files:

```bash
mypy app/
```

Check a specific file:

```bash
mypy app/main.py
```

Check with strict mode (more rigorous):

```bash
mypy --strict app/
```

---

## 🧹 Unused Import Removal

### Autoflake (Remove unused imports)

Check what would be removed (dry-run):

```bash
autoflake --remove-all-unused-imports --check app/
```

Actually remove unused imports:

```bash
autoflake --remove-all-unused-imports --in-place -r app/
```

Remove unused imports and variables:

```bash
autoflake --remove-all-unused-imports --remove-unused-variables --in-place -r app/
```

---

## 🚀 Full Development Workflow

Run all checks and formatting:

```bash
# 1. Format code
black app/

# 2. Remove unused imports
autoflake --remove-all-unused-imports --in-place -r app/

# 3. Check types
mypy app/
```

Or as a one-liner:

```bash
black app/ && autoflake --remove-all-unused-imports --in-place -r app/ && mypy app/
```

---

## 📋 Create a Helper Script

Save this as `scripts/lint.sh`:

```bash
#!/bin/bash

echo "🎨 Formatting code with black..."
black app/

echo "🧹 Removing unused imports with autoflake..."
autoflake --remove-all-unused-imports --in-place -r app/

echo "✅ Checking types with mypy..."
mypy app/

echo "✨ All checks passed!"
```

Make it executable:

```bash
chmod +x scripts/lint.sh
```

Run it:

```bash
./scripts/lint.sh
```

---

## 🔍 Individual Tool Details

### Black Options

- `--line-length 88` - Default line length (can customize)
- `--check` - Dry-run, don't modify files
- `--diff` - Show diffs of what would change

### Mypy Options

- `--strict` - Enable all optional checks
- `--ignore-missing-imports` - Ignore packages without type stubs
- `--show-error-codes` - Show error codes for suppression

### Autoflake Options

- `--remove-all-unused-imports` - Remove unused imports
- `--remove-unused-variables` - Remove unused variables
- `--in-place` - Modify files in place
- `-r` or `--recursive` - Process directories recursively
- `--check` - Dry-run mode

---

## 📦 Requirements Files

### Production

```bash
pip install -r requirements-prod.txt
```

### Development (with tools)

```bash
pip install -r requirements-dev.txt
```

---

## 🎯 CI/CD Integration

Add to your CI pipeline:

```yaml
# Example GitHub Actions
- name: Format check with black
  run: black --check app/

- name: Type check with mypy
  run: mypy app/

- name: Check for unused imports
  run: autoflake --remove-all-unused-imports --check -r app/
```

---

## ⚡ Pro Tips

1. **Run before committing:**

   ```bash
   black app/ && autoflake --remove-all-unused-imports --in-place -r app/
   ```

2. **Set up a Git pre-commit hook** to auto-format before commits

3. **Integrate with your IDE:**
   - VS Code: Add to settings.json for on-save formatting
   - PyCharm: Configure as external tool

4. **Gradual mypy adoption:**
   Start with `--ignore-missing-imports` and gradually enable stricter checks

---

Last updated: March 7, 2026
