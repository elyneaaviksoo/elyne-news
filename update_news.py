import os
import requests
import time
import datetime
from openai import OpenAI

GNEWS_KEY = os.environ.get("GNEWS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# 1. Kategooriad (8 tk, igast 5 uudist = 40)
categories = [
    {"name": "Päevakajalised", "endpoint": "top-headlines?category=general"},
    {"name": "Majandus", "endpoint": "top-headlines?category=business"},
    {"name": "(Geo)poliitika", "endpoint": "top-headlines?category=world"},
    {"name": "Haridus", "endpoint": 'search?q="education" OR "university" OR "school"'},
    {"name": "Autod", "endpoint": 'search?q="supercars" OR "automotive" OR "electric cars"'},
    {"name": "Kellad ja ehted", "endpoint": 'search?q="luxury watches" OR "jewelry" OR "diamonds"'},
    {"name": "Meelelahutus", "endpoint": "top-headlines?category=entertainment"},
    {"name": "Tervis", "endpoint": "top-headlines?category=health"}
]

all_articles = []

print("Otsin 40 uudist 8 kategooriast...")

for cat in categories:
    cat_name = cat["name"]
    url = f"https://gnews.io/api/v4/{cat['endpoint']}&lang=en&max=5&apikey={GNEWS_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "articles" in data:
        for art in data["articles"]:
            all_articles.append({
                "category": cat_name,
                "title": art["title"],
                "description": art["description"],
                "url": art["url"],
                "image": art["image"]
            })
    time.sleep(1)

# 2. Tänane kuupäev
kuud = ["jaanuar", "veebruar", "märts", "aprill", "mai", "juuni", "juuli", "august", "september", "oktoober", "november", "detsember"]
tana = datetime.datetime.now()
kuupaev_tekst = f"{tana.day}. {kuud[tana.month - 1]} {tana.year}"

# 3. HTML Baas (Disain 1: Neobrutalism)
html = f"""
<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minu Uudisteleht</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        body {{ 
            background-color: #ffd6e0; 
            font-family: 'Inter', sans-serif; 
            color: #111;
        }}
        .font-marquee {{ font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px; }}
        .brutal-card {{
            background-color: #ffffff;
            border: 4px solid #000000;
            box-shadow: 8px 8px 0px 0px #000000;
            transition: all 0.2s ease-in-out;
        }}
        .brutal-card:hover {{
            transform: translate(-4px, -4px);
            box-shadow: 12px 12px 0px 0px #000000;
        }}
        .brutal-tag {{ border: 2px solid #000; box-shadow: 2px 2px 0px 0px #000; }}
    </style>
</head>
<body class="antialiased p-4 md:p-8">

    <!-- PÄIS JA INTRO -->
    <header class="max-w-7xl mx-auto mb-16 brutal-card p-8 md:p-12 bg-yellow-50">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 border-b-4 border-black pb-4">
            <h1 class="text-7xl md:text-9xl font-marquee uppercase leading-none">Minu Uudised</h1>
            <div class="text-2xl font-black mt-4 md:mt-0 font-marquee">{kuupaev_tekst}</div>
        </div>
        <p class="text-lg md:text-xl font-medium leading-relaxed max-w-4xl">
            Ma eriti ei loe uudiseid ja olemasolevate uudisteportaaline ning ajalehtede uudiste valik tundus mulle liiga kallutatud.. seega mõtlesin, et vaib-koudin endale oma isikliku uudistesaidi, mis iga päev kogub kokku maailmast 40 erinevat uudist. Ja ise valin teemad endale! Et küll ma siis alles hakkan lugema. Aga vaib-koodisin valmis ja tuli välja, et ma lihtsalt ei viitsi uudiseid lugeda ☹ Kuni ma välja mõtlen, mis edasi teha, jookseb see leht siin edasi.. iga päev, 40 uudist maailmas, minu valitud teemadel.
        </p>
    </header>

    <main class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 pb-20">
"""

print("Tõlgin uudiseid, määran regioone ja arvutan skoore...")

# 4. Laseme AI-l andmeid töödelda
for art in all_articles:
    prompt = f"Määra, millisest maailmajaost (Eesti, Euroopa, Aafrika, Aasia, Põhja-Ameerika, Lõuna-Ameerika või Globaalne) järgnev uudis räägib. Hinda 10 palli süsteemis, kui oluline või mõjukas on see uudis maailma mastaabis (anna ainult number, nt 7.5). Tõlgi pealkiri eesti keelde ja tee sisust täpselt 3-lauseline eestikeelne kokkuvõte.\n\nPealkiri: {art['title']}\nSisu: {art['description']}\n\nVasta TÄPSELT sellises formaadis:\nREGIOON: [Maailmajagu]\nSKOOR: [Number]\nPEALKIRI: [Eestikeelne pealkiri]\nKOKKUVÕTE: [3-lauseline kokkuvõte]"
    
    try:
        ai_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        vastus = ai_response.choices[0].message.content
        
        est_title = art['title']
        est_summary = art['description']
        est_region = "Globaalne"
        est_score = "5.0"
        
        for line in vastus.split('\n'):
            line = line.strip()
            if line.startswith('REGIOON:'):
                est_region = line.replace('REGIOON:', '').strip()
            elif line.startswith('SKOOR:'):
                est_score = line.replace('SKOOR:', '').strip()
            elif line.startswith('PEALKIRI:'):
                est_title = line.replace('PEALKIRI:', '').strip()
            elif line.startswith('KOKKUVÕTE:'):
                est_summary = line.replace('KOKKUVÕTE:', '').strip()
    except Exception as e:
        est_title = "Viga töötlemisel"
        est_summary = "Selle artikli tõlkimine ebaõnnestus."
        est_region = "Määramata"
        est_score = "?"

    img_url = art['image'] or 'https://via.placeholder.com/800x600/ffd6e0/000000?text=PILT+PUUDUB'
    
    html += f"""
        <article class="brutal-card flex flex-col">
            <div class="border-b-4 border-black relative">
                <img src="{img_url}" alt="Pilt" class="w-full h-56 object-cover">
                <div class="absolute bottom-4 right-4 bg-black text-white px-3 py-1 font-bold text-sm">🔥 Mõju: {est_score}/10</div>
            </div>
            <div class="p-6 flex flex-col flex-grow">
                <div class="flex flex-wrap gap-2 mb-4">
                    <span class="bg-pink-300 text-black px-2 py-1 text-xs font-bold uppercase brutal-tag">{art['category']}</span>
                    <span class="bg-blue-300 text-black px-2 py-1 text-xs font-bold uppercase brutal-tag">{est_region}</span>
                </div>
                <a href="{art['url']}" target="_blank" class="hover:text-pink-600 transition-colors">
                    <h2 class="text-4xl font-marquee uppercase leading-tight mb-4">{est_title}</h2>
                </a>
                <p class="text-sm font-medium leading-relaxed mb-6 flex-grow">{est_summary}</p>
            </div>
        </article>
    """

html += """
    </main>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Kõik 40 uudist on valmis ja uues disainis salvestatud!")
