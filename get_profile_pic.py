#!/usr/bin/env python3

import requests
import re
import os
import base64
import json
from io import BytesIO
import time

def get_instagram_profile_pic(username, output_format='url', save_dir=None):
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
    
    Returns:
        Based on output_format:
        - url: string with direct image URL ending with .jpg
        - json: dictionary with all profile data
        - base64: base64 encoded image with data:image/jpeg;base64 prefix
        - file: path to saved file
    """
    username = username.lower().strip()
    
    # Request user page to get the profile picture URL
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    # First, try to get data from the public Instagram API
    try:
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
                raise Exception(f"No profile picture found for user @{username}")
            
            # Ensure URL ends with .jpg for direct image access
            if '?' in profile_pic_url:
                profile_pic_url = profile_pic_url.split('?')[0]
            
            if not profile_pic_url.endswith('.jpg'):
                profile_pic_url += '.jpg'
            
            if output_format == 'url':
                return profile_pic_url
            
            elif output_format == 'json':
                return user_data
            
            else:  # For base64 and file formats, we need to download the image
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
                    file_path = os.path.join(save_dir, f"{username}_profile_pic.jpg")
                    with open(file_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    return file_path
        
        else:
            raise Exception(f"Invalid response format from Instagram API for user @{username}")
    
    except Exception as e:
        # Fallback method: scrape the HTML page
        try:
            url = f"https://www.instagram.com/{username}/"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Find JSON data in shared_data script tag
            shared_data_match = re.search(r'<script type="text/javascript">window._sharedData = (.+?);</script>', response.text)
            
            if shared_data_match:
                shared_data = json.loads(shared_data_match.group(1))
                
                if 'entry_data' in shared_data and 'ProfilePage' in shared_data['entry_data']:
                    profile_data = shared_data['entry_data']['ProfilePage'][0]['graphql']['user']
                    profile_pic_url = profile_data.get('profile_pic_url_hd', profile_data.get('profile_pic_url', None))
                    
                    if not profile_pic_url:
                        raise Exception(f"No profile picture found for user @{username}")
                    
                    # Ensure URL ends with .jpg for direct image access
                    if '?' in profile_pic_url:
                        profile_pic_url = profile_pic_url.split('?')[0]
                    
                    if not profile_pic_url.endswith('.jpg'):
                        profile_pic_url += '.jpg'
                    
                    if output_format == 'url':
                        return profile_pic_url
                    
                    elif output_format == 'json':
                        return profile_data
                    
                    else:  # For base64 and file formats, we need to download the image
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
                            file_path = os.path.join(save_dir, f"{username}_profile_pic.jpg")
                            with open(file_path, 'wb') as f:
                                f.write(img_response.content)
                            
                            return file_path
            
            # If we reach here, try to find data in another script tag
            # Find script tags with items like "profile_pic_url"
            alt_match = re.search(r'<script type="application/ld\+json">(.+?)</script>', response.text)
            if alt_match:
                try:
                    json_data = json.loads(alt_match.group(1))
                    if 'author' in json_data and 'image' in json_data['author']:
                        profile_pic_url = json_data['author']['image']
                        
                        # Ensure URL ends with .jpg for direct image access
                        if '?' in profile_pic_url:
                            profile_pic_url = profile_pic_url.split('?')[0]
                        
                        if not profile_pic_url.endswith('.jpg'):
                            profile_pic_url += '.jpg'
                        
                        if output_format == 'url':
                            return profile_pic_url
                        
                        elif output_format == 'json':
                            return json_data['author']
                        
                        else:  # For base64 and file formats, we need to download the image
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
                                file_path = os.path.join(save_dir, f"{username}_profile_pic.jpg")
                                with open(file_path, 'wb') as f:
                                    f.write(img_response.content)
                                
                                return file_path
                except:
                    pass
                    
            # If all else fails, look for the image URL directly in the HTML
            img_match = re.search(r'<img[^>]+class="[^"]*(?:profile-pic|_aa8j)[^"]*"[^>]+src="([^"]+)"', response.text)
            if img_match:
                profile_pic_url = img_match.group(1)
                
                # Ensure URL ends with .jpg for direct image access
                if '?' in profile_pic_url:
                    profile_pic_url = profile_pic_url.split('?')[0]
                
                if not profile_pic_url.endswith('.jpg'):
                    profile_pic_url += '.jpg'
                
                if output_format == 'url':
                    return profile_pic_url
                
                elif output_format == 'json':
                    return {"profile_pic_url": profile_pic_url, "username": username}
                
                else:  # For base64 and file formats, we need to download the image
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
                        file_path = os.path.join(save_dir, f"{username}_profile_pic.jpg")
                        with open(file_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        return file_path
            
            raise Exception(f"Could not find profile picture for user @{username}")
        
        except Exception as e2:
            raise Exception(f"Failed to get Instagram profile picture: {str(e2)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Get Instagram profile picture URL or image data')
    parser.add_argument('username', help='Instagram username')
    parser.add_argument('--format', choices=['url', 'json', 'base64', 'file'], default='url',
                        help='Format to return the image data')
    parser.add_argument('--save-dir', help='Directory to save file when output_format is "file"')
    
    args = parser.parse_args()
    
    try:
        result = get_instagram_profile_pic(args.username, output_format=args.format, save_dir=args.save_dir)
        
        if args.format == 'json':
            print(json.dumps(result, indent=2))
        else:
            print(result)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1) 