import os
import imghdr
import sys

def verify_images(directory):
    print(f"--- Verifying images in {directory} ---")
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        return False

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    all_ok = True

    for filename in files:
        filepath = os.path.join(directory, filename)
        size = os.path.getsize(filepath)
        
        # Check size > 1KB
        if size < 1024:
            print(f"❌ {filename}: Too small ({size} bytes). Likely an error page.")
            all_ok = False
            continue
            
        # Check file type
        img_type = imghdr.what(filepath)
        if img_type not in ['jpeg', 'png', 'gif', 'webp']:
            print(f"❌ {filename}: Not a valid image (detected as {img_type}).")
            all_ok = False
            continue
            
        print(f"✅ {filename}: OK ({img_type}, {size/1024:.1f} KB)")

    return all_ok

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Verify images in a directory.")
    parser.add_argument("--dir", type=str, default="imgs/2026/01/26", help="Directory to verify")
    args = parser.parse_args()
    
    if not verify_images(args.dir):
        sys.exit(1)
    else:
        print(f"--- All images in {args.dir} verified successfully ---")
        sys.exit(0)
