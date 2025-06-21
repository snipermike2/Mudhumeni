# sms_notifications.py

import os
import requests
import json
import schedule
import time
import threading
from datetime import datetime, timedelta
import random

# Import from main app
from app import (
    get_current_season,
    seasonal_crops,
    user_preferences,
    chatbot_response
)

class FarmingSMSNotification:
    """Handle SMS notifications for farming events and advice"""
    
    def __init__(self, sms_api_key=None, sms_sender_id=None):
        """Initialize the SMS notification system"""
        self.api_key = sms_api_key or os.environ.get('SMS_API_KEY')
        self.sender_id = sms_sender_id or os.environ.get('SMS_SENDER_ID', 'Mudhumeni')
        self.running = False
        self.scheduler_thread = None
        
        # Notification templates
        self.templates = {
            'planting_reminder': (
                "Mudhumeni: It's time to prepare for planting {crops} in your area. "
                "Optimal planting window begins soon. Reply *123# for more info."
            ),
            'fertilizer_reminder': (
                "Mudhumeni: Time to apply fertilizer to your {crop} crops. "
                "For specific advice, dial *123# and select Farming Advice."
            ),
            'pest_alert': (
                "Mudhumeni ALERT: {pest} reported in your region. "
                "Check your {crop} fields and apply control measures if needed. Dial *123# for advice."
            ),
            'rainfall_forecast': (
                "Mudhumeni: Rain forecast for {location} in next 48hrs. "
                "Consider {activity} for your {crop} crops."
            ),
            'market_price': (
                "Mudhumeni: Current market prices in {location}: {prices}. "
                "Dial *123# for more agricultural info."
            ),
            'seasonal_transition': (
                "Mudhumeni: {current_season} is ending soon. Time to prepare for {next_season}. "
                "Recommended activities: {activities}. Dial *123# for details."
            ),
            'harvest_reminder': (
                "Mudhumeni: Optimal harvest time for {crop} approaching. "
                "For harvesting best practices, dial *123# and select Harvesting Advice."
            )
        }
        
        # Initialize notification scheduling
        self._setup_schedules()
    
    def _setup_schedules(self):
        """Set up scheduled notifications"""
        # Daily weather notifications at 6 AM
        schedule.every().day.at("06:00").do(self.send_weather_notifications)
        
        # Seasonal transition notifications (check weekly)
        schedule.every().monday.at("08:00").do(self.check_seasonal_transitions)
        
        # Pest alerts (randomized to simulate real events - twice a week)
        schedule.every().wednesday.at("09:00").do(self.check_pest_alerts)
        schedule.every().saturday.at("09:00").do(self.check_pest_alerts)
        
        # Market prices (weekly)
        schedule.every().friday.at("12:00").do(self.send_market_price_updates)
        
        # Planting reminders (every 3 days during planting seasons)
        schedule.every(3).days.at("07:00").do(self.send_planting_reminders)
        
        # Maintenance reminders (check every 10 days)
        schedule.every(10).days.at("10:00").do(self.send_crop_maintenance_reminders)
    
    def _format_phone_number(self, phone_number):
        """Format phone number for SMS API"""
        # Remove any non-digit characters
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Ensure it has country code (add +27 for South Africa if needed)
        if len(cleaned) == 10 and cleaned.startswith('0'):
            return '+27' + cleaned[1:]
        elif not cleaned.startswith('+'):
            return '+' + cleaned
        
        return cleaned
    
    def send_sms(self, phone_number, message):
        """Send SMS message to a user"""
        if not self.api_key:
            print(f"[MOCK SMS] To: {phone_number}, Message: {message}")
            return True
        
        # Format phone number
        formatted_number = self._format_phone_number(phone_number)
        
        try:
            # This is a generic SMS API call - adjust for your specific provider
            url = "https://api.yoursmsgateway.com/messages"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "recipient": formatted_number,
                "message": message,
                "sender_id": self.sender_id
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            print(f"SMS sent to {formatted_number}")
            return True
            
        except Exception as e:
            print(f"Error sending SMS to {formatted_number}: {str(e)}")
            return False
    
    def send_weather_notifications(self):
        """Send weather-related notifications to users"""
        print("Checking weather forecasts for notifications...")
        
        # Group users by location for batch processing
        users_by_location = {}
        
        for user_id, prefs in user_preferences.items():
            if not prefs.get('phone_number'):
                continue
                
            location = prefs.get('location', 'Unknown')
            if location not in users_by_location:
                users_by_location[location] = []
            
            users_by_location[location].append({
                'user_id': user_id,
                'phone_number': prefs['phone_number'],
                'farming_type': prefs.get('farming_type', 'crop farming')
            })
        
        # For each location, get weather forecast and send notifications
        for location, users in users_by_location.items():
            # In a real implementation, you would fetch actual weather data
            # Here we simulate weather conditions
            weather_conditions = self._simulate_weather_forecast(location)
            
            if weather_conditions.get('rainfall_probability', 0) > 70:
                # Heavy rain expected
                for user in users:
                    crop_type = self._get_primary_crop_for_user(user['user_id'])
                    activity = "harvesting" if weather_conditions.get('rainfall_amount', 0) > 30 else "covering seedlings"
                    
                    message = self.templates['rainfall_forecast'].format(
                        location=location,
                        activity=activity,
                        crop=crop_type
                    )
                    
                    self.send_sms(user['phone_number'], message)
            
            elif weather_conditions.get('temperature', 0) > 35:
                # Extreme heat warning
                for user in users:
                    message = (
                        f"Mudhumeni: High temperatures expected in {location} "
                        f"({weather_conditions.get('temperature')}°C). Ensure adequate irrigation "
                        f"for your crops. Dial *123# for heat management advice."
                    )
                    
                    self.send_sms(user['phone_number'], message)
    
    def check_seasonal_transitions(self):
        """Check for upcoming seasonal transitions and notify users"""
        print("Checking for seasonal transitions...")
        
        current_season = get_current_season()
        
        # Calculate days until next season
        today = datetime.now()
        next_season_start = None
        
        if current_season == "summer":
            # Summer -> autumn transition (around March 1)
            next_season = "autumn"
            next_season_start = datetime(today.year, 3, 1)
        elif current_season == "autumn":
            # Autumn -> winter transition (around June 1)
            next_season = "winter"
            next_season_start = datetime(today.year, 6, 1)
        elif current_season == "winter":
            # Winter -> spring transition (around September 1)
            next_season = "spring"
            next_season_start = datetime(today.year, 9, 1)
        elif current_season == "spring":
            # Spring -> summer transition (around December 1)
            next_season = "summer"
            next_season_start = datetime(today.year, 12, 1)
        
        if next_season_start and next_season_start < today:
            # Adjust for next year if the date has passed
            next_season_start = next_season_start.replace(year=today.year + 1)
        
        if next_season_start:
            days_until_transition = (next_season_start - today).days
            
            # If within 14 days of transition, send notifications
            if days_until_transition <= 14:
                seasonal_activities = self._get_seasonal_transition_activities(current_season, next_season)
                
                for user_id, prefs in user_preferences.items():
                    if not prefs.get('phone_number'):
                        continue
                    
                    message = self.templates['seasonal_transition'].format(
                        current_season=current_season.title(),
                        next_season=next_season.title(),
                        activities=seasonal_activities
                    )
                    
                    self.send_sms(prefs['phone_number'], message)
    
    def check_pest_alerts(self):
        """Check for pest alerts and notify users based on their crops"""
        print("Checking for pest alerts...")
        
        # In a real system, you would fetch actual pest outbreak data
        # Here we simulate some pest alerts for demonstration
        
        # Common pests by season
        season = get_current_season()
        seasonal_pests = {
            "summer": ["Fall Armyworm", "Stalk Borer", "Aphids"],
            "autumn": ["Bollworm", "Red Spider Mites", "Whitefly"],
            "winter": ["Aphids", "Cutworms", "Diamondback Moth"],
            "spring": ["Thrips", "Leaf Miners", "African Armyworm"]
        }
        
        # Randomly select if there's a pest alert (30% chance)
        if random.random() < 0.3:
            # Select a random pest for this season
            pest = random.choice(seasonal_pests.get(season, ["Unknown Pest"]))
            
            # Determine affected crops
            affected_crops = {
                "Fall Armyworm": ["maize", "sorghum", "millet"],
                "Stalk Borer": ["maize", "sorghum"],
                "Aphids": ["vegetables", "cotton", "tobacco"],
                "Bollworm": ["cotton", "maize", "tomatoes"],
                "Red Spider Mites": ["cotton", "tomatoes"],
                "Whitefly": ["cotton", "vegetables"],
                "Cutworms": ["seedlings", "vegetables"],
                "Diamondback Moth": ["cabbage", "vegetables"],
                "Thrips": ["onions", "cotton", "vegetables"],
                "Leaf Miners": ["vegetables", "leafy greens"],
                "African Armyworm": ["maize", "pasture", "cereals"]
            }
            
            target_crops = affected_crops.get(pest, ["crops"])
            
            # Determine affected regions (simulate)
            affected_regions = random.sample([
                "Harare", "Bulawayo", "Manicaland", "Mashonaland Central", 
                "Mashonaland East", "Mashonaland West", "Masvingo", 
                "Matabeleland North", "Matabeleland South", "Midlands",
                "Gauteng", "Western Cape", "Limpopo"
            ], k=random.randint(1, 5))
            
            # Notify users in affected regions with relevant crops
            for user_id, prefs in user_preferences.items():
                if not prefs.get('phone_number') or not prefs.get('location'):
                    continue
                
                user_location = prefs['location']
                if user_location not in affected_regions:
                    continue
                
                # Check if user has the affected crops
                user_crop = self._get_primary_crop_for_user(user_id)
                
                if any(crop in user_crop.lower() for crop in target_crops):
                    message = self.templates['pest_alert'].format(
                        pest=pest,
                        crop=user_crop
                    )
                    
                    self.send_sms(prefs['phone_number'], message)
    
    def send_market_price_updates(self):
        """Send market price updates to users"""
        print("Sending market price updates...")
        
        # In a real system, you would fetch actual market prices
        # Here we simulate market prices
        
        # Group users by location
        users_by_location = {}
        
        for user_id, prefs in user_preferences.items():
            if not prefs.get('phone_number'):
                continue
                
            location = prefs.get('location', 'Unknown')
            if location not in users_by_location:
                users_by_location[location] = []
            
            users_by_location[location].append({
                'user_id': user_id,
                'phone_number': prefs['phone_number']
            })
        
        # For each location, generate market prices and send notifications
        for location, users in users_by_location.items():
            # Simulate market prices
            prices = self._simulate_market_prices()
            
            # Format price information
            price_text = ", ".join([f"{crop}: ${price}/kg" for crop, price in prices.items()])
            
            # Send to each user in the location
            for user in users:
                message = self.templates['market_price'].format(
                    location=location,
                    prices=price_text
                )
                
                self.send_sms(user['phone_number'], message)
    
    def send_planting_reminders(self):
        """Send planting reminders based on season and location"""
        print("Checking for planting reminders...")
        
        current_season = get_current_season()
        next_season = self._get_next_season(current_season)
        
        # Check if we're near the end of the current season (good time for planting reminders)
        today = datetime.now()
        season_end_approaching = False
        
        if current_season == "winter" and today.month >= 8:
            # Winter ending, prepare for spring planting
            season_end_approaching = True
            planting_season = "spring"
        elif current_season == "spring" and today.month >= 11:
            # Spring ending, prepare for summer planting
            season_end_approaching = True
            planting_season = "summer"
        elif current_season == "summer" and today.month >= 2:
            # Summer ending, prepare for autumn planting
            season_end_approaching = True
            planting_season = "autumn"
        elif current_season == "autumn" and today.month >= 5:
            # Autumn ending, prepare for winter planting
            season_end_approaching = True
            planting_season = "winter"
        
        if season_end_approaching:
            # Get recommended crops for the upcoming season
            upcoming_crops = seasonal_crops.get(planting_season, [])
            if not upcoming_crops:
                return
            
            # Select 3 random crops to recommend
            selected_crops = ", ".join(random.sample(upcoming_crops, min(3, len(upcoming_crops))))
            
            # Send notifications to all users
            for user_id, prefs in user_preferences.items():
                if not prefs.get('phone_number'):
                    continue
                
                message = self.templates['planting_reminder'].format(
                    crops=selected_crops
                )
                
                self.send_sms(prefs['phone_number'], message)
    
    def send_crop_maintenance_reminders(self):
        """Send reminders about crop maintenance based on growth stage"""
        print("Sending crop maintenance reminders...")
        
        current_season = get_current_season()
        
        # Determine maintenance activities based on season
        maintenance_activities = {
            "summer": {
                "maize": "top dressing fertilizer application and weeding",
                "tobacco": "topping and sucker control",
                "cotton": "pest monitoring and control",
                "groundnuts": "weeding and disease monitoring"
            },
            "autumn": {
                "maize": "harvesting preparation and storage planning",
                "tobacco": "harvesting and curing",
                "wheat": "land preparation and planting",
                "vegetables": "planting of winter vegetables"
            },
            "winter": {
                "wheat": "fertilizer application and irrigation",
                "vegetables": "frost protection and pest control",
                "orchards": "pruning and disease management",
                "pasture": "supplementary feeding planning"
            },
            "spring": {
                "maize": "land preparation and seed selection",
                "cotton": "land preparation and seed planting",
                "tobacco": "seedbed preparation and seedling care",
                "vegetables": "nursery preparation and transplanting"
            }
        }
        
        seasonal_activities = maintenance_activities.get(current_season, {})
        if not seasonal_activities:
            return
        
        # Send reminders to users based on their primary crops
        for user_id, prefs in user_preferences.items():
            if not prefs.get('phone_number'):
                continue
            
            user_crop = self._get_primary_crop_for_user(user_id)
            
            # If we have specific advice for their crop, send it
            if user_crop.lower() in seasonal_activities:
                activity = seasonal_activities[user_crop.lower()]
                
                message = (
                    f"Mudhumeni: Time for {activity} on your {user_crop} crop. "
                    f"For detailed advice, dial *123# and select Farming Advice."
                )
                
                self.send_sms(prefs['phone_number'], message)
            else:
                # Generic maintenance reminder
                random_crop = random.choice(list(seasonal_activities.keys()))
                activity = seasonal_activities[random_crop]
                
                message = (
                    f"Mudhumeni: {current_season.title()} crop maintenance reminder. "
                    f"Consider {activity}. Dial *123# for more specific advice."
                )
                
                self.send_sms(prefs['phone_number'], message)
    
    def _get_primary_crop_for_user(self, user_id):
        """Determine the primary crop for a user based on their preferences or location"""
        # In a real system, you'd have this information stored
        # Here we make an educated guess based on available data
        
        user_prefs = user_preferences.get(user_id, {})
        farming_type = user_prefs.get('farming_type', '').lower()
        location = user_prefs.get('location', '').lower()
        season = get_current_season()
        
        # Get seasonal crops
        season_crops = seasonal_crops.get(season, [])
        
        if "maize" in farming_type or not farming_type:
            return "maize"  # Most common crop in Southern Africa
        elif "cotton" in farming_type:
            return "cotton"
        elif "tobacco" in farming_type:
            return "tobacco"
        elif "vegetable" in farming_type:
            return "vegetables"
        elif "livestock" in farming_type:
            return "pasture"
        elif season_crops:
            return random.choice(season_crops)
        else:
            return "crops"  # Generic fallback
    
    def _get_next_season(self, current_season):
        """Get the next season in the cycle"""
        seasons = ["summer", "autumn", "winter", "spring"]
        current_index = seasons.index(current_season)
        next_index = (current_index + 1) % 4
        return seasons[next_index]
    
    def _get_seasonal_transition_activities(self, current_season, next_season):
        """Get activities for the transition between seasons"""
        transition_activities = {
            ("summer", "autumn"): "harvesting summer crops, soil testing, planning winter crops",
            ("autumn", "winter"): "planting winter wheat, frost protection, equipment maintenance",
            ("winter", "spring"): "seedbed preparation, soil warming techniques, early planting",
            ("spring", "summer"): "main crop planting, irrigation system setup, pest monitoring"
        }
        
        return transition_activities.get((current_season, next_season), "preparation for next season")
    
    def _simulate_weather_forecast(self, location):
        """Simulate weather forecast for a location"""
        # In a real system, you would fetch actual weather data
        
        season = get_current_season()
        
        # Base values by season
        base_values = {
            "summer": {"temp_min": 18, "temp_max": 32, "rain_prob": 60, "rain_amount": 15},
            "autumn": {"temp_min": 12, "temp_max": 25, "rain_prob": 40, "rain_amount": 8},
            "winter": {"temp_min": 5, "temp_max": 20, "rain_prob": 20, "rain_amount": 3},
            "spring": {"temp_min": 12, "temp_max": 28, "rain_prob": 30, "rain_amount": 10}
        }
        
        # Adjust for location
        location_adjustments = {
            "harare": {"temp": 0, "rain": 0},
            "bulawayo": {"temp": 2, "rain": -10},
            "manicaland": {"temp": -1, "rain": 10},
            "mashonaland": {"temp": 0, "rain": 5},
            "masvingo": {"temp": 1, "rain": -5},
            "matabeleland": {"temp": 3, "rain": -15},
            "midlands": {"temp": 0, "rain": 0},
            "gauteng": {"temp": 0, "rain": 0},
            "western cape": {"temp": -2, "rain": 5},
            "eastern cape": {"temp": -1, "rain": 10},
            "limpopo": {"temp": 3, "rain": -10}
        }
        
        # Find the best matching location adjustment
        location_lower = location.lower()
        adjustment = {"temp": 0, "rain": 0}
        
        for loc_key, loc_adj in location_adjustments.items():
            if loc_key in location_lower:
                adjustment = loc_adj
                break
        
        # Get base values for the season
        base = base_values.get(season, {"temp_min": 15, "temp_max": 25, "rain_prob": 30, "rain_amount": 5})
        
        # Apply location adjustment and randomness
        temp_min = base["temp_min"] + adjustment["temp"] + random.uniform(-3, 3)
        temp_max = base["temp_max"] + adjustment["temp"] + random.uniform(-3, 3)
        rain_prob = base["rain_prob"] + adjustment["rain"] + random.uniform(-15, 15)
        rain_amount = base["rain_amount"] + (adjustment["rain"] / 5) + random.uniform(-3, 5)
        
        # Ensure values are within reasonable ranges
        rain_prob = max(0, min(100, rain_prob))
        rain_amount = max(0, rain_amount)
        
        # Today's temperature (random point between min and max)
        temperature = temp_min + (temp_max - temp_min) * random.random()
        
        return {
            "temperature": round(temperature, 1),
            "temperature_min": round(temp_min, 1),
            "temperature_max": round(temp_max, 1),
            "rainfall_probability": round(rain_prob),
            "rainfall_amount": round(rain_amount, 1)
        }
    
    def _simulate_market_prices(self):
        """Simulate market prices for common crops"""
        # Base prices for common crops (in local currency per kg)
        base_prices = {
            "maize": 0.30,
            "tomatoes": 1.20,
            "potatoes": 0.80,
            "onions": 0.90,
            "cabbage": 0.60
        }
        
        # Apply some random variation
        prices = {}
        for crop, base_price in base_prices.items():
            # Random variation of +/- 20%
            variation = random.uniform(-0.2, 0.2)
            price = base_price * (1 + variation)
            prices[crop] = round(price, 2)
        
        return prices
    
    def start(self):
        """Start the notification scheduler"""
        if self.running:
            print("Notification system already running")
            return
        
        def run_scheduler():
            self.running = True
            print("Starting SMS notification scheduler")
            
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop(self):
        """Stop the notification scheduler"""
        if not self.running:
            print("Notification system not running")
            return
        
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
        
        print("SMS notification scheduler stopped")

# Function to register with the main app
def register_sms_notification_system(app):
    """Register the SMS notification system with the main app"""
    sms_system = FarmingSMSNotification()
    app.config['SMS_SYSTEM'] = sms_system
    
    # Start the SMS notification system
    sms_system.start()
    
    # Register a shutdown handler
    @app.teardown_appcontext
    def shutdown_sms_system(exception=None):
        sms_system = app.config.get('SMS_SYSTEM')
        if sms_system:
            sms_system.stop()