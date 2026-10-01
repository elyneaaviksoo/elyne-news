import os
import requests
import time
from openai import OpenAI

GNEWS_KEY = os.environ.get("GNEWS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# 1. Määratleme kategooriad ja spetsiaalsed otsingud
# "Päevakajalised sündmused" teeb kaks päringut: 6 globaalset ja kohustuslikud 2 uudist Aasiast!
categories = [
    {"name": "Päevakajalised sündmused", "queries": [
        {"endpoint": "top-headlines?category=general", "max": 6},
        {"endpoint": 'search?q="Asia" OR "China" OR "India" OR "Japan"', "max": 2}
    ]},
    {"name": "Majandus & Äri", "queries": [{"endpoint": "top-headlines?category=business", "max": 8}]},
    {"name": "Poliitika & Geopoliitika", "queries": [{"endpoint": "top-headlines?category=world", "max": 8}]},
    {"name": "Teadus & Haridus", "queries": [{"endpoint": "top-headlines?category=science", "max": 8}]},
    {"name": "Kunst, Autod ja Kellad", "queries": [{"endpoint": 'search?q="art" OR "supercars" OR "luxury watches" OR "hypercars"', "max": 8}]}
]

all_articles_by_category = {}

print("Alustan uudiste otsimist...")

# 2. Otsime andmed
for cat in categories:
    cat_name = cat["name"]
    valid_articles = []
    
    for q in cat["queries"]:
        url = f"https://gnews.io/api/v4/{q['endpoint']}&lang=en&max={q['max']}&apikey={GNEWS_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if "articles" in data:
            for art in data["articles"]:
                valid_articles.append({
                    "title": art["title"],
                    "description": art["description"],
                    "url": art["url"],
                    "image": art["image"]
                })
        time.sleep(1) # Ootame 1 sekundi, et süsteemi mitte üle koormata
        
    all_articles_by_category[cat_name] = valid_articles

# 3. Loome disaini (koos ajakirja stiilis fontidega)
html = """
<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elyne Ajaleht</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=Lato:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Lato', sans-serif; background-color: #faf9f9; color: #1a1a1a; }
        h1, h2, h3, .magazine-font { font-family: 'Playfair Display', serif; }
        .text-blush { color: #d98cb3; } 
        .border-blush { border-color: #fce4ec; } 
        .bg-blush-light { background-color: #fff0f5; }
    </style>
</head>
<body class="antialiased">

    <!-- Päis -->
    <header class="bg-blush-light pt-24 pb-20 px-4 mb-20 border-b-2 border-blush text-center">
        <h1 class="text-7xl md:text-[9rem] font-black text-gray-900 mb-4 tracking-tighter uppercase leading-none">Elyne</h1>
        <p class="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto font-light tracking-wide">Päevakajaline ülevaade maailma olulisimatest sündmustest.</p>
    </header>

    <main class="max-w-screen-2xl mx-auto px-6 sm:px-12 lg:px-16">
"""

print("Tõlgin uudiseid ja määran regiooni...")

# 4. Käime uudised läbi ja küsime AI-lt tõlget + regiooni
for cat_name, articles in all_articles_by_category.items():
    if not articles:
        continue
        
    html += f"""
    <section class="mb-28">
        <div class="flex items-center mb-12">
            <h2 class="text-5xl md:text-6xl font-bold text-gray-900 italic pr-6">{cat_name}</h2>
            <div class="flex-grow border-t-2 border-blush"></div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-x-12 gap-y-16">
    """
    
    for art in articles:
        # Õpetame AI-d lisama regiooni!
        prompt = f"Määra, millisest maailmajaost (nt Aasia, Euroopa, Põhja-Ameerika, Lõuna-Ameerika, Aafrika, Austraalia/Okeaania või Globaalne) järgnev uudis peamiselt räägib. Tõlgi pealkiri eesti keelde ja tee sisust täpselt 3-lauseline eestikeelne kokkuvõte.\n\nPealkiri: {art['title']}\nSisu: {art['description']}\n\nVasta TÄPSELT sellises formaadis (ilma tühjade ridadeta):\nREGIOON: [Maailmajagu]\nPEALKIRI: [eestikeelne pealkiri]\nKOKKUVÕTE: [3-lauseline kokkuvõte]"
        
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
            
            for line in vastus.split('\n'):
                if line.startswith('REGIOON:'):
                    est_region = line.replace('REGIOON:', '').strip()
                elif line.startswith('PEALKIRI:'):
                    est_title = line.replace('PEALKIRI:', '').strip()
                elif line.startswith('KOKKUVÕTE:'):
                    est_summary = line.replace('KOKKUVÕTE:', '').strip()
        except Exception as e:
            est_title = "Viga töötlemisel"
            est_summary = "Selle artikli tõlkimine ebaõnnestus."
            est_region = "Määramata"

        img_url = art['image'] or 'https://via.placeholder.com/600x400?text=ELYNE+NEWS'
        
        # Lisasime regiooni (est_region) disaini pealkirja kohale!
        html += f"""
        <article class="flex flex-col group">
            <div class="overflow-hidden mb-5">
                <img src="{img_url}" alt="Uudise pilt" class="w-full h-64 object-cover transform group-hover:scale-105 transition-transform duration-700 ease-in-out">
            </div>
            <span class="text-blush font-bold text-xs tracking-[0.2em] uppercase mb-3 block">{est_region}</span>
            <h3 class="text-3xl font-bold text-gray-900 mb-4 leading-tight group-hover:text-gray-600 transition-colors duration-300">{est_title}</h3>
            <p class="text-gray-700 text-lg mb-6 font-light leading-relaxed flex-grow">{est_summary}</p>
            <a href="{art['url']}" target="_blank" class="text-blush font-bold text-sm tracking-[0.2em] uppercase hover:text-pink-800 transition-colors inline-flex items-center mt-auto pb-2 border-b border-transparent hover:border-pink-800 w-max">
                Loe originaali &rarr;
            </a>
        </article>
        """
    html += '</div></section>'

html += """
    </main>
    <footer class="bg-gray-900 pt-32 pb-20 px-4 text-center mt-32">
        <h2 class="text-7xl md:text-[12rem] font-black text-white mb-8 magazine-font tracking-tighter uppercase leading-none opacity-90">Elyne</h2>
        <div class="w-24 h-1 bg-blush mx-auto mb-8"></div>
        <p class="text-gray-400 font-light text-lg tracking-widest uppercase">Tehisintellekti kureeritud globaalne ülevaade</p>
    </footer>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Kõik uudised koos regioonidega töödeldud ja salvestatud!")

