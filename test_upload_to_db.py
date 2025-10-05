"""
Test upload image and verify database save
"""

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import time

print("🧪 TESTING OCR UPLOAD → DATABASE SAVE")
print("=" * 60)

# Check database before upload
print("\n1️⃣ Checking database BEFORE upload...")
try:
    conn = psycopg2.connect(
        "postgresql://postgres:123@localhost:5432/ocr_database",
        cursor_factory=RealDictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM invoices")
    before_count = cursor.fetchone()['count']
    print(f"   📊 Invoices before: {before_count}")
    conn.close()
except Exception as e:
    print(f"   ❌ Database error: {e}")
    exit(1)

# Test upload endpoint
print("\n2️⃣ Testing upload endpoint...")
image_path = "f:/DoAnCN/fastapi_backend/uploads/mau-hoa-don-mtt.jpg"

try:
    with open(image_path, 'rb') as f:
        files = {'file': ('mau-hoa-don-mtt.jpg', f, 'image/jpeg')}
        
        print(f"   📤 Uploading: {image_path}")
        response = requests.post(
            'http://localhost:8000/api/ocr/upload-image',
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Upload successful!")
            print(f"   📄 Filename: {result.get('filename')}")
            print(f"   🏷️  Type: {result.get('invoice_type')}")
            print(f"   💰 Amount: {result.get('total_amount')}")
            print(f"   💾 DB Saved: {result.get('saved_to_database', 'Unknown')}")
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            exit(1)
            
except FileNotFoundError:
    print(f"   ⚠️ File not found: {image_path}")
    print(f"   Using test API call instead...")
    
except Exception as e:
    print(f"   ❌ Upload error: {e}")
    exit(1)

# Wait a moment for database write
print("\n3️⃣ Waiting for database write...")
time.sleep(2)

# Check database after upload
print("\n4️⃣ Checking database AFTER upload...")
try:
    conn = psycopg2.connect(
        "postgresql://postgres:123@localhost:5432/ocr_database",
        cursor_factory=RealDictCursor
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM invoices")
    after_count = cursor.fetchone()['count']
    print(f"   📊 Invoices after: {after_count}")
    
    if after_count > before_count:
        print(f"   ✅ SUCCESS! Added {after_count - before_count} new invoice(s)")
        
        # Show newest invoice
        cursor.execute("""
            SELECT filename, invoice_code, buyer_name, total_amount, 
                   confidence_score, created_at
            FROM invoices 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        newest = cursor.fetchone()
        print(f"\n   📄 Newest invoice:")
        print(f"      File: {newest['filename']}")
        print(f"      Code: {newest['invoice_code']}")
        print(f"      Buyer: {newest['buyer_name']}")
        print(f"      Amount: {newest['total_amount']}")
        print(f"      Confidence: {float(newest['confidence_score'])*100:.1f}%")
        print(f"      Created: {newest['created_at']}")
    else:
        print(f"   ❌ FAILED! No new invoice added to database")
        print(f"   Check backend logs for 'save_to_database' errors")
    
    conn.close()
    
except Exception as e:
    print(f"   ❌ Database error: {e}")

print("\n" + "=" * 60)
print("💡 If no new invoice was added, check:")
print("   1. Backend logs for 'save_to_database' messages")
print("   2. OCR service has psycopg2 imported")
print("   3. Database connection string is correct")
print("=" * 60)
