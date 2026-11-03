export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const targetPath = req.url.replace(/^\/api\/proxy\//, '').split('?')[0];
  const targetUrl = `https://elen-backend-v2.onrender.com/${targetPath}`;

  try {
    const headers = { 'Content-Type': 'application/json' };
    
    if (req.headers.authorization) {
      headers['Authorization'] = req.headers.authorization;
    }

    const options = {
      method: req.method,
      headers: headers
    };

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      options.body = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
    }

    const response = await fetch(targetUrl, options);
    const data = await response.text();
    
    res.status(response.status).setHeader('Content-Type', 'application/json').send(data);
  } catch (error) {
    res.status(500).json({ error: 'Proxy Error', details: error.message });
  }
}
