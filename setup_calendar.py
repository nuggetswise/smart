#!/usr/bin/env python3
"""
Google Calendar Setup Script for SmartDeskAI

This script helps you set up Google Calendar integration by:
1. Checking for existing credentials
2. Guiding you through the setup process
3. Testing the connection
4. Providing troubleshooting information
"""

import os
import json
import sys
from pathlib import Path

def check_existing_credentials():
    """Check for existing credential files."""
    print("🔍 Checking for existing credentials...")
    
    credential_paths = [
        'credentials.json',
        'token.json',
        '.credentials/credentials.json',
        '.credentials/token.json',
        os.path.expanduser('~/.credentials/credentials.json'),
        os.path.expanduser('~/.credentials/token.json')
    ]
    
    found_credentials = []
    for path in credential_paths:
        if os.path.exists(path):
            found_credentials.append(path)
            print(f"  ✅ Found: {path}")
    
    if not found_credentials:
        print("  ❌ No credential files found")
        return False
    
    return True

def validate_credentials_file(file_path):
    """Validate that a credentials file has the correct structure."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check for OAuth 2.0 client credentials structure (desktop app)
        if 'installed' in data and 'client_id' in data['installed']:
            print(f"  ✅ Valid OAuth 2.0 client credentials (Desktop) found in {file_path}")
            return True
        # Check for OAuth 2.0 web client credentials structure
        elif 'web' in data and 'client_id' in data['web']:
            print(f"  ✅ Valid OAuth 2.0 web client credentials found in {file_path}")
            return True
        elif 'client_id' in data:
            print(f"  ✅ Valid OAuth 2.0 credentials found in {file_path}")
            return True
        else:
            print(f"  ❌ Invalid credentials structure in {file_path}")
            return False
    except Exception as e:
        print(f"  ❌ Error reading {file_path}: {e}")
        return False

def setup_credentials_directory():
    """Create the credentials directory if it doesn't exist."""
    cred_dir = Path.home() / '.credentials'
    if not cred_dir.exists():
        cred_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created credentials directory: {cred_dir}")
    else:
        print(f"  ✅ Credentials directory exists: {cred_dir}")
    return cred_dir

def copy_credentials_to_standard_location():
    """Copy credentials to the standard location."""
    source_paths = ['credentials.json', 'token.json']
    target_dir = Path.home() / '.credentials'
    
    for source in source_paths:
        if os.path.exists(source):
            target = target_dir / source
            if not target.exists():
                import shutil
                shutil.copy2(source, target)
                print(f"  ✅ Copied {source} to {target}")
            else:
                print(f"  ℹ️  {target} already exists")

def test_calendar_connection():
    """Test the calendar connection."""
    print("\n🧪 Testing Calendar Connection...")
    
    try:
        from core.tools.calendar_tool import CalendarTool
        
        calendar_tool = CalendarTool()
        
        if not calendar_tool.credentials_available:
            print(f"  ❌ Calendar connection failed: {calendar_tool.error_message}")
            return False
        
        print("  ✅ Calendar tool initialized successfully")
        
        # Test getting events
        events = calendar_tool.get_upcoming_events(hours=1)
        if events and not events.startswith("Error"):
            print(f"  ✅ Successfully retrieved events: {events}")
        else:
            print(f"  ℹ️  No events found or error: {events}")
        
        # Get detailed status
        status = calendar_tool.get_calendar_status()
        print(f"  📊 Calendar status: {status}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Calendar connection test failed: {e}")
        return False

def print_setup_instructions():
    """Print detailed setup instructions."""
    print("\n📋 Google Calendar Setup Instructions:")
    print("=" * 50)
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
    print("2. Create a new project or select an existing one")
    print("3. Enable the Google Calendar API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Calendar API'")
    print("   - Click on it and click 'Enable'")
    print("4. Create OAuth 2.0 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth client ID'")
    print("   - Application type: Web application (recommended for Streamlit)")
    print("   - Name: SmartDeskAI Calendar")
    print("   - Add Authorized JavaScript origins:")
    print("     * http://localhost:8508")
    print("     * http://localhost:8501")
    print("   - Add Authorized redirect URIs:")
    print("     * http://localhost:8508/_stcore/authorize")
    print("     * http://localhost:8508/")
    print("     * http://localhost:8501/_stcore/authorize")
    print("     * http://localhost:8501/")
    print("   - Click 'Create'")
    print("5. Download the credentials:")
    print("   - Click 'Download JSON'")
    print("   - Save as 'credentials.json' in the project root")
    print("6. Run this script again to test the connection")
    print("\nAlternative: For desktop development, use 'Desktop application' type")

def main():
    """Main setup function."""
    print("🚀 SmartDeskAI - Google Calendar Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('core/tools/calendar_tool.py'):
        print("❌ Error: Please run this script from the SmartDeskAI project root directory")
        return
    
    # Check for existing credentials
    has_credentials = check_existing_credentials()
    
    if has_credentials:
        print("\n✅ Credentials found! Validating...")
        
        # Validate credentials
        credential_paths = ['credentials.json', 'token.json']
        valid_credentials = False
        
        for path in credential_paths:
            if os.path.exists(path):
                if validate_credentials_file(path):
                    valid_credentials = True
                    break
        
        if valid_credentials:
            # Set up credentials directory
            setup_credentials_directory()
            copy_credentials_to_standard_location()
            
            # Test connection
            if test_calendar_connection():
                print("\n🎉 Calendar setup completed successfully!")
                print("You can now use calendar features in SmartDeskAI.")
            else:
                print("\n⚠️  Calendar setup completed but connection test failed.")
                print("Check the error messages above for troubleshooting.")
        else:
            print("\n❌ Invalid credentials found.")
            print_setup_instructions()
    else:
        print("\n❌ No credentials found.")
        print_setup_instructions()
    
    print("\n📚 Additional Resources:")
    print("- Calendar Setup Guide: CALENDAR_SETUP.md")
    print("- Comprehensive Testing: python test_calendar_detailed.py")
    print("- Google Calendar API Docs: https://developers.google.com/calendar")

if __name__ == "__main__":
    main() 