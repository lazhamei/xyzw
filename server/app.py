#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XYZW Token URL 获取服务
基于 Flask 的 Token 管理后端服务
"""

import os
import json
import base64
import hashlib
from flask import Flask, request, jsonify, send_from_directory, render_template_string, redirect, url_for, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

# 配置
CONFIG_FILE = '/app/data/config.json'
UPLOAD_FOLDER = '/app/data/uploads'
ALLOWED_EXTENSIONS = {'bin'}

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            'users': {
                'admin': generate_password_hash('admin123')
            }
        }
        save_config(default_config)
        return default_config
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_user_upload_dir(username):
    """获取用户上传目录"""
    user_dir = os.path.join(UPLOAD_FOLDER, username)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def allowed_file(filename):
    """检查文件类型"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_user_token(username):
    """生成用户 Token"""
    salt = app.secret_key
    token = hashlib.sha256(f"{username}{salt}".encode()).hexdigest()[:16]
    return token

def verify_user_token(token, username):
    """验证用户 Token"""
    return token == generate_user_token(username)

# HTML 模板
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>XYZW Token 管理</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        h1 { color: #333; }
        .form-group { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #45a049; }
        .error { color: red; }
        .success { color: green; }
        .file-list { margin-top: 20px; }
        .file-item { background: white; padding: 10px; margin: 10px 0; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
        .token-url { background: #e8f4f8; padding: 8px; border-radius: 4px; font-family: monospace; word-break: break-all; }
        .nav { margin-bottom: 20px; }
        .nav a { margin-right: 15px; text-decoration: none; color: #333; }
    </style>
</head>
<body>
    <div class="container">
        {% if not session.get('username') %}
            <h1>登录</h1>
            {% if error %}<p class="error">{{ error }}</p>{% endif %}
            <form method="post" action="/login">
                <div class="form-group">
                    <label>用户名</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>密码</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">登录</button>
            </form>
            <p style="margin-top: 20px;">还没有账号？<a href="/register">注册新账号</a></p>
        {% else %}
            <div class="nav">
                <span>欢迎, {{ session.username }}!</span>
                <a href="/logout">退出</a>
                <a href="/change-password">修改密码</a>
                {% if session.username != 'admin' %}
                    <a href="/delete-account" onclick="return confirm('确定要注销账号吗？此操作不可恢复！')">注销账号</a>
                {% endif %}
            </div>
            <h1>Bin 文件管理</h1>
            {% if message %}<p class="success">{{ message }}</p>{% endif %}
            <form method="post" action="/upload" enctype="multipart/form-data">
                <div class="form-group">
                    <label>上传 .bin 文件</label>
                    <input type="file" name="file" accept=".bin" multiple required>
                </div>
                <button type="submit">上传</button>
            </form>
            <div class="file-list">
                <h2>已上传的文件</h2>
                {% if files %}
                    {% for file in files %}
                        <div class="file-item">
                            <div>
                                <strong>{{ file.filename }}</strong>
                                <div class="token-url">{{ file.url }}</div>
                            </div>
                            <div>
                                <button onclick="navigator.clipboard.writeText('{{ file.url }}').then(() => alert('已复制!'))">复制链接</button>
                                <form method="post" action="/delete/{{ file.filename }}" style="display: inline;">
                                    <button type="submit" style="background: #f44336;">删除</button>
                                </form>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>暂无文件</p>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    if not session.get('username'):
        return render_template_string(INDEX_TEMPLATE)
    username = session['username']
    user_dir = get_user_upload_dir(username)
    user_token = generate_user_token(username)
    files = []
    if os.path.exists(user_dir):
        for filename in os.listdir(user_dir):
            if filename.endswith('.bin'):
                file_path = os.path.join(user_dir, filename)
                with open(file_path, 'rb') as f:
                    content = f.read()
                b64_content = base64.b64encode(content).decode('utf-8')
                url = f"{request.host_url}{user_token}/{filename}/{b64_content}"
                files.append({'filename': filename, 'url': url})
    return render_template_string(INDEX_TEMPLATE, files=files)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    config = load_config()
    if username in config['users'] and check_password_hash(config['users'][username], password):
        session['username'] = username
        return redirect(url_for('index'))
    return render_template_string(INDEX_TEMPLATE, error='用户名或密码错误')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>注册</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
                .form-group { margin: 15px 0; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>注册新账号</h1>
                <form method="post">
                    <div class="form-group">
                        <label>用户名</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>密码</label>
                        <input type="password" name="password" required>
                    </div>
                    <button type="submit">注册</button>
                </form>
                <p><a href="/">返回登录</a></p>
            </div>
        </body>
        </html>
        '''
    username = request.form.get('username')
    password = request.form.get('password')
    config = load_config()
    if username in config['users']:
        return '用户名已存在', 400
    config['users'][username] = generate_password_hash(password)
    save_config(config)
    return redirect(url_for('index'))

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if not session.get('username'):
        return redirect(url_for('index'))
    if request.method == 'GET':
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>修改密码</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
                .form-group { margin: 15px 0; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>修改密码</h1>
                <form method="post">
                    <div class="form-group">
                        <label>旧密码</label>
                        <input type="password" name="old_password" required>
                    </div>
                    <div class="form-group">
                        <label>新密码</label>
                        <input type="password" name="new_password" required>
                    </div>
                    <button type="submit">修改</button>
                </form>
                <p><a href="/">返回</a></p>
            </div>
        </body>
        </html>
        '''
    username = session['username']
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    config = load_config()
    if not check_password_hash(config['users'][username], old_password):
        return '旧密码错误', 400
    config['users'][username] = generate_password_hash(new_password)
    save_config(config)
    return redirect(url_for('index'))

@app.route('/delete-account', methods=['POST'])
def delete_account():
    if not session.get('username') or session['username'] == 'admin':
        return redirect(url_for('index'))
    username = session['username']
    config = load_config()
    if username in config['users']:
        del config['users'][username]
        save_config(config)
    user_dir = get_user_upload_dir(username)
    if os.path.exists(user_dir):
        import shutil
        shutil.rmtree(user_dir)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if not session.get('username'):
        return redirect(url_for('index'))
    if 'file' not in request.files:
        return redirect(url_for('index'))
    files = request.files.getlist('file')
    username = session['username']
    user_dir = get_user_upload_dir(username)
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(user_dir, filename))
    return redirect(url_for('index'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    if not session.get('username'):
        return redirect(url_for('index'))
    username = session['username']
    user_dir = get_user_upload_dir(username)
    file_path = os.path.join(user_dir, secure_filename(filename))
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('index'))

@app.route('/<user_token>/<filename>/<b64_content>')
def get_token(user_token, filename, b64_content):
    config = load_config()
    username = None
    for user in config['users']:
        if verify_user_token(user_token, user):
            username = user
            break
    if not username:
        return jsonify({'error': 'Invalid token'}), 401
    try:
        content = base64.b64decode(b64_content)
        token = base64.b64encode(content).decode('utf-8')
        return jsonify({
            'token': token,
            'server': 'XYZW Server'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
