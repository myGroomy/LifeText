# GitHub Setup & Deployment Guide

**Status**: Ready for GitHub Push  
**Repository Structure**: Organized for CI/CD  
**CI/CD Pipelines**: GitHub Actions configured

---

## 📋 Pre-Push Checklist

Before pushing to GitHub, ensure:

- [ ] `.gitignore` is properly configured
- [ ] No secrets in code (API keys, passwords, tokens)
- [ ] All documentation in `doc/` folder
- [ ] CI/CD workflows in `.github/workflows/`
- [ ] Local `.env` not committed

---

## 🚀 Setup Instructions

### Step 1: Create GitHub Repository

```bash
# Go to https://github.com/new
# Create repository: LifeText
# Do NOT initialize with README (we have one)
# Choose MIT License (or your preferred license)
```

### Step 2: Add Remote & Push

```bash
cd LifeText

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/LifeText.git

# Rename branch to main (if needed)
git branch -M main

# Initial commit
git commit -m "Initial commit: LifeText MVP with Phase 5 spec

- Phase 0-4 complete: ASR, post-processing, intelligence, chat
- Model-agnostic LLM support (any provider)
- Comprehensive documentation in doc/ folder
- CI/CD pipelines (GitHub Actions)
- Production roadmap (Phase 5 tasks)
"

# Push to GitHub
git push -u origin main
```

### Step 3: Configure GitHub Settings

#### Protect Main Branch
1. Go to Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - "Require a pull request before merging"
   - "Require status checks to pass before merging"
   - Select workflows: `Tests`, `Security & Quality`

#### Enable CI/CD
1. Go to Actions → Enable GitHub Actions
2. Workflows auto-enable:
   - `test.yml` - Runs on every push/PR
   - `security.yml` - Security checks
   - `docker.yml` - Build Docker image

#### Configure Secrets (Optional)
1. Go to Settings → Secrets and variables → Actions
2. Add secrets (for automated deployments):
   - `DOCKER_REGISTRY_PASSWORD` (if using Docker Hub)
   - `AWS_ACCESS_KEY_ID` (if using AWS)
   - `AWS_SECRET_ACCESS_KEY`
   - `SENTRY_DSN` (if using Sentry)

---

## 📁 Repository Structure

```
LifeText/
├── .github/
│   ├── workflows/              ← CI/CD Pipelines
│   │   ├── test.yml           ← Run tests on push
│   │   ├── security.yml       ← Security checks
│   │   └── docker.yml         ← Build Docker image
│   └── pull_request_template.md
│
├── ci/                         ← CI/CD Scripts
│   ├── lint.sh
│   ├── test.sh
│   └── security.sh
│
├── doc/                        ← All Documentation
│   ├── 00_START_HERE.md       ← Entry point
│   ├── QUICK_START.md
│   ├── COMPLETE_SETUP_GUIDE.md
│   ├── LLM_CONFIGURATION.md
│   ├── FINAL_CHECKLIST.md     ← MVP Status
│   ├── PHASE_5_*.md           ← Production Spec
│   └── ... (20+ docs)
│
├── src/                        ← Source Code
│   ├── main.py                ← FastAPI app
│   ├── config.py              ← Configuration
│   ├── db.py                  ← Database setup
│   ├── models/                ← Data models
│   ├── services/              ← Business logic
│   ├── routers/               ← API endpoints
│   └── workers/               ← Async tasks
│
├── tests/                      ← Tests
│   ├── test_api.py
│   └── test_asr.py
│
├── prompts/                    ← System prompts
│   ├── system_transcription.txt
│   ├── system_meeting_notes.txt
│   ├── system_interview.txt
│   └── system_qa_chat.txt
│
├── scripts/                    ← Utilities
│   └── init_db.py
│
├── .env.example               ← Configuration template
├── .gitignore                 ← Git ignore rules
├── Dockerfile                 ← API container
├── docker-compose.yml         ← Local orchestration
├── Makefile                   ← Development tasks
├── requirements.txt           ← Dependencies
├── pytest.ini                 ← Test config
├── README.md                  ← Main readme
└── GITHUB_SETUP.md            ← This file
```

---

## 🔄 CI/CD Workflows

### test.yml - Run on Every Push
```
Triggers: push to main/develop, pull requests
Steps:
  1. Lint code (flake8, pylint)
  2. Type check (mypy)
  3. Run tests (pytest with coverage)
  4. Upload coverage to Codecov
```

### security.yml - Security Checks
```
Triggers: push to main/develop, pull requests
Steps:
  1. Scan for hardcoded secrets
  2. Security check with bandit
  3. Check dependencies for CVEs
  4. Code quality checks (black, isort)
```

### docker.yml - Docker Build & Push
```
Triggers: push to main (branches/tags)
Steps:
  1. Build Docker image
  2. Push to ghcr.io (GitHub Container Registry)
  3. Tag with branch/version/sha
```

---

## 🧪 Local Testing Before Push

```bash
# Install dependencies
make install

# Run tests
make test

# Run linting
make lint

# Run security checks
make security

# Build Docker image
make docker-build
```

---

## 📝 Commit Message Convention

**Format**: `<type>: <subject>`

```
feat: Add API key authentication
fix: Resolve connection pool leak
docs: Update Phase 5 documentation
chore: Update dependencies
ci: Add GitHub Actions workflow
test: Add authentication tests
```

**Examples**:
```
feat: Implement Sentry integration for error tracking

- Added Sentry SDK initialization
- Error context includes job_id and user
- Sensitive data redacted before sending
- Tests added for error scenarios

Closes #123
```

---

## 🚀 Making Your First PR

1. Create feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes and commit:
   ```bash
   git add .
   git commit -m "feat: Add my feature"
   ```

3. Push to GitHub:
   ```bash
   git push origin feature/my-feature
   ```

4. Open Pull Request on GitHub:
   - Fill out PR template
   - Reference related issues
   - Wait for CI/CD checks to pass

5. After approval, merge to main

---

## 📊 Monitoring Workflows

### GitHub Actions Dashboard
- Go to repository → Actions
- See all workflow runs
- Click run to see logs
- View failed step details

### Badge in README
Add to your README.md to show CI/CD status:

```markdown
[![Tests](https://github.com/YOUR_USERNAME/LifeText/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/LifeText/actions)
[![Security](https://github.com/YOUR_USERNAME/LifeText/actions/workflows/security.yml/badge.svg)](https://github.com/YOUR_USERNAME/LifeText/actions)
```

---

## 🔐 Secrets Management

### Never Commit
- `.env` files with real credentials
- API keys (OpenAI, Anthropic, etc.)
- Database passwords
- AWS credentials
- Any sensitive data

### Use GitHub Secrets
For automated deployments, use GitHub Secrets:
```yaml
# In workflow
- name: Deploy
  env:
    API_KEY: ${{ secrets.API_KEY }}
```

### Local Development
- Use `.env` file (in .gitignore)
- Copy from `.env.example`
- Fill with your credentials
- Never commit `.env`

---

## 🐳 Docker Registry

### GitHub Container Registry (GHCR)

Images automatically pushed to:
```
ghcr.io/your-username/lifetext:latest
ghcr.io/your-username/lifetext:v1.0.0
```

#### Pull Image
```bash
docker pull ghcr.io/your-username/lifetext:latest
docker run ghcr.io/your-username/lifetext:latest
```

#### If Private Repository
```bash
# Generate GitHub token with packages scope
# Then login:
echo YOUR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# Pull private image
docker pull ghcr.io/your-username/lifetext:latest
```

---

## 📈 Next Steps After Initial Push

### Immediate
1. ✅ Push to GitHub
2. ✅ Enable branch protection
3. ✅ Verify CI/CD runs
4. ✅ Add repository topics/description

### Short-term (Phase 5)
1. Create `develop` branch for development
2. Start Phase 5 tasks on feature branches
3. Create PRs for review
4. Merge to develop after approval
5. Merge develop to main for releases

### Medium-term (Phase 6)
1. Set up Codecov for coverage tracking
2. Add GitHub Issue templates
3. Set up Dependabot for dependency updates
4. Consider GitHub Projects for task tracking

---

## 🎯 GitHub Best Practices

### Branch Strategy
```
main                    ← Production releases (stable)
  ↑
develop                 ← Development integration
  ↑
feature/*               ← Individual features
hotfix/*                ← Emergency fixes
```

### PR Review Checklist
- [ ] Passes all CI/CD checks
- [ ] Code reviewed for quality
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No security issues
- [ ] Approved by reviewer

### Releases
```bash
# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag (triggers docker.yml)
git push origin v1.0.0
```

---

## 📚 Useful Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)

---

## 🔗 Quick Links

After pushing to GitHub:

- Repository: `https://github.com/YOUR_USERNAME/LifeText`
- Actions: `https://github.com/YOUR_USERNAME/LifeText/actions`
- Issues: `https://github.com/YOUR_USERNAME/LifeText/issues`
- Releases: `https://github.com/YOUR_USERNAME/LifeText/releases`
- Container Registry: `https://github.com/YOUR_USERNAME/LifeText/pkgs/container/LifeText`

---

## 📞 Troubleshooting

### CI/CD Failing?
1. Check GitHub Actions logs
2. Run locally: `make test`, `make lint`, `make security`
3. Fix issues locally
4. Push again

### Docker Build Failing?
1. Check `docker build . -f Dockerfile`
2. Verify all dependencies in `requirements.txt`
3. Check for secrets in Dockerfile

### Secret Leaked?
1. Immediately rotate the credential
2. Run `detect-secrets baseline`
3. Update `.secrets.baseline` in git
4. Never commit the secret again

---

## ✅ Completion Checklist

Before declaring "Ready for Production":

- [ ] Repository pushed to GitHub
- [ ] CI/CD workflows passing
- [ ] Branch protection enabled
- [ ] Documentation complete
- [ ] No secrets in git history
- [ ] Docker image building successfully
- [ ] Tests passing with >80% coverage
- [ ] Security checks passing
- [ ] Code reviewed
- [ ] README updated with GitHub links

---

**Repository is now ready for collaborative development and production deployment!** 🚀

