import os
import requests
import time
import datetime
import xml.etree.ElementTree as ET
from openai import OpenAI

GNEWS_KEY = os.environ.get("GNEWS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

all_articles = []
seen_urls = set()

print("Otsin Eesti uudiseid otse ERR-ist...")

# 1. ERR-i UUDISTE LUGEMINE
try:
    err_response = requests.get("https://www.err.ee/rss")
    err_root = ET.fromstring(err_response.content)
    
    added_err = 0
    # Käime läbi kõik ERR-i uudised
    for item in err_root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        description = item.find('description').text
        
        # Proovime leida uudise pilti
        image_url = ""
        enclosure = item.find('enclosure')
        if enclosure is not None:
            image_url = enclosure.get('url', '')
            
        if link not in seen_urls:
            seen_urls.add(link)
            all_articles.append({
                "category": "Päevakajalised",
                "title": title,
                "description": description,
                "url": link,
                "image": image_url
            })
            added_err += 1
            
        # Võtame täpselt 2 kõige värskemat ERR-i uudist
        if added_err >= 2:
            break
except Exception as e:
    print("Viga ERR-ist lugemisel:", e)


# 2. GNEWS MAAILMAUUDISTE LUGEMINE (22 uudist)
print("Otsin ülejäänud maailmauudiseid GNewsist...")

categories = [
    # Päevakajaliste alt võtame nüüd vaid 1 globaalse (sest 2 tk on juba ERRist käes)
    {"name": "Päevakajalised", "queries": [{"endpoint": "top-headlines?category=general", "limit": 1}]},
    {"name": "Majandus", "queries": [{"endpoint": "top-headlines?category=business", "limit": 3}]},
    {"name": "(Geo)poliitika", "queries": [{"endpoint": "top-headlines?category=world", "limit": 3}]},
    {"name": "Haridus", "queries": [{"endpoint": 'search?q="education" OR "university" OR "school"', "limit": 3}]},
    {"name": "Autod", "queries": [{"endpoint": 'search?q="supercars" OR "automotive" OR "electric cars"', "limit": 3}]},
    {"name": "Kellad ja ehted", "queries": [{"endpoint": 'search?q="luxury watches" OR "jewelry" OR "diamonds"', "limit": 3}]},
    {"name": "Meelelahutus", "queries": [{"endpoint": "top-headlines?category=entertainment", "limit": 3}]},
    {"name": "Tervis", "queries": [{"endpoint": "top-headlines?category=health", "limit": 3}]}
]

for cat in categories:
    cat_name = cat["name"]
    for q in cat["queries"]:
        url = f"https://gnews.io/api/v4/{q['endpoint']}&lang=en&max=5&apikey={GNEWS_KEY}"
        response = requests.get(url)
        data = response.json()
        
        added_count = 0
        if "articles" in data:
            for art in data["articles"]:
                art_url = art["url"]
                if art_url not in seen_urls:
                    seen_urls.add(art_url)
                    all_articles.append({
                        "category": cat_name,
                        "title": art["title"],
                        "description": art["description"],
                        "url": art_url,
                        "image": art["image"]
                    })
                    added_count += 1
                    if added_count >= q["limit"]:
                        break
        time.sleep(1)


# 3. TÄNANE KUUPÄEV
kuud = ["jaanuar", "veebruar", "märts", "aprill", "mai", "juuni", "juuli", "august", "september", "oktoober", "november", "detsember"]
tana = datetime.datetime.now()
kuupaev_tekst = f"{tana.day}. {kuud[tana.month - 1]} {tana.year}"

# 4. HTML BAAS (Disain 1: Neobrutalism)
html = f"""
<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lihtsalt üks valik uudiseid</title>
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

    <header class="max-w-7xl mx-auto mb-16 brutal-card p-8 md:p-12 bg-yellow-50">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 border-b-4 border-black pb-4">
            <h1 class="text-7xl md:text-9xl font-marquee uppercase leading-none">Lihtsalt üks valik uudiseid</h1>
            <div class="text-2xl font-black mt-4 md:mt-0 font-marquee">{kuupaev_tekst}</div>
        </div>
        <p class="text-lg md:text-xl font-medium leading-relaxed max-w-4xl">
            Ma ei satu eriti uudiseid lugema.. seega mõtlesin, et vaib-koodin endale oma isikliku uudistesaidi, mis iga päev kogub kokku maailmast 24 erinevat uudist. Ja ise valin teemad endale! <br>Et küll ma siis alles hakkan lugema. <br>Aga vaib-koodisin valmis ja tuli välja, et ma lihtsalt ei viitsi uudiseid lugeda ☹ <br>Kuni ma välja mõtlen, mis edasi teha, jookseb see leht siin edasi.. iga päev, 24 uudist maailmas, minu valitud teemadel.
        </p>
    </header>

    <main class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10 pb-20">
"""

print(f"Tõlgin uudiseid ({len(all_articles)} tk), määran regioone ja arvutan skoore...")

# 5. LASEME AI-L ANDMEID TÖÖDELDA
for art in all_articles:
    # Lisasime juhendisse punkti, et eestikeelseid pealkirju ei tõlgitaks!
    prompt = f"Määra, millisest maailmajaost (Eesti, Euroopa, Aafrika, Aasia, Põhja-Ameerika, Lõuna-Ameerika või Globaalne) järgnev uudis räägib. Hinda 10 palli süsteemis, kui oluline või mõjukas on see uudis (anna ainult number, nt 7.5). Kui tekst on juba eesti keeles, jäta pealkiri originaali, muidu tõlgi see eesti keelde. Tee sisust täpselt 3-lauseline eestikeelne kokkuvõte.\n\nPealkiri: {art['title']}\nSisu: {art['description']}\n\nVasta TÄPSELT sellises formaadis:\nREGIOON: [Maailmajagu]\nSKOOR: [Number]\nPEALKIRI: [Eestikeelne pealkiri]\nKOKKUVÕTE: [3-lauseline kokkuvõte]"
    
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
        est_title = art['title']
        est_summary = "Selle artikli töötlemine ebaõnnestus."
        est_region = "Määramata"
        est_score = "?"

    img_url = art['image'] or 'https://via.placeholder.com/800x600/ffd6e0/000000?text=PILT+PUUDUB'
    
    html += f"""
        <article class="brutal-card flex flex-col">
            <div class="border-b-4 border-black relative">
                <img src="{img_url}" alt="Pilt" class="w-full h-56 object-cover bg-white">
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


print("Kõik 24 unikaalset uudist on valmis ja salvestatud!")
