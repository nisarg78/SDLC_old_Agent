# Autonomous SDLC Multi-Agent System

![Status](https://img.shields.io/badge/status-production--ready-green)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

**Transform requirements documents into production-ready full-stack applications with ZERO human intervention.**

## 🚀 Overview

This is a fully autonomous Software Development Life Cycle (SDLC) factory that uses multiple AI agents to:

1. **Analyze** requirements documents
2. **Design** system architecture with autonomous decision-making
3. **Generate** complete backend code (Node.js/Python)
4. **Generate** complete frontend code (React)
5. **Test** the generated code automatically
6. **Self-heal** when tests fail (up to 5 attempts)
7. **Validate** final output quality
8. **Package** everything for deployment

### Key Features

✅ **Zero Human Intervention** - Set it and forget it  
✅ **Multi-Agent Architecture** - 8 specialized AI agents working together  
✅ **Self-Healing** - Automatically fixes bugs and test failures  
✅ **Decision Logging** - All architectural decisions documented  
✅ **Production-Ready Code** - Complete with error handling, validation, and security  
✅ **AWS Deployment Scripts** - CDK/Terraform code included  
✅ **Full Test Suite** - Automated QA with comprehensive checks  

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SUPERVISOR AGENT                            │
│              (Orchestrates workflow & transitions)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
    ┌─────────────────┐          ┌─────────────────┐
    │ ANALYST AGENT   │          │ ARCHITECT AGENT │
    │ Parse & Structure│         │ Design System   │
    └─────────────────┘          └─────────────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
            ┌────────────────────────────────┐
            │  BACKEND AGENT │ FRONTEND AGENT│
            │  Generate Code │ Generate Code │
            └────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   QA AGENT      │
                    │   Run Tests     │
                    └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ Tests Pass?       │
                    └─────────┬─────────┘
                        NO │       │ YES
                           ▼       ▼
                ┌─────────────┐  ┌─────────────┐
                │HEALER AGENT │  │ VALIDATOR   │
                │Self-Correct │  │Final Checks │
                └─────────────┘  └─────────────┘
                       │              │
                       └──────┬───────┘
                              ▼
                    ┌─────────────────┐
                    │  FINAL OUTPUT   │
                    │  Full App Code  │
                    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- Anthropic API key (Claude)
- 1GB+ free disk space

## 🔧 Installation

### 1. Clone or Download

```bash
# Option 1: If you have git
git clone <repository-url>
cd autonomous_sdlc

# Option 2: If you downloaded the zip
unzip autonomous_sdlc.zip
cd autonomous_sdlc
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up API Key

```bash
# Linux/Mac
export ANTHROPIC_API_KEY='your-api-key-here'

# Windows PowerShell
$env:ANTHROPIC_API_KEY='your-api-key-here'

# Windows CMD
set ANTHROPIC_API_KEY=your-api-key-here
```

**Get your API key:** https://console.anthropic.com/

## 🎯 Quick Start

### Step 1: Create a Requirements Document

Create a file `my_requirements.md`:

```markdown
# Task Management Application

## Overview
Build a task management web application where users can create, edit, and track tasks.

## Features
- User authentication and login
- Create, read, update, delete tasks
- Mark tasks as complete/incomplete
- Filter tasks by status
- Simple dashboard showing task statistics

## Requirements
- RESTful API backend
- React frontend
- PostgreSQL database
- User should be able to register and login
- Tasks should have: title, description, status, due date
```

### Step 2: Run the System

```bash
python main.py my_requirements.md
```

### Step 3: Watch the Magic ✨

The system will:
1. Analyze your requirements ⏱️ ~30 seconds
2. Design architecture ⏱️ ~45 seconds
3. Generate backend code ⏱️ ~2 minutes
4. Generate frontend code ⏱️ ~2 minutes
5. Run tests ⏱️ ~1 minute
6. Self-heal if needed ⏱️ ~2 minutes (if tests fail)
7. Validate & package ⏱️ ~30 seconds

**Total time: ~8-10 minutes** (zero human intervention)

### Step 4: Access Your Application

```bash
cd output/

# View the generated files
ls -la

# Read the decisions log
cat decisions.log

# Check final report
cat final_report.json

# Install and run backend
cd backend
npm install
npm start

# In another terminal, install and run frontend
cd output/frontend
npm install
npm start
```

Your app is now running! 🎉
- Backend: http://localhost:3000
- Frontend: http://localhost:3001

## 📂 Output Structure

```
output/
├── backend/                    # Complete Node.js backend
│   ├── server.js              # Main server file
│   ├── package.json           # Dependencies
│   ├── routes/                # API routes
│   ├── controllers/           # Business logic
│   ├── models/                # Database models
│   ├── middleware/            # Authentication, errors
│   ├── config/                # Database config
│   └── README.md              # Backend docs
│
├── frontend/                   # Complete React frontend
│   ├── package.json           # Dependencies
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── index.js
│   │   ├── App.js             # Main app component
│   │   ├── components/        # React components
│   │   └── services/          # API client
│   └── README.md              # Frontend docs
│
├── deployment/                 # AWS deployment scripts
│   ├── cdk_app.py             # AWS CDK code
│   └── deploy.sh              # Deployment script
│
├── docs/                       # Technical documentation
│   └── ARCHITECTURE.md
│
├── decisions.log               # All autonomous decisions
├── state.json                  # Build state tracker
├── final_report.json           # Summary report
└── README.md                   # Project README
```

## 🧠 How It Works

### 1. Analyst Agent
- Parses requirements document
- Uses Claude API to understand intent
- Structures requirements into features, user stories, constraints
- Makes assumptions when requirements are vague

### 2. Architect Agent
- **Autonomous Decisions:**
  - Chooses tech stack (Node.js vs Python, React vs Vue)
  - Designs database schema
  - Defines API endpoints
  - Plans deployment architecture
- **Decision Criteria:**
  - Complexity of requirements
  - Presence of real-time features
  - Number of entities
  - Authentication needs

### 3. Backend Agent
- Generates complete backend:
  - Express/FastAPI server
  - RESTful API routes
  - Database models
  - Authentication middleware
  - Error handling
  - Input validation
- Language-agnostic (supports Node.js and Python)

### 4. Frontend Agent
- Generates complete React app:
  - Component hierarchy
  - State management
  - API integration
  - Routing
  - Form handling
  - Error states

### 5. QA Agent
- Runs comprehensive tests:
  - Syntax validation
  - File structure checks
  - API endpoint verification
  - Component structure validation
  - Integration checks
- Provides detailed failure reports

### 6. Healer Agent (Self-Correction)
- **Triggers automatically** on test failures
- **Max 5 attempts** per bug
- **Fixes:**
  - Missing dependencies
  - Syntax errors
  - Missing files
  - Configuration issues
- **Logs all fixes** for transparency

### 7. Validator Agent
- Final quality checks:
  - Security (SQL injection, XSS, hardcoded secrets)
  - Performance (pagination, indexing)
  - Best practices (error handling, validation)
  - Documentation quality
- Issues warnings vs critical errors

### 8. Supervisor Agent
- Orchestrates entire workflow
- Manages state transitions
- Decides when to trigger healing
- Makes architectural decisions when ambiguous
- Maintains decision log

## ⚙️ Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your-api-key

# Optional
CLAUDE_MODEL=claude-sonnet-4-20250514  # Default
MAX_TOKENS=4000                         # Token limit per API call
MAX_HEAL_ATTEMPTS=5                     # Self-healing attempts
OUTPUT_DIR=./output                     # Output directory
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING
```

### Advanced Configuration

Create `.env` file:

```ini
ANTHROPIC_API_KEY=your-key-here
CLAUDE_MODEL=claude-sonnet-4-20250514
MAX_HEAL_ATTEMPTS=5
LOG_LEVEL=INFO
DEFAULT_DB_TYPE=postgresql
AWS_REGION=us-east-1
```

## 📊 Decision Logging

All autonomous decisions are logged in `decisions.log`:

```
[2024-01-15T10:30:45] ARCHITECTURE_DESIGN
Decision: Backend: Node.js with Express
Rationale: Standard choice for web APIs, large ecosystem
Alternatives: Python/FastAPI, Go/Gin, Java/Spring Boot

[2024-01-15T10:31:22] ARCHITECTURE_DESIGN
Decision: Database: PostgreSQL
Rationale: Relational data with complex relationships
Alternatives: MySQL, MongoDB, DynamoDB
```

## 🔍 Example Requirements Documents

### Example 1: E-commerce Site

```markdown
# E-commerce Platform

## Features
- Product catalog with search and filtering
- Shopping cart
- User accounts
- Order history
- Admin panel for product management

## Requirements
- Product images and descriptions
- Checkout process
- Payment integration (prepare structure, no actual payment)
- Email notifications for orders
```

### Example 2: Blog Platform

```markdown
# Blog Platform

## Overview
Create a blogging platform with posts, comments, and tags.

## Features
- Create, edit, delete blog posts
- Comment on posts
- Tag posts with categories
- User profiles
- Markdown support for posts

## Technical Requirements
- SEO-friendly URLs
- Responsive design
- Image uploads for post headers
```

## 🐛 Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"

```bash
export ANTHROPIC_API_KEY='sk-ant-...'
```

### Issue: "Module not found"

```bash
pip install -r requirements.txt
```

### Issue: "Permission denied" on deploy.sh

```bash
chmod +x output/deployment/deploy.sh
```

### Issue: Tests keep failing

- Check `state.json` to see which tests are failing
- Review `decisions.log` for what the Healer attempted
- The system tries 5 times before moving forward
- Some failures are logged as warnings and don't block progress

## 🚀 Deployment (One Command)

After generation completes:

```bash
cd output/deployment
./deploy.sh
```

This will:
1. Deploy backend to AWS Lambda
2. Deploy frontend to S3 + CloudFront
3. Set up RDS PostgreSQL
4. Configure API Gateway
5. Output live URLs

**Note:** Requires AWS CLI configured with credentials.

## 📈 Performance

- **Simple app (3-5 features):** ~5 minutes
- **Medium app (8-12 features):** ~8 minutes
- **Complex app (15+ features):** ~12 minutes

Self-healing adds ~2 minutes per failure (max 5 attempts).

## 🔐 Security

The system generates code with:
- ✅ Parameterized SQL queries (no SQL injection)
- ✅ CORS configuration
- ✅ Helmet.js security headers
- ✅ JWT authentication (when needed)
- ✅ Input validation
- ✅ Error handling (no information leakage)

## 🛠️ Extending the System

### Add New Agent

```python
# agents/custom_agent.py
class CustomAgent:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    async def process(self, data):
        # Your logic here
        return result
```

### Modify Decision Logic

Edit `agents/architect.py` → `_select_tech_stack()` method

### Add New Tech Stack

Edit `agents/backend_agent.py` → Add new `_generate_*_backend()` method

## 📚 API Reference

### Main Class

```python
from main import AutonomousSDLCFactory

factory = AutonomousSDLCFactory(
    requirements_file="requirements.md",
    output_dir="./output"
)

result = await factory.execute()
# Returns: {status, backend, frontend, validation, next_steps}
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional tech stacks (Vue, Angular, Svelte)
- More backend languages (Go, Ruby, Java)
- Enhanced testing strategies
- Better error recovery
- UI for monitoring progress

## 📝 License

MIT License - use freely for commercial or personal projects

## 🙏 Acknowledgments
- Nisarg Zaveri Dev
- Inspired by autonomous agent systems
- Built for developers who value automation

##  Support

- **Issues:** Check `decisions.log` and `factory.log`
- **Questions:** Review this README
- **Feature Requests:** Open an issue

---

**Built with ❤️ for autonomous development**

*Last updated: 2024-01-15*
