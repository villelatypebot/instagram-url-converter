#!/usr/bin/env python3

import requests
import os
import base64
import json
import re
from io import BytesIO

# Token do ImgBB
IMGBB_API_KEY = "755ab7dc4f57880bb1322fca5b572c57"

def get_instagram_profile_pic(username, output_format='url', save_dir=None, fb_token=None):
    """
    Get Instagram profile picture and upload to ImgBB
    
    Args:
        username (str): Instagram username
        output_format (str): Format to return the image data
            - 'url': Return direct ImgBB image URL with jpg extension
            - 'json': Return all data including ImgBB response
            - 'base64': Return base64 encoded image
            - 'file': Save file to disk and return path
        save_dir (str, optional): Directory to save file when output_format is 'file'
    
    Returns:
        Based on output_format:
        - url: string with direct ImgBB image URL ending with .jpg
        - json: dictionary with all profile data
        - base64: base64 encoded image with data:image/jpeg;base64 prefix
        - file: path to saved file
    """
    username = username.lower().strip()
    
    # Primeiro, tente obter a imagem do perfil do Instagram
    image_data = None
    error_messages = []
    
    # Tentativa 1: URL direta do Instagram
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        instagram_url = f"https://www.instagram.com/{username}/"
        response = requests.get(instagram_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Tente encontrar a URL da imagem no HTML
            html_content = response.text
            
            # Vários padrões para encontrar a imagem
            patterns = [
                r'<meta property="og:image" content="([^"]+)"',
                r'"profile_pic_url":"([^"]+)"',
                r'"profile_pic_url_hd":"([^"]+)"',
                r'<img[^>]+class="[^"]*(?:profile-pic|_aa8j)[^"]*"[^>]+src="([^"]+)"',
                r'<img[^>]+(?:data-testid="user-avatar"|alt="[^"]* profile picture")[^>]+src="([^"]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html_content)
                if match:
                    profile_pic_url = match.group(1).replace("\\u0026", "&")
                    
                    # Baixe a imagem
                    img_response = requests.get(profile_pic_url, timeout=10)
                    if img_response.status_code == 200:
                        image_data = img_response.content
                        break
        
        if not image_data:
            error_messages.append("Não foi possível extrair a imagem da página do Instagram")
    
    except Exception as e:
        error_messages.append(f"Erro ao acessar Instagram: {str(e)}")
    
    # Tentativa 2: Use a API não oficial
    if not image_data:
        try:
            api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            api_headers = headers.copy()
            api_headers['x-ig-app-id'] = '936619743392459'  # Instagram web app ID
            
            response = requests.get(api_url, headers=api_headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and 'user' in data['data']:
                    user_data = data['data']['user']
                    profile_pic_url = user_data.get('profile_pic_url_hd', user_data.get('profile_pic_url', None))
                    
                    if profile_pic_url:
                        img_response = requests.get(profile_pic_url, timeout=10)
                        if img_response.status_code == 200:
                            image_data = img_response.content
        
        except Exception as e:
            error_messages.append(f"Erro na API não oficial: {str(e)}")
    
    # Se todas as tentativas falharem, use um fallback ou retorne erro
    if not image_data:
        return {"error": f"Falha ao obter imagem de perfil para @{username}. Erros: {'; '.join(error_messages)}"}
    
    # Faça upload para o ImgBB
    try:
        # Converta os dados da imagem para base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Faça a requisição para o ImgBB
        imgbb_url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_API_KEY,
            "image": image_base64,
            "name": f"{username}_profile_pic"
        }
        
        imgbb_response = requests.post(imgbb_url, payload)
        imgbb_data = imgbb_response.json()
        
        if not imgbb_response.ok or not imgbb_data.get('success'):
            return {"error": f"Falha ao fazer upload para ImgBB: {imgbb_data.get('error', {}).get('message', 'Erro desconhecido')}"}
        
        # Obtenha as URLs resultantes
        result = {
            "direct_url": imgbb_data['data']['url'],
            "display_url": imgbb_data['data']['url_viewer'],
            "delete_url": imgbb_data['data']['delete_url'],
            "thumbnail": imgbb_data['data']['thumb']['url'] if 'thumb' in imgbb_data['data'] else None
        }
        
        # Processe o resultado conforme o formato solicitado
        if output_format == 'url':
            return result['direct_url']
        
        elif output_format == 'json':
            return result
        
        elif output_format == 'base64':
            return f"data:image/jpeg;base64,{image_base64}"
        
        elif output_format == 'file':
            if not save_dir:
                save_dir = os.getcwd()
            
            # Create directory if it doesn't exist
            os.makedirs(save_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(save_dir, f"{username}_profile_pic.jpg")
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            result['file_path'] = file_path
            return result
        
    except Exception as e:
        return {"error": f"Erro ao processar upload para ImgBB: {str(e)}"}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Get Instagram profile picture URL via ImgBB')
    parser.add_argument('username', help='Instagram username')
    parser.add_argument('--format', choices=['url', 'json', 'base64', 'file'], default='url',
                        help='Format to return the image data')
    parser.add_argument('--save-dir', help='Directory to save file when output_format is "file"')
    
    args = parser.parse_args()
    
    try:
        result = get_instagram_profile_pic(args.username, output_format=args.format, save_dir=args.save_dir)
        
        if isinstance(result, dict) and 'error' in result:
            print(f"Error: {result['error']}")
            exit(1)
        
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(result)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)
