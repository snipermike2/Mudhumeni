# Complete app.py with AI-powered USSD

from flask import Flask, render_template, request, jsonify, send_from_directory, session, make_response, redirect, url_for
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import os
import shutil
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pickle
import json
import requests
from datetime import datetime
import uuid
import re
from functools import wraps
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import csv
from io import StringIO
from bson.objectid import ObjectId

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, 
    static_url_path='', 
    static_folder='static',
    template_folder='templates')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

# Initialize global variables
llm = None
user_preferences = {}  # Store user preferences
ussd_sessions = {}     # Store USSD sessions

# USSD menu structure
MAIN_MENU = """🌾 Mudhumeni AI Farm Guide
1. Get Farming Advice
2. Crop Recommendations  
3. Current Season Info
4. Set My Location
5. Set Farming Type
6. Language Options
0. Chat with AI Assistant
"""

# Define seasons in Southern Africa
def get_current_season():
    current_month = datetime.now().month
    if 3 <= current_month <= 5:
        return "autumn"
    elif 6 <= current_month <= 8:
        return "winter"
    elif 9 <= current_month <= 11:
        return "spring"
    else:
        return "summer"

# Define common crops by season in Southern Africa
seasonal_crops = {
    "summer": ["maize", "sorghum", "millet", "groundnuts", "cotton", "soybeans", "sunflower", "tobacco", "vegetables"],
    "autumn": ["winter wheat", "barley", "potatoes", "vegetable harvest", "land preparation"],
    "winter": ["wheat", "barley", "oats", "peas", "leafy greens", "onions", "garlic"],
    "spring": ["maize preparation", "tobacco seedbeds", "cotton preparation", "vegetable planting", "soil preparation"]
}

# Define the LLM - Using Groq
def initialize_llm():
    """Initializes the Groq language model with Llama."""
    
    api_key = os.environ.get("GROQ_API_KEY", "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")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    # Initialize Groq with Llama
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.2,
        max_tokens=4096,
    )
    return llm

# MongoDB Connection Setup
def setup_mongodb():
    """Setup MongoDB connection"""
    try:
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
        client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        print("MongoDB connection successful")
        
        db = client['mudhumeni_db']
        crop_recommendations = db['crop_recommendations']
        crop_recommendations.create_index([("user_id", 1)])
        
        return {
            "client": client,
            "db": db,
            "collections": {
                "crop_recommendations": crop_recommendations
            }
        }
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return None

# AI-Powered USSD Handler

@app.route('/ussd', methods=['POST'])
def ussd_handler():
    """AI-Powered USSD handler"""
    
    session_id = request.form.get('sessionId', '')
    service_code = request.form.get('serviceCode', '')
    phone_number = request.form.get('phoneNumber', '')
    text = request.form.get('text', '')
    
    print(f"USSD Request: sessionId={session_id}, text='{text}'")
    
    # Create or retrieve user session
    if session_id not in ussd_sessions:
        user_id = str(uuid.uuid4())
        ussd_sessions[session_id] = {
            'user_id': user_id,
            'phone_number': phone_number,
            'mode': 'menu',
            'conversation_history': [],
            'start_time': datetime.now()
        }
        
        if user_id not in user_preferences:
            user_preferences[user_id] = {
                'phone_number': phone_number,
                'language': 'en',
                'location': '',
                'farming_type': ''
            }
    
    user_session = ussd_sessions[session_id]
    user_id = user_session['user_id']
    
    # Process the USSD request
    if not text:
        return "CON " + MAIN_MENU
        
    navigation = text.split('*')
    current_choice = navigation[-1]
    
    # Handle AI Chat Mode (Option 0)
    if (len(navigation) == 1 and current_choice == '0') or user_session.get('mode') == 'chat':
        if len(navigation) == 1 and current_choice == '0':
            user_session['mode'] = 'chat'
            return "CON 🤖 Mudhumeni AI Chat\nAsk me any farming question!\n\nType 'menu' to return to main menu.\n\nYour question:"
        
        elif user_session.get('mode') == 'chat':
            if current_choice.lower() == 'menu':
                user_session['mode'] = 'menu'
                user_session['conversation_history'] = []
                return "CON " + MAIN_MENU
            else:
                # Get AI response
                try:
                    print(f"Getting AI response for: {current_choice}")
                    ai_response = chatbot_response(current_choice, user_id)
                    
                    # Format for USSD
                    if len(ai_response) > 140:
                        # Truncate to fit USSD
                        sentences = ai_response.split('. ')
                        formatted_response = ""
                        for sentence in sentences:
                            if len(formatted_response + sentence + '. ') <= 140:
                                formatted_response += sentence + '. '
                            else:
                                break
                        if not formatted_response:
                            formatted_response = ai_response[:137] + "..."
                        else:
                            formatted_response = formatted_response.strip()
                    else:
                        formatted_response = ai_response
                    
                    return f"END 💡 {formatted_response}\n\n💬 To continue chatting, dial {service_code} again"
                    
                except Exception as e:
                    print(f"AI Response Error: {str(e)}")
                    return "END Sorry, I'm having trouble right now. Please try again later."
    
    # Handle Menu Navigation with AI Enhancement
    if len(navigation) == 1:
        if current_choice == '1':
            return "CON 🌱 Farming Advice:\n1. Planting Times\n2. Fertilizer Use\n3. Pest Control\n4. Irrigation\n5. Harvesting\n6. Ask Custom Question"
        elif current_choice == '2':
            return "CON 🌽 Crop Recommendations:\n1. Best crops for my area\n2. Soil analysis guide\n3. Seasonal recommendations\n4. Ask about specific crop"
        elif current_choice == '3':
            # Use AI for seasonal info
            try:
                season = get_current_season()
                query = f"What should farmers focus on during {season} season in Southern Africa? Give 2-3 key activities."
                ai_response = chatbot_response(query, user_id)
                
                # Format for USSD
                if len(ai_response) > 120:
                    ai_response = ai_response[:117] + "..."
                
                return f"END 🌿 {season.title()} Season:\n{ai_response}"
            except Exception as e:
                print(f"AI Error: {e}")
                season = get_current_season()
                crops = ", ".join(seasonal_crops[season][:3])
                return f"END 🌿 Current season: {season}\nRecommended crops: {crops}"
        
        elif current_choice == '4':
            return "CON 📍 Select Your Province:\n1. Harare\n2. Bulawayo\n3. Manicaland\n4. Mashonaland Central\n5. Other"
        elif current_choice == '5':
            return "CON 🚜 Select Farming Type:\n1. Subsistence\n2. Small-scale commercial\n3. Large-scale commercial\n4. Mixed farming"
        elif current_choice == '6':
            return "CON 🗣️ Select Language:\n1. English\n2. Shona\n3. Ndebele\n4. Afrikaans"
        else:
            return "CON Invalid selection. " + MAIN_MENU
            
    elif len(navigation) == 2:
        main_choice = navigation[0]
        sub_choice = current_choice
        
        if main_choice == '1':  # Farming Advice
            if sub_choice == '6':
                return "CON ❓ Ask your farming question:"
            else:
                # Use AI for advice
                topics = {
                    '1': 'When is the best time to plant major crops in Southern Africa?',
                    '2': 'What are the best fertilizer practices for Southern African farming?',
                    '3': 'How do I control common pests in Southern African crops?',
                    '4': 'What are effective irrigation methods for Southern African climate?',
                    '5': 'What are the best harvesting practices for Southern African crops?'
                }
                
                question = topics.get(sub_choice)
                if question:
                    try:
                        print(f"Getting AI advice for: {question}")
                        ai_response = chatbot_response(question, user_id)
                        
                        # Format for USSD
                        if len(ai_response) > 140:
                            sentences = ai_response.split('. ')
                            formatted_response = ""
                            for sentence in sentences:
                                if len(formatted_response + sentence + '. ') <= 140:
                                    formatted_response += sentence + '. '
                                else:
                                    break
                            if not formatted_response:
                                formatted_response = ai_response[:137] + "..."
                        else:
                            formatted_response = ai_response
                        
                        return f"END 💡 {formatted_response}"
                    except Exception as e:
                        print(f"AI Error: {e}")
                        # Fallback responses
                        fallbacks = {
                            '1': "Plant maize Nov-Dec after good rains. Wheat May-Jun. Beans Oct-Nov.",
                            '2': "Use compound fertilizer at planting. Top-dress with nitrogen at 4-6 weeks.",
                            '3': "Check crops weekly. Use integrated pest management. Early detection key.",
                            '4': "Maize needs 500-800mm water. Critical at flowering. Drip irrigation saves water.",
                            '5': "Harvest maize at 20-25% moisture. Check for black layer. Dry days best."
                        }
                        return f"END 💡 {fallbacks.get(sub_choice, 'Invalid selection')}"
                        
        elif main_choice == '2':  # Crop Recommendations
            if sub_choice == '4':
                return "CON 🌱 Which crop? (e.g. maize, tobacco, cotton):"
            else:
                # Use AI for crop recommendations
                queries = {
                    '1': f"What are the best crops for {user_preferences.get(user_id, {}).get('location', 'Southern Africa')} right now?",
                    '2': "How do I test my soil for crop selection in Southern Africa?",
                    '3': f"What crops should I plant during {get_current_season()} season in Southern Africa?"
                }
                
                query = queries.get(sub_choice)
                if query:
                    try:
                        print(f"Getting AI crop advice: {query}")
                        ai_response = chatbot_response(query, user_id)
                        
                        # Format for USSD
                        if len(ai_response) > 140:
                            formatted_response = ai_response[:137] + "..."
                        else:
                            formatted_response = ai_response
                        
                        return f"END 🌾 {formatted_response}"
                    except Exception as e:
                        print(f"AI Error: {e}")
                        season = get_current_season()
                        crops = ", ".join(seasonal_crops[season][:3])
                        return f"END 🌾 {season} season crops: {crops}"
                        
        # Handle location, farming type, language settings (same as before)
        elif main_choice == '4':  # Set Location
            locations = {'1': 'Harare', '2': 'Bulawayo', '3': 'Manicaland', '4': 'Mashonaland Central', '5': 'Other'}
            location = locations.get(sub_choice, 'Unknown')
            user_preferences[user_id]['location'] = location
            return f"END 📍 Location set to: {location}"
            
        elif main_choice == '5':  # Set Farming Type
            farming_types = {'1': 'Subsistence', '2': 'Small-scale commercial', '3': 'Large-scale commercial', '4': 'Mixed farming'}
            farming_type = farming_types.get(sub_choice, 'Unknown')
            user_preferences[user_id]['farming_type'] = farming_type
            return f"END 🚜 Farming type set to: {farming_type}"
            
        elif main_choice == '6':  # Set Language
            languages = {'1': 'English', '2': 'Shona', '3': 'Ndebele', '4': 'Afrikaans'}
            language = languages.get(sub_choice, 'English')
            user_preferences[user_id]['language'] = language
            return f"END 🗣️ Language set to: {language}"
            
    elif len(navigation) == 3:
        main_choice = navigation[0]
        sub_choice = navigation[1]
        user_question = current_choice
        
        if main_choice == '1' and sub_choice == '6':  # Custom farming question
            try:
                print(f"Getting AI response for custom question: {user_question}")
                ai_response = chatbot_response(user_question, user_id)
                
                # Format for USSD
                if len(ai_response) > 140:
                    formatted_response = ai_response[:137] + "..."
                else:
                    formatted_response = ai_response
                
                return f"END 💡 {formatted_response}"
            except Exception as e:
                print(f"AI Error: {e}")
                return "END Sorry, couldn't process your question. Please try again later."
                
        elif main_choice == '2' and sub_choice == '4':  # Specific crop question
            try:
                query = f"Tell me about growing {user_question} in Southern Africa"
                print(f"Getting AI crop info: {query}")
                ai_response = chatbot_response(query, user_id)
                
                if len(ai_response) > 140:
                    formatted_response = ai_response[:137] + "..."
                else:
                    formatted_response = ai_response
                
                return f"END 🌱 {user_question.title()}:\n{formatted_response}"
            except Exception as e:
                print(f"AI Error: {e}")
                return f"END 🌱 {user_question.title()} is grown in Southern Africa. For detailed info, visit our web platform."
        
    return "END Session too long. Please start again."

def handle_ai_chat(user_session, navigation, current_choice):
    """Handle AI chatbot conversations via USSD"""
    user_id = user_session['user_id']
    
    if len(navigation) == 1 and current_choice == '0':
        user_session['mode'] = 'chat'
        return "CON 🤖 Mudhumeni AI Chat\nAsk me any farming question!\n\nType 'menu' to return to main menu.\n\nYour question:"
    
    elif user_session['mode'] == 'chat':
        if current_choice.lower() == 'menu':
            user_session['mode'] = 'menu'
            user_session['conversation_history'] = []
            return "CON " + MAIN_MENU
        else:
            try:
                ai_response = get_ussd_ai_response(current_choice, user_id, user_session['conversation_history'])
                user_session['conversation_history'].append({'role': 'user', 'content': current_choice})
                user_session['conversation_history'].append({'role': 'assistant', 'content': ai_response})
                
                formatted_response = format_ussd_response(ai_response)
                return f"END {formatted_response}\n\n💬 To continue chatting, dial {request.form.get('serviceCode', '*123#')} again"
                
            except Exception as e:
                print(f"AI Response Error: {str(e)}")
                return "END Sorry, I'm having trouble right now. Please try again later."

def handle_menu_navigation(user_session, navigation, current_choice):
    """Handle traditional menu navigation with AI integration"""
    user_id = user_session['user_id']
    
    if len(navigation) == 1:
        if current_choice == '1':
            return "CON 🌱 Farming Advice:\n1. Planting Times\n2. Fertilizer Use\n3. Pest Control\n4. Irrigation\n5. Harvesting\n6. Ask Custom Question"
        elif current_choice == '2':
            return "CON 🌽 Crop Recommendations:\n1. Best crops for my area\n2. Soil analysis guide\n3. Seasonal recommendations\n4. Ask about specific crop"
        elif current_choice == '3':
            season = get_current_season()
            try:
                query = f"Give me current season information for {season} in Southern Africa including recommended crops and activities"
                ai_response = get_ussd_ai_response(query, user_id, [])
                formatted_response = format_ussd_response(ai_response)
                return f"END 🌿 {season.title()} Season Info:\n{formatted_response}"
            except:
                crops = ", ".join(seasonal_crops[season][:3])
                return f"END 🌿 Current season: {season}\nRecommended crops: {crops}\nFocus: planting, maintenance, harvesting"
        elif current_choice == '4':
            return "CON 📍 Select Your Province:\n1. Harare\n2. Bulawayo\n3. Manicaland\n4. Mashonaland Central\n5. Other"
        elif current_choice == '5':
            return "CON 🚜 Select Farming Type:\n1. Subsistence\n2. Small-scale commercial\n3. Large-scale commercial\n4. Mixed farming"
        elif current_choice == '6':
            return "CON 🗣️ Select Language:\n1. English\n2. Shona\n3. Ndebele\n4. Afrikaans"
        else:
            return "CON Invalid selection. " + MAIN_MENU
            
    elif len(navigation) == 2:
        main_choice = navigation[0]
        sub_choice = current_choice
        
        if main_choice == '1':  # Farming Advice
            if sub_choice == '6':
                return "CON ❓ Ask your farming question:"
            else:
                topics = {
                    '1': 'planting times and schedules for crops in Southern Africa',
                    '2': 'fertilizer application and nutrient management for Southern African farming',
                    '3': 'pest and disease control methods for Southern African crops',
                    '4': 'irrigation techniques and water management for Southern African climate',
                    '5': 'harvesting practices and post-harvest handling for Southern African crops'
                }
                
                topic = topics.get(sub_choice)
                if topic:
                    try:
                        ai_response = get_ussd_ai_response(f"Give me practical advice about {topic}", user_id, [])
                        formatted_response = format_ussd_response(ai_response)
                        return f"END 💡 {formatted_response}"
                    except:
                        return get_static_advice_response(sub_choice)
                        
        elif main_choice == '2':  # Crop Recommendations
            if sub_choice == '4':
                return "CON 🌱 Which crop? (e.g. maize, tobacco, cotton):"
            else:
                queries = {
                    '1': f"What are the best crops for {user_preferences.get(user_id, {}).get('location', 'Southern Africa')} during {get_current_season()} season?",
                    '2': "How do I analyze my soil for crop selection in Southern Africa?",
                    '3': f"What crops should I plant during {get_current_season()} season in Southern Africa?"
                }
                
                query = queries.get(sub_choice)
                if query:
                    try:
                        ai_response = get_ussd_ai_response(query, user_id, [])
                        formatted_response = format_ussd_response(ai_response)
                        return f"END 🌾 {formatted_response}"
                    except:
                        return get_static_crop_response(sub_choice, user_id)
                        
        elif main_choice == '4':  # Set Location
            locations = {'1': 'Harare', '2': 'Bulawayo', '3': 'Manicaland', '4': 'Mashonaland Central', '5': 'Other'}
            location = locations.get(sub_choice, 'Unknown')
            user_preferences[user_id]['location'] = location
            return f"END 📍 Location set to: {location}\nPreferences saved!"
            
        elif main_choice == '5':  # Set Farming Type
            farming_types = {'1': 'Subsistence', '2': 'Small-scale commercial', '3': 'Large-scale commercial', '4': 'Mixed farming'}
            farming_type = farming_types.get(sub_choice, 'Unknown')
            user_preferences[user_id]['farming_type'] = farming_type
            return f"END 🚜 Farming type set to: {farming_type}\nPreferences saved!"
            
        elif main_choice == '6':  # Set Language
            languages = {'1': 'English', '2': 'Shona', '3': 'Ndebele', '4': 'Afrikaans'}
            language = languages.get(sub_choice, 'English')
            user_preferences[user_id]['language'] = language
            return f"END 🗣️ Language set to: {language}\nPreferences saved!"
            
    elif len(navigation) == 3:
        main_choice = navigation[0]
        sub_choice = navigation[1]
        user_question = current_choice
        
        if main_choice == '1' and sub_choice == '6':  # Custom farming question
            try:
                ai_response = get_ussd_ai_response(user_question, user_id, [])
                formatted_response = format_ussd_response(ai_response)
                return f"END 💡 {formatted_response}"
            except:
                return "END Sorry, couldn't process your question. Please try again later."
                
        elif main_choice == '2' and sub_choice == '4':  # Specific crop question
            try:
                query = f"Tell me about growing {user_question} in Southern Africa - planting, care, and harvesting tips"
                ai_response = get_ussd_ai_response(query, user_id, [])
                formatted_response = format_ussd_response(ai_response)
                return f"END 🌱 {user_question.title()}:\n{formatted_response}"
            except:
                return f"END 🌱 {user_question.title()} is grown in Southern Africa. For detailed info, visit our web platform."
        
    return "END Session too long. Please start again."

def get_ussd_ai_response(question, user_id, conversation_history):
    """Get AI response optimized for USSD format"""
    global llm
    
    system_prompt = generate_ussd_system_prompt(user_id)
    
    # Build conversation context (last 2 exchanges only for USSD)
    context = ""
    if conversation_history:
        for msg in conversation_history[-4:]:
            role = "User" if msg['role'] == 'user' else "Assistant"
            context += f"{role}: {msg['content']}\n"
    
    full_prompt = f"""{system_prompt}

{context}User: {question}
Assistant:"""
    
    response = llm.invoke(full_prompt)
    return response.content

def generate_ussd_system_prompt(user_id=None):
    """Generate system prompt optimized for USSD responses"""
    season = get_current_season()
    user_location = user_preferences.get(user_id, {}).get('location', 'Southern Africa')
    farming_type = user_preferences.get(user_id, {}).get('farming_type', 'farming')
    
    return f"""You are Mudhumeni AI, a practical farming assistant for Southern Africa.

CRITICAL USSD RULES:
- Keep responses under 120 characters total
- Use simple, clear language
- Give only the most important advice
- Use short sentences
- Be direct and actionable

Context: {season} season in {user_location}
User: {farming_type}

Provide brief, practical farming advice."""

def format_ussd_response(response):
    """Format AI response for USSD constraints"""
    max_length = 120  # Conservative limit for USSD
    
    if len(response) <= max_length:
        return response
    
    # Try to fit complete sentences
    sentences = response.split('. ')
    formatted_response = ""
    
    for sentence in sentences:
        if len(formatted_response + sentence + '. ') <= max_length:
            formatted_response += sentence + '. '
        else:
            break
    
    # If no complete sentences fit, truncate at word boundary
    if not formatted_response.strip():
        words = response.split()
        formatted_response = ""
        for word in words:
            if len(formatted_response + word + ' ') <= max_length - 3:
                formatted_response += word + ' '
            else:
                break
        formatted_response = formatted_response.strip() + "..."
    
    return formatted_response.strip()

def get_static_advice_response(sub_choice):
    """Fallback static responses"""
    responses = {
        '1': "END 🌱 PLANTING:\nMaize: Nov-Dec\nWheat: May-Jun\nBeans: Oct-Nov\nPlant after 25mm rain",
        '2': "END 🧪 FERTILIZER:\nBasal at planting\nTop dress at 4-6 weeks\n200-400kg/ha compound",
        '3': "END 🐛 PEST CONTROL:\nCheck weekly\nEarly detection key\nUse registered chemicals",
        '4': "END 💧 IRRIGATION:\nMaize needs 500-800mm\nCritical: flowering stage\nIrrigate when 50% dry",
        '5': "END 🌾 HARVESTING:\nMaize: 20-25% moisture\nCheck black layer\nHarvest on dry days"
    }
    return responses.get(sub_choice, "END Invalid selection")

def get_static_crop_response(sub_choice, user_id):
    """Fallback static crop responses"""
    if sub_choice == '1':
        season = get_current_season()
        crops = ", ".join(seasonal_crops[season][:3])
        return f"END 🌾 {season.title()} crops:\n{crops}\nCheck soil & water needs"
    elif sub_choice == '2':
        return "END 🧪 Test N, P, K levels\nCheck pH 6-7\nConsult extension services\nVisit web platform"
    elif sub_choice == '3':
        season = get_current_season()
        crops = ", ".join(seasonal_crops[season][:2])
        return f"END 🌿 {season.title()} season:\n{crops}\nPlant with good rains"
    return "END Invalid selection"

# Utility functions
def sanitize_input(input_string):
    """Remove potentially dangerous characters"""
    if input_string is None:
        return None
    return re.sub(r'[${}()"]', '', input_string)

def validate_recommendation_data(data):
    """Validate recommendation data before insertion"""
    required_fields = ['nitrogen', 'phosphorus', 'potassium', 'temperature', 'humidity', 'ph', 'rainfall']
    
    for field in required_fields:
        if field not in data['inputs']:
            return False, f"Missing required field: {field}"
            
    # Validate ranges
    if not (0 <= data['inputs']['nitrogen'] <= 150):
        return False, "Nitrogen must be between 0 and 150 mg/kg"
    if not (0 <= data['inputs']['phosphorus'] <= 150):
        return False, "Phosphorus must be between 0 and 150 mg/kg"
    if not (0 <= data['inputs']['potassium'] <= 150):
        return False, "Potassium must be between 0 and 150 mg/kg"
    if not (0 <= data['inputs']['temperature'] <= 50):
        return False, "Temperature must be between 0 and 50 °C"
    if not (0 <= data['inputs']['humidity'] <= 100):
        return False, "Humidity must be between 0 and 100%"
    if not (0 <= data['inputs']['ph'] <= 14):
        return False, "pH must be between 0 and 14"
    if not (0 <= data['inputs']['rainfall'] <= 5000):
        return False, "Rainfall must be between 0 and 5000 mm"
        
    return True, "Data is valid"

# Generate system prompt for web chatbot
def generate_system_prompt(user_id=None):
    season = get_current_season()
    seasonal_focus = ", ".join(seasonal_crops[season][:5])
    
    user_location = "Southern Africa"
    farming_type = "various types of"
    
    if user_id and user_id in user_preferences:
        prefs = user_preferences[user_id]
        if prefs.get("location"):
            user_location = prefs["location"]
        if prefs.get("farming_type"):
            farming_type = prefs["farming_type"]
    
    return f"""You are Mudhumeni AI, an AI-powered farming guide specifically designed for farmers in Southern Africa.
    
    Current context: It is currently {season} season in Southern Africa, which is typically good for {seasonal_focus}.
    
    The user is likely from {user_location} and engaged in {farming_type} farming.
    
    Provide practical advice on planting, irrigation, pest control, harvesting, and sustainability that is appropriate for the Southern African context.
    Consider the specific challenges of the region such as drought, variable rainfall, and resource constraints.
    """

# Web chatbot response function
def chatbot_response(user_input, user_id=None):
    global llm
    try:
        if not user_input.strip():
            return "Please enter a valid question."
        
        # Handle preference setting
        if user_input.lower().startswith("set location:"):
            location = user_input[13:].strip()
            if user_id not in user_preferences:
                user_preferences[user_id] = {}
            user_preferences[user_id]["location"] = location
            return f"Thank you! I've noted that you're farming in {location}."
        
        # Handle season inquiry
        if "season" in user_input.lower() and ("current" in user_input.lower() or "now" in user_input.lower()):
            season = get_current_season()
            crops = ", ".join(seasonal_crops[season])
            return f"We're currently in {season} season in Southern Africa. Recommended crops: {crops}"
        
        # Get conversation history
        chat_history = session.get('chat_history', [])
        history_text = ""
        
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        for exchange in recent_history:
            if exchange["role"] == "user":
                history_text += f"User: {exchange['content']}\n"
            else:
                history_text += f"Assistant: {exchange['content']}\n"
        
        system_prompt = generate_system_prompt(user_id)
        
        if history_text:
            full_prompt = f"{system_prompt}\n\nPrevious conversation:\n{history_text}\n\nUser: {user_input}\nAssistant:"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {user_input}\nAssistant:"
            
        response = llm.invoke(full_prompt)
        return response.content
        
    except Exception as e:
        print(f"Error in chatbot response: {str(e)}")
        return "I apologize, but I encountered an error. Please try asking your question differently."

# Initialize the application
print("Initializing Mudhumeni AI Chatbot......")
llm = initialize_llm()

mongo_data = setup_mongodb()
if mongo_data:
    app.config['MONGO_DATA'] = mongo_data
    print("MongoDB integration initialized successfully")
else:
    print("WARNING: MongoDB connection failed. Some features may be limited.")
    app.config['MONGO_DATA'] = None

print("USSD AI interface registered successfully")

# Web routes
@app.route('/')
@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/chatbot')
def chatbot():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('index.html')

@app.route('/crop-recommendation')
def crop_recommendation():
    return render_template('crop_recommendation.html')

@app.route('/predict_crop', methods=['POST'])
def predict_crop():
    try:
        model = pickle.load(open('model.pkl', 'rb'))
        minmaxscaler = pickle.load(open('minmaxscaler.pkl', 'rb'))
        standscaler = pickle.load(open('standscaler.pkl', 'rb'))
        
        data = request.form
        N = float(data['N'])
        P = float(data['P'])
        K = float(data['K'])
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        ph = float(data['ph'])
        rainfall = float(data['rainfall'])
        province = sanitize_input(data.get('province', ''))
        
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        mx_features = minmaxscaler.transform(features)
        sc_mx_features = standscaler.transform(mx_features)
        prediction = model.predict(sc_mx_features)
        
        crop_dict = {
            1: 'rice', 2: 'maize', 3: 'jute', 4: 'cotton', 5: 'coconut',
            6: 'papaya', 7: 'orange', 8: 'apple', 9: 'muskmelon', 10: 'watermelon',
            11: 'grapes', 12: 'mango', 13: 'banana', 14: 'pomegranate',
            15: 'lentil', 16: 'blackgram', 17: 'mungbean', 18: 'mothbeans',
            19: 'pigeonpeas', 20: 'kidneybeans', 21: 'chickpea', 22: 'coffee'
        }
        
        predicted_crop = crop_dict[prediction[0]]
        season = get_current_season()
        
        seasonal_advice = ""
        if predicted_crop in seasonal_crops[season]:
            seasonal_advice = f"Good choice! {predicted_crop.title()} is well-suited for the current {season} season."
        else:
            appropriate_season = next((s for s, crops in seasonal_crops.items() if predicted_crop in crops), None)
            if appropriate_season:
                seasonal_advice = f"Note: {predicted_crop.title()} is typically better for {appropriate_season} season."
        
        return jsonify({
            'success': True, 
            'prediction': predicted_crop,
            'season': season,
            'seasonal_advice': seasonal_advice
        })
    
    except Exception as e:
        print(f"Error in predict_crop: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form["user_input"]
    user_id = session.get('user_id')
    
    chat_history = session.get('chat_history', [])
    chat_history.append({"role": "user", "content": user_input})
    
    response = chatbot_response(user_input, user_id)
    chat_history.append({"role": "assistant", "content": response})
    
    session['chat_history'] = chat_history
    
    return jsonify({"response": response, "chat_history": chat_history})

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    try:
        model = pickle.load(open('model.pkl', 'rb'))
        minmaxscaler = pickle.load(open('minmaxscaler.pkl', 'rb'))
        standscaler = pickle.load(open('standscaler.pkl', 'rb'))
        print("ML models loaded successfully")
    except Exception as e:
        print(f"Error loading ML models: {str(e)}")
        print("Application will run, but crop recommendation may not work properly")
    
    app.run(debug=True, port=8000)