import bcrypt from 'bcryptjs';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const envPath = path.join(__dirname, '..', '..', '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf-8');
  envContent.split('\n').forEach(line => {
    const [key, value] = line.split('=');
    if (key && value) {
      process.env[key.trim()] = value.trim();
    }
  });
}

import { initDB, getDB } from '../db/index.js';

const dbPath = process.env.DB_PATH || path.join(__dirname, '..', '..', 'data', 'xyzw.sqlite.bin');
initDB(dbPath);

async function initAdmin() {
  try {
    const username = process.env.ADMIN_USERNAME || 'admin';
    const email = process.env.ADMIN_EMAIL || 'admin@example.com';
    const password = process.env.ADMIN_PASSWORD || 'admin123';

    const db = getDB();

    const existingAdmin = db.prepare('SELECT id FROM users WHERE role = ?').get('admin');
    if (existingAdmin) {
      console.log('[Init] Admin user already exists');
      process.exit(0);
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const adminId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

    db.prepare(`
      INSERT INTO users (id, username, email, password, avatar, role)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(adminId, username, email, hashedPassword, '/icons/xiaoyugan.png', 'admin');

    console.log('[Init] Admin user created successfully');
    console.log(`  Username: ${username}`);
    console.log(`  Email: ${email}`);
    console.log(`  Password: ${password}`);
    console.log('\n[Warning] Please change the default password immediately!');

    process.exit(0);
  } catch (error) {
    console.error('[Init] Error creating admin:', error);
    process.exit(1);
  }
}

initAdmin();
