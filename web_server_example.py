#!/usr/bin/env python3

from flask import Flask, request, jsonify, send_file, render_template_string
import os
import io
import base64
from get_profile_pic import get_instagram_profile_pic

app = Flask(__name__)

# Diretório para cache de imagens
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# Template HTML simples para teste
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Instagram Profile Picture Proxy</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { text-align: center; }
        .profile-pic { max-width: 200px; border-radius: 50%; }
        form { margin: 20px 0; }
        input[type="text"] { padding: 8px; width: 200px; }
        button { padding: 8px 16px; background: #0095f6; color: white; border: none; cursor: pointer; }
        .formats { margin: 20px 0; }
        .format-option { margin: 10px; padding: 10px; border: 1px solid #ccc; }
        pre { background: #f5f5f5; padding: 10px; overflow: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Instagram Profile Picture Proxy</h1>
        
        <form action="/" method="get">
            <input type="text" name="username" placeholder="Instagram username" value="{{ username }}">
            <button type="submit">Get Profile Picture</button>
        </form>
        
        {% if username %}
        <h2>Profile Picture for @{{ username }}</h2>
        <img src="/image/{{ username }}" class="profile-pic" alt="{{ username }} profile picture">
        
        <div class="formats">
            <div class="format-option">
                <h3>Direct Image URL:</h3>
                <pre>{{ request.url_root }}image/{{ username }}</pre>
            </div>
            
            <div class="format-option">
                <h3>Direct Image URL (com .jpg):</h3>
                <pre>{{ request.url_root }}image/{{ username }}.jpg</pre>
            </div>
            
            <div class="format-option">
                <h3>JSON API:</h3>
                <pre>{{ request.url_root }}api/profile-pic/{{ username }}</pre>
            </div>
            
            <div class="format-option">
                <h3>HTML Image Tag:</h3>
                <pre>&lt;img src="{{ request.url_root }}image/{{ username }}" alt="{{ username }} profile picture"&gt;</pre>
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''


@app.route('/')
def index():
    username = request.args.get('username', '')
    return render_template_string(HTML_TEMPLATE, username=username, request=request)


@app.route('/image/<username>')
@app.route('/image/<username>.jpg')  # Adicionando rota que termina com .jpg
def get_image(username):
    """Serve the Instagram profile picture directly"""
    # Remove .jpg do username se estiver presente
    if username.endswith('.jpg'):
        username = username[:-4]
        
    try:
        # Check cache first
        cache_file = os.path.join(CACHE_DIR, f"{username}_profile_pic.jpg")
        
        # If cache is older than 1 day or doesn't exist, refresh it
        if not os.path.exists(cache_file) or \
           (os.path.exists(cache_file) and \
            (os.path.getmtime(cache_file) < os.time() - 86400)):
            
            # Get fresh image and save to cache
            get_instagram_profile_pic(username, output_format='file', save_dir=CACHE_DIR)
        
        return send_file(cache_file, mimetype='image/jpeg')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/profile-pic/<username>')
def api_profile_pic(username):
    """API endpoint to get profile picture information"""
    try:
        format_type = request.args.get('format', 'url')
        
        if format_type not in ['url', 'base64']:
            return jsonify({'error': 'Invalid format. Use "url" or "base64"'}), 400
        
        result = get_instagram_profile_pic(username, output_format=format_type)
        
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