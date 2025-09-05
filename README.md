# URL Screenshot API 📸

A powerful, production-ready API service for capturing high-quality screenshots of any webpage with advanced customization options and anti-bot protection.

![URL Screenshot API](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red.svg)
![React](https://img.shields.io/badge/React-18+-blue.svg)

## ✨ Features

- 🚀 **Fast & Reliable**: Built with FastAPI and Playwright for high-performance screenshot capture
- 🔐 **Secure Authentication**: API key-based authentication with usage tracking
- 🎨 **Customizable Screenshots**: 
  - Multiple formats (PNG, JPEG)
  - Custom viewport sizes
  - Full page or viewport capture
  - Quality control for JPEG
  - Configurable delays
- 🛡️ **Anti-Bot Detection**: Advanced stealth mode for capturing protected websites
- 🌐 **Beautiful Web Interface**: React-based dashboard for easy testing and management
- 📊 **Usage Analytics**: Track API key usage and screenshot statistics
- 🐳 **Docker Ready**: One-command deployment with Docker Compose

## 🖼️ Screenshots

### Web Interface
![Screenshot Interface](docs/screenshot-interface.png)

### API Response
```json
{
  "status": "success",
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAB...",
  "format": "png",
  "timestamp": "2025-09-05T17:22:45.123Z",
  "url": "https://example.com"
}
```

## 🚀 Quick Start

### Method 1: Docker Deployment (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/url-screenshot-api.git
cd url-screenshot-api
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Access the application**
- Web Interface: http://localhost:3000
- API Endpoint: http://localhost:8001/api

### Method 2: Manual Installation

#### Prerequisites
- Python 3.8+
- Node.js 18+
- MongoDB 4.4+
- Git

#### Backend Setup
```bash
# Clone repository
git clone https://github.com/yourusername/url-screenshot-api.git
cd url-screenshot-api/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB connection string

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### Frontend Setup
```bash
# In a new terminal
cd url-screenshot-api/frontend

# Install dependencies
npm install
# or
yarn install

# Configure environment
cp .env.example .env
# Edit .env with your backend URL

# Start development server
npm start
# or
yarn start
```

#### MongoDB Setup
```bash
# Install MongoDB (Ubuntu/Debian)
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)
```env
# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=screenshot_api

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Playwright Browser Path (for Docker)
PLAYWRIGHT_BROWSERS_PATH=/pw-browsers

# API Configuration (optional)
MAX_SCREENSHOT_SIZE=5MB
DEFAULT_TIMEOUT=60000
```

#### Frontend (.env)
```env
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001

# Optional: Analytics/Monitoring
REACT_APP_GA_TRACKING_ID=your_ga_id
```

### Docker Configuration

The `docker-compose.yml` includes:
- **MongoDB**: Database service with persistent storage
- **Backend**: FastAPI service with Playwright
- **Frontend**: React application served by Nginx
- **Networks**: Internal communication between services

## 📚 API Documentation

### Authentication
All API requests require an API key in the Authorization header:
```
Authorization: Bearer your_api_key_here
```

### Endpoints

#### Create API Key
```http
POST /api/api-keys
Content-Type: application/json

{
  "name": "My API Key"
}
```

#### Capture Screenshot
```http
POST /api/v1/screenshot
Authorization: Bearer your_api_key
Content-Type: application/json

{
  "url": "https://example.com",
  "options": {
    "width": 1920,
    "height": 1080,
    "format": "png",
    "quality": 90,
    "fullPage": false,
    "delay": 2000
  }
}
```

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | required | Target URL to screenshot |
| `width` | integer | 1920 | Viewport width (100-4000) |
| `height` | integer | 1080 | Viewport height (100-4000) |
| `format` | string | "png" | Image format ("png" or "jpeg") |
| `quality` | integer | 90 | JPEG quality (1-100) |
| `fullPage` | boolean | false | Capture full page or viewport only |
| `delay` | integer | 0 | Delay before capture (0-30000ms) |

### Response Format

```json
{
  "status": "success",
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAB...",
  "format": "png",
  "timestamp": "2025-09-05T17:22:45.123Z",
  "url": "https://example.com"
}
```

## 🌐 Usage Examples

### cURL
```bash
# Create API key
API_KEY=$(curl -s -X POST "http://localhost:8001/api/api-keys" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Key"}' | jq -r '.key')

# Take screenshot
curl -X POST "http://localhost:8001/api/v1/screenshot" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com",
    "options": {
      "width": 1280,
      "height": 720,
      "format": "png",
      "fullPage": true,
      "delay": 3000
    }
  }'
```

### Python
```python
import requests
import base64

# Create API key
response = requests.post('http://localhost:8001/api/api-keys', 
    json={'name': 'Python Client'})
api_key = response.json()['key']

# Take screenshot
headers = {'Authorization': f'Bearer {api_key}'}
data = {
    'url': 'https://github.com',
    'options': {
        'width': 1280,
        'height': 720,
        'format': 'png',
        'delay': 2000
    }
}

response = requests.post('http://localhost:8001/api/v1/screenshot', 
    json=data, headers=headers)

if response.status_code == 200:
    result = response.json()
    # Save image
    image_data = result['image'].split(',')[1]
    with open('screenshot.png', 'wb') as f:
        f.write(base64.b64decode(image_data))
```

### JavaScript/Node.js
```javascript
const axios = require('axios');
const fs = require('fs');

async function takeScreenshot() {
  // Create API key
  const keyResponse = await axios.post('http://localhost:8001/api/api-keys', {
    name: 'Node.js Client'
  });
  const apiKey = keyResponse.data.key;

  // Take screenshot
  const response = await axios.post('http://localhost:8001/api/v1/screenshot', {
    url: 'https://github.com',
    options: {
      width: 1280,
      height: 720,
      format: 'png',
      delay: 2000
    }
  }, {
    headers: {
      'Authorization': `Bearer ${apiKey}`
    }
  });

  // Save image
  const imageData = response.data.image.split(',')[1];
  fs.writeFileSync('screenshot.png', imageData, 'base64');
}

takeScreenshot();
```

## 🚀 Production Deployment

### Docker Production Setup

1. **Create production environment file**
```bash
cp .env.example .env.production
# Configure production values
```

2. **Use production Docker Compose**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **Set up reverse proxy (Nginx)**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 120s;
    }
}
```

4. **Enable SSL with Let's Encrypt**
```bash
sudo certbot --nginx -d your-domain.com
```

### Server Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 20GB storage
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+

**Recommended:**
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ SSD storage
- Load balancer for high traffic

## 🛠️ Development

### Project Structure
```
url-screenshot-api/
├── backend/
│   ├── server.py              # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment template
├── frontend/
│   ├── src/
│   │   ├── App.js            # React main component
│   │   └── App.css           # Styles
│   ├── package.json          # Node.js dependencies
│   └── .env.example          # Environment template
├── docker-compose.yml        # Development setup
├── docker-compose.prod.yml   # Production setup
└── README.md                 # This file
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔧 Troubleshooting

### Common Issues

**1. Playwright Browser Issues**
```bash
# Reinstall browsers
playwright install chromium
playwright install-deps
```

**2. Memory Issues**
- Increase server RAM
- Limit concurrent screenshot operations
- Use smaller viewport sizes

**3. Timeout Errors**
- Increase delay for complex sites
- Check network connectivity
- Verify target site accessibility

**4. MongoDB Connection Issues**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check connection string in .env
MONGO_URL=mongodb://localhost:27017
```

### Performance Optimization

- Use Redis for caching frequent screenshots
- Implement request queuing for high load
- Configure MongoDB indexes
- Use CDN for serving screenshot files
- Monitor resource usage with tools like htop, docker stats

## 📊 Monitoring & Logging

### View Logs
```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# System logs
tail -f /var/log/screenshot-api.log
```

### Health Checks
- Backend health: `GET /api/`
- MongoDB connection: Check backend logs
- Frontend: Access web interface

## 🔒 Security

- Use strong API keys
- Implement rate limiting
- Regular security updates
- Configure firewall properly
- Use HTTPS in production
- Monitor access logs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/url-screenshot-api/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/url-screenshot-api/discussions)
- **Email**: support@yoursite.com

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for browser automation
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [React](https://reactjs.org/) for the frontend
- [MongoDB](https://www.mongodb.com/) for data storage

---

⭐ **Star this repository if you find it helpful!**