#!/usr/bin/env python3

import requests
import os
import base64
import json
import re
from io import BytesIO

# Token do ImgBB
IMGBB_API_KEY = "755ab7dc4f57880bb1322fca5b572c57"

def process_instagram_image_url(image_url, output_format='url', save_dir=None):
    """
    Process an Instagram image URL, upload to ImgBB and return clean URL
    
    Args:
        image_url (str): Direct Instagram image URL
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
    # Remover '@' do início da URL, se existir
    if image_url.startswith('@'):
        image_url = image_url[1:]
    
    try:
        # Download da imagem
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        image_data = response.content
        
        # Determinar um nome para a imagem a partir da URL
        # Extrai o nome do arquivo da URL (antes dos parâmetros)
        image_name = "instagram_image"
        if '/' in image_url:
            parts = image_url.split('/')
            for part in reversed(parts):
                if part and '.' in part:
                    name_part = part.split('?')[0]
                    if name_part:
                        image_name = name_part
                        break
        
        # Upload para o ImgBB
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        imgbb_url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_API_KEY,
            "image": image_base64,
            "name": image_name
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
            "thumbnail": imgbb_data['data']['thumb']['url'] if 'thumb' in imgbb_data['data'] else None,
            "original_url": image_url
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
            file_path = os.path.join(save_dir, image_name)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            result['file_path'] = file_path
            return result
        
    except Exception as e:
        return {"error": f"Erro ao processar URL da imagem: {str(e)}"}

# Mantenha a função original para compatibilidade
def get_instagram_profile_pic(username, output_format='url', save_dir=None, fb_token=None):
    # Código original...
    return {"error": "Essa função foi substituída. Use process_instagram_image_url."}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Instagram image URL via ImgBB')
    parser.add_argument('url', help='Instagram image URL')
    parser.add_argument('--format', choices=['url', 'json', 'base64', 'file'], default='url',
                        help='Format to return the image data')
    parser.add_argument('--save-dir', help='Directory to save file when output_format is "file"')
    
    args = parser.parse_args()
    
    try:
        result = process_instagram_image_url(args.url, output_format=args.format, save_dir=args.save_dir)
        
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
