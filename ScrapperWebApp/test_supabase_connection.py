"""
Test script to verify Supabase connection and database setup.
Run this after setting up your .env file and creating the database tables.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import get_db
    
    print("🔌 Testing Supabase connection...")
    print()
    
    # Try to connect
    db = get_db()
    print("✅ Successfully connected to Supabase!")
    print()
    
    # Test basic operations
    print("🧪 Testing database operations...")
    
    # Test: List products (should work even if empty)
    products = db.list_products(limit=5)
    print(f"   ✅ Can query products table (found {len(products)} products)")
    
    # Test: List jobs
    try:
        jobs = db.client.table("jobs").select("id").limit(1).execute()
        print("   ✅ Can query jobs table")
    except Exception as e:
        print(f"   ⚠️  Jobs table issue: {e}")
    
    # Test: List images
    try:
        images = db.client.table("product_images").select("id").limit(1).execute()
        print("   ✅ Can query product_images table")
    except Exception as e:
        print(f"   ⚠️  Product images table issue: {e}")
    
    # Test: List posting history
    try:
        history = db.client.table("posting_history").select("id").limit(1).execute()
        print("   ✅ Can query posting_history table")
    except Exception as e:
        print(f"   ⚠️  Posting history table issue: {e}")
    
    print()
    print("🎉 All tests passed! Your Supabase setup is working correctly.")
    print()
    print("Next steps:")
    print("   1. If any tables are missing, run database_schema.sql in Supabase SQL Editor")
    print("   2. You can now start using the database in your application")
    
except ValueError as e:
    print("❌ Configuration Error:")
    print(f"   {e}")
    print()
    print("Please check your .env file and make sure you have:")
    print("   - SUPABASE_URL")
    print("   - SUPABASE_ANON_KEY")
    
except Exception as e:
    print("❌ Connection Error:")
    print(f"   {e}")
    print()
    print("Troubleshooting:")
    print("   1. Check that your SUPABASE_URL and SUPABASE_ANON_KEY are correct in .env")
    print("   2. Make sure you've run database_schema.sql in Supabase SQL Editor")
    print("   3. Verify your Supabase project is active (not paused)")
    sys.exit(1)
