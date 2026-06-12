import os
import smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup
from datetime import datetime

EMAIL_USER = os.environ.get("SENDER_EMAIL")
EMAIL_PASS = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ml,en-US;q=0.9,en;q=0.8"
}

def scrape_mathrubhumi():
    headlines = []
    url = "https://www.mathrubhumi.com/news/kerala"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        for link_element in soup.find_all("a"):
            title_element = link_element.find("h2") or link_element.find("h3")
            if title_element:
                title = title_element.get_text(strip=True)
                link = link_element["href"]
                if title and link and len(title) > 15:
                    if not link.startswith("http"):
                        link = "https://www.mathrubhumi.com" + link
                    if {"title": title, "link": link} not in headlines:
                        headlines.append({"title": title, "link": link})
            if len(headlines) >= 5:
                break
    except Exception as e:
        print(f"Error Mathrubhumi: {e}")
    return headlines

def scrape_manorama():
    headlines = []
    url = "https://www.manoramaonline.com/news/kerala.html"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        for link_element in soup.find_all("a"):
            link = link_element.get("href", "")
            if ".html" in link and any(keyword in link for keyword in ["/news/", "/kerala/"]):
                title = link_element.get_text(strip=True)
                if title and len(title) > 20 and not title.startswith("തീയതി"):
                    if not link.startswith("http"):
                        link = "https://www.manoramaonline.com" + link
                    if {"title": title, "link": link} not in headlines:
                        headlines.append({"title": title, "link": link})
            if len(headlines) >= 5:
                break
    except Exception as e:
        print(f"Error Manorama: {e}")
    return headlines

def scrape_asianet():
    headlines = []
    url = "https://www.asianetnews.com/news"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        for link_element in soup.find_all("a"):
            link = link_element.get("href", "")
            if "-" in link and any(char.isdigit() for char in link) and link.startswith("https://www.asianetnews.com/"):
                title = link_element.get_text(strip=True)
                if title and len(title) > 20:
                    if {"title": title, "link": link} not in headlines:
                        headlines.append({"title": title, "link": link})
            if len(headlines) >= 5:
                break
    except Exception as e:
        print(f"Error Asianet: {e}")
    return headlines

def build_html_body(news_data):
    today_str = datetime.now().strftime("%A, %B %d, %Y")
    
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="font-family: 'Gayathri', 'Manjari', Arial, sans-serif; color: #333; background-color: #f4f6f9; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e1e8ed;">
            <h1 style="color: #0c4a6e; border-bottom: 3px solid #0c4a6e; padding-bottom: 10px; margin-top: 0; font-size: 24px;">മലയാളം വാർത്താ ചുരുക്കം (Malayalam Digest)</h1>
            <p style="color: #657786; font-style: italic;">തീയതി: {today_str}</p>
    """
    
    for source, articles in news_data.items():
        html += f'<h2 style="color: #b91c1c; margin-top: 25px; border-bottom: 1px solid #e1e8ed; padding-bottom: 5px; font-size: 18px;">{source}</h2>'
        if not articles:
            html += '<p style="color: #999;">വാർത്തകൾ ലഭ്യമല്ല.</p>'
        else:
            html += '<ul style="padding-left: 20px; margin: 0; line-height: 1.6;">'
            for art in articles:
                html += f"""
                <li style="margin-bottom: 12px;">
                    <a href="{art['link']}" style="color: #0284c7; font-weight: bold; text-decoration: none; font-size: 15px;">{art['title']}</a>
                </li>
                """
            html += '</ul>'
            
    html += """
            <hr style="border: 0; border-top: 1px solid #e1e8ed; margin-top: 30px;">
            <p style="font-size: 11px; color: #aab8c2; text-align: center; margin-bottom: 0;">Automated Malayalam News Summary Bot powered by GitHub Actions.</p>
        </div>
    </body>
    </html>
    """
    return html

def main():
    print("Beginning Malayalam portal sweep...")
    news_data = {
        "Mathrubhumi (മാതൃഭൂമി)": scrape_mathrubhumi(),
        "Manorama Online (മനോരമ ഓൺലൈൻ)": scrape_manorama(),
        "Asianet News (ഏഷ്യാനെറ്റ് ന്യൂസ്)": scrape_asianet()
    }
    
    html_content = build_html_body(news_data)
    
    msg = EmailMessage()
    msg["Subject"] = f"മലയാളം വാർത്തകൾ - {datetime.now().strftime('%d %b')}"
    msg["From"] = EMAIL_USER
    msg["To"] = RECEIVER_EMAIL
    
    msg.set_content("Please use an HTML enabled email client to read the digest.")
    msg.add_alternative(html_content, subtype="html")
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print("Malayalam newsletter successfully dispatched!")
    except Exception as e:
        print(f"Error handling email transport: {e}")

if __name__ == "__main__":
    main()