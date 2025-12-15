# 🌿 Git Branching Strategy - Logistics Twin

**Purpose:** Safe development with easy rollback & risk mitigation

---

## 📊 Branch Structure

```
main (production)
├── develop (integration)
    ├── feature/v5.7-testing
    ├── feature/design-system
    ├── feature/github-actions
    └── hotfix/critical-bug (if needed)
```

---

## 🎯 Branch Types

### 1. **main** - Production Ready
- **Purpose:** Stable, deployable code only
- **Protection:** Never commit directly!
- **Deploy:** Auto-deploy to production (future)
- **Tag:** Every release (v5.6.1, v5.7.0, etc.)

### 2. **develop** - Integration Branch
- **Purpose:** Latest working features
- **Merge from:** Feature branches
- **Merge to:** main (via PR)
- **Testing:** All tests must pass

### 3. **feature/*** - New Features
- **Naming:** `feature/v5.7-testing`, `feature/atomic-components`
- **Branch from:** develop
- **Merge to:** develop
- **Lifetime:** Delete after merge

### 4. **hotfix/*** - Emergency Fixes
- **Naming:** `hotfix/security-patch`
- **Branch from:** main
- **Merge to:** main AND develop
- **Priority:** Immediate

---

## 🚀 Workflow for V5.7 Update

### Step 1: Create Feature Branch
```bash
cd logistics-twin

# Make sure you're on main and updated
git checkout main
git pull origin main

# Create develop branch (if not exists)
git checkout -b develop

# Create feature branch
git checkout -b feature/v5.7-testing
```

### Step 2: Work on Feature
```bash
# Make changes (implement tests, etc.)
git add .
git commit -m "feat: implement skipped tests for v5.7"

# Push to GitHub
git push -u origin feature/v5.7-testing
```

### Step 3: Test Before Merge
```bash
# Run all tests
python -m pytest -v

# Check coverage
python -m pytest --cov

# Manual testing
python app.py
# Test in browser: http://localhost:5000
```

### Step 4: Merge to Develop
```bash
# Switch to develop
git checkout develop

# Merge feature
git merge feature/v5.7-testing

# Push
git push origin develop
```

### Step 5: Release to Main (When Ready)
```bash
# Switch to main
git checkout main

# Merge develop
git merge develop

# Tag version
git tag v5.7.0 -m "Release V5.7: Testing & Monitoring"

# Push with tags
git push origin main --tags
```

---

## 🛡️ Safety Measures

### Before Starting Any Work
```bash
# 1. Tag current stable version
git tag v5.6.1-stable -m "Stable before V5.7 work"
git push origin v5.6.1-stable

# 2. Verify you're on feature branch
git branch  # Should show * feature/v5.7-testing
```

### If Something Breaks
```bash
# Option A: Rollback to last commit
git reset --hard HEAD~1

# Option B: Rollback to specific commit
git log --oneline  # Find good commit hash
git reset --hard <commit-hash>

# Option C: Abandon branch, start fresh
git checkout develop
git branch -D feature/v5.7-testing
git checkout -b feature/v5.7-testing-v2
```

### Emergency Rollback to Stable
```bash
# Go back to tagged stable version
git checkout v5.6.1-stable

# Create emergency branch
git checkout -b emergency-recovery

# OR: Reset main to stable (DANGER!)
git checkout main
git reset --hard v5.6.1-stable
git push origin main --force  # ⚠️ Use with caution!
```

---

## 📝 Branch Naming Convention

**Pattern:** `<type>/<description>`

**Types:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code restructure
- `test/` - Test additions
- `chore/` - Maintenance

**Examples:**
```bash
feature/v5.7-testing
feature/atomic-design-system
fix/health-endpoint-timeout
docs/api-documentation
refactor/frontend-components
test/coverage-improvement
chore/dependency-updates
```

---

## ✅ Pre-Merge Checklist

Before merging feature → develop:
- [ ] All tests passing
- [ ] Coverage not decreased
- [ ] No console errors
- [ ] Manual testing done
- [ ] CHANGELOG.md updated
- [ ] Version bumped (if needed)

Before merging develop → main:
- [ ] All features tested together
- [ ] Performance regression check
- [ ] README.md accurate
- [ ] Tag prepared
- [ ] Rollback plan ready

---

## 🔄 Daily Workflow

### Morning
```bash
# Start day: pull latest
git checkout develop
git pull origin develop

# Create/continue feature
git checkout feature/your-branch
git merge develop  # Get latest changes
```

### During Day
```bash
# Commit frequently (small commits)
git add .
git commit -m "feat: add X functionality"

# Push to backup work
git push origin feature/your-branch
```

### End of Day
```bash
# Final commit
git add .
git commit -m "chore: WIP - implemented X, tested Y"
git push origin feature/your-branch

# Switch back to main (safe state)
git checkout main
```

---

## 🎯 Your Specific Case: V5.7 Testing

### Recommended Approach

**Option A: Conservative (Recommended)**
```bash
# 1. Tag current state
git tag v5.6.1-stable

# 2. Create feature branch
git checkout -b feature/v5.7-testing

# 3. Work on tests
# - Implement test_calculate_distance
# - Implement test_route_validity
# - Push regularly

# 4. When tests pass
git checkout main
git merge feature/v5.7-testing
git tag v5.7.0
git push origin main --tags
```

**Option B: Aggressive (If confident)**
```bash
# 1. Tag current
git tag v5.6.1-before-testing

# 2. Work directly on develop
git checkout -b develop
# Make changes, test, commit

# 3. Merge to main when ready
git checkout main
git merge develop
```

**Option C: Multiple Features**
```bash
# Create separate branches per feature
git checkout -b feature/implement-tests
git checkout -b feature/design-rules
git checkout -b feature/github-actions

# Merge one by one to develop
# Test each integration
# Final merge to main
```

---

## 🚨 Common Mistakes to Avoid

❌ **DON'T:** Commit directly to main  
✅ **DO:** Always use feature branches

❌ **DON'T:** Force push to main  
✅ **DO:** Force push only to your feature branch

❌ **DON'T:** Delete branches before confirming merge  
✅ **DO:** Keep branches until release is stable

❌ **DON'T:** Merge without testing  
✅ **DO:** Run full test suite before merge

---

## 💡 Pro Tips

1. **Commit Often:** Small commits easier to rollback
2. **Descriptive Messages:** Future you will thank you
3. **Push Daily:** GitHub is your backup
4. **Tag Milestones:** Easy to find stable points
5. **Delete Merged Branches:** Keep repo clean

---

## 📊 Success Metrics

**Week 1:**
- ✅ 3+ feature branches created
- ✅ 0 direct commits to main
- ✅ 10+ tagged commits

**Month 1:**
- ✅ Clean git history
- ✅ Easy rollback demonstrated
- ✅ Team-ready workflow

---

**Ready to start?** Run the commands below! 🚀

```bash
# Tag current stable
git tag v5.6.1-stable -m "Stable before V5.7 work"
git push origin main --tags

# Create feature branch
git checkout -b feature/v5.7-testing

# Verify
git branch  # Should show * feature/v5.7-testing
```
