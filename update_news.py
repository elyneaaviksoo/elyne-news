import os
import requests
from openai import OpenAI

# 1. Loeme salajased võtmed GitHubi seifist
GNEWS_KEY = os.environ.get("GNEWS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# 2. Küsime GNewsist viimaseid uudiseid (näitena ingliskeelsed maailmauudised)
url = f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&max=5&apikey={GNEWS_KEY}"
response = requests.get(url)
news_data = response.json()

# Siia hakkame koguma uut HTML sisu
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

# 3. Käime uudised läbi ja laseme AI-l kokkuvõtted teha
if "articles" in news_data:
    for article in news_data["articles"]:
        title = article["title"]
        url = article["url"]
        image = article["image"]
        
        # Palume AI-l teha eestikeelne kokkuvõte
        prompt = f"Tõlgi ja tee sellest uudisest lühike 3-lauseline eestikeelne kokkuvõte: {article['description']} {article['content']}"
        
        ai_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        kokkuvote = ai_response.choices[0].message.content
        
        # Lisame uudise meie HTML lehele
        html_content += f"""
        <div style="margin-bottom: 30px; border-bottom: 1px solid #ccc; padding-bottom: 20px;">
            <h2><a href="{url}" style="color: #333; text-decoration: none;">{title}</a></h2>
            <img src="{image}" style="max-width: 300px; border-radius: 8px;">
            <p>{kokkuvote}</p>
        </div>
        """

html_content += "</body></html>"

# 4. Salvestame uue lehe (kirjutab vana index.html üle)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Uudised uuendatud ja index.html salvestatud!")
