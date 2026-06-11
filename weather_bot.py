import os
import smtplib
from email.message import EmailMessage
import requests

# 1. Configuration from GitHub Secrets / Environment Variables
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
LAT = os.environ.get("WEATHER_LAT", "10.77")   
LON = os.environ.get("WEATHER_LON", "76.31")  
EMAIL_USER = os.environ.get("SENDER_EMAIL")
EMAIL_PASS = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

# 2. Fetch data from the One Call 4.0 API
# Note: Adding '&units=metric' ensures temperature is in Celsius
url = f"https://api.openweathermap.org/data/4.0/onecall/current?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # The One Call API structures current weather inside a nested 'current' object
    current_data = data["current"]
    temp = current_data["temp"]
    weather_main = [w["main"].lower() for w in current_data["weather"]]

    print(f"Current temperature at coordinates ({LAT}, {LON}): {temp}°C")
    print(f"Weather conditions: {', '.join(weather_main)}")

    # 3. Check thresholds
    is_hot = temp > 35
    is_raining = "rain" in weather_main

    if is_hot or is_raining:
        print("Conditions met! Preparing alert email...")

        subject = f"Weather Alert for Coordinates {LAT}, {LON}!"
        body = f"An automated alert has been triggered.\n\n"
        if is_hot:
            body += f"⚠️ High Temperature Alert: It is currently {temp}°C (Threshold: >35°C).\n"
        if is_raining:
            body += f"🌧️ Rain Alert: Precipitation has been detected in the current conditions.\n"

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = EMAIL_USER
        msg["To"] = RECEIVER_EMAIL
        msg.set_content(body)

        # 4. Send Email via SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        print("Email sent successfully!")
    else:
        print("Weather is within safe parameters. No email sent.")

except Exception as e:
    print(f"An error occurred: {e}")