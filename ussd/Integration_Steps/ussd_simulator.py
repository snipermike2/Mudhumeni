# ussd_simulator.py
import requests
import sys

def simulate_ussd_session():
    """Simulate a USSD session for testing"""
    session_id = "test-session-123"
    service_code = "*123#"
    phone_number = "+27123456789" 
    
    print("=== MUDHUMENI AI USSD SIMULATOR ===")
    print("Starting new USSD session...")
    print("Type 'exit' to quit, 'restart' to start new session")
    print("=" * 40)
    
    # Start session
    text = ""
    response = send_ussd_request(session_id, service_code, phone_number, text)
    
    # Continue session based on user input
    while True:
        user_input = input("\nEnter your selection: ").strip()
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'restart':
            print("\n" + "=" * 40)
            print("Starting new session...")
            text = ""
            session_id = f"test-session-{hash(str(requests.utils.default_user_agent()))}"  # New session ID
            response = send_ussd_request(session_id, service_code, phone_number, text)
            continue
        
        # Append user input to the session history
        if text:
            text += "*" + user_input
        else:
            text = user_input
        
        # Send the request
        response = send_ussd_request(session_id, service_code, phone_number, text)
        
        # If it's an END response, ask if user wants to start new session
        if response and response.startswith("END"):
            print("\n" + "-" * 40)
            restart_choice = input("Session ended. Start new session? (y/n): ").strip().lower()
            if restart_choice == 'y':
                print("\n" + "=" * 40)
                print("Starting new session...")
                text = ""
                session_id = f"test-session-{hash(str(requests.utils.default_user_agent()))}"  # New session ID
                send_ussd_request(session_id, service_code, phone_number, text)
            elif restart_choice == 'n':
                print("Goodbye!")
                break

def send_ussd_request(session_id, service_code, phone_number, text):
    """Send a USSD request to the local server"""
    data = {
        'sessionId': session_id,
        'serviceCode': service_code,
        'phoneNumber': phone_number,
        'text': text
    }
    
    try:
        response = requests.post('http://localhost:8000/ussd', data=data, timeout=10)
        
        if response.status_code == 200:
            # Clean up the response for display
            response_text = response.text
            if response_text.startswith('CON '):
                response_text = response_text[4:]  # Remove 'CON '
                print(f"\n{response_text}")
            elif response_text.startswith('END '):
                response_text = response_text[4:]  # Remove 'END '
                print(f"\n{response_text}")
                print("\n[SESSION ENDED]")
            else:
                print(f"\n{response_text}")
            
            return response.text
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure your Flask app is running on port 8000.")
        return None
    except requests.exceptions.Timeout:
        print("Error: Request timed out. Server might be busy.")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    simulate_ussd_session()