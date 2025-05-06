#!/usr/bin/env python3

import requests
import re
import os
import base64
import json
from io import BytesIO
import time

def get_instagram_profile_pic(username, output_format='url', save_dir=None, fb_token=None):
    """
    Get Instagram profile picture URL or image data
    
    Args:
        username (str): Instagram username
        output_format (str): Format to return the image data
            - 'url': Return direct image URL with jpg extension
            - 'json': Return all data from Instagram API
            - 'base64': Return base64 encoded image
            - 'file': Save file to disk and return path
        save_dir (str, optional): Directory to save file when output_format is 'file'
        fb_token (str, optional): Facebook Graph API token for direct access
    
    Returns:
        Based on output_format:
        - url: string with direct image URL ending with .jpg
        - json: dictionary with all profile data
        - base64: base64 encoded image with data:image/jpeg;base64 prefix
        - file: path to saved file
    """
    username = username.lower().strip()
    
    # Primeiro, tente usar o token do Facebook se disponível
    if fb_token:
        try:
            return _try_facebook_graph_api(username, output_format, save_dir, fb_token)
        except Exception as e:
            # Se falhar, continue com os outros métodos
            print(f"Facebook Graph API failed: {str(e)}")
    
    # Inicialize a lista de erros para coletar problemas de cada método
    errors = []
    
    # Lista de métodos para tentar obter a imagem de perfil
    methods = [
        _try_instagram_api,
        _try_html_scraping,
        _try_oembed_api,
        _try_imginn_service,
        _try_insta_stories_service,
        _try_profile_picture_finder
    ]
    
    # Tente cada método até que um funcione
    for method in methods:
        try:
            result = method(username, output_format, save_dir)
            if result:
                return result
        except Exception as e:
            errors.append(f"{method.__name__}: {str(e)}")
            # Continue para o próximo método
    
    # Se chegou aqui, todos os métodos falharam
    raise Exception(f"Failed to get Instagram profile picture: All methods failed. Details: {'; '.join(errors)}")

def _try_facebook_graph_api(username, output_format='url', save_dir=None, token=None):
    """Tenta obter a imagem de perfil usando a Facebook Graph API com o token fornecido"""
    
    if not token:
        raise Exception("Facebook Graph API token is required")
    
    # Primeiro, procure o ID do usuário do Instagram
    search_url = f"https://graph.facebook.com/v18.0/ig_username/{username}?access_token={token}"
    response = requests.get(search_url, timeout=10)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get Instagram user ID: {response.text}")
    
    user_data = response.json()
    if 'id' not in user_data:
        raise Exception("Instagram user ID not found in response")
    
    instagram_id = user_data['id']
    
    # Agora, obtenha os detalhes do usuário, incluindo a imagem de perfil
    profile_url = f"https://graph.facebook.com/v18.0/{instagram_id}?fields=profile_picture_url,username,name&access_token={token}"
    profile_response = requests.get(profile_url, timeout=10)
    
    if profile_response.status_code != 200:
        raise Exception(f"Failed to get profile picture: {profile_response.text}")
    
    profile_data = profile_response.json()
    
    if 'profile_picture_url' not in profile_data:
        raise Exception("Profile picture URL not found in response")
    
    profile_pic_url = profile_data['profile_picture_url']
    
    return _process_profile_pic_url(profile_pic_url, output_format, save_dir, profile_data)

def _try_instagram_api(username, output_format='url', save_dir=None):
    """Tenta obter a imagem de perfil usando a API oficial do Instagram"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    api_headers = headers.copy()
    api_headers['x-ig-app-id'] = '936619743392459'  # Instagram web app ID
    
    response = requests.get(api_url, headers=api_headers, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    if 'data' in data and 'user' in data['data']:
        user_data = data['data']['user']
        
        # Extract profile pic URL
        profile_pic_url = user_data.get('profile_pic_url_hd', user_data.get('profile_pic_url', None))
        
        if not profile_pic_url:
            raise Exception("No profile picture found in API response")
        
        return _process_profile_pic_url(profile_pic_url, output_format, save_dir, user_data)
    
    raise Exception("Invalid response format from Instagram API")

def _try_html_scraping(username, output_format='url', save_dir=None):
    """Tenta obter a imagem de perfil raspando o HTML da página de perfil"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    url = f"https://www.instagram.com/{username}/"
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    # Tenta múltiplas estratégias de extração do HTML
    
    # 1. Busca por dados JSON no HTML
    # Tenta encontrar o sharedData JSON
    shared_data_match = re.search(r'<script type="text/javascript">window\._sharedData = (.+?);</script>', response.text)
    if shared_data_match:
        try:
            shared_data = json.loads(shared_data_match.group(1))
            
            if 'entry_data' in shared_data and 'ProfilePage' in shared_data['entry_data']:
                profile_data = shared_data['entry_data']['ProfilePage'][0]['graphql']['user']
                profile_pic_url = profile_data.get('profile_pic_url_hd', profile_data.get('profile_pic_url', None))
                
                if profile_pic_url:
                    return _process_profile_pic_url(profile_pic_url, output_format, save_dir, profile_data)
        except:
            pass
    
    # 2. Tenta encontrar LD+JSON
    ld_json_match = re.search(r'<script type="application/ld\+json">(.+?)</script>', response.text)
    if ld_json_match:
        try:
            json_data = json.loads(ld_json_match.group(1))
            if 'author' in json_data and 'image' in json_data['author']:
                profile_pic_url = json_data['author']['image']
                return _process_profile_pic_url(profile_pic_url, output_format, save_dir, json_data['author'])
        except:
            pass
    
    # 3. Tenta encontrar a imagem diretamente no HTML usando vários padrões
    # Buscar pelas classes mais recentes
    patterns = [
        r'<img[^>]+class="[^"]*(?:profile-pic|_aa8j)[^"]*"[^>]+src="([^"]+)"',
        r'<img[^>]+(?:data-testid="user-avatar"|alt="[^"]* profile picture")[^>]+src="([^"]+)"',
        r'<img[^>]+(?:alt="[^"]* profile picture")[^>]+src="([^"]+)"'
    ]
    
    for pattern in patterns:
        img_match = re.search(pattern, response.text)
        if img_match:
            profile_pic_url = img_match.group(1)
            return _process_profile_pic_url(profile_pic_url, output_format, save_dir, {"username": username})
    
    raise Exception("Could not find profile picture in HTML")

def _try_oembed_api(username, output_format='url', save_dir=None):
    """Tenta obter a imagem de perfil usando a API oEmbed do Instagram"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    url = f"https://api.instagram.com/oembed/?url=https://www.instagram.com/{username}/&hidecaption=true"
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if 'thumbnail_url' in data:
            return _process_profile_pic_url(data['thumbnail_url'], output_format, save_dir, data)
    
    raise Exception("oEmbed API failed to return thumbnail URL")

def _try_imginn_service(username, output_format='url', save_dir=None):
    """Tenta obter a imagem de perfil pelo serviço ImgInn"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    # imginn.org é um serviço popular para visualizar perfis do Instagram
    url = f"https://imginn.org/{username}/"
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        # Procura pela imagem de perfil
        img_match = re.search(r'<img[^>]+class="img-fluid rounded-circle[^"]*"[^>]+src="([^"]+)"', response.text)
        if img_match:
            profile_pic_url = img_match.group(1)
            if not profile_pic_url.startswith('http'):
                profile_pic_url = f"https://imginn.org{profile_pic_url}" if profile_pic_url.startswith('/') else f"https://imginn.org/{profile_pic_url}"
            return _process_profile_pic_url(profile_pic_url, output_format, save_dir, {"username": username})
    
    raise Exception("ImgInn service did not return a profile picture")

def _try_insta_stories_service(username, output_format='url', save_dir=None):
    """Tenta obter a imagem de perfil pelo serviço Insta-Stories"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    # insta-stories.online é outro serviço para ver perfis
    url = f"https://insta-stories.online/profile/{username}"
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        # Procura pela imagem de perfil
        img_match = re.search(r'<div class="profile-avatar">.*?<img[^>]+src="([^"]+)"', response.text, re.DOTALL)
        if img_match:
            profile_pic_url = img_match.group(1)
            return _process_profile_pic_url(profile_pic_url, output_format, save_dir, {"username": username})
    
    raise Exception("Insta-Stories service did not return a profile picture")

def _try_profile_picture_finder(username, output_format='url', save_dir=None):
    """Tenta obter a imagem de perfil usando um serviço de terceiros Profile Picture Finder"""
    
    # Este serviço geralmente tem acesso às imagens de perfil
    fallback_url = f"https://www.instadp.com/dp/{username}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    response = requests.get(fallback_url, headers=headers, timeout=15)
    
    if response.status_code == 200:
        # Procura pela imagem de perfil
        img_match = re.search(r'<div class="instadp-popup-body">.*?<img[^>]+src="([^"]+)"', response.text, re.DOTALL)
        if img_match:
            profile_pic_url = img_match.group(1)
            return _process_profile_pic_url(profile_pic_url, output_format, save_dir, {"username": username})
    
    raise Exception("Profile Picture Finder service did not return a profile picture")

def _process_profile_pic_url(profile_pic_url, output_format, save_dir, metadata=None):
    """
    Processa a URL da foto de perfil conforme o formato de saída desejado
    """
    # Remover parâmetros e garantir que termine com .jpg
    if '?' in profile_pic_url:
        profile_pic_url = profile_pic_url.split('?')[0]
    
    if not profile_pic_url.endswith('.jpg'):
        profile_pic_url += '.jpg'
    
    if output_format == 'url':
        return profile_pic_url
    
    elif output_format == 'json':
        return metadata if metadata else {"profile_pic_url": profile_pic_url}
    
    # Para base64 e file, baixamos a imagem
    img_response = requests.get(profile_pic_url, timeout=10)
    img_response.raise_for_status()
    
    if output_format == 'base64':
        img_b64 = base64.b64encode(img_response.content).decode('utf-8')
        return f"data:image/jpeg;base64,{img_b64}"
    
    elif output_format == 'file':
        if not save_dir:
            save_dir = os.getcwd()
        
        # Create directory if it doesn't exist
        os.makedirs(save_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(save_dir, f"{metadata.get('username', 'instagram')}_profile_pic.jpg")
        with open(file_path, 'wb') as f:
            f.write(img_response.content)
        
        return file_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Get Instagram profile picture URL or image data')
    parser.add_argument('username', help='Instagram username')
    parser.add_argument('--format', choices=['url', 'json', 'base64', 'file'], default='url',
                        help='Format to return the image data')
    parser.add_argument('--save-dir', help='Directory to save file when output_format is "file"')
    parser.add_argument('--fb-token', help='Facebook Graph API token for direct access')
    
    args = parser.parse_args()
    
    try:
        result = get_instagram_profile_pic(args.username, output_format=args.format, save_dir=args.save_dir, fb_token=args.fb_token)
        
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(result)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
