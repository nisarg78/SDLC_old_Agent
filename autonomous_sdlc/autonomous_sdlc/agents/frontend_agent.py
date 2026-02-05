"""
Frontend Agent
Generates complete frontend application code based on architecture and backend.
"""

import json
from typing import Dict


class FrontendAgent:
    """
    Generates frontend code including:
    - React components
    - State management
    - API client
    - Routing
    - Styling
    """
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
    
    async def generate(self, architecture: Dict, backend_code: Dict) -> Dict:
        """Generate complete frontend code"""
        self.logger.info("Frontend Agent: Generating frontend code...")
        
        tech = architecture["frontend"]["technology"]
        
        if "react" in tech.lower():
            return await self._generate_react_frontend(architecture, backend_code)
        else:
            return await self._generate_react_frontend(architecture, backend_code)
    
    async def _generate_react_frontend(self, architecture: Dict, backend_code: Dict) -> Dict:
        """Generate React frontend"""
        self.logger.info("Frontend Agent: Generating React frontend...")
        
        files = {}
        
        # package.json
        files["package.json"] = self._generate_package_json(architecture)
        
        # public/index.html
        files["public/index.html"] = self._generate_index_html(architecture)
        
        # src/index.js
        files["src/index.js"] = self._generate_index_js()
        
        # src/App.js
        files["src/App.js"] = self._generate_app_js(architecture)
        
        # API client
        files["src/services/api.js"] = self._generate_api_client(architecture)
        
        # Components based on backend resources
        for endpoint in architecture["api_endpoints"][:5]:
            resource = endpoint["path"].split("/")[2] if len(endpoint["path"].split("/")) > 2 else "items"
            if resource and resource not in ["health"]:
                files[f"src/components/{resource.capitalize()}List.js"] = self._generate_list_component(resource)
                files[f"src/components/{resource.capitalize()}Form.js"] = self._generate_form_component(resource)
        
        # Styles
        files["src/App.css"] = self._generate_app_css()
        files["src/index.css"] = self._generate_index_css()
        
        # README
        files["README.md"] = self._generate_frontend_readme(architecture)
        
        return {
            "files": files,
            "entry_point": "public/index.html",
            "technology": "React",
            "install_command": "npm install",
            "start_command": "npm start"
        }
    
    def _generate_package_json(self, architecture: Dict) -> str:
        """Generate package.json for React"""
        package = {
            "name": "frontend-app",
            "version": "1.0.0",
            "description": "Auto-generated frontend application",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0",
                "axios": "^1.6.2"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "devDependencies": {
                "react-scripts": "5.0.1"
            },
            "browserslist": {
                "production": [">0.2%", "not dead", "not op_mini all"],
                "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
            }
        }
        
        return json.dumps(package, indent=2)
    
    def _generate_index_html(self, architecture: Dict) -> str:
        """Generate public/index.html"""
        project_name = architecture.get("overview", "").split(" - ")[0] or "Application"
        
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Auto-generated application" />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
"""
    
    def _generate_index_js(self) -> str:
        """Generate src/index.js"""
        return """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    
    def _generate_app_js(self, architecture: Dict) -> str:
        """Generate src/App.js"""
        endpoints = architecture["api_endpoints"]
        
        # Get unique resources
        resources = []
        for endpoint in endpoints:
            parts = endpoint["path"].split("/")
            if len(parts) > 2 and parts[2] not in ["health"] and parts[2] not in resources:
                resources.append(parts[2])
        
        imports = "\n".join([
            f"import {r.capitalize()}List from './components/{r.capitalize()}List';"
            for r in resources[:3]
        ])
        
        routes = "\n        ".join([
            f'<Route path="/{r}" element={{<{r.capitalize()}List />}} />'
            for r in resources[:3]
        ])
        
        nav_links = "\n          ".join([
            f'<Link to="/{r}" className="nav-link">{r.capitalize()}</Link>'
            for r in resources[:3]
        ])
        
        return f"""import React from 'react';
import {{ BrowserRouter as Router, Routes, Route, Link }} from 'react-router-dom';
import './App.css';
{imports}

function Home() {{
  return (
    <div className="home">
      <h1>Welcome to Your Application</h1>
      <p>Auto-generated full-stack application</p>
    </div>
  );
}}

function App() {{
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">App</div>
          <div className="nav-links">
            <Link to="/" className="nav-link">Home</Link>
            {nav_links}
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={{<Home />}} />
            {routes}
          </Routes>
        </main>
      </div>
    </Router>
  );
}}

export default App;
"""
    
    def _generate_api_client(self, architecture: Dict) -> str:
        """Generate API client service"""
        return """import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Generic CRUD operations
export const apiService = {
  get: (endpoint) => api.get(endpoint),
  post: (endpoint, data) => api.post(endpoint, data),
  put: (endpoint, data) => api.put(endpoint, data),
  delete: (endpoint) => api.delete(endpoint),
};

export default api;
"""
    
    def _generate_list_component(self, resource: str) -> str:
        """Generate a list component"""
        component_name = resource.capitalize() + "List"
        singular = resource[:-1] if resource.endswith('s') else resource
        
        return f"""import React, {{ useState, useEffect }} from 'react';
import {{ apiService }} from '../services/api';
import {resource.capitalize()}Form from './{resource.capitalize()}Form';

function {component_name}() {{
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {{
    fetchItems();
  }}, []);

  const fetchItems = async () => {{
    try {{
      setLoading(true);
      const response = await apiService.get('/{resource}');
      setItems(response.data || []);
    }} catch (error) {{
      console.error('Error fetching {resource}:', error);
    }} finally {{
      setLoading(false);
    }}
  }};

  const handleDelete = async (id) => {{
    if (window.confirm('Are you sure you want to delete this item?')) {{
      try {{
        await apiService.delete(`/{resource}/${{id}}`);
        fetchItems();
      }} catch (error) {{
        console.error('Error deleting {singular}:', error);
      }}
    }}
  }};

  const handleEdit = (item) => {{
    setEditingItem(item);
    setShowForm(true);
  }};

  const handleFormClose = () => {{
    setShowForm(false);
    setEditingItem(null);
    fetchItems();
  }};

  if (loading) {{
    return <div className="loading">Loading...</div>;
  }}

  return (
    <div className="list-container">
      <div className="list-header">
        <h2>{resource.capitalize()}</h2>
        <button onClick={{() => setShowForm(true)}} className="btn btn-primary">
          Add New
        </button>
      </div>

      {{showForm && (
        <{resource.capitalize()}Form 
          item={{editingItem}} 
          onClose={{handleFormClose}} 
        />
      )}}

      <div className="items-grid">
        {{items.length === 0 ? (
          <p>No {resource} found. Create your first one!</p>
        ) : (
          items.map((item) => (
            <div key={{item.id}} className="item-card">
              <div className="item-content">
                <h3>{{item.name || item.title || `{singular.capitalize()} #${{item.id.slice(0, 8)}}`}}</h3>
                <p>{{item.description || item.content || 'No description'}}</p>
              </div>
              <div className="item-actions">
                <button onClick={{() => handleEdit(item)}} className="btn btn-secondary">
                  Edit
                </button>
                <button onClick={{() => handleDelete(item.id)}} className="btn btn-danger">
                  Delete
                </button>
              </div>
            </div>
          ))
        )}}
      </div>
    </div>
  );
}}

export default {component_name};
"""
    
    def _generate_form_component(self, resource: str) -> str:
        """Generate a form component"""
        component_name = resource.capitalize() + "Form"
        singular = resource[:-1] if resource.endswith('s') else resource
        
        return f"""import React, {{ useState, useEffect }} from 'react';
import {{ apiService }} from '../services/api';

function {component_name}({{ item, onClose }}) {{
  const [formData, setFormData] = useState({{
    name: '',
    description: '',
  }});
  const [loading, setLoading] = useState(false);

  useEffect(() => {{
    if (item) {{
      setFormData({{
        name: item.name || item.title || '',
        description: item.description || item.content || '',
      }});
    }}
  }}, [item]);

  const handleSubmit = async (e) => {{
    e.preventDefault();
    setLoading(true);

    try {{
      if (item) {{
        await apiService.put(`/{resource}/${{item.id}}`, formData);
      }} else {{
        await apiService.post('/{resource}', formData);
      }}
      onClose();
    }} catch (error) {{
      console.error('Error saving {singular}:', error);
      alert('Failed to save {singular}');
    }} finally {{
      setLoading(false);
    }}
  }};

  const handleChange = (e) => {{
    setFormData({{
      ...formData,
      [e.target.name]: e.target.value,
    }});
  }};

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h3>{{item ? 'Edit' : 'Create'}} {singular.capitalize()}</h3>
          <button onClick={{onClose}} className="close-btn">&times;</button>
        </div>

        <form onSubmit={{handleSubmit}}>
          <div className="form-group">
            <label htmlFor="name">Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={{formData.name}}
              onChange={{handleChange}}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={{formData.description}}
              onChange={{handleChange}}
              rows="4"
            />
          </div>

          <div className="form-actions">
            <button type="button" onClick={{onClose}} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={{loading}}>
              {{loading ? 'Saving...' : 'Save'}}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}}

export default {component_name};
"""
    
    def _generate_app_css(self) -> str:
        """Generate App.css"""
        return """.App {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background 0.3s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.home {
  text-align: center;
  padding: 4rem 2rem;
}

.list-container {
  padding: 2rem 0;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.item-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1.5rem;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.item-content h3 {
  margin: 0 0 0.5rem 0;
}

.item-actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: opacity 0.2s;
}

.btn:hover {
  opacity: 0.9;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  font-size: 1.2rem;
  color: #7f8c8d;
}
"""
    
    def _generate_index_css(self) -> str:
        """Generate index.css"""
        return """* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f5f5;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New', monospace;
}
"""
    
    def _generate_frontend_readme(self, architecture: Dict) -> str:
        """Generate frontend README"""
        return f"""# Frontend Application

Auto-generated React frontend

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure API endpoint:
```bash
# Create .env file
echo "REACT_APP_API_URL=http://localhost:3000/api" > .env
```

3. Start development server:
```bash
npm start
```

4. Build for production:
```bash
npm run build
```

## Technology Stack

- Framework: React 18
- Routing: React Router v6
- HTTP Client: Axios
- Styling: CSS3

## Features

- CRUD operations for all resources
- Responsive design
- Error handling
- Loading states
"""
