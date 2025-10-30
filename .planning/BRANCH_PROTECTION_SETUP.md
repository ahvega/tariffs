# Branch Protection Setup Guide

Since your repository is private, branch protection rules need to be set up through the GitHub website (GitHub Pro required for API access, but manual setup is free!).

## 🔒 What Are Branch Protection Rules?

Branch protection rules prevent bad code from entering your master branch by:
- Requiring pull requests (no direct commits to master)
- Requiring tests to pass before merging
- Preventing accidental deletions
- Requiring code reviews (optional)

---

## 📋 Step-by-Step Setup

### Step 1: Navigate to Settings

1. Go to your repository: https://github.com/ahvega/tariffs
2. Click **Settings** tab (top right)
3. Click **Branches** in the left sidebar (under "Code and automation")

### Step 2: Add Branch Protection Rule

1. Click **Add branch protection rule**
2. In "Branch name pattern" field, enter: `master`

### Step 3: Configure Protection Rules

**Recommended settings for solo development:**

#### ✅ **Require a pull request before merging**
- Check this box
- **Sub-options:**
  - ❌ Require approvals: 0 (you're solo, so not needed)
  - ✅ Dismiss stale pull request approvals: (optional)
  - ❌ Require review from Code Owners: (not needed for solo)

#### ✅ **Require status checks to pass before merging**
- Check this box
- ✅ **Require branches to be up to date before merging**
- **Search for status checks:** (these will appear after first CI run)
  - Type and select: `backend-tests`
  - Type and select: `code-quality`
  - Type and select: `security` (optional)

#### ✅ **Require conversation resolution before merging**
- Check this box (ensures you don't merge with unresolved comments)

#### ❌ **Require signed commits**
- Leave unchecked (advanced feature, not needed for now)

#### ❌ **Require linear history**
- Leave unchecked (allows merge commits, which is fine)

#### ❌ **Require deployments to succeed**
- Leave unchecked (you don't have deployments yet)

#### ✅ **Lock branch** (Optional - more strict)
- Leave unchecked for now (this makes the branch read-only)

#### ✅ **Do not allow bypassing the above settings**
- Check this if you want to enforce rules even for admins
- ⚠️ **Warning:** If checked, even YOU can't bypass the rules. Uncheck if you want the option to force-push in emergencies.

#### ✅ **Rules applied to administrators**
- Check this to apply rules to yourself (good practice!)

#### ✅ **Restrict who can push to matching branches** (Optional)
- Leave unchecked for solo development

#### ✅ **Allow force pushes**
- ❌ Leave unchecked (force pushes can overwrite history - dangerous!)

#### ✅ **Allow deletions**
- ❌ Leave unchecked (prevents accidental deletion of master)

### Step 4: Save Changes

1. Scroll to bottom
2. Click **Create** or **Save changes**

---

## 🎯 What This Accomplishes

After setup:

### ✅ **You CANNOT directly commit to master**
```bash
# This will be rejected:
git checkout master
git add .
git commit -m "fix something"
git push  # ❌ ERROR: Protected branch
```

### ✅ **You MUST use pull requests**
```bash
# This is required:
git checkout -b feature/my-feature
git add .
git commit -m "Add feature"
git push -u origin feature/my-feature
gh pr create  # Create PR on GitHub
# Then merge via GitHub web interface
```

### ✅ **Tests MUST pass before merging**
- If tests fail, the "Merge" button is disabled
- You must fix the issues and push again
- Tests run automatically on every push to PR

### ✅ **Branch MUST be up-to-date**
- If master changes while your PR is open, you must update your branch:
```bash
git checkout feature/my-feature
git merge master
git push
```

---

## 🚦 What Happens After Setup?

### Creating a Pull Request

1. **Push your feature branch:**
   ```bash
   git push -u origin feature/my-feature
   ```

2. **GitHub automatically runs CI checks:**
   - ⏳ **Pending:** Tests are running
   - ✅ **Passed:** All tests passed, ready to merge
   - ❌ **Failed:** Tests failed, cannot merge

3. **Review the PR:**
   - Check the "Files changed" tab
   - Ensure all tests passed (green checkmarks)
   - Click "Merge pull request"

4. **After merge:**
   - GitHub automatically deletes the branch (if enabled)
   - Pull latest master locally:
     ```bash
     git checkout master
     git pull origin master
     ```

---

## ⚙️ Testing the Protection

After setting up, try this to verify it works:

```bash
# Try to push directly to master (should fail)
git checkout master
echo "test" > test.txt
git add test.txt
git commit -m "test"
git push

# Expected output:
# remote: error: GH006: Protected branch update failed
# ! [remote rejected] master -> master (protected branch hook declined)
```

✅ If you see this error, **protection is working!**

---

## 🔧 Modifying Rules Later

To change rules:
1. Go to **Settings** → **Branches**
2. Click **Edit** next to your protection rule
3. Modify settings
4. Click **Save changes**

To disable temporarily:
1. Go to **Settings** → **Branches**
2. Click **Delete** next to your protection rule
3. Re-add later when needed

---

## 💡 Tips

### For Solo Development
- Keep rules simple (PR + tests required)
- Don't require approvals (you're the only reviewer)
- Enable admin bypass for emergencies

### For Team Development
- Require at least 1 approval
- Require conversation resolution
- Apply rules to administrators
- No admin bypass

### Common Issue: "Can't merge - checks have not run"
**Problem:** Status checks don't appear in the list when setting up protection.

**Solution:**
1. Create a PR first (to trigger CI)
2. Wait for CI to run
3. Then set up branch protection (checks will appear)
4. Close the test PR

---

## 📚 Additional Resources

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)

---

## 🎓 What You Learned

- **Branch protection** = Rules that enforce good practices
- **Pull requests** = Required for all changes (no direct commits)
- **Status checks** = Automated tests must pass
- **Manual setup** = Free for all repos (API requires GitHub Pro)
