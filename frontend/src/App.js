import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [url, setUrl] = useState('https://www.google.com');
  const [apiKey, setApiKey] = useState('');
  const [screenshot, setScreenshot] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [apiKeys, setApiKeys] = useState([]);
  const [keyName, setKeyName] = useState('Test Key');
  
  // Screenshot options
  const [options, setOptions] = useState({
    width: 1920,
    height: 1080,
    fullPage: false,
    delay: 5000, // Increased default delay for complex sites
    format: 'png',
    quality: 90
  });

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const response = await axios.get(`${API}/api-keys`);
      setApiKeys(response.data);
    } catch (e) {
      console.error('Error fetching API keys:', e);
    }
  };

  const createApiKey = async () => {
    try {
      const response = await axios.post(`${API}/api-keys`, { name: keyName });
      setApiKeys([...apiKeys, response.data]);
      setApiKey(response.data.key);
      setKeyName('');
    } catch (e) {
      console.error('Error creating API key:', e);
      setError('Failed to create API key');
    }
  };

  const takeScreenshot = async () => {
    if (!url || !apiKey) {
      setError('Please provide both URL and API key');
      return;
    }

    setLoading(true);
    setError('');
    setScreenshot(null);

    try {
      const response = await axios.post(
        `${API}/v1/screenshot`,
        {
          url: url,
          options: options
        },
        {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const screenshotData = response.data;
      setScreenshot(screenshotData);
      
      // Check if the screenshot might contain an error page
      if (url.includes('myntr.it') || url.includes('fkrt.cc')) {
        console.log('Note: Shortened URLs may redirect through anti-bot systems');
      }
    } catch (e) {
      console.error('Screenshot error:', e);
      const errorMsg = e.response?.data?.detail || 'Failed to capture screenshot';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            URL Screenshot API
          </h1>
          <p className="text-gray-600">
            Capture high-quality screenshots of any webpage
          </p>
        </div>

        {/* API Key Management */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">API Key Management</h2>
          
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              placeholder="API Key Name"
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={createApiKey}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Create API Key
            </button>
          </div>

          {apiKeys.length > 0 && (
            <div className="space-y-2">
              <h3 className="font-medium">Available API Keys:</h3>
              {apiKeys.map((key) => (
                <div
                  key={key.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
                >
                  <div>
                    <span className="font-medium">{key.name}</span>
                    <span className="ml-2 text-sm text-gray-500">
                      (Used {key.usage_count} times)
                    </span>
                  </div>
                  <button
                    onClick={() => setApiKey(key.key)}
                    className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600"
                  >
                    Use This Key
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Screenshot Configuration */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Screenshot Configuration</h2>
          
          {/* URL Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Website URL
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="mt-1 text-sm text-gray-500">
              💡 For e-commerce sites (Amazon, Myntra, Flipkart), use higher delay (8000+ ms) for better results
            </p>
          </div>

          {/* API Key Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Key
            </label>
            <input
              type="text"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Your API key"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Options Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Width
              </label>
              <input
                type="number"
                value={options.width}
                onChange={(e) => setOptions({...options, width: parseInt(e.target.value)})}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Height
              </label>
              <input
                type="number"
                value={options.height}
                onChange={(e) => setOptions({...options, height: parseInt(e.target.value)})}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Delay (ms)
              </label>
              <input
                type="number"
                value={options.delay}
                onChange={(e) => setOptions({...options, delay: parseInt(e.target.value)})}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                title="Wait time before capturing screenshot. Use 5000+ for e-commerce sites"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Format
              </label>
              <select
                value={options.format}
                onChange={(e) => setOptions({...options, format: e.target.value})}
                className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="png">PNG</option>
                <option value="jpeg">JPEG</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-4 mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={options.fullPage}
                onChange={(e) => setOptions({...options, fullPage: e.target.checked})}
                className="mr-2"
              />
              Full Page Screenshot
            </label>
            
            {options.format === 'jpeg' && (
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">
                  Quality:
                </label>
                <input
                  type="range"
                  min="1"
                  max="100"
                  value={options.quality}
                  onChange={(e) => setOptions({...options, quality: parseInt(e.target.value)})}
                  className="w-20"
                />
                <span className="text-sm text-gray-600">{options.quality}%</span>
              </div>
            )}
          </div>

          <button
            onClick={takeScreenshot}
            disabled={loading || !url || !apiKey}
            className="w-full px-4 py-3 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {loading ? 'Capturing Screenshot...' : 'Take Screenshot'}
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Screenshot Display */}
        {screenshot && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Screenshot Result</h2>
            <div className="mb-4">
              <p className="text-sm text-gray-600">
                <strong>URL:</strong> {screenshot.url}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Format:</strong> {screenshot.format.toUpperCase()}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Captured:</strong> {new Date(screenshot.timestamp).toLocaleString()}
              </p>
            </div>
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <img 
                src={screenshot.image} 
                alt="Website screenshot"
                className="w-full h-auto"
                style={{ maxHeight: '600px', objectFit: 'contain' }}
              />
            </div>
            <div className="mt-4">
              <a
                href={screenshot.image}
                download={`screenshot-${Date.now()}.${screenshot.format}`}
                className="inline-block px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
              >
                Download Screenshot
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;