import os
import requests
from openai import OpenAI
import json

GNEWS_KEY = os.environ.get("GNEWS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

html_content = """
<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <title>Elyne Uudised</title>
</head>
<body style="font-family: sans-serif; background: #fdfbfb; color: #333; padding: 20px;">
    <h1 style="color: #ffb6c1;">Minu Igapäevane Ajaleht</h1>
"""

try:
    # 1. Kontrollime, kas võtmed on üldse olemas
    if not GNEWS_KEY or not OPENAI_KEY:
        html_content += "<p style='color:red;'>VIGA: API võtmed puuduvad GitHubi Secrets alt!</p>"
    else:
        client = OpenAI(api_key=OPENAI_KEY)
        
        # 2. Küsime uudiseid
        url = f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&max=5&apikey={GNEWS_KEY}"
        response = requests.get(url)
        news_data = response.json()
        
        # 3. Vaatame, kas saime artiklid või veateate
        if "articles" in news_data:
            if len(news_data["articles"]) == 0:
                html_content += "<p>Uudiseid ei leitud, aga süsteem töötab.</p>"
            else:
                for article in news_data["articles"]:
                    prompt = f"Tõlgi ja tee sellest uudisest 3-lauseline eestikeelne kokkuvõte: {article['description']}"
                    
                    ai_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    kokkuvote = ai_response.choices[0].message.content
                    
                    html_content += f"""
                    <div style="margin-bottom: 30px; border-bottom: 1px solid #ccc; padding-bottom: 20px;">
                        <h2><a href="{article['url']}">{article['title']}</a></h2>
                        <img src="{article['image']}" style="max-width: 300px; border-radius: 8px;">
                        <p>{kokkuvote}</p>
                    </div>
                    """
        else:
            # 4. KUI TEKKIS VIGA, TRÜKIME SELLE VEEBILEHELE
            html_content += f"<p style='color:red;'><b>Viga GNews API-lt:</b> {json.dumps(news_data)}</p>"
            
except Exception as e:
    # Kui tekib mingi muu, nt OpenAI viga
    html_content += f"<p style='color:red;'><b>Süsteemne viga:</b> {str(e)}</p>"

html_content += "</body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Skript lõpetas töö!")
