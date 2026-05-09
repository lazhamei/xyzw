import express from 'express';
import { getDB } from '../db/index.js';
import { authenticateToken } from '../middleware/auth.js';

const router = express.Router();

router.get('/daily-tasks', authenticateToken, (req, res) => {
  try {
    const { token_id } = req.query;
    const db = getDB();

    let query = 'SELECT * FROM daily_tasks WHERE user_id = ?';
    const params = [req.user.id];

    if (token_id) {
      query += ' AND token_id = ?';
      params.push(token_id);
    }

    query += ' ORDER BY created_at DESC';
    const tasks = db.prepare(query).all(...params);

    res.json({ success: true, data: tasks });
  } catch (error) {
    console.error('[DailyTasks] List error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.get('/daily-tasks/status', authenticateToken, (req, res) => {
  try {
    const { token_id } = req.query;
    const db = getDB();

    const today = new Date().toISOString().split('T')[0];
    let query = `
      SELECT task_type, status, COUNT(*) as count
      FROM daily_tasks
      WHERE user_id = ? AND DATE(created_at) = ?
    `;
    const params = [req.user.id, today];

    if (token_id) {
      query += ' AND token_id = ?';
      params.push(token_id);
    }

    query += ' GROUP BY task_type, status';
    const status = db.prepare(query).all(...params);

    res.json({ success: true, data: status });
  } catch (error) {
    console.error('[DailyTasks] Status error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.post('/daily-tasks/:id/complete', authenticateToken, (req, res) => {
  try {
    const db = getDB();
    const { token_id } = req.body;

    const result = db.prepare(`
      UPDATE daily_tasks
      SET status = 'completed', completed_at = CURRENT_TIMESTAMP
      WHERE id = ? AND user_id = ?
    `).run(req.params.id, req.user.id);

    if (result.changes === 0) {
      return res.status(404).json({ success: false, message: '任务不存在' });
    }

    const task = db.prepare('SELECT * FROM daily_tasks WHERE id = ?').get(req.params.id);

    res.json({ success: true, message: '任务已完成', data: task });
  } catch (error) {
    console.error('[DailyTasks] Complete error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.get('/daily-tasks/history', authenticateToken, (req, res) => {
  try {
    const { token_id, page = 1, limit = 20 } = req.query;
    const db = getDB();

    const offset = (page - 1) * limit;
    let query = 'SELECT * FROM daily_tasks WHERE user_id = ?';
    const params = [req.user.id];

    if (token_id) {
      query += ' AND token_id = ?';
      params.push(token_id);
    }

    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(Number(limit), offset);

    const tasks = db.prepare(query).all(...params);

    const countQuery = token_id
      ? 'SELECT COUNT(*) as total FROM daily_tasks WHERE user_id = ? AND token_id = ?'
      : 'SELECT COUNT(*) as total FROM daily_tasks WHERE user_id = ?';
    const countParams = token_id ? [req.user.id, token_id] : [req.user.id];
    const { total } = db.prepare(countQuery).get(...countParams);

    res.json({
      success: true,
      data: {
        tasks,
        pagination: {
          page: Number(page),
          limit: Number(limit),
          total,
          totalPages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    console.error('[DailyTasks] History error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

export default router;
