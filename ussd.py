# ussd.py - Updated with translation support
from flask import Blueprint, request, jsonify
import os
import uuid
import json
from datetime import datetime
import re

# Import translation system
from translations import translation_manager, translate, get_menu_text

# Create the blueprint
ussd_blueprint = Blueprint('ussd', __name__)

# USSD session management
ussd_sessions = {}

# Language codes for translation
LANGUAGE_CODES = {
    "1": "en",    # English
    "2": "sn",    # Shona
    "3": "nd",    # Ndebele
    "4": "zu",    # isiZulu
    "5": "xh",    # isiXhosa
    "6": "af",    # Afrikaans
    "7": "st",    # Sesotho
    "8": "tn",    # Setswana
    "9": "sw",    # Swahili
    "10": "pt"    # Portuguese
}

# Mapping of provinces for Southern Africa
PROVINCES = {
    "1": "Harare", "2": "Bulawayo", "3": "Manicaland", "4": "Mashonaland Central",
    "5": "Mashonaland East", "6": "Mashonaland West", "7": "Masvingo",
    "8": "Matabeleland North", "9": "Matabeleland South", "10": "Midlands",
    "11": "Gauteng", "12": "Western Cape", "13": "Eastern Cape", "14": "Northern Cape",
    "15": "Limpopo", "16": "Mpumalanga", "17": "Free State", "18": "North West",
    "19": "KwaZulu-Natal", "20": "Lusaka", "21": "Copperbelt", "22": "Maputo",
    "23": "Gaza", "24": "Gaborone", "25": "Other"
}

# Farming types
FARMING_TYPES = {
    "1": "subsistence", "2": "small_scale_commercial", "3": "large_scale_commercial",
    "4": "mixed_farming", "5": "livestock", "6": "crop", "7": "other"
}

@ussd_blueprint.route('/', methods=['POST'])
def ussd_handler():
    """Main USSD handler that processes all USSD requests"""
    
    # Get USSD parameters
    session_id = request.form.get('sessionId', '')
    service_code = request.form.get('serviceCode', '')
    phone_number = request.form.get('phoneNumber', '')
    text = request.form.get('text', '')
    
    # Import these functions from main app on demand
    from app import get_current_season, seasonal_crops, user_preferences, chatbot_response, sanitize_input
    
    # Create or retrieve user session
    if session_id not in ussd_sessions:
        user_id = str(uuid.uuid4())
        
        ussd_sessions[session_id] = {
            'user_id': user_id,
            'phone_number': phone_number,
            'menu_level': 0,
            'language': 'en',  # Default language
            'last_response': '',
            'context': {},
            'navigation_history': [],
            'start_time': datetime.now()
        }
        
        # Check if phone number exists in user_preferences
        for uid, prefs in user_preferences.items():
            if prefs.get('phone_number') == phone_number:
                ussd_sessions[session_id]['user_id'] = uid
                # Get user's preferred language
                ussd_sessions[session_id]['language'] = prefs.get('language', 'en')
                break
    
    # Get the current user session
    user_session = ussd_sessions[session_id]
    user_id = user_session['user_id']
    user_lang = user_session['language']
    
    # Add user ID to user_preferences if not exists
    if user_id not in user_preferences:
        user_preferences[user_id] = {
            'phone_number': phone_number,
            'language': user_lang,
            'location': '',
            'farming_type': ''
        }
    
    # Process the USSD request based on the text input
    if not text:
        # Start of USSD session - show main menu in user's language
        user_session['menu_level'] = 0
        main_menu = get_menu_text('main_menu', user_lang)
        response = "CON " + main_menu
    else:
        # Split the text by * to determine the navigation path
        navigation = text.split('*')
        current_level = navigation[-1]
        
        # Add to navigation history
        user_session['navigation_history'].append(current_level)
        
        # Determine the response based on the navigation path
        if len(navigation) == 1:
            # Main menu options
            response = handle_main_menu(user_session, current_level)
        else:
            # Sub-menu options
            response = handle_sub_menu(user_session, navigation)
    
    # Update the last response
    user_session['last_response'] = response
    
    return response

def handle_main_menu(user_session, option):
    """Handle main menu selections with translation support"""
    
    user_id = user_session['user_id']
    user_lang = user_session['language']
    
    if option == '1':
        # Farming Advice
        user_session['menu_level'] = 1
        user_session['context']['menu'] = 'advice'
        advice_menu = get_menu_text('advice_menu', user_lang)
        return "CON " + advice_menu
    
    elif option == '2':
        # Crop Recommendations
        user_session['menu_level'] = 1
        user_session['context']['menu'] = 'crop_recommendation'
        crop_menu = f"""{translate('crop_recommendations', user_lang)}
1. {translate('best_crops_location', user_lang)}
2. {translate('custom_recommendation', user_lang)}
3. {translate('return_to_menu', user_lang)}"""
        return "CON " + crop_menu
    
    elif option == '3':
        # Seasonal Information
        user_session['menu_level'] = 1
        user_session['context']['menu'] = 'seasonal_info'
        from app import get_current_season
        season = get_current_season()
        season_translated = translate(season, user_lang)
        seasonal_menu = get_menu_text('seasonal_menu', user_lang, season=season_translated)
        return "CON " + seasonal_menu
    
    elif option == '4':
        # Set My Location
        user_session['menu_level'] = 1
        user_session['context']['menu'] = 'set_location'
        
        province_menu = translate('select_province', user_lang) + "\n"
        for key, province in PROVINCES.items():
            province_menu += f"{key}. {province}\n"
        
        return "CON " + province_menu
    
    elif option == '5':
        # Set Farming Type
        user_session['menu_level'] = 1
        user_session['context']['menu'] = 'set_farming_type'
        
        farming_menu = translate('select_farming_type', user_lang) + "\n"
        for key, farm_type in FARMING_TYPES.items():
            farming_type_translated = translate(farm_type, user_lang)
            farming_menu += f"{key}. {farming_type_translated}\n"
        
        return "CON " + farming_menu
    
    elif option == '6':
        # Language Options
        user_session['menu_level'] = 1
        user_session['context']['menu'] = 'language'
        language_menu = get_menu_text('language_menu', user_lang)
        return "CON " + language_menu
    
    else:
        # Invalid option
        invalid_msg = translate('invalid_selection', user_lang)
        main_menu = get_menu_text('main_menu', user_lang)
        return "CON " + invalid_msg + ". " + main_menu

def handle_sub_menu(user_session, navigation):
    """Handle sub-menu selections with translation support"""
    
    user_id = user_session['user_id']
    user_lang = user_session['language']
    current_menu = user_session['context'].get('menu', '')
    
    if current_menu == 'advice':
        return handle_advice_menu(user_session, navigation)
    elif current_menu == 'crop_recommendation':
        return handle_crop_recommendation_menu(user_session, navigation)
    elif current_menu == 'seasonal_info':
        return handle_seasonal_info_menu(user_session, navigation)
    elif current_menu == 'set_location':
        return handle_set_location_menu(user_session, navigation)
    elif current_menu == 'set_farming_type':
        return handle_set_farming_type_menu(user_session, navigation)
    elif current_menu == 'language':
        return handle_language_menu(user_session, navigation)
    else:
        # Invalid menu - return to main menu
        user_session['menu_level'] = 0
        user_session['context'] = {}
        invalid_msg = translate('invalid_selection', user_lang)
        main_menu = get_menu_text('main_menu', user_lang)
        return "CON " + invalid_msg + ". " + main_menu

def handle_advice_menu(user_session, navigation):
    """Handle the farming advice menu with translation"""
    
    user_id = user_session['user_id']
    user_lang = user_session['language']
    current_level = navigation[-1]
    
    if len(navigation) == 2:
        if current_level == '1':
            # Planting Times
            response = get_planting_advice(user_id, user_lang)
            return "END " + response
        
        elif current_level == '2':
            # Fertilizer Use
            response = get_fertilizer_advice(user_id, user_lang)
            return "END " + response
        
        elif current_level == '3':
            # Pest Control
            response = get_pest_control_advice(user_id, user_lang)
            return "END " + response
        
        elif current_level == '4':
            # Irrigation
            response = get_irrigation_advice(user_id, user_lang)
            return "END " + response
        
        elif current_level == '5':
            # Harvesting
            response = get_harvesting_advice(user_id, user_lang)
            return "END " + response
        
        elif current_level == '6':
            # Ask a Question
            question_prompt = translate('type_farming_question', user_lang, 
                                      default="Type your farming question:")
            return "CON " + question_prompt
        
        else:
            # Invalid option
            invalid_msg = translate('invalid_selection', user_lang)
            advice_menu = get_menu_text('advice_menu', user_lang)
            return "CON " + invalid_msg + ". " + advice_menu
    
    elif len(navigation) == 3 and navigation[-2] == '6':
        # Process user's question
        question = current_level
        response = ask_farming_question(user_id, question, user_lang)
        return "END " + response
    
    else:
        # Invalid navigation
        invalid_msg = translate('invalid_selection', user_lang)
        advice_menu = get_menu_text('advice_menu', user_lang)
        return "CON " + invalid_msg + ". " + advice_menu

def handle_language_menu(user_session, navigation):
    """Handle the language selection menu"""
    
    from app import user_preferences
    
    user_id = user_session['user_id']
    current_level = navigation[-1]
    
    if len(navigation) == 2:
        # Set the language based on the selected option
        if current_level in LANGUAGE_CODES:
            new_language = LANGUAGE_CODES[current_level]
            
            # Update user preferences
            if user_id not in user_preferences:
                user_preferences[user_id] = {}
            
            user_preferences[user_id]['language'] = new_language
            user_session['language'] = new_language
            
            # Get language name in the new language
            language_name = translation_manager.supported_languages.get(new_language, new_language)
            
            # Response in the newly selected language
            success_msg = translate('language_set', new_language, 
                                  default="Your language has been set to") + f" {language_name}."
            return "END " + success_msg
        else:
            # Invalid option
            current_lang = user_session['language']
            invalid_msg = translate('invalid_selection', current_lang)
            language_menu = get_menu_text('language_menu', current_lang)
            return "CON " + invalid_msg + ". " + language_menu
    
    else:
        # Invalid navigation
        current_lang = user_session['language']
        invalid_msg = translate('invalid_selection', current_lang)
        language_menu = get_menu_text('language_menu', current_lang)
        return "CON " + invalid_msg + ". " + language_menu

def handle_set_location_menu(user_session, navigation):
    """Handle the set location menu with translation"""
    
    from app import user_preferences
    
    user_id = user_session['user_id']
    user_lang = user_session['language']
    current_level = navigation[-1]
    
    if len(navigation) == 2:
        # Set the location based on the selected province
        if current_level in PROVINCES:
            location = PROVINCES[current_level]
            if user_id not in user_preferences:
                user_preferences[user_id] = {}
            
            user_preferences[user_id]['location'] = location
            
            success_msg = translate('location_set', user_lang) + f" {location}."
            return "END " + success_msg
        else:
            # Invalid option
            invalid_msg = translate('invalid_selection', user_lang)
            province_menu = translate('select_province', user_lang) + "\n"
            for key, province in PROVINCES.items():
                province_menu += f"{key}. {province}\n"
            
            return "CON " + invalid_msg + ". " + province_menu
    
    else:
        # Invalid navigation
        invalid_msg = translate('invalid_selection', user_lang)
        province_menu = translate('select_province', user_lang) + "\n"
        for key, province in PROVINCES.items():
            province_menu += f"{key}. {province}\n"
        
        return "CON " + invalid_msg + ". " + province_menu

def handle_set_farming_type_menu(user_session, navigation):
    """Handle the set farming type menu with translation"""
    
    from app import user_preferences
    
    user_id = user_session['user_id']
    user_lang = user_session['language']
    current_level = navigation[-1]
    
    if len(navigation) == 2:
        # Set the farming type based on the selected option
        if current_level in FARMING_TYPES:
            farming_type = FARMING_TYPES[current_level]
            if user_id not in user_preferences:
                user_preferences[user_id] = {}
            
            user_preferences[user_id]['farming_type'] = farming_type
            
            farming_type_translated = translate(farming_type, user_lang)
            success_msg = translate('farming_type_set', user_lang) + f" {farming_type_translated}."
            return "END " + success_msg
        else:
            # Invalid option
            invalid_msg = translate('invalid_selection', user_lang)
            farming_menu = translate('select_farming_type', user_lang) + "\n"
            for key, farm_type in FARMING_TYPES.items():
                farming_type_translated = translate(farm_type, user_lang)
                farming_menu += f"{key}. {farming_type_translated}\n"
            
            return "CON " + invalid_msg + ". " + farming_menu
    
    else:
        # Invalid navigation
        invalid_msg = translate('invalid_selection', user_lang)
        farming_menu = translate('select_farming_type', user_lang) + "\n"
        for key, farm_type in FARMING_TYPES.items():
            farming_type_translated = translate(farm_type, user_lang)
            farming_menu += f"{key}. {farming_type_translated}\n"
        
        return "CON " + invalid_msg + ". " + farming_menu

def handle_crop_recommendation_menu(user_session, navigation):
    """Handle the crop recommendation menu with translation"""
    
    from app import user_preferences
    
    user_id = user_session['user_id']
    user_lang = user_session['language']
    current_level = navigation[-1]
    
    if len(navigation) == 2:
        if current_level == '1':
            # Best Crops for My Location
            if user_preferences.get(user_id, {}).get('location'):
                response = get_location_crops(user_id, user_lang)
                return "END " + response
            else:
                no_location_msg = translate('no_location_set', user_lang, 
                                          default="You need to set your location first")
                province_menu = translate('select_province', user_lang) + "\n"
                for key, province in list(PROVINCES.items())[:10]:  # Limit for USSD
                    province_menu += f"{key}. {province}\n"
                
                return "CON " + no_location_msg + ".\n" + province_menu
        
        elif current_level == '2':
            # Custom Recommendation (Soil Data)
            user_session['context']['submenu'] = 'soil_data'
            nitrogen_prompt = translate('enter_nitrogen', user_lang)
            return "CON " + nitrogen_prompt
        
        elif current_level == '3':
            # Return to Main Menu
            user_session['menu_level'] = 0
            user_session['context'] = {}
            main_menu = get_menu_text('main_menu', user_lang)
            return "CON " + main_menu
        
        else:
            # Invalid option
            invalid_msg = translate('invalid_selection', user_lang)
            crop_menu = f"""{translate('crop_recommendations', user_lang)}
1. {translate('best_crops_location', user_lang)}
2. {translate('custom_recommendation', user_lang)}
3. {translate('return_to_menu', user_lang)}"""
            return "CON " + invalid_msg + ". " + crop_menu
    
    elif user_session['context'].get('submenu') == 'soil_data':
        # Process soil data input
        return handle_soil_data_input(user_session, navigation)
    
    else:
        # Invalid navigation
        invalid_msg = translate('invalid_selection', user_lang)
        crop_menu = f"""{translate('crop_recommendations', user_lang)}
1. {translate('best_crops_location', user_lang)}
2. {translate('custom_recommendation', user_lang)}
3. {translate('return_to_menu', user_lang)}"""
        return "CON " + invalid_msg + ". " + crop_menu

def handle_seasonal_info_menu(user_session, navigation):
    """Handle the seasonal information menu with translation"""
    
    from app import get_current_season
    
    user_id = user_session['user_id']
    user_lang = user_session['language']
    current_level = navigation[-1]
    season = get_current_season()
    season_translated = translate(season, user_lang)
    
    if len(navigation) == 2:
        if current_level == '1':
            # View Recommended Crops
            from app import seasonal_crops
            crops_list = [translate(crop, user_lang) for crop in seasonal_crops[season][:5]]
            crops = ", ".join(crops_list)
            recommended_msg = translate('recommended_crops', user_lang)
            return "END " + recommended_msg + f" {season_translated}:\n" + crops
        
        elif current_level == '2':
            # View Farming Activities
            activities = get_seasonal_activities(season, user_lang)
            activities_msg = translate('farming_activities', user_lang)
            return "END " + activities_msg + f" {season_translated}:\n" + activities
        
        elif current_level == '3':
            # View Weather Guidance
            guidance = get_weather_guidance(season, user_id, user_lang)
            weather_msg = translate('weather_guidance', user_lang)
            return "END " + weather_msg + f" {season_translated}:\n" + guidance
        
        elif current_level == '4':
            # Return to Main Menu
            user_session['menu_level'] = 0
            user_session['context'] = {}
            main_menu = get_menu_text('main_menu', user_lang)
            return "CON " + main_menu
        
        else:
            # Invalid option
            invalid_msg = translate('invalid_selection', user_lang)
            seasonal_menu = get_menu_text('seasonal_menu', user_lang, season=season_translated)
            return "CON " + invalid_msg + ". " + seasonal_menu
    
    else:
        # Invalid navigation
        invalid_msg = translate('invalid_selection', user_lang)
        seasonal_menu = get_menu_text('seasonal_menu', user_lang, season=season_translated)
        return "CON " + invalid_msg + ". " + seasonal_menu

def handle_soil_data_input(user_session, navigation):
    """Handle the soil data input for crop recommendations with translation"""
    
    from app import user_preferences, validate_recommendation_data
    
    user_id = user_session['user_id']
    user_lang = user_session['language']
    
    # The expected order of inputs
    soil_parameters = [
        'nitrogen', 'phosphorus', 'potassium', 'temperature', 
        'humidity', 'ph', 'rainfall'
    ]
    
    # Calculate which parameter we're currently collecting
    param_index = len(navigation) - 2
    
    # If we've collected all parameters
    if param_index >= len(soil_parameters):
        # Process the collected data
        soil_data = {'inputs': {}}
        
        # Extract values from navigation
        for i, param in enumerate(soil_parameters):
            try:
                soil_data['inputs'][param] = float(navigation[i + 2])
            except (ValueError, IndexError):
                error_msg = translate('invalid_input', user_lang)
                return "END " + error_msg
        
        # Add user location if available
        if user_preferences.get(user_id, {}).get('location'):
            soil_data['inputs']['province'] = user_preferences[user_id]['location']
        
        # Validate the data
        is_valid, message = validate_recommendation_data(soil_data)
        if not is_valid:
            validation_msg = translate('data_validation_failed', user_lang)
            return "END " + validation_msg
        
        # Get recommendation
        recommendation = get_crop_recommendation(user_id, soil_data, user_lang)
        return "END " + recommendation
    
    # Still collecting parameters
    current_param = soil_parameters[param_index]
    
    # Validate the previous input
    if param_index > 0:
        previous_param = soil_parameters[param_index - 1]
        try:
            value = float(navigation[-1])
            # Validation with translated error messages
            if previous_param == 'nitrogen' and (value < 0 or value > 150):
                return "CON " + translate('invalid_nitrogen', user_lang)
            elif previous_param == 'phosphorus' and (value < 0 or value > 150):
                return "CON " + translate('invalid_phosphorus', user_lang)
            elif previous_param == 'potassium' and (value < 0 or value > 150):
                return "CON " + translate('invalid_potassium', user_lang)
            elif previous_param == 'temperature' and (value < 0 or value > 50):
                return "CON " + translate('invalid_temperature', user_lang)
            elif previous_param == 'humidity' and (value < 0 or value > 100):
                return "CON " + translate('invalid_humidity', user_lang)
            elif previous_param == 'ph' and (value < 0 or value > 14):
                return "CON " + translate('invalid_ph', user_lang)
            elif previous_param == 'rainfall' and (value < 0 or value > 5000):
                return "CON " + translate('invalid_rainfall', user_lang)
        except ValueError:
            return "CON " + translate('invalid_input', user_lang)
    
    # Prompt for the next parameter in user's language
    next_param_key = f"enter_{current_param}"
    prompt = translate(next_param_key, user_lang)
    
    return "CON " + prompt

# Utility functions with translation support
def get_planting_advice(user_id, user_lang):
    """Get planting advice in user's language"""
    from app import get_current_season, user_preferences, chatbot_response
    
    season = get_current_season()
    season_translated = translate(season, user_lang)
    location = user_preferences.get(user_id, {}).get('location', 'Southern Africa')
    
    # Create localized advice
    planting_advice_template = translate('planting_advice', user_lang, 
                                       default="Best time to plant in your area is {season}. Consider local weather patterns.")
    
    response = planting_advice_template.format(season=season_translated)
    
    return format_ussd_response(response)

def get_fertilizer_advice(user_id, user_lang):
    """Get fertilizer advice in user's language"""
    from app import user_preferences
    
    location = user_preferences.get(user_id, {}).get('location', 'Southern Africa')
    farming_type = user_preferences.get(user_id, {}).get('farming_type', 'crop farming')
    farming_type_translated = translate(farming_type, user_lang)
    
    fertilizer_advice = translate('fertilizer_advice', user_lang,
                                default="For {crop}, apply balanced fertilizer before planting and top-dress during growth.")
    
    response = fertilizer_advice.format(crop=farming_type_translated)
    
    return format_ussd_response(response)

def get_pest_control_advice(user_id, user_lang):
    """Get pest control advice in user's language"""
    from app import get_current_season
    
    season = get_current_season()
    season_translated = translate(season, user_lang)
    
    pest_advice = translate('pest_advice', user_lang,
                           default="Common pests in {season} include various insects. Use integrated pest management.")
    
    response = pest_advice.format(season=season_translated)
    
    return format_ussd_response(response)

def get_irrigation_advice(user_id, user_lang):
    """Get irrigation advice in user's language"""
    irrigation_advice = translate('irrigation_advice', user_lang,
                                default="Water requirements vary by crop and season. Monitor soil moisture regularly.")
    
    return format_ussd_response(irrigation_advice)

def get_harvesting_advice(user_id, user_lang):
    """Get harvesting advice in user's language"""
    harvest_advice = translate('harvest_advice', user_lang,
                              default="Harvest when crops reach maturity. Check for proper moisture content.")
    
    return format_ussd_response(harvest_advice)

def ask_farming_question(user_id, question, user_lang):
    """Process a custom farming question with translation"""
    from app import chatbot_response, sanitize_input
    
    # Sanitize the input
    question = sanitize_input(question)
    
    # Get the response from the chatbot
    response = chatbot_response(question, user_id)
    
    # If user language is not English, apply basic translation
    if user_lang != 'en':
        response = translation_manager.translate_response(response, user_lang)
    
    return format_ussd_response(response)

def get_location_crops(user_id, user_lang):
    """Get recommended crops based on user location with translation"""
    from app import get_current_season, user_preferences
    
    location = user_preferences.get(user_id, {}).get('location', 'Southern Africa')
    season = get_current_season()
    season_translated = translate(season, user_lang)
    
    # Sample crops for the current season (translated)
    from app import seasonal_crops
    crops_list = [translate(crop, user_lang) for crop in seasonal_crops[season][:3]]
    crops = ", ".join(crops_list)
    
    recommended_msg = translate('recommended_crops', user_lang)
    response = f"{recommended_msg} {location} ({season_translated}):\n{crops}"
    
    return format_ussd_response(response)

def get_crop_recommendation(user_id, soil_data, user_lang):
    """Get crop recommendation based on soil data with translation"""
    from app import get_current_season
    
    province = soil_data['inputs'].get('province', translate('your_region', user_lang, default='your region'))
    
    # Simplified recommendation logic
    nitrogen = soil_data['inputs'].get('nitrogen', 0)
    phosphorus = soil_data['inputs'].get('phosphorus', 0)
    potassium = soil_data['inputs'].get('potassium', 0)
    rainfall = soil_data['inputs'].get('rainfall', 0)
    
    if nitrogen > 100 and phosphorus > 100 and rainfall > 1000:
        crops = ["maize", "tobacco", "cotton"]
    elif 50 <= nitrogen <= 100 and rainfall > 800:
        crops = ["groundnuts", "soybeans", "sunflower"]
    elif nitrogen < 50 and rainfall < 800:
        crops = ["sorghum", "millet", "cowpeas"]
    else:
        crops = ["maize", "beans", "vegetables"]
    
    # Translate crops
    crops_translated = [translate(crop, user_lang) for crop in crops]
    
    recommended_msg = translate('recommended_crops', user_lang)
    response = f"{recommended_msg} {province}:\n"
    
    for i, crop in enumerate(crops_translated, 1):
        response += f"{i}. {crop}\n"
    
    season = get_current_season()
    season_translated = translate(season, user_lang)
    current_season_msg = translate('current_season', user_lang)
    response += f"\n{current_season_msg}: {season_translated}"
    
    return response

def get_seasonal_activities(season, user_lang):
    """Get recommended farming activities for the current season in user's language"""
    activities = {
        "summer": f"- {translate('planting', user_lang)} {translate('maize', user_lang)}, {translate('sorghum', user_lang)}\n- {translate('weeding', user_lang, default='Regular weeding')}\n- {translate('pest_control', user_lang)}\n- {translate('irrigation', user_lang)}",
        "autumn": f"- {translate('harvesting', user_lang)} {translate('summer_crops', user_lang, default='summer crops')}\n- {translate('land_preparation', user_lang, default='Land preparation')}\n- {translate('planting', user_lang)} {translate('wheat', user_lang)}\n- {translate('soil_testing', user_lang, default='Soil testing')}",
        "winter": f"- {translate('maintain_crops', user_lang, default='Maintain winter crops')}\n- {translate('prune_trees', user_lang, default='Prune fruit trees')}\n- {translate('repair_equipment', user_lang, default='Repair farm equipment')}\n- {translate('plan_planting', user_lang, default='Plan for spring planting')}",
        "spring": f"- {translate('prepare_seedbeds', user_lang, default='Prepare seedbeds')}\n- {translate('early_planting', user_lang, default='Start early planting')}\n- {translate('apply_fertilizer', user_lang, default='Apply pre-season fertilizer')}\n- {translate('prepare_irrigation', user_lang, default='Prepare irrigation systems')}"
    }
    
    return activities.get(season, translate('no_activities', user_lang, default="No specific activities for this season"))

def get_weather_guidance(season, user_id, user_lang):
    """Get weather guidance based on the season and user location in user's language"""
    from app import user_preferences
    
    location = user_preferences.get(user_id, {}).get('location', 'Southern Africa')
    
    guidance_templates = {
        "summer": translate('summer_weather_guidance', user_lang, 
                          default="Expect hot temperatures and rainfall. Ensure proper drainage and monitor for diseases."),
        "autumn": translate('autumn_weather_guidance', user_lang,
                          default="Temperatures drop. Harvest on dry days and reduce irrigation."),
        "winter": translate('winter_weather_guidance', user_lang,
                          default="Cooler temperatures and drier conditions. Protect crops from frost."),
        "spring": translate('spring_weather_guidance', user_lang,
                          default="Temperatures rise. Watch for late frosts and prepare for rains.")
    }
    
    return guidance_templates.get(season, translate('no_weather_guidance', user_lang, 
                                                  default=f"No specific weather guidance for {season}"))

def format_ussd_response(response):
    """Format a response to fit USSD constraints"""
    max_length = 160
    
    if len(response) > max_length:
        truncated = response[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > 0:
            return truncated[:last_period + 1]
        else:
            last_space = truncated.rfind(' ')
            if last_space > 0:
                return truncated[:last_space] + "..."
            else:
                return truncated + "..."
    
    return response

def handle_request():
    """Handles USSD requests - called from app.py"""
    return ussd_handler()

def register_ussd_blueprint(app):
    """Register the USSD blueprint with the Flask app"""
    app.register_blueprint(ussd_blueprint, url_prefix='/ussd')
    return ussd_blueprint