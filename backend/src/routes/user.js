import express from 'express';
import bcrypt from 'bcryptjs';
import { getDB } from '../db/index.js';
import { authenticateToken } from '../middleware/auth.js';

const router = express.Router();

router.get('/profile', authenticateToken, (req, res) => {
  try {
    const db = getDB();
    const user = db.prepare('SELECT id, username, email, avatar, role, created_at FROM users WHERE id = ?').get(req.user.id);

    res.json({ success: true, data: user });
  } catch (error) {
    console.error('[User] Get profile error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.put('/profile', authenticateToken, (req, res) => {
  try {
    const { username, email, avatar } = req.body;
    const db = getDB();

    db.prepare(`
      UPDATE users
      SET username = COALESCE(?, username),
          email = COALESCE(?, email),
          avatar = COALESCE(?, avatar),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(username || null, email || null, avatar || null, req.user.id);

    const updatedUser = db.prepare('SELECT id, username, email, avatar, role, created_at FROM users WHERE id = ?').get(req.user.id);

    res.json({ success: true, message: '更新成功', data: updatedUser });
  } catch (error) {
    console.error('[User] Update profile error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.put('/password', authenticateToken, async (req, res) => {
  try {
    const { old_password, new_password } = req.body;

    if (!old_password || !new_password) {
      return res.status(400).json({ success: false, message: '旧密码和新密码为必填项' });
    }

    const db = getDB();
    const user = db.prepare('SELECT password FROM users WHERE id = ?').get(req.user.id);

    const validPassword = await bcrypt.compare(old_password, user.password);
    if (!validPassword) {
      return res.status(400).json({ success: false, message: '旧密码错误' });
    }

    const hashedPassword = await bcrypt.hash(new_password, 10);
    db.prepare('UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?').run(hashedPassword, req.user.id);

    res.json({ success: true, message: '密码修改成功' });
  } catch (error) {
    console.error('[User] Change password error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.get('/stats', authenticateToken, (req, res) => {
  try {
    const db = getDB();

    const tokenCount = db.prepare('SELECT COUNT(*) as count FROM game_tokens WHERE user_id = ?').get(req.user.id).count;
    const taskCount = db.prepare('SELECT COUNT(*) as count FROM daily_tasks WHERE user_id = ?').get(req.user.id).count;
    const completedTaskCount = db.prepare('SELECT COUNT(*) as count FROM daily_tasks WHERE user_id = ? AND status = "completed"').get(req.user.id).count;

    res.json({
      success: true,
      data: {
        token_count: tokenCount,
        task_count: taskCount,
        completed_task_count: completedTaskCount
      }
    });
  } catch (error) {
    console.error('[User] Get stats error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

export default router;
