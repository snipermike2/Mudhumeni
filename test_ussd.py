# test_ussd.py - Quick test for USSD functionality
import requests

def test_ussd_endpoint():
    """Test the USSD endpoint with a simple request"""
    
    print("Testing USSD endpoint...")
    
    # Test 1: Initial menu
    print("\n1. Testing initial menu...")
    data = {
        'sessionId': 'test-123',
        'serviceCode': '*123#',
        'phoneNumber': '+27123456789',
        'text': ''
    }
    
    try:
        response = requests.post('http://localhost:8000/ussd', data=data)
        print(f"Response: {response.text}")
        
        # Test 2: Select option 1 (Farming Advice)
        print("\n2. Testing option 1 (Farming Advice)...")
        data['text'] = '1'
        response = requests.post('http://localhost:8000/ussd', data=data)
        print(f"Response: {response.text}")
        
        # Test 3: Select sub-option 1 (Planting Times)
        print("\n3. Testing sub-option 1 (Planting Times)...")
        data['text'] = '1*1'
        response = requests.post('http://localhost:8000/ussd', data=data)
        print(f"Response: {response.text}")
        
        print("\n✅ USSD endpoint is working correctly!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server.")
        print("Make sure your Flask app is running on port 8000")
        print("Run: python app.py")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_ussd_endpoint()