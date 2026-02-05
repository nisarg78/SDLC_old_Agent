# 🚀 QUICKSTART GUIDE

Get your full-stack application built in **5 minutes with 3 commands**.

## Prerequisites Check ✓

```bash
# Check Python version (need 3.8+)
python --version

# Check pip
pip --version
```

## Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

## Step 2: Set Your API Key (10 seconds)

Get your key from: https://console.anthropic.com/

```bash
# Linux/Mac
export ANTHROPIC_API_KEY='sk-ant-your-key-here'

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

## Step 3: Run It! (8-10 minutes, zero intervention)

```bash
python main.py example_requirements.md
```

## What Happens Next

You'll see real-time progress like this:

```
================================================================================
AUTONOMOUS SDLC MULTI-AGENT FACTORY
================================================================================

Requirements: example_requirements.md
Output directory: ./output

Starting autonomous build process...

[PHASE 1] REQUIREMENTS ANALYSIS
Analyst: Processing requirements document...
Analyst: Identified 12 features
Analyst: Extracted 8 user stories

[PHASE 2] ARCHITECTURE DESIGN
Architect: Designing system architecture...
Architect Decision: Backend=Node.js, Frontend=React, DB=PostgreSQL

[PHASE 3] BACKEND DEVELOPMENT
Backend Agent: Generating backend code...
Backend code generated: 15 files

[PHASE 4] FRONTEND DEVELOPMENT
Frontend Agent: Generating frontend code...
Frontend code generated: 12 files

[PHASE 5] INTEGRATION & TESTING
QA Agent: Running tests...
Tests completed: 14/14 passed

[PHASE 7] FINAL VALIDATION
Validator Agent: Performing final checks...
✓ Validation PASSED

[PHASE 8] PACKAGING
Packaging final deliverables...

================================================================================
BUILD COMPLETE!
================================================================================
```

## Step 4: Run Your Application

### Backend
```bash
cd output/backend
npm install
npm start
```

Backend running at: http://localhost:3000

### Frontend (in new terminal)
```bash
cd output/frontend
npm install
npm start
```

Frontend running at: http://localhost:3001

## 🎉 That's It!

Your complete application is now running with:
- ✅ RESTful API backend
- ✅ React frontend
- ✅ Database models
- ✅ Authentication (if specified)
- ✅ CRUD operations
- ✅ Error handling
- ✅ Tests
- ✅ Documentation

## What You Get

```
output/
├── backend/           # Complete Node.js backend
├── frontend/          # Complete React frontend
├── deployment/        # AWS deployment scripts
├── docs/              # Technical docs
├── decisions.log      # All decisions made
└── final_report.json  # Build summary
```

## Next Steps

1. **Review Code:**
   ```bash
   cat output/decisions.log  # See all autonomous decisions
   ```

2. **Customize:**
   - Edit components in `output/frontend/src/components/`
   - Modify API routes in `output/backend/routes/`
   - Adjust styles in `output/frontend/src/*.css`

3. **Deploy:**
   ```bash
   cd output/deployment
   ./deploy.sh  # Requires AWS CLI configured
   ```

## Troubleshooting

**API key error?**
```bash
export ANTHROPIC_API_KEY='your-key'
python main.py example_requirements.md
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**Tests failing?**
- System will auto-heal (up to 5 attempts)
- Check `output/state.json` for details
- Review `output/factory.log` for errors

## Create Your Own App

1. Create `my_app_requirements.md`:
   ```markdown
   # My Amazing App
   
   ## Features
   - Feature 1
   - Feature 2
   - Feature 3
   
   ## Requirements
   - Requirement 1
   - Requirement 2
   ```

2. Run:
   ```bash
   python main.py my_app_requirements.md
   ```

3. Wait 8-10 minutes ☕

4. Launch your app! 🚀

---

**Questions?** Read the full [README.md](README.md)
