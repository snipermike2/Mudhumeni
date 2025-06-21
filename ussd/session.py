# ussd/session.py
# Store USSD sessions
ussd_sessions = {}

def handle_main_menu(user_session, option):
    """Handle main menu selections"""
    # Implement your main menu logic here
    return "CON Main menu option " + option

def handle_sub_menu(user_session, navigation):
    """Handle sub-menu selections"""
    # Implement your sub-menu logic here
    return "CON Sub-menu"