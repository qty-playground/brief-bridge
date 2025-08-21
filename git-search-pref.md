# Search Preferences :search-pref

Please follow these rules to find a piece of code:

- For file and text searches in git projects, prefer `git grep` and git-related commands
- Only use `grep` for single file searches when necessary
- Use `rg` (ripgrep) only for searching large numbers of files when git grep isn't suitable
- For general programming projects, use `git grep` and check `git status` for uncommitted/untracked files, then use Read or Grep tools to examine them

## Git Grep Correct Usage Guide

### ⚠️ Critical Parameter Order
**ALWAYS follow this order:** `git grep [options] <pattern> [-- <pathspec>...]`

```bash
# ❌ WRONG - pathspec cannot come before pattern
git grep src/ "function"
git grep *.js "console.log"

# ✅ CORRECT - options → pattern → pathspec
git grep "function" src/
git grep "console.log" -- "*.js"
git grep -n "TODO" -- "**/*.py"

# ⚠️ SPECIAL CASE: Boolean operations require -e for ALL patterns
# ❌ WRONG - mixed usage of -e and bare patterns
git grep "pattern1" --and -e "pattern2"

# ✅ CORRECT - consistent -e usage for boolean operations
git grep -e "pattern1" --and -e "pattern2"
```

### 🔍 Git-Specific Search Scopes

```bash
# Search tracked files (default)
git grep "pattern"

# Include untracked files
git grep --untracked "pattern"

# Search only staged/cached files
git grep --cached "pattern"

# Search outside git repo (like regular grep)
git grep --no-index "pattern"

# Search specific commit/branch
git grep "pattern" HEAD~1
git grep "pattern" main
```

### 🛡️ Use `--` to Protect Pathspecs

```bash
# ❌ WRONG - shell may expand before git sees it
git grep "function" **/*.js

# ✅ CORRECT - protect pathspec from shell expansion
git grep "function" -- "**/*.js"
git grep "import" -- "*.{js,ts,jsx,tsx}"
git grep "class" -- ":^tests/"  # exclude tests/ directory
```

### 🚨 Patterns Starting with `-`

```bash
# ❌ WRONG - treated as option
git grep "--help"
git grep "-v"

# ✅ CORRECT - use -e to specify pattern
git grep -e "--help"
git grep -e "-v"
```

### 🔗 Boolean Pattern Combinations

**⚠️ CRITICAL: ALL patterns in boolean operations MUST use `-e` prefix**

```bash
# Search for lines with BOTH patterns
git grep -e "function" --and -e "async"

# Search for lines with EITHER pattern  
git grep -e "TODO" --or -e "FIXME"

# Complex combinations (note parentheses escaping)
git grep -e "#define" --and \( -e "MAX_PATH" --or -e "PATH_MAX" \)

# Files that have ALL specified patterns (anywhere in file)
git grep --all-match -e "import" -e "export" -- "*.js"

# ❌ COMMON MISTAKE - missing -e prefix on first pattern
git grep "function" --and -e "async"  # ERROR: will fail!

# ✅ CORRECT - both patterns have -e prefix
git grep -e "function" --and -e "async"

# Combining with line numbers and file filters
git grep -n -e "event" --and -e "log" -- "**/*.py"
git grep -l -e "import" --or -e "require" -- "**/*.{js,ts}"
```

**Alternative approaches when boolean operators fail:**
```bash
# Using pipe (reliable fallback)
git grep -n "event" -- "**/*.py" | grep "log"

# Using regex pattern
git grep -n ".*event.*log\|.*log.*event" -- "**/*.py"

# Sequential search with file list
git grep -l "event" -- "**/*.py" | xargs git grep -n "log"
```

### 📍 Common Useful Options

```bash
# Show line numbers
git grep -n "pattern"

# Show only filenames
git grep -l "pattern"

# Case insensitive
git grep -i "pattern"

# Word boundaries (whole words only)
git grep -w "function"

# Show context (3 lines before/after)
git grep -C 3 "pattern"

# Count matches per file
git grep -c "pattern"

# Show function context
git grep -W "pattern"
```

### 🎯 File Type Filtering

```bash
# C/C++ files
git grep "malloc" -- "**/*.[ch]" "**/*.cpp"

# JavaScript/TypeScript
git grep "useState" -- "**/*.{js,jsx,ts,tsx}"

# Python files only
git grep "def " -- "**/*.py"

# Exclude specific directories
git grep "pattern" -- ":^node_modules/" ":^.git/"
```

### ⚡ Performance Tips

- `git grep` is faster than `grep -r` in git repos (uses git's index)
- Use `--threads=N` for large repos to control parallelism
- Use `--max-count=N` to limit matches per file
- Prefer `git grep` over external tools like `ag` or `rg` in git projects
