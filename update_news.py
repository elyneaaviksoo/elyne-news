import os
import requests
import time
from openai import OpenAI

GNEWS_KEY = os.environ.get("GNEWS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# 2. Määratleme teemad. 
# Viimase kategooria puhul kasutame spetsiaalset märksõnaotsingut (search?q=...), et leida kunsti, kellasid ja autosid!
categories = [
    {"name": "Päevakajalised sündmused", "endpoint": "top-headlines?category=general"},
    {"name": "Majandus & Äri", "endpoint": "top-headlines?category=business"},
    {"name": "Poliitika & Geopoliitika", "endpoint": "top-headlines?category=world"},
    {"name": "Teadus & Haridus", "endpoint": "top-headlines?category=science"},
    {"name": "Kunst, Autod ja Kellad", "endpoint": 'search?q="art" OR "supercars" OR "luxury watches" OR "hypercars"'}
]

all_articles_by_category = {}

print("Alustan uudiste otsimist...")

# 3. Otsime iga teema kohta 8 uudist (kokku 40)
for cat in categories:
    cat_name = cat["name"]
    endpoint = cat["endpoint"]
    
    url = f"https://gnews.io/api/v4/{endpoint}&lang=en&max=8&apikey={GNEWS_KEY}"
    response = requests.get(url)
    data = response.json()
    
    valid_articles = []
    if "articles" in data:
        for art in data["articles"]:
            valid_articles.append({
                "title": art["title"],
                "description": art["description"],
                "url": art["url"],
                "image": art["image"]
            })
    all_articles_by_category[cat_name] = valid_articles
    time.sleep(1) # Ootame 1 sekundi, et süsteemi mitte üle koormata

# 4. Loome disaini (roosa, tumehall, must)
html = """
<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elyne Igapäevane Ajaleht</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #fcfcfc; color: #111827; }
        h1, h2, h3, .serif { font-family: 'Playfair Display', serif; }
        .bg-blush { background-color: #fdf2f8; }
        .text-darkgray { color: #374151; }
    </style>
</head>
<body class="antialiased">

    <!-- Päis -->
    <header class="bg-blush py-20 px-4 mb-16 border-b border-pink-100 text-center">
        <h1 class="text-6xl md:text-8xl font-bold text-gray-900 mb-6 tracking-tight">Elyne Ajaleht</h1>
        <p class="text-xl text-gray-700 max-w-2xl mx-auto font-light">Sinu isiklik, tehisintellekti poolt kokku pandud ülevaade tänase päeva olulisimatest sündmustest terves maailmas.</p>
    </header>

    <main class="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
"""

print("Tõlgin uudiseid...")

# 5. Käime kõik 40 uudist läbi ja laseme OpenAI-l teha kokkuvõtted
for cat_name, articles in all_articles_by_category.items():
    if not articles:
        continue
        
    html += f"""
    <section class="mb-20">
        <h2 class="text-5xl font-bold text-gray-900 mb-10 pb-4 border-b-2 border-pink-200">{cat_name}</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
    """
    
    for art in articles:
        prompt = f"Tõlgi järgneva ingliskeelse uudise pealkiri eesti keelde. Seejärel tee uudise sisust täpselt 3-lauseline eestikeelne kokkuvõte.\n\nPealkiri: {art['title']}\nSisu: {art['description']}\n\nVasta TÄPSELT sellises formaadis:\nPEALKIRI: [sinu eestikeelne pealkiri]\nKOKKUVÕTE: [sinu 3-lauseline kokkuvõte]"
        
        try:
            ai_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            vastus = ai_response.choices[0].message.content
            
            est_title = art['title']
            est_summary = art['description']
            
            for line in vastus.split('\n'):
                if line.startswith('PEALKIRI:'):
                    est_title = line.replace('PEALKIRI:', '').strip()
                elif line.startswith('KOKKUVÕTE:'):
                    est_summary = line.replace('KOKKUVÕTE:', '').strip()
        except Exception as e:
            est_title = "Viga tõlkimisel"
            est_summary = "Selle artikli kokkuvõtte tegemine ebaõnnestus."

        img_url = art['image'] or 'https://via.placeholder.com/600x400?text=Pilt+puudub'
        
        html += f"""
        <article class="bg-white rounded-lg shadow hover:shadow-xl transition-shadow duration-300 overflow-hidden flex flex-col border border-gray-200">
            <img src="{img_url}" alt="Uudise pilt" class="w-full h-52 object-cover">
            <div class="p-6 flex-1 flex flex-col">
                <h3 class="text-2xl font-bold text-gray-900 mb-4 leading-snug">{est_title}</h3>
                <p class="text-gray-900 text-base mb-6 flex-1">{est_summary}</p>
                <a href="{art['url']}" target="_blank" class="text-pink-600 font-bold text-sm hover:text-pink-800 transition-colors uppercase tracking-widest inline-flex items-center mt-auto">
                    Loe originaali &rarr;
                </a>
            </div>
        </article>
        """
    html += '</div></section>'

html += """
    </main>
    <footer class="bg-gray-900 py-16 text-center mt-20">
        <h2 class="text-5xl font-bold text-white mb-6 serif tracking-widest uppercase">ELYNE</h2>
        <p class="text-gray-400 font-light">See leht uueneb igal hommikul automaatselt tehisintellekti abil.</p>
    </footer>
</body>
</html>
"""

# 6. Salvestame HTML faili
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Kõik uudised edukalt töödeldud ja index.html salvestatud!")
