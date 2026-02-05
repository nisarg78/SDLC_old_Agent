"""
Backend Agent
Generates complete backend application code based on architecture design.
"""

import json
from typing import Dict


class BackendAgent:
    """
    Generates backend code including:
    - API routes and controllers
    - Database models
    - Business logic
    - Authentication
    - Tests
    """
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.claude_api_key = config.ANTHROPIC_API_KEY
    
    async def generate(self, architecture: Dict) -> Dict:
        """Generate complete backend code"""
        self.logger.info("Backend Agent: Generating backend code...")
        
        tech = architecture["backend"]["technology"]
        
        if "node" in tech.lower():
            return await self._generate_nodejs_backend(architecture)
        elif "python" in tech.lower():
            return await self._generate_python_backend(architecture)
        else:
            # Default to Node.js
            return await self._generate_nodejs_backend(architecture)
    
    async def _generate_nodejs_backend(self, architecture: Dict) -> Dict:
        """Generate Node.js/Express backend"""
        self.logger.info("Backend Agent: Generating Node.js backend...")
        
        files = {}
        
        # package.json
        files["package.json"] = self._generate_package_json(architecture)
        
        # Main server file
        files["server.js"] = self._generate_server_js(architecture)
        
        # Routes
        files["routes/index.js"] = self._generate_routes(architecture)
        
        # Controllers
        for endpoint in architecture["api_endpoints"][:5]:  # Limit to 5 resources
            resource = endpoint["path"].split("/")[2] if len(endpoint["path"].split("/")) > 2 else "items"
            if resource and resource not in ["health"]:
                files[f"controllers/{resource}Controller.js"] = self._generate_controller(resource, architecture)
        
        # Models
        for table in architecture["database"]["tables"][:5]:
            files[f"models/{table['name'][:-1]}.js"] = self._generate_model(table, architecture)
        
        # Database config
        files["config/database.js"] = self._generate_db_config(architecture)
        
        # Middleware
        files["middleware/errorHandler.js"] = self._generate_error_handler()
        files["middleware/auth.js"] = self._generate_auth_middleware(architecture)
        
        # Environment example
        files[".env.example"] = self._generate_env_example(architecture)
        
        # README
        files["README.md"] = self._generate_backend_readme(architecture)
        
        return {
            "files": files,
            "entry_point": "server.js",
            "technology": "Node.js + Express",
            "install_command": "npm install",
            "start_command": "npm start"
        }
    
    def _generate_package_json(self, architecture: Dict) -> str:
        """Generate package.json"""
        has_auth = architecture["tech_stack"].get("authentication") == "JWT"
        
        dependencies = {
            "express": "^4.18.2",
            "cors": "^2.8.5",
            "dotenv": "^16.0.3",
            "pg": "^8.11.0",
            "helmet": "^7.1.0"
        }
        
        if has_auth:
            dependencies.update({
                "jsonwebtoken": "^9.0.2",
                "bcryptjs": "^2.4.3"
            })
        
        package = {
            "name": "backend-app",
            "version": "1.0.0",
            "description": "Auto-generated backend application",
            "main": "server.js",
            "scripts": {
                "start": "node server.js",
                "dev": "nodemon server.js",
                "test": "jest"
            },
            "dependencies": dependencies,
            "devDependencies": {
                "nodemon": "^3.0.1",
                "jest": "^29.7.0"
            }
        }
        
        return json.dumps(package, indent=2)
    
    def _generate_server_js(self, architecture: Dict) -> str:
        """Generate main server.js file"""
        has_auth = architecture["tech_stack"].get("authentication") == "JWT"
        
        return f"""const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();

const routes = require('./routes');
const errorHandler = require('./middleware/errorHandler');
{"const auth = require('./middleware/auth');" if has_auth else ""}

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({{ extended: true }}));

// Health check
app.get('/health', (req, res) => {{
  res.json({{ status: 'healthy', timestamp: new Date().toISOString() }});
}});

// API Routes
app.use('/api', routes);

// Error handling
app.use(errorHandler);

// Start server
app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});

module.exports = app;
"""
    
    def _generate_routes(self, architecture: Dict) -> str:
        """Generate main routes file"""
        endpoints = architecture["api_endpoints"]
        
        # Get unique resources
        resources = set()
        for endpoint in endpoints:
            parts = endpoint["path"].split("/")
            if len(parts) > 2 and parts[2] not in ["health"]:
                resources.add(parts[2])
        
        routes = "const express = require('express');\nconst router = express.Router();\n\n"
        
        for resource in list(resources)[:5]:  # Limit to 5
            routes += f"const {resource}Controller = require('../controllers/{resource}Controller');\n"
        
        routes += "\n// Routes\n"
        
        for resource in list(resources)[:5]:
            routes += f"""
router.get('/{resource}', {resource}Controller.getAll);
router.get('/{resource}/:id', {resource}Controller.getById);
router.post('/{resource}', {resource}Controller.create);
router.put('/{resource}/:id', {resource}Controller.update);
router.delete('/{resource}/:id', {resource}Controller.delete);
"""
        
        routes += "\nmodule.exports = router;\n"
        
        return routes
    
    def _generate_controller(self, resource: str, architecture: Dict) -> str:
        """Generate a controller file"""
        singular = resource[:-1] if resource.endswith('s') else resource
        model_name = singular.capitalize()
        
        return f"""const db = require('../config/database');

exports.getAll = async (req, res, next) => {{
  try {{
    const result = await db.query('SELECT * FROM {resource} ORDER BY created_at DESC');
    res.json({{ success: true, data: result.rows }});
  }} catch (error) {{
    next(error);
  }}
}};

exports.getById = async (req, res, next) => {{
  try {{
    const {{ id }} = req.params;
    const result = await db.query('SELECT * FROM {resource} WHERE id = $1', [id]);
    
    if (result.rows.length === 0) {{
      return res.status(404).json({{ success: false, message: '{model_name} not found' }});
    }}
    
    res.json({{ success: true, data: result.rows[0] }});
  }} catch (error) {{
    next(error);
  }}
}};

exports.create = async (req, res, next) => {{
  try {{
    const data = req.body;
    const columns = Object.keys(data).join(', ');
    const values = Object.values(data);
    const placeholders = values.map((_, i) => `$${{i + 1}}`).join(', ');
    
    const result = await db.query(
      `INSERT INTO {resource} (${{columns}}) VALUES (${{placeholders}}) RETURNING *`,
      values
    );
    
    res.status(201).json({{ success: true, data: result.rows[0] }});
  }} catch (error) {{
    next(error);
  }}
}};

exports.update = async (req, res, next) => {{
  try {{
    const {{ id }} = req.params;
    const data = req.body;
    
    const updates = Object.keys(data)
      .map((key, i) => `${{key}} = $${{i + 2}}`)
      .join(', ');
    
    const values = [id, ...Object.values(data)];
    
    const result = await db.query(
      `UPDATE {resource} SET ${{updates}}, updated_at = NOW() WHERE id = $1 RETURNING *`,
      values
    );
    
    if (result.rows.length === 0) {{
      return res.status(404).json({{ success: false, message: '{model_name} not found' }});
    }}
    
    res.json({{ success: true, data: result.rows[0] }});
  }} catch (error) {{
    next(error);
  }}
}};

exports.delete = async (req, res, next) => {{
  try {{
    const {{ id }} = req.params;
    const result = await db.query('DELETE FROM {resource} WHERE id = $1 RETURNING id', [id]);
    
    if (result.rows.length === 0) {{
      return res.status(404).json({{ success: false, message: '{model_name} not found' }});
    }}
    
    res.json({{ success: true, message: '{model_name} deleted successfully' }});
  }} catch (error) {{
    next(error);
  }}
}};
"""
    
    def _generate_model(self, table: Dict, architecture: Dict) -> str:
        """Generate a model file"""
        model_name = table["name"][:-1].capitalize()
        
        return f"""const db = require('../config/database');

class {model_name} {{
  static async findAll() {{
    const result = await db.query('SELECT * FROM {table["name"]}');
    return result.rows;
  }}
  
  static async findById(id) {{
    const result = await db.query('SELECT * FROM {table["name"]} WHERE id = $1', [id]);
    return result.rows[0];
  }}
  
  static async create(data) {{
    const columns = Object.keys(data).join(', ');
    const values = Object.values(data);
    const placeholders = values.map((_, i) => `$${{i + 1}}`).join(', ');
    
    const result = await db.query(
      `INSERT INTO {table["name"]} (${{columns}}) VALUES (${{placeholders}}) RETURNING *`,
      values
    );
    
    return result.rows[0];
  }}
  
  static async update(id, data) {{
    const updates = Object.keys(data)
      .map((key, i) => `${{key}} = $${{i + 2}}`)
      .join(', ');
    
    const values = [id, ...Object.values(data)];
    
    const result = await db.query(
      `UPDATE {table["name"]} SET ${{updates}}, updated_at = NOW() WHERE id = $1 RETURNING *`,
      values
    );
    
    return result.rows[0];
  }}
  
  static async delete(id) {{
    await db.query('DELETE FROM {table["name"]} WHERE id = $1', [id]);
    return true;
  }}
}}

module.exports = {model_name};
"""
    
    def _generate_db_config(self, architecture: Dict) -> str:
        """Generate database configuration"""
        return """const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'app_db',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'password',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

module.exports = {
  query: (text, params) => pool.query(text, params)
};
"""
    
    def _generate_error_handler(self) -> str:
        """Generate error handling middleware"""
        return """module.exports = (err, req, res, next) => {
  console.error('Error:', err);
  
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';
  
  res.status(statusCode).json({
    success: false,
    error: {
      message,
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    }
  });
};
"""
    
    def _generate_auth_middleware(self, architecture: Dict) -> str:
        """Generate authentication middleware"""
        if architecture["tech_stack"].get("authentication") != "JWT":
            return "// No authentication configured\n"
        
        return """const jwt = require('jsonwebtoken');

const auth = async (req, res, next) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      throw new Error('No token provided');
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ success: false, message: 'Authentication required' });
  }
};

module.exports = auth;
"""
    
    def _generate_env_example(self, architecture: Dict) -> str:
        """Generate .env.example file"""
        env = """# Server
PORT=3000
NODE_ENV=development

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=app_db
DB_USER=postgres
DB_PASSWORD=password
"""
        
        if architecture["tech_stack"].get("authentication") == "JWT":
            env += "\n# JWT\nJWT_SECRET=your-secret-key-change-in-production\n"
        
        return env
    
    def _generate_backend_readme(self, architecture: Dict) -> str:
        """Generate backend README"""
        return f"""# Backend Application

Auto-generated backend using {architecture["backend"]["technology"]}

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Run migrations:
```bash
# Create database schema
# SQL files would be in migrations/
```

4. Start server:
```bash
npm start
# or for development:
npm run dev
```

## API Endpoints

{self._format_endpoints(architecture["api_endpoints"])}

## Technology Stack

- Runtime: Node.js
- Framework: Express
- Database: {architecture["database"]["type"]}
- Authentication: {architecture["tech_stack"].get("authentication", "None")}
"""
    
    def _format_endpoints(self, endpoints: List[Dict]) -> str:
        """Format API endpoints for documentation"""
        formatted = ""
        for endpoint in endpoints[:10]:  # Limit display
            formatted += f"- `{endpoint['method']} {endpoint['path']}` - {endpoint['description']}\n"
        return formatted
    
    async def _generate_python_backend(self, architecture: Dict) -> Dict:
        """Generate Python/FastAPI backend"""
        self.logger.info("Backend Agent: Python backend generation not fully implemented, using Node.js")
        return await self._generate_nodejs_backend(architecture)
