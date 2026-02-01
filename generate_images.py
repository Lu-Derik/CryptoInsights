import os
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_image(text, filename, color=(70, 70, 70)):
    # Create a 800x600 image
    img = Image.new('RGB', (800, 600), color=color)
    d = ImageDraw.Draw(img)
    
    # Draw some text
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        font = None
        
    d.text((50, 250), text, fill=(255, 255, 255))
    
    # Save the image
    path = os.path.join('imgs/2026/02/01', filename)
    img.save(path)
    print(f"Created {path}")

# Ensure directory exists
os.makedirs('imgs/2026/02/01', exist_ok=True)

# Create images for today's news
create_placeholder_image("BTC ETF Outflow - Jan 2026", "btc_outflow.jpg", color=(255, 153, 0))
create_placeholder_image("Hyperunit Whale ETH Exit", "whale_exit.jpg", color=(59, 130, 246))
create_placeholder_image("Step Finance Hack Investigation", "step_hack.jpg", color=(239, 68, 68))
create_placeholder_image("Tether 2025 Profit Report", "tether_profit.jpg", color=(139, 92, 246))
create_placeholder_image("Strategic BTC Reserve Blueprint", "btc_reserve.jpg", color=(34, 197, 94))
create_placeholder_image("Binance Macro Risk Report", "binance_report.jpg", color=(234, 179, 8))
create_placeholder_image("White House Stablecoin Summit", "whitehouse_summit.jpg", color=(107, 114, 128))
