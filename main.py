#!/usr/bin/env python3

from flask import Flask, request, jsonify, send_file, render_template_string, redirect, url_for
import os
import io
import base64
import json
import time
from get_profile_pic import process_instagram_image_url

# Configuração da aplicação Flask
app = Flask(__name__)

# Diretório para cache de imagens
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# Template HTML simplificado
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
        h1, h2 { color: #e1306c; text-align: center; }
        .container {
            background-color: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .form-group { margin-bottom: 20px; }
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
        }
        .result { margin-top: 30px; }
        .url-box {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            position: relative;
            word-break: break-all;
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
        .preview-image {
            display: block;
            max-width: 200px;
            margin: 20px auto;
            border-radius: 8px;
            border: 2px solid #e1306c;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram URL Converter</h1>
        
        <form action="/" method="post">
            <div class="form-group">
                <label for="instagram_url">URL da imagem do Instagram:</label>
                <input type="text" id="instagram_url" name="instagram_url" placeholder="Cole a URL da imagem aqui" required>
            </div>
            <button type="submit">Converter URL</button>
        </form>
        
        {% if result %}
        <div class="result">
            <h2>Resultado da Conversão</h2>
            
            {% if result.error %}
                <div style="color: red; text-align: center; margin: 20px 0;">
                    {{ result.error }}
                </div>
            {% else %}
                <img src="{{ result.direct_url }}" alt="Imagem convertida" class="preview-image">
                
                <div class="url-box" id="url1">
                    <strong>URL Direta (ImgBB):</strong><br>
                    {{ result.direct_url }}
                    <button class="copy-btn" onclick="copyToClipboard('url1')">Copiar</button>
                </div>
                
                <div class="url-box" id="url2">
                    <strong>URL Original:</strong><br>
                    {{ result.original_url }}
                    <button class="copy-btn" onclick="copyToClipboard('url2')">Copiar</button>
                </div>
                
                {% if result.delete_url %}
                <div class="url-box" id="url3">
                    <strong>URL de Exclusão (guardar):</strong><br>
                    {{ result.delete_url }}
                    <button class="copy-btn" onclick="copyToClipboard('url3')">Copiar</button>
                </div>
                {% endif %}
            {% endif %}
        </div>
        {% endif %}
    </div>
    
    <script>
        function copyToClipboard(elementId) {
            const element = document.getElementById(elementId);
            const text = element.innerText.split('\n')[1].trim();
            
            navigator.clipboard.writeText(text).then(() => {
                const button = element.querySelector('.copy-btn');
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

@app.route('/', methods=['GET', 'POST'])
def index():
    """Página principal - aceita GET e POST"""
    if request.method == 'POST':
        instagram_url = request.form.get('instagram_url', '')
        
        if instagram_url:
            result = process_instagram_image_url(instagram_url, output_format='json')
            return render_template_string(HTML_TEMPLATE, result=result)
    
    return render_template_string(HTML_TEMPLATE, result=None)

@app.route('/convert', methods=['POST'])
def convert_url():
    """API endpoint para converter URL de imagem do Instagram"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL da imagem não fornecida. Envie um JSON com o campo "url"'}), 400
        
        instagram_url = data['url']
        format_type = data.get('format', 'url')
        
        if format_type not in ['url', 'json', 'base64']:
            return jsonify({'error': 'Formato inválido. Use "url", "base64" ou "json"'}), 400
        
        result = process_instagram_image_url(instagram_url, output_format=format_type)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Retorne o resultado conforme o formato
        if format_type == 'url':
            return jsonify({
                'url': result,
                'original_url': instagram_url
            })
        elif format_type == 'json':
            return jsonify(result)
        else:  # base64
            return jsonify({
                'base64': result,
                'original_url': instagram_url
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/convert-url')
def convert_url_get():
    """API endpoint para converter URL via parâmetro GET"""
    try:
        instagram_url = request.args.get('url', '')
        
        if not instagram_url:
            return jsonify({'error': 'URL da imagem não fornecida. Use o parâmetro "url"'}), 400
        
        format_type = request.args.get('format', 'url')
        
        if format_type not in ['url', 'json', 'base64']:
            return jsonify({'error': 'Formato inválido. Use "url", "base64" ou "json"'}), 400
        
        result = process_instagram_image_url(instagram_url, output_format=format_type)
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # Retorne o resultado conforme o formato
        if format_type == 'url':
            return jsonify({
                'url': result,
                'original_url': instagram_url
            })
        elif format_type == 'json':
            return jsonify(result)
        else:  # base64
            return jsonify({
                'base64': result,
                'original_url': instagram_url
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
