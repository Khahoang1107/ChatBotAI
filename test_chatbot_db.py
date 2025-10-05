"""
Test chatbot database query
"""

import sys
sys.path.insert(0, 'f:/DoAnCN/chatbot')

print("🤖 Testing Chatbot Database Query...")
print("=" * 60)

try:
    from utils.database_tools import get_database_tools
    
    print("\n1️⃣ Initializing database tools...")
    db_tools = get_database_tools()
    db_tools.connect()
    print("   ✅ Database tools initialized")
    
    print("\n2️⃣ Testing get_all_invoices()...")
    invoices = db_tools.get_all_invoices(limit=10)
    print(f"   ✅ Found {len(invoices)} invoices")
    
    if invoices:
        print("\n📄 Invoice List:")
        for idx, inv in enumerate(invoices, 1):
            print(f"\n   {idx}. {inv.get('filename')}")
            print(f"      • Code: {inv.get('invoice_code')}")
            print(f"      • Buyer: {inv.get('buyer_name')}")
            print(f"      • Amount: {inv.get('total_amount')}")
            print(f"      • Type: {inv.get('invoice_type')}")
    else:
        print("   ⚠️ No invoices found")
    
    print("\n3️⃣ Testing natural_language_query()...")
    result = db_tools.natural_language_query("xem dữ liệu")
    print(f"   ✅ Query type: {result.get('type')}")
    print(f"   ✅ Message: {result.get('message')}")
    print(f"   ✅ Data count: {result.get('count', 0)}")
    
    print("\n4️⃣ Testing get_statistics()...")
    stats = db_tools.get_statistics()
    print(f"   ✅ Total invoices: {stats.get('total_invoices')}")
    print(f"   ✅ Avg confidence: {stats.get('avg_confidence', 0)*100:.1f}%")
    print(f"   ✅ Recent 7 days: {stats.get('recent_7days')}")
    print(f"   ✅ Types: {stats.get('invoice_types')}")
    
    print("\n" + "=" * 60)
    print("✅ CHATBOT DATABASE TOOLS WORKING PERFECTLY!")
    print("=" * 60)
    print("\n💡 Chatbot sẽ trả về dữ liệu thật từ PostgreSQL")
    print("   khi user hỏi: 'xem dữ liệu', 'tìm kiếm', 'thống kê'")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
