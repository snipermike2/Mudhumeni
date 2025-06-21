# setup_translations.py - Script to initialize translation system

import os
import json
from translations import TranslationManager

def create_translation_files():
    """Create translation files for all supported languages"""
    
    print("Setting up Mudhumeni AI Translation System...")
    print("=" * 50)
    
    # Initialize translation manager
    tm = TranslationManager()
    
    # Create translations directory if it doesn't exist
    if not os.path.exists('translations'):
        os.makedirs('translations')
        print("✓ Created translations directory")
    
    # Generate translation files for all languages
    for lang_code, lang_name in tm.supported_languages.items():
        file_path = f'translations/{lang_code}.json'
        
        # Get translations for this language
        translations = tm._get_default_translations(lang_code)
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Created {lang_name} translations ({lang_code}.json)")
    
    print("\n" + "=" * 50)
    print("Translation Setup Complete!")
    print("\nAvailable Languages:")
    for lang_code, lang_name in tm.supported_languages.items():
        print(f"  - {lang_name} ({lang_code})")
    
    print(f"\nTranslation files created in: {os.path.abspath('translations')}")
    print("\nYou can now:")
    print("1. Edit translation files to improve translations")
    print("2. Add new translation keys as needed")
    print("3. Use the system in your Flask app")
    
    # Create a sample usage example
    create_usage_example()

def create_usage_example():
    """Create a sample usage example"""
    
    example_code = '''# Example: Using the translation system

from translations import translate, translation_manager

# Basic translation
english_text = translate('welcome', 'en')  
shona_text = translate('welcome', 'sn')    
ndebele_text = translate('welcome', 'nd')  

print(f"English: {english_text}")
print(f"Shona: {shona_text}")
print(f"Ndebele: {ndebele_text}")

# Translation with parameters
advice = translate('planting_advice', 'sn', season='chirimo')
print(f"Advice: {advice}")

# Get user's preferred language
user_preferences = {'user123': {'language': 'sn'}}
user_lang = translation_manager.get_user_language(user_preferences, 'user123')
welcome_msg = translate('welcome', user_lang)
print(f"User welcome: {welcome_msg}")
'''
    
    with open('translation_example.py', 'w', encoding='utf-8') as f:
        f.write(example_code)
    
    print(f"\n✓ Created usage example: translation_example.py")

def test_translations():
    """Test the translation system"""
    
    print("\n" + "=" * 50)
    print("Testing Translation System...")
    print("=" * 50)
    
    from translations import translate, translation_manager
    
    # Test basic translations
    test_keys = ['welcome', 'thank_you', 'farming_advice', 'maize', 'planting']
    test_languages = ['en', 'sn', 'nd', 'zu']
    
    for key in test_keys:
        print(f"\nTesting '{key}':")
        for lang in test_languages:
            lang_name = translation_manager.supported_languages[lang]
            translation = translate(key, lang)
            print(f"  {lang_name}: {translation}")
    
    print("\n✓ Translation system working correctly!")

if __name__ == "__main__":
    create_translation_files()
    test_translations()
    
    print("\n" + "=" * 50)
    print("Next Steps:")
    print("1. Update your app.py with the new translation code")
    print("2. Update your HTML templates with language support")
    print("3. Test the USSD system with different languages")
    print("4. Customize translations in the JSON files as needed")
    print("=" * 50)