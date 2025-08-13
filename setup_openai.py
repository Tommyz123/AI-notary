"""
Quick setup script to configure OpenAI API for faster responses
"""

import os
import re

def setup_openai_api():
    """Interactive setup for OpenAI API configuration."""
    print("🚀 OpenAI API Setup for Faster Responses")
    print("=" * 50)
    
    # Get API key from user
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ API key is required!")
        return False
    
    # Validate API key format (basic check)
    if not re.match(r'^sk-[a-zA-Z0-9]{48}$', api_key):
        print("⚠️ Warning: API key format doesn't match expected OpenAI format")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != 'y':
            return False
    
    # Choose model
    print("\nAvailable OpenAI models:")
    models = {
        "1": "gpt-3.5-turbo (Fastest, most cost-effective)",
        "2": "gpt-4 (Higher quality, slower)",
        "3": "gpt-4-turbo (Balanced speed and quality)"
    }
    
    for key, desc in models.items():
        print(f"{key}. {desc}")
    
    model_choice = input("\nSelect model (1-3, default 1): ").strip()
    
    model_map = {
        "1": "gpt-3.5-turbo",
        "2": "gpt-4",
        "3": "gpt-4-turbo",
        "": "gpt-3.5-turbo"  # default
    }
    
    selected_model = model_map.get(model_choice, "gpt-3.5-turbo")
    
    # Read current .env file
    env_file = ".env"
    env_lines = []
    
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            env_lines = f.readlines()
    
    # Update configuration
    new_config = {
        "API_PROVIDER": "openai",
        "OPENAI_API_KEY": api_key,
        "OPENAI_MODEL": selected_model,
        "ENABLE_RESPONSE_CACHING": "true"
    }
    
    # Update or add configuration lines
    updated_lines = []
    updated_keys = set()
    
    for line in env_lines:
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key = line.split("=")[0].strip()
            if key in new_config:
                updated_lines.append(f"{key}={new_config[key]}\n")
                updated_keys.add(key)
            else:
                updated_lines.append(line + "\n")
        else:
            updated_lines.append(line + "\n")
    
    # Add new configuration lines that weren't in the file
    for key, value in new_config.items():
        if key not in updated_keys:
            updated_lines.append(f"{key}={value}\n")
    
    # Write updated configuration
    with open(env_file, "w") as f:
        f.writelines(updated_lines)
    
    print(f"\n✅ Configuration updated successfully!")
    print(f"   Provider: OpenAI")
    print(f"   Model: {selected_model}")
    print(f"   Caching: Enabled")
    print(f"   Config file: {env_file}")
    
    # Test the configuration
    print("\n🧪 Testing API connection...")
    
    try:
        # Import and test
        from config import config
        from ai_api import call_deepseek
        
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'API test successful' if you can see this message."}
        ]
        
        response = call_deepseek(test_messages)
        print(f"✅ API test successful!")
        print(f"   Response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("Please check your API key and try again.")
        return False


def show_speed_comparison():
    """Show expected speed improvements."""
    print("\n📊 Expected Performance Improvements:")
    print("=" * 40)
    print("OpenAI GPT-3.5-turbo vs DeepSeek:")
    print("• Response time: 2-5x faster")
    print("• With caching: 10-50x faster for repeated requests")
    print("• Global availability: Better uptime")
    print("• Optimized parameters: Faster generation")
    
    print("\nCaching Benefits:")
    print("• Identical questions get instant responses")
    print("• Cache duration: 60 minutes (configurable)")
    print("• Significant cost savings on repeated requests")


def main():
    """Main setup function."""
    print("Welcome to the OpenAI API Speed Optimization Setup!")
    print()
    
    show_speed_comparison()
    print()
    
    proceed = input("Would you like to configure OpenAI API now? (Y/n): ").strip().lower()
    
    if proceed in ['', 'y', 'yes']:
        success = setup_openai_api()
        
        if success:
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Restart your Streamlit application")
            print("2. Log in and try asking questions")
            print("3. Notice the faster response times!")
            print("\nTo start the application:")
            print("   streamlit run app.py")
        else:
            print("\n❌ Setup failed. Please try again or check your API key.")
    else:
        print("Setup cancelled. You can run this script again anytime.")


if __name__ == "__main__":
    main()