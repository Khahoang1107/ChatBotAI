"""
Test script để verify OCR → Database → Chatbot workflow
"""

import requests
import time
import psycopg2
from psycopg2.extras import RealDictCursor

print("=" * 60)
print("🧪 TESTING OCR → DATABASE → CHATBOT WORKFLOW")
print("=" * 60)

# Step 1: Check database connection
print("\n📊 Step 1: Checking PostgreSQL connection...")
try:
    conn = psycopg2.connect(
        "postgresql://postgres:123@localhost:5432/ocr_database",
        cursor_factory=RealDictCursor
    )
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM invoices")
        before_count = cursor.fetchone()['count']
        print(f"✅ Database connected")
        print(f"   Invoices before test: {before_count}")
    
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("   Make sure PostgreSQL is running on port 5432")
    exit(1)

# Step 2: Check backend health
print("\n🔧 Step 2: Checking FastAPI backend...")
try:
    response = requests.get("http://localhost:8000/health", timeout=3)
    if response.status_code == 200:
        print(f"✅ Backend is running on port 8000")
    else:
        print(f"⚠️ Backend returned status {response.status_code}")
except Exception as e:
    print(f"❌ Backend not responding: {e}")
    print("   Start with: python fastapi_backend/main.py")
    exit(1)

# Step 3: Check chatbot health
print("\n🤖 Step 3: Checking Chatbot service...")
try:
    response = requests.get("http://localhost:5001/health", timeout=3)
    if response.status_code == 200:
        print(f"✅ Chatbot is running on port 5001")
    else:
        print(f"⚠️ Chatbot returned status {response.status_code}")
except Exception as e:
    print(f"❌ Chatbot not responding: {e}")
    print("   Start with: cd chatbot && python app.py")
    exit(1)

# Step 4: Upload test image (simulated)
print("\n📤 Step 4: Testing OCR upload...")
print("   Note: Actual file upload needs to be done from frontend or curl")
print("   Command: curl -X POST http://localhost:8000/api/ocr/upload-image -F 'file=@path/to/image.jpg'")

# Step 5: Check if database has new data
print("\n💾 Step 5: Checking database after OCR...")
time.sleep(1)  # Wait a bit
try:
    conn = psycopg2.connect(
        "postgresql://postgres:123@localhost:5432/ocr_database",
        cursor_factory=RealDictCursor
    )
    
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM invoices")
        after_count = cursor.fetchone()['count']
        
        print(f"   Invoices after test: {after_count}")
        
        if after_count > before_count:
            print(f"✅ New invoices added: {after_count - before_count}")
            
            # Show recent invoice
            cursor.execute("""
                SELECT filename, invoice_code, buyer_name, total_amount, created_at
                FROM invoices
                ORDER BY created_at DESC
                LIMIT 1
            """)
            recent = cursor.fetchone()
            print(f"\n   📄 Most recent invoice:")
            print(f"      File: {recent['filename']}")
            print(f"      Code: {recent['invoice_code']}")
            print(f"      Buyer: {recent['buyer_name']}")
            print(f"      Amount: {recent['total_amount']}")
            print(f"      Created: {recent['created_at']}")
        else:
            print(f"⚠️ No new invoices (still {after_count})")
            print(f"   Upload an image to test OCR")
    
    conn.close()
except Exception as e:
    print(f"❌ Database check failed: {e}")

# Step 6: Test chatbot query
print("\n🤖 Step 6: Testing chatbot database query...")
try:
    response = requests.post(
        "http://localhost:5001/chat",
        json={"message": "xem dữ liệu"},
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Chatbot responded")
        print(f"   Response preview: {result.get('message', '')[:200]}...")
        
        # Check if response contains real data
        if 'database' in result.get('message', '').lower() or 'invoice' in result.get('message', '').lower():
            print(f"✅ Response contains database-related content")
        else:
            print(f"⚠️ Response might not be querying database")
    else:
        print(f"❌ Chatbot returned status {response.status_code}")
        
except Exception as e:
    print(f"❌ Chatbot query failed: {e}")

print("\n" + "=" * 60)
print("🎯 TEST SUMMARY")
print("=" * 60)
print("✅ Services Status:")
print("   - PostgreSQL: Running")
print("   - FastAPI Backend: Port 8000")
print("   - Chatbot: Port 5001")
print("\n📝 Next Steps:")
print("   1. Upload image: Use frontend or curl command")
print("   2. Check logs: Backend should show 'Saved to database'")
print("   3. Ask chatbot: 'xem dữ liệu' should return real data")
print("=" * 60)
