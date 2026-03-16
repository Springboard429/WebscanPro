#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup

# Try different approaches to setup DVWA
print("🔧 DVWA Database Setup - Alternative Approaches...")

session = requests.Session()

# Get setup page
response = session.get("http://localhost:45/setup.php")
soup = BeautifulSoup(response.text, 'html')

# Look for all forms and inputs
print("🔍 Analyzing setup page forms...")

forms = soup.find_all('form')
for i, form in enumerate(forms):
    print(f"\nForm {i+1}:")
    print(f"  Action: {form.get('action', 'N/A')}")
    print(f"  Method: {form.get('method', 'N/A')}")
    
    inputs = form.find_all('input')
    for inp in inputs:
        name = inp.get('name', 'N/A')
        input_type = inp.get('type', 'N/A')
        value = inp.get('value', 'N/A')
        print(f"  Input: {name} ({input_type}) = '{value}'")

# Try clicking the setup button with different data
print(f"\n🎯 Trying database creation...")

# Try approach 1: Look for any submit button
submit_buttons = soup.find_all('input', {'type': ['submit', 'button']})
print(f"Found {len(submit_buttons)} submit buttons")

for button in submit_buttons:
    button_name = button.get('name', '')
    button_value = button.get('value', '')
    print(f"Button: {button_name} = '{button_value}'")
    
    if button_name:  # If button has a name, try submitting
        setup_data = {button_name: button_value}
        
        response = session.post("http://localhost:45/setup.php", data=setup_data)
        print(f"Response with {button_name}: {response.status_code}")
        
        if 'login.php' in response.text.lower() or 'successfully' in response.text.lower():
            print("✅ Database setup successful!")
            break

# Try approach 2: Direct POST without data
print(f"\n🔄 Trying empty POST to setup...")
response = session.post("http://localhost:45/setup.php", data={})
print(f"Empty POST response: {response.status_code}")

# Try approach 3: Check if there are any config issues
print(f"\n⚙️  Checking for configuration messages...")
if 'config' in response.text.lower() or 'permission' in response.text.lower():
    print("Found configuration-related text in response")
    
print(f"\n📄 Last response preview (500 chars):")
print(response.text[:500])
