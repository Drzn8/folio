import os
import smtplib
from email.message import EmailMessage
import requests

# 1. Configuration from GitHub Secrets / Environment Variables
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
CITY = os.environ.get("WEATHER_CITY", "London")  # Fallback to London if not set
EMAIL_USER = os.environ.get("SENDER_EMAIL")
EMAIL_PASS = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

# 2. Fetch data from OpenWeatherMap (Current Weather Data API)
url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Extract required fields
    temp = data["main"]["temp"]
    # OpenWeatherMap groups conditions like 'Rain', 'Snow', 'Clear', etc.
    weather_main = [w["main"].lower() for w in data["weather"]]

    print(f"Current temperature in {CITY}: {temp}°C")
    print(f"Weather conditions: {', '.join(weather_main)}")

    # 3. Check thresholds (Temp > 35°C or Rain predicted/occurring)
    is_hot = temp > 35
    is_raining = "rain" in weather_main

    if is_hot or is_raining:
        print("Conditions met! Preparing alert email...")

        # Build email alert content
        subject = f"Weather Alert for {CITY}!"
        body = f"An automated alert has been triggered for {CITY}.\n\n"
        if is_hot:
            body += f"⚠️ High Temperature Alert: It is currently {temp}°C (Threshold: >35°C).\n"
        if is_raining:
            body += f"🌧️ Rain Alert: Precipitation has been detected in the current conditions.\n"

        # Create message object
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = RECEIVER_EMAIL
        msg.set_content(body)

        # 4. Send Email via SMTP (Example using Gmail's server)
        # Note: If using Gmail, you MUST generate an "App Password" 
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        print("Email sent successfully!")
    else:
        print("Weather is within safe parameters. No email sent.")

except Exception as e:
    print(f"An error occurred: {e}")