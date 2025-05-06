#!/usr/bin/env python3

import requests
import json
import argparse
import os
from get_profile_pic import get_instagram_profile_pic


def create_nifty_image_with_instagram_profile(instagram_username, nifty_template_id, nifty_api_key):
    """
    Create a Nifty Image using an Instagram profile picture
    
    Args:
        instagram_username (str): Instagram username
        nifty_template_id (str): Nifty Images template ID
        nifty_api_key (str): Nifty Images API key
    
    Returns:
        str: URL of the created Nifty Image
    """
    # Get Instagram profile picture as base64
    try:
        profile_pic_base64 = get_instagram_profile_pic(instagram_username, output_format='base64')
    except Exception as e:
        raise Exception(f"Failed to get Instagram profile picture: {str(e)}")
    
    # Remove the data:image/jpeg;base64, prefix if needed by Nifty
    if profile_pic_base64.startswith('data:image/jpeg;base64,'):
        profile_pic_base64 = profile_pic_base64[len('data:image/jpeg;base64,'):]
    
    # Create Nifty Image
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {nifty_api_key}'
    }
    
    payload = {
        'templateId': nifty_template_id,
        'data': {
            'instagram_profile_pic': profile_pic_base64
            # Add other template variables as needed
        }
    }
    
    response = requests.post(
        'https://api.niftyimages.com/render',
        headers=headers,
        data=json.dumps(payload)
    )
    
    response.raise_for_status()
    result = response.json()
    
    return result.get('url')


def main():
    parser = argparse.ArgumentParser(description='Create Nifty Image with Instagram profile picture')
    parser.add_argument('instagram_username', help='Instagram username')
    parser.add_argument('--template-id', required=True, help='Nifty Images template ID')
    parser.add_argument('--api-key', required=True, help='Nifty Images API key')
    args = parser.parse_args()
    
    try:
        nifty_url = create_nifty_image_with_instagram_profile(
            args.instagram_username,
            args.template_id,
            args.api_key
        )
        print(f"Nifty Image created successfully: {nifty_url}")
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())