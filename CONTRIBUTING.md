# Contributing to SicargaBox

Welcome! This guide will help you contribute to the SicargaBox project using Git and GitHub.

## 🎯 For Git Beginners

### What is Git?

Git is a **version control system** - think of it as a "save game" system for your code:

- Each **commit** = a save point you can return to
- Each **branch** = a parallel universe where you can experiment
- **GitHub** = cloud storage for your Git repository

### Basic Git Commands Explained

```bash
# See what files have changed
git status

# See which branch you're on
git branch

# See your commit history
git log --oneline

# See what changed in files
git diff
```

---

## 🔄 Development Workflow

### The Big Picture

1. **Branch** - Create a copy to work in
2. **Commit** - Save your progress frequently
3. **Push** - Upload to GitHub
4. **Pull Request** - Ask to merge your changes
5. **Merge** - Integrate your changes into master
6. **Update Task** - Mark task as completed in task-orchestrator

---

## 📋 Step-by-Step: Working on a New Feature

### Step 1: Check Task-Orchestrator for Next Task

Before starting work, see what needs to be done:

```bash
# Use Claude Code MCP tools to check tasks
# This will show you what to work on next
```

### Step 2: Update Your Local Master Branch

**Why?** Make sure you have the latest code before starting.

```bash
# Switch to master branch
git checkout master

# Download latest changes from GitHub
git pull origin master
```

**Explanation:**

- `git checkout master` - Switches to the master branch (like opening a specific save file)
- `git pull origin master` - Downloads new commits from GitHub and merges them into your local master
  - `origin` = the nickname for your GitHub repository
  - `master` = the branch name

### Step 3: Create a Feature Branch

**Why?** Keep your work separate from the stable master branch.

```bash
# Create and switch to a new branch
git checkout -b feature/phase1-quote-calculator

# This is shorthand for:
# git branch feature/phase1-quote-calculator  (creates branch)
# git checkout feature/phase1-quote-calculator  (switches to it)
```

**Branch Naming Convention:**

```bash
<type>/<brief-description>
```

Types:

```bash
- feature/  - New functionality
- bugfix/   - Fixing a bug
- hotfix/   - Critical production fix
- refactor/ - Improving existing code
- docs/     - Documentation updates
- test/     - Adding tests
```

Examples:

```bash
✅ feature/phase1-quote-calculator
✅ bugfix/elasticsearch-timeout
✅ docs/setup-instructions
❌ my-changes (too vague)
❌ fix (not descriptive)
```

### Step 4: Make Your Changes

Edit files in your code editor as normal. Git is watching!

```bash
# Check what you've changed
git status

# See specific changes in files
git diff
```

**Understanding git status output:**

```bash
Changes not staged for commit:
  (use "git add <file>..." to include in what will be committed)
        modified:   backend/sicargabox/MiCasillero/views.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        new_file.py
```

- **Modified** = File exists, you changed it
- **Untracked** = New file Git doesn't know about yet

### Step 5: Stage Your Changes

**What is "staging"?** Selecting which changes to include in your next commit (save point).

```bash
# Stage specific files
git add backend/sicargabox/MiCasillero/views.py
git add backend/sicargabox/MiCasillero/serializers.py

# Or stage all changes at once
git add .

# Unstage if you made a mistake
git restore --staged <file>
```

**Tip:** Stage related changes together. If you fixed 2 different things, make 2 separate commits.

### Step 6: Commit Your Changes

**A commit** = A snapshot of your code + a message explaining what you did.

```bash
# Commit with a descriptive message
git commit -m "Add quote calculator API endpoint"

# For longer messages (opens text editor)
git commit
```

**Good Commit Messages:**

```bash
✅ Add quote calculator API endpoint
✅ Fix Elasticsearch timeout on large queries
✅ Refactor PartidaArancelaria search logic
✅ Update README with setup instructions

❌ "update" (too vague)
❌ "fixed stuff" (not descriptive)
❌ "asdfasdf" (meaningless)
```

**Commit Often!** Small, focused commits are better than one giant commit.

### Step 7: Push Your Branch to GitHub

**What is pushing?** Uploading your local commits to GitHub.

```bash
# First time pushing a new branch
git push -u origin feature/phase1-quote-calculator

# After that, just
git push
```

**Explanation:**

- `git push` - Uploads commits to GitHub
- `-u origin feature/phase1-quote-calculator` - Sets up tracking so future pushes know where to go
  - `-u` = set upstream (tracking relationship)
  - `origin` = GitHub (the remote)
  - `feature/phase1-quote-calculator` = branch name

### Step 8: Create a Pull Request (PR)

**What is a PR?** A request to merge your changes into master.

#### **Option A: Using GitHub CLI (gh)**

```bash
gh pr create --title "Feature: Quote Calculator" \
             --body "Implements Phase 1 quote calculator API endpoint"
```

#### **Option B: Using GitHub Website**

1. Go to <https://github.com/ahvega/tariffs>
2. GitHub will show a yellow banner: "Compare & pull request"
3. Click it
4. Add title and description
5. Click "Create pull request"

**Good PR Description:**

```markdown
## Summary
Implements the public quote calculator API endpoint for Phase 1.

## Changes
- Add `/api/v1/quote/calculate` endpoint
- Add QuoteCalculator serializer
- Add validation for item weight/dimensions
- Add unit tests for calculator logic

## Testing
- ✅ Unit tests pass
- ✅ Manual testing with Postman
- ✅ Edge cases handled (zero weight, negative values)

## Related Task
- Task ID: [task-uuid-from-orchestrator]
```

### Step 9: Review and Merge

**For Solo Development:**

1. Review your own changes on GitHub
2. Make sure tests pass (if CI is set up)
3. Click "Merge pull request"
4. Choose "Squash and merge" (combines all commits into one)
5. Delete the branch after merging

**For Team Development:**

1. Request review from teammate
2. Address feedback
3. Get approval
4. Merge

### Step 10: Update Your Local Master

After merging on GitHub:

```bash
# Switch back to master
git checkout master

# Download the merged changes
git pull origin master

# Delete your local feature branch (it's merged now)
git branch -d feature/phase1-quote-calculator
```

### Step 11: Update Task-Orchestrator

Mark the task as completed using the MCP tools.

---

## 🆘 Common Git Problems & Solutions

### "I committed to master by mistake!"

```bash
# See your recent commits
git log --oneline

# Undo last commit but keep changes
git reset --soft HEAD~1

# Create the feature branch you should have created
git checkout -b feature/my-feature

# Commit again
git add .
git commit -m "Your commit message"
```

### "I want to undo my last commit completely"

```bash
# Undo last commit AND discard changes (⚠️ DANGEROUS)
git reset --hard HEAD~1
```

### "I have uncommitted changes but need to switch branches"

```bash
# Option 1: Commit them
git add .
git commit -m "WIP: Work in progress"

# Option 2: Stash them (temporary storage)
git stash
# Later, restore them
git stash pop
```

### "My branch is behind master"

```bash
# Make sure you're on your feature branch
git checkout feature/my-feature

# Pull latest master changes into your branch
git merge master

# Resolve conflicts if any (see below)
```

### "I have merge conflicts!"

**What are conflicts?** When Git can't automatically merge changes (e.g., you and someone else edited the same line).

1. Git marks conflicts in files:

```python
<<<<<<< HEAD
your_code = "your version"
=======
their_code = "their version"
>>>>>>> master
```

2. Edit the file, choose which version to keep (or combine them)
3. Remove the markers (`<<<<<<<`, `=======`, `>>>>>>>`)
4. Stage and commit:

```bash
git add conflicted_file.py
git commit -m "Resolve merge conflict"
```

### "I want to see what changed"

```bash
# See unstaged changes
git diff

# See staged changes
git diff --staged

# See changes in a specific commit
git show <commit-hash>

# See file change history
git log -p <file>
```

---

## 📝 Commit Message Best Practices

### Format

```html
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring (no behavior change)
- `test`: Adding tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(quote): Add public quote calculator API

Implements the /api/v1/quote/calculate endpoint that allows
anonymous users to get shipping cost estimates.

- Add QuoteCalculatorView
- Add input validation for weight/dimensions
- Add tax calculation logic
- Add unit tests

Closes: #123

---

fix(search): Resolve Elasticsearch timeout on large queries

The search was timing out when querying partidas with large
result sets. Added pagination and increased timeout to 30s.

Fixes: #456

---

docs(readme): Update development setup instructions

Added missing step about Elasticsearch requirement and updated
Python version to 3.11+.
```

---

## 🔒 Branch Protection Rules (Set Up Later)

Once you're comfortable with the workflow, we'll enable:

- ✅ Require pull requests (no direct commits to master)
- ✅ Require status checks to pass (tests must pass)
- ✅ Require up-to-date branches
- ✅ Delete branches after merge

---

## 🧪 Testing Before Committing

Always test your changes:

```bash
# Backend tests
cd backend/sicargabox
pytest

# With coverage
pytest --cov

# Specific test file
pytest tests/MiCasillero/test_views.py

# Linting
black .
flake8
isort .
```

---

## 🚀 Quick Reference Card

| Task | Command |
|------|---------|
| See status | `git status` |
| See branches | `git branch` |
| Create branch | `git checkout -b feature/name` |
| Switch branch | `git checkout branch-name` |
| Stage changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push` |
| Pull latest | `git pull origin master` |
| See history | `git log --oneline` |
| See changes | `git diff` |

---

## 💡 Tips for Success

1. **Commit often** - Small commits are easier to review and rollback
2. **Write clear messages** - Your future self will thank you
3. **Test before committing** - Don't commit broken code
4. **Pull before starting** - Always work with the latest code
5. **One feature per branch** - Keep changes focused
6. **Delete merged branches** - Keep your workspace clean
7. **Ask for help** - Git can be confusing at first!

---

## 📚 Learning Resources

- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [Visualizing Git](https://git-school.github.io/visualizing-git/)
- [Oh Sh*t, Git!?!](https://ohshitgit.com/) - Common problems and fixes

---

## 🤝 Getting Help

If you're stuck:

1. Check this guide
2. Use `git status` to see current state
3. Use `git log` to see history
4. Ask Claude Code for help
5. Check Git documentation

Remember: Git is powerful but forgiving. Most mistakes can be undone!
