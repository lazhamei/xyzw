import express from 'express';
import { getDB } from '../db/index.js';
import { authenticateToken } from '../middleware/auth.js';

const router = express.Router();

router.get('/gamerole_list', authenticateToken, (req, res) => {
  try {
    const db = getDB();
    const tokens = db.prepare('SELECT * FROM game_tokens WHERE user_id = ? ORDER BY created_at DESC').all(req.user.id);

    res.json({ success: true, data: tokens });
  } catch (error) {
    console.error('[GameRoles] List error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.post('/gameroles', authenticateToken, (req, res) => {
  try {
    const { name, token, ws_url, server, remark, import_method, source_url, avatar } = req.body;

    if (!name || !token) {
      return res.status(400).json({ success: false, message: '名称和Token为必填项' });
    }

    const db = getDB();
    const tokenId = 'token_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

    db.prepare(`
      INSERT INTO game_tokens (id, user_id, name, token, ws_url, server, remark, import_method, source_url, avatar)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(tokenId, req.user.id, name, token, ws_url || null, server || '', remark || '', import_method || 'manual', source_url || null, avatar || '');

    const newToken = db.prepare('SELECT * FROM game_tokens WHERE id = ?').get(tokenId);

    res.json({ success: true, message: '添加成功', data: newToken });
  } catch (error) {
    console.error('[GameRoles] Create error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.get('/gameroles/:id', authenticateToken, (req, res) => {
  try {
    const db = getDB();
    const token = db.prepare('SELECT * FROM game_tokens WHERE id = ? AND user_id = ?').get(req.params.id, req.user.id);

    if (!token) {
      return res.status(404).json({ success: false, message: 'Token不存在' });
    }

    res.json({ success: true, data: token });
  } catch (error) {
    console.error('[GameRoles] Get error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.put('/gameroles/:id', authenticateToken, (req, res) => {
  try {
    const { name, token, ws_url, server, remark, avatar } = req.body;
    const db = getDB();

    const existing = db.prepare('SELECT id FROM game_tokens WHERE id = ? AND user_id = ?').get(req.params.id, req.user.id);
    if (!existing) {
      return res.status(404).json({ success: false, message: 'Token不存在' });
    }

    db.prepare(`
      UPDATE game_tokens
      SET name = COALESCE(?, name),
          token = COALESCE(?, token),
          ws_url = ?,
          server = COALESCE(?, server),
          remark = ?,
          avatar = COALESCE(?, avatar),
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ? AND user_id = ?
    `).run(name || null, token || null, ws_url || null, server || null, remark || null, avatar || null, req.params.id, req.user.id);

    const updated = db.prepare('SELECT * FROM game_tokens WHERE id = ?').get(req.params.id);

    res.json({ success: true, message: '更新成功', data: updated });
  } catch (error) {
    console.error('[GameRoles] Update error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

router.delete('/gameroles/:id', authenticateToken, (req, res) => {
  try {
    const db = getDB();

    const result = db.prepare('DELETE FROM game_tokens WHERE id = ? AND user_id = ?').run(req.params.id, req.user.id);

    if (result.changes === 0) {
      return res.status(404).json({ success: false, message: 'Token不存在' });
    }

    res.json({ success: true, message: '删除成功' });
  } catch (error) {
    console.error('[GameRoles] Delete error:', error);
    res.status(500).json({ success: false, message: '服务器错误' });
  }
});

export default router;
