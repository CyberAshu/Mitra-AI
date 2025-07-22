#!/usr/bin/env python3
"""
Test script for face verification API
Usage: python test_face_verify.py <image_path>
"""

import base64
import json
import sys
import requests
import os

def encode_image_to_base64(image_path):
    """Convert image file to base64 string"""
    try:
        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            return base64_string
    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found.")
        return None
    except Exception as e:
        print(f"Error reading image: {e}")
        return None

def test_face_verification(image_path, token, tolerance=None):
    """Test face verification API"""
    
    # Encode image
    base64_image = encode_image_to_base64(image_path)
    if not base64_image:
        return
    
    # API endpoint
    url = "http://127.0.0.1:8000/api/v1/face/verify"
    
    # Headers
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Request data
    data = {
        "image_data": base64_image
    }
    
    if tolerance is not None:
        data["tolerance"] = tolerance
    
    print(f"Testing face verification with image: {image_path}")
    print(f"Image size: {len(base64_image)} characters (base64)")
    print(f"URL: {url}")
    print("Sending request...")
    
    try:
        # Send request
        response = requests.post(url, headers=headers, json=data)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Also print the curl command for reference
        print(f"\n" + "="*50)
        print("Equivalent curl command:")
        print(f"curl -X 'POST' \\")
        print(f"  '{url}' \\")
        print(f"  -H 'accept: application/json' \\")
        print(f"  -H 'Authorization: Bearer {token}' \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{json.dumps(data)}'")
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {response.text}")

def main():
    # Your JWT token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBeXVzaCIsInVzZXJfaWQiOiIyY2UzOWFjMy1iZjQzLTQwMGItODE0MC0yZjQ0ZGMzOThkMWQiLCJleHAiOjE3NTMxOTU2MDB9.vF1KgP3swWfTpwncv120BFAK1G4ykC3bKkF1d4N2BRQ"
    
    if len(sys.argv) < 2:
        print("Usage: python test_face_verify.py <image_path> [tolerance]")
        print("Example: python test_face_verify.py ./test_image.jpg 0.6")
        
        # Check if there are any uploaded images
        uploads_dir = "./uploads/faces"
        if os.path.exists(uploads_dir):
            print(f"\nAvailable images in {uploads_dir}:")
            for file in os.listdir(uploads_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    print(f"  - {file}")
        return
    
    image_path = sys.argv[1]
    tolerance = float(sys.argv[2]) if len(sys.argv) > 2 else None
    
    test_face_verification(image_path, token, tolerance)

if __name__ == "__main__":
    main()
