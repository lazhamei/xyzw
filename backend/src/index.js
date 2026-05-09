import express from 'express';
import cors from 'cors';
import http from 'http';
import { WebSocketServer } from 'ws';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

import { initDB } from './db/index.js';
import authRoutes from './routes/auth.js';
import gameRolesRoutes from './routes/gameRoles.js';
import dailyTasksRoutes from './routes/dailyTasks.js';
import userRoutes from './routes/user.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const envPath = path.join(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf-8');
  envContent.split('\n').forEach(line => {
    const [key, value] = line.split('=');
    if (key && value) {
      process.env[key.trim()] = value.trim();
    }
  });
}

const requiredEnvVars = ['JWT_SECRET', 'AES_KEY'];
for (const envVar of requiredEnvVars) {
  if (!process.env[envVar] || process.env[envVar].includes('replace_')) {
    console.error(`[Error] Missing or invalid ${envVar} in .env`);
    process.exit(1);
  }
}

const PORT = process.env.BACKEND_PORT || 8787;
const dbPath = process.env.DB_PATH || path.join(__dirname, '..', 'data', 'xyzw.sqlite.bin');

initDB(dbPath);

const app = express();
const server = http.createServer(app);

const corsOrigins = (process.env.CORS_ORIGINS || 'http://localhost:3000').split(',');
app.use(cors({
  origin: (origin, callback) => {
    if (!origin || corsOrigins.includes(origin) || corsOrigins.includes('*')) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true
}));

app.use(express.json());

if (process.env.LOG_REQUESTS === 'true') {
  app.use((req, res, next) => {
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}');
    next();
  });
}

app.get('/health', (req, res) => {
  res.json({ success: true, message: 'Server is running', timestamp: new Date().toISOString() });
});

app.use('/api/v1', authRoutes);
app.use('/api/v1', gameRolesRoutes);
app.use('/api/v1', dailyTasksRoutes);
app.use('/api/v1', userRoutes);

const wss = new WebSocketServer({ server, path: '/ws' });

const clients = new Map();

wss.on('connection', (ws, req) => {
  console.log('[WebSocket] New connection');

  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data);
      console.log('[WebSocket] Received:', message.type);
    } catch (error) {
      console.error('[WebSocket] Message error:', error);
    }
  });

  ws.on('close', () => {
    console.log('[WebSocket] Connection closed');
  });

  ws.on('error', (error) => {
    console.error('[WebSocket] Error:', error);
  });
});

export function broadcast(message) {
  wss.clients.forEach((client) => {
    if (client.readyState === 1) {
      client.send(JSON.stringify(message));
    }
  });
}

app.use((err, req, res, next) => {
  console.error('[Error]', err);
  res.status(500).json({ success: false, message: '服务器内部错误' });
});

server.listen(PORT, () => {
  console.log(`[Server] Running on http://localhost:${PORT}`);
  console.log(`[Server] WebSocket on ws://localhost:${PORT}/ws`);
});

export default app;
