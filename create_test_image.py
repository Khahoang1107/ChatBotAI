#!/usr/bin/env python
"""Create a simple test invoice image"""

from PIL import Image, ImageDraw, ImageFont

# Create image
img = Image.new('RGB', (600, 400), color='white')
draw = ImageDraw.Draw(img)

# Draw invoice content
text = """
HOA DON
Invoice Number: INV-2025-TEST-001
Date: 21/10/2025

From: ABC Corporation
To: XYZ Company

Item 1: Service Fee         5,000,000 VND
Item 2: Product             3,500,000 VND

Total: 8,500,000 VND
Tax (10%): 850,000 VND

Grand Total: 9,350,000 VND
"""

# Draw text
draw.text((20, 20), text, fill='black')

# Save image
img.save('test_invoice.jpg')
print("[+] Test invoice image created: test_invoice.jpg")
