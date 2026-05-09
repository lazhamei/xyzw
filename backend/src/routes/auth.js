import express from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { getDB } from '../db/index.js';
import { authenticateToken } from '../middleware/auth.js';

const router = express.Router();

router.post('/register', async (req, res) => {
  try {
    const { username, email, password } = req.body;

    if (!username || !email || !password) {
      return res.status(400).json({ success: false, message: '用户名、邮箱和密码为必填项' });
    }

    const db = getDB();

    const existingUser = db.prepare('SELECT id FROM users WHERE username = ? OR email = ?').get(username, email);
    if (existingUser) {
      return res.status(400).json({ success: false, message: '用户名或邮箱已存在' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

    db.prepare(`
      INSERT INTO users (id, username, email, password, avatar, role)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(userId, username, email, hashedPassword, '/icons/xiaoyugan.png', 'user');

    const token = jwt.sign({ userId }, process.env.JWT_SECRET, { expiresIn: '7d' });

    res.json({
      success: true, message: '注册成功', data: { token } });
  } catch (error) {
    console.error('[Auth] Register error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({ success: false, message: '用户名和密码为必填项' });
    }

    const db = getDB();
    const user = db.prepare('SELECT * FROM users WHERE username = ?').get(username);

    if (!user) {
      return res.status(401).json({ success: false, message: '用户名或密码错误' });
    }

    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(401).json({ success: false, message: '用户名或密码错误' });
    }

    if (!user.is_active) {
      return res.status(403).json({ success: false, message: '账户已被禁用' });
    }

    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '7d' });

    const { password: _, ...userWithoutPassword } = user;

    res.json({
      success: true, message: '登录成功', data: { token, user: userWithoutPassword });
  } catch (error) {
    console.error('[Auth] Login error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.post('/logout', authenticateToken, (req, res) => {
  res.json({ success: true, message: '登出成功' });
});

router.get('/user', authenticateToken, (req, res) => {
  try {
    const db = getDB();
    const user = db.prepare('SELECT id, username, email, avatar, role, created_at FROM users WHERE id = ?').get(req.user.id);

    res.json({ success: true, data: user });
  } catch (error) {
    console.error('[Auth] Get user error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.post('/refresh', authenticateToken, (req, res) => {
  try {
    const token = jwt.sign({ userId: req.user.id }, process.env.JWT_SECRET, { expiresIn: '7d' });
    res.json({ success: true, data: { token } });
  } catch (error) {
    console.error('[Auth] Refresh token error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

export default router;
