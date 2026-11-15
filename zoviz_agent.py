import os
import requests
import json

# --- Configuration ---
# Best practice: Use environment variables for API keys (NEVER hardcode in GitHub)
API_KEY = os.getenv("ZOVIZ_API_KEY", "YOUR_API_KEY_HERE") 
BASE_URL = "https://developer.zoviz.com/api/v1"
OUTPUT_DIR = "generated_assets"

def setup_environment():
    """Create a directory for output if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[*] Created output directory: {OUTPUT_DIR}/")

def get_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

def extract_brand_data(website_url):
    """Fetches brand identity (colors, description) from Zoviz."""
    print(f"[*] Extracting brand data from: {website_url}")
    endpoint = f"{BASE_URL}/brand-extractor"
    payload = {"url": website_url}
    
    try:
        response = requests.post(endpoint, headers=get_headers(), json=payload, timeout=60)
        response.raise_for_status()
        
        # Extracting from the 'result' object based on Zoviz API docs
        data = response.json().get("result", {})
        brand_name = data.get("brand_name", "Unknown_Brand")
        brand_desc = data.get("description", "No description available.")
        brand_colors = data.get("brand_colors", [])
        
        return brand_name, brand_desc, brand_colors
        
    except requests.exceptions.RequestException as e:
        print(f"[!] Error extracting brand data: {e}")
        return None, None, None

def generate_visual(brand_name, brand_desc, brand_colors):
    """Generates an image based on the extracted brand data."""
    print(f"[*] Generating image for: {brand_name}")
    
    # Constructing a smart prompt using the brand's actual data
    prompt = (
        f"A professional, modern social media visual for {brand_name}. "
        f"Context: {brand_desc}. "
        f"Style: Sleek, corporate, high-quality. "
        f"Color palette to use: {brand_colors}."
    )
    
    print("[*] Waiting for AI to generate image (this takes ~10-20s)...")
    endpoint = f"{BASE_URL}/image-generator-2"
    payload = {
        "prompt": prompt,
        "dimension": "1024x1024"
    }
    
    try:
        response = requests.post(endpoint, headers=get_headers(), json=payload, timeout=120)
        response.raise_for_status()
        
        if "image" in response.headers.get("Content-Type", ""):
            filepath = os.path.join(OUTPUT_DIR, f"{brand_name}_social_post.png")
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"[+] SUCCESS: Image saved to {filepath}")
        else:
            print(f"[!] Received JSON instead of image: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"[!] Error generating image: {e}")

def main():
    print("--- Zoviz AI Marketing Agent ---")
    setup_environment()
    
    # Test URL (Can be changed by the user)
    target_website = "https://stripe.com" 
    
    name, desc, colors = extract_brand_data(target_website)
    
    if name and desc:
        print(f"[+] Brand Identified: {name}")
        print(f"[+] Brand Colors: {colors}")
        generate_visual(name, desc, colors)
    else:
        print("[!] Workflow aborted due to extraction error.")

if __name__ == "__main__":
    main()