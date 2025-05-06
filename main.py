#!/usr/bin/env python3

from flask import Flask, request, jsonify, send_file, render_template_string, redirect, url_for
import os
import io
import base64
import json
import time
from get_profile_pic import get_instagram_profile_pic

# Configuração da aplicação Flask
app = Flask(__name__)

# Suporte para token do Facebook Graph API
FB_APP_ID = os.environ.get('FB_APP_ID', '')
FB_APP_SECRET = os.environ.get('FB_APP_SECRET', '')
FB_ACCESS_TOKEN = os.environ.get('FB_ACCESS_TOKEN', 'EAANSJdJyLWoBO7HvkFcosxQEWkKdZAnUaBqysG0q72dHD23ZAj2ODZBmiJQ2t9OiHntRWyrg59c9wTpAwZBDa3ZA7fFpsGyOavtrjVmg9Rcc4nhZBJa0DXe01knTFuNdnGwZBQZAAk8noCxsjtZC9e9LPruBm6p0EFiBpuF35ZBgBnoZB2PBelViSVz9zZAlu78U5swtHPhPk1fkMMCJO9V3bgZDZD')

# Diretório para cache de imagens
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# Template HTML para a página principal
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram URL Converter</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }
        h1 {
            color: #e1306c;
            text-align: center;
            margin-bottom: 30px;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background-color: #e1306c;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #c13584;
        }
        .result {
            margin-top: 30px;
            display: {{ 'block' if username else 'none' }};
        }
        .profile-pic {
            display: block;
            max-width: 150px;
            border-radius: 50%;
            margin: 0 auto 20px;
            border: 3px solid #e1306c;
        }
        .url-box {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            position: relative;
        }
        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #0095f6;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 12px;
        }
        .url-title {
            font-weight: 600;
            margin-bottom: 10px;
            color: #555;
        }
        .url-content {
            word-break: break-all;
            font-family: monospace;
            margin-right: 50px;
        }
        footer {
            margin-top: 40px;
            text-align: center;
            color: #999;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram URL Converter</h1>
        
        <form action="/" method="get">
            <div class="form-group">
                <label for="username">Nome de usuário do Instagram:</label>
                <input type="text" id="username" name="username" placeholder="Ex: instagram" value="{{ username }}" required>
            </div>
            <button type="submit">Obter URLs</button>
        </form>
        
        <div class="result">
            {% if username %}
                <h2 style="text-align: center;">Resultados para @{{ username }}</h2>
                <img src="/image/{{ username }}" class="profile-pic" alt="{{ username }} profile picture">
                
                <div class="url-box">
                    <div class="url-title">URL Direta da Imagem:</div>
                    <div class="url-content" id="url1">{{ request.url_root }}image/{{ username }}.jpg</div>
                    <button class="copy-btn" onclick="copyToClipboard('url1')">Copiar</button>
                </div>
                
                <div class="url-box">
                    <div class="url-title">URL para API (JSON):</div>
                    <div class="url-content" id="url2">{{ request.url_root }}api/profile-pic/{{ username }}</div>
                    <button class="copy-btn" onclick="copyToClipboard('url2')">Copiar</button>
                </div>
                
                <div class="url-box">
                    <div class="url-title">Tag HTML para Imagem:</div>
                    <div class="url-content" id="url3">&lt;img src="{{ request.url_root }}image/{{ username }}.jpg" alt="{{ username }} profile picture"&gt;</div>
                    <button class="copy-btn" onclick="copyToClipboard('url3')">Copiar</button>
                </div>
                
            {% endif %}
        </div>
    </div>
    
    <footer>
        <p>Esta ferramenta extrai URLs diretas de imagens de perfil do Instagram, contornando os problemas de hashes.</p>
    </footer>
    
    <script>
        function copyToClipboard(elementId) {
            const element = document.getElementById(elementId);
            const text = element.innerText;
            
            navigator.clipboard.writeText(text).then(() => {
                const button = element.nextElementSibling;
                const originalText = button.innerText;
                button.innerText = 'Copiado!';
                setTimeout(() => {
                    button.innerText = originalText;
                }, 2000);
            });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """Rota principal da aplicação"""
    username = request.args.get('username', '')
    return render_template_string(HTML_TEMPLATE, username=username, request=request)


@app.route('/image/<username>')
@app.route('/image/<username>.jpg')  # Rota que termina com .jpg
@app.route('/image/<username>.png')  # Rota que termina com .png
def get_image(username):
    """Rota para servir a imagem de perfil diretamente"""
    # Remove extensões do username se estiverem presentes
    if username.endswith(('.jpg', '.png')):
        username = username.rsplit('.', 1)[0]
        
    try:
        token = request.args.get('token', FB_ACCESS_TOKEN)
        # Verifica o cache primeiro
        cache_file = os.path.join(CACHE_DIR, f"{username}_profile_pic.jpg")
        
        # Se o cache tem mais de 1 dia ou não existe, atualize-o
        if not os.path.exists(cache_file) or \
           (os.path.exists(cache_file) and \
            (os.path.getmtime(cache_file) < time.time() - 86400)):
            
            # Obtém imagem nova e salva no cache
            get_instagram_profile_pic(username, output_format='file', save_dir=CACHE_DIR, fb_token=token)
        
        return send_file(cache_file, mimetype='image/jpeg')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile-pic/<username>')
def api_profile_pic(username):
    """API endpoint para obter informações da imagem de perfil"""
    try:
        format_type = request.args.get('format', 'url')
        token = request.args.get('token', FB_ACCESS_TOKEN)
        
        if format_type not in ['url', 'base64', 'json']:
            return jsonify({'error': 'Formato inválido. Use "url", "base64" ou "json"'}), 400
        
        result = get_instagram_profile_pic(username, output_format=format_type, fb_token=token)
        
        # Para o formato URL, garantimos que ela termine com .jpg
        if format_type == 'url' and not result.endswith('.jpg'):
            if '?' in result:
                result = result.split('?')[0]
            if not result.endswith('.jpg'):
                result += '.jpg'
        
        return jsonify({
            'username': username,
            'format': format_type,
            'result': result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
