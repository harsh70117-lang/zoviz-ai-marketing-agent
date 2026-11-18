import argparse
import os
import re
import sys

import requests

# --- Configuration ---
# The API key is read from the environment. Never hardcode it in the source.
API_KEY = os.getenv("ZOVIZ_API_KEY")
BASE_URL = "https://developer.zoviz.com/api/v1"
OUTPUT_DIR = "generated_assets"
DEFAULT_URL = "https://stripe.com"


def require_api_key():
    """Stop early, with a clear message, if the API key is not set."""
    if not API_KEY:
        sys.exit(
            "[!] ZOVIZ_API_KEY is not set.\n"
            "    macOS/Linux:        export ZOVIZ_API_KEY=\"your-key-here\"\n"
            "    Windows PowerShell: $env:ZOVIZ_API_KEY=\"your-key-here\""
        )


def setup_environment():
    """Create a directory for output if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[*] Created output directory: {OUTPUT_DIR}/")


def get_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def safe_filename(name):
    """Turn a brand name into a safe filename (no slashes, dots or odd characters)."""
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")
    return cleaned or "brand"


def extract_brand_data(website_url):
    """Fetches brand identity (name, description, colors) from Zoviz.

    Returns (name, description, colors), or None if the request failed or the
    response is missing the brand name or description.
    """
    print(f"[*] Extracting brand data from: {website_url}")
    endpoint = f"{BASE_URL}/brand-extractor"
    payload = {"url": website_url}

    try:
        response = requests.post(endpoint, headers=get_headers(), json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Error extracting brand data: {e}")
        return None

    data = response.json().get("result") or {}
    brand_name = (data.get("brand_name") or "").strip()
    brand_desc = (data.get("description") or "").strip()
    brand_colors = data.get("brand_colors") or []

    missing = [
        field
        for field, value in (("brand_name", brand_name), ("description", brand_desc))
        if not value
    ]
    if missing:
        print(f"[!] The extractor did not return: {', '.join(missing)}. Stopping.")
        return None

    return brand_name, brand_desc, brand_colors


def generate_visual(brand_name, brand_desc, brand_colors):
    """Generates an image based on the extracted brand data. Returns True on success."""
    print(f"[*] Generating image for: {brand_name}")

    # Build the prompt from the brand's own data
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
        "dimension": "1024x1024",
    }

    try:
        response = requests.post(endpoint, headers=get_headers(), json=payload, timeout=120)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[!] Error generating image: {e}")
        return False

    if "image" not in response.headers.get("Content-Type", ""):
        print(f"[!] Received JSON instead of image: {response.text}")
        return False

    filepath = os.path.join(OUTPUT_DIR, f"{safe_filename(brand_name)}_social_post.png")
    with open(filepath, "wb") as f:
        f.write(response.content)
    print(f"[+] SUCCESS: Image saved to {filepath}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Extract a brand from a website and generate a matching social visual with Zoviz."
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=DEFAULT_URL,
        help=f"Website to extract the brand from (default: {DEFAULT_URL})",
    )
    args = parser.parse_args()

    print("--- Zoviz AI Marketing Agent ---")
    require_api_key()
    setup_environment()

    brand = extract_brand_data(args.url)
    if brand is None:
        sys.exit("[!] Workflow aborted due to extraction error.")

    name, desc, colors = brand
    print(f"[+] Brand Identified: {name}")
    print(f"[+] Brand Colors: {colors}")

    if not generate_visual(name, desc, colors):
        sys.exit(1)


if __name__ == "__main__":
    main()
