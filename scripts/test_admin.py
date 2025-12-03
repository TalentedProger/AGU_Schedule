#!/usr/bin/env python3
"""Admin panel API test script."""
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_admin_panel():
    """Test admin panel endpoints."""
    print("🔐 Testing Admin Panel")
    print("=" * 50)
    
    # Create session
    session = requests.Session()
    
    # Test 1: Login page
    print("\n1️⃣ Testing login page...")
    r = session.get(f"{BASE_URL}/admin/login")
    assert r.status_code == 200, f"Login page failed: {r.status_code}"
    print("   ✅ Login page: 200 OK")
    
    # Test 2: Login with password
    print("\n2️⃣ Testing login...")
    r = session.post(f"{BASE_URL}/admin/login", data={"username": "admin", "password": "salimoonKA23!"}, allow_redirects=True)
    assert r.status_code == 200, f"Login failed: {r.status_code}"
    assert "dashboard" in r.url or "Дашборд" in r.text or "Статистика" in r.text, "Login did not redirect to dashboard"
    print("   ✅ Login successful")
    
    # Test 3: Dashboard
    print("\n3️⃣ Testing dashboard...")
    r = session.get(f"{BASE_URL}/admin/dashboard")
    assert r.status_code == 200, f"Dashboard failed: {r.status_code}"
    print("   ✅ Dashboard: 200 OK")
    
    # Test 4: Directions list
    print("\n4️⃣ Testing directions list...")
    r = session.get(f"{BASE_URL}/admin/directions")
    assert r.status_code == 200, f"Directions failed: {r.status_code}"
    assert "Направления" in r.text or "directions" in r.text.lower()
    print("   ✅ Directions list: 200 OK")
    
    # Test 5: Pairs list
    print("\n5️⃣ Testing pairs list...")
    r = session.get(f"{BASE_URL}/admin/pairs")
    assert r.status_code == 200, f"Pairs failed: {r.status_code}"
    print("   ✅ Pairs list: 200 OK")
    
    # Test 6: Time slots
    print("\n6️⃣ Testing time slots...")
    r = session.get(f"{BASE_URL}/admin/slots")
    assert r.status_code == 200, f"Slots failed: {r.status_code}"
    print("   ✅ Time slots: 200 OK")
    
    # Test 7: Broadcast page
    print("\n7️⃣ Testing broadcast page...")
    r = session.get(f"{BASE_URL}/admin/broadcast")
    assert r.status_code == 200, f"Broadcast failed: {r.status_code}"
    print("   ✅ Broadcast page: 200 OK")
    
    # Test 8: Logs page
    print("\n8️⃣ Testing logs page...")
    r = session.get(f"{BASE_URL}/admin/logs")
    assert r.status_code == 200, f"Logs failed: {r.status_code}"
    print("   ✅ Logs page: 200 OK")
    
    # Test 9: New pair form
    print("\n9️⃣ Testing new pair form...")
    r = session.get(f"{BASE_URL}/admin/pairs/new")
    assert r.status_code == 200, f"New pair failed: {r.status_code}"
    print("   ✅ New pair form: 200 OK")
    
    # Test 10: New direction form
    print("\n🔟 Testing new direction form...")
    r = session.get(f"{BASE_URL}/admin/directions/new")
    assert r.status_code == 200, f"New direction failed: {r.status_code}"
    print("   ✅ New direction form: 200 OK")
    
    # Test 11: 404 page
    print("\n1️⃣1️⃣ Testing 404 page...")
    r = session.get(f"{BASE_URL}/nonexistent-page")
    assert r.status_code == 404, f"Expected 404, got: {r.status_code}"
    print("   ✅ 404 page: 404 Not Found (correct)")
    
    # Test 12: Logout
    print("\n1️⃣2️⃣ Testing logout...")
    r = session.post(f"{BASE_URL}/admin/logout", allow_redirects=False)
    assert r.status_code in [302, 303], f"Logout failed: {r.status_code}"
    print("   ✅ Logout: Redirect to login")
    
    print("\n" + "=" * 50)
    print("✅ All admin panel tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_admin_panel()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to admin panel. Is it running?")
        sys.exit(1)
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
