import os
import requests
import time
import datetime
from openai import OpenAI

GNEWS_KEY = os.environ.get("GNEWS_API_KEY")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# 1. Määratleme kategooriad ja otsingud
categories = [
    {"name": "Päevakajalised sündmused", "id": "paevakajaline", "queries": [
        {"endpoint": "top-headlines?category=general", "max": 6},
        {"endpoint": 'search?q="Asia" OR "China" OR "India" OR "Japan"', "max": 2}
    ]},
    {"name": "Majandus & Äri", "id": "majandus", "queries": [{"endpoint": "top-headlines?category=business", "max": 8}]},
    {"name": "Poliitika & Geopoliitika", "id": "poliitika", "queries": [{"endpoint": "top-headlines?category=world", "max": 8}]},
    {"name": "Teadus & Haridus", "id": "teadus", "queries": [{"endpoint": "top-headlines?category=science", "max": 8}]},
    {"name": "Kunst, Autod ja Kellad", "id": "elustiil", "queries": [{"endpoint": 'search?q="art" OR "supercars" OR "luxury watches" OR "hypercars"', "max": 8}]}
]

all_articles_by_category = {}

print("Alustan uudiste otsimist...")

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
        time.sleep(1)
        
    all_articles_by_category[cat_name] = valid_articles

# 2. Arvutame tänase kuupäeva eesti keeles
kuud = ["jaanuar", "veebruar", "märts", "aprill", "mai", "juuni", "juuli", "august", "september", "oktoober", "november", "detsember"]
tana = datetime.datetime.now()
tanane_kuupaev = f"{tana.day}. {kuud[tana.month - 1]} {tana.year}"

# 3. Loome disaini baasi (kasutades sinu "sait.html" disaini)
html = f"""
<!DOCTYPE html>
<html lang="et">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ELYNE - Sinu Isiklik Päevaleht</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&display=swap" rel="stylesheet">
    
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        'elegant-pink': '#F8C8DC',
                        'elegant-blush': '#fdf6f8',
                        'elegant-dark': '#2c2c2c',
                        'elegant-text': '#111111'
                    }},
                    fontFamily: {{
                        'serif': ['"Playfair Display"', 'serif'],
                        'sans': ['Inter', 'sans-serif'],
                    }}
                }}
            }}
        }}
    </script>

    <style>
        body {{
            background-color: #FAFAFA;
            scroll-behavior: smooth;
        }}
        .article-card {{
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .article-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px -15px rgba(0,0,0,0.05);
        }}
        .image-zoom {{
            transition: transform 0.6s ease;
        }}
        .article-card:hover .image-zoom {{
            transform: scale(1.05);
        }}
        .hero-title {{
            font-size: clamp(4rem, 12vw, 12rem);
            line-height: 0.9;
        }}
        .footer-title {{
            font-size: clamp(3rem, 10vw, 10rem);
            line-height: 0.9;
        }}
    </style>
</head>
<body class="font-sans text-elegant-text antialiased selection:bg-elegant-pink selection:text-black">

    <header class="pt-12 pb-8 border-b border-gray-200 bg-elegant-blush relative overflow-hidden">
        <div class="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
            <h1 class="font-serif font-black uppercase hero-title text-elegant-dark tracking-tighter mb-4">
                Elyne
            </h1>
            <div class="flex flex-col md:flex-row items-center justify-center gap-2 md:gap-6 text-sm md:text-lg font-light tracking-[0.2em] text-gray-500 uppercase">
                <span>Päevaleht</span>
                <span class="hidden md:inline-block w-12 h-px bg-elegant-pink"></span>
                <span class="text-elegant-dark font-medium">{tanane_kuupaev}</span>
                <span class="hidden md:inline-block w-12 h-px bg-elegant-pink"></span>
                <span>Globaalne ülevaade</span>
            </div>
        </div>
    </header>

    <!-- Menüüriba (Tumehall) -->
    <div class="bg-elegant-dark text-white sticky top-0 z-50 shadow-md">
        <div class="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
            <nav class="flex overflow-x-auto space-x-8 py-4 text-xs md:text-sm font-medium uppercase tracking-widest no-scrollbar">
"""

# Genereerime menüü lingid
for cat in categories:
    html += f'<a href="#{cat["id"]}" class="hover:text-elegant-pink whitespace-nowrap transition-colors duration-300">{cat["name"]}</a>\n'

html += """
            </nav>
        </div>
    </div>

    <main class="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-24">
"""

print("Tõlgin uudiseid ja määran regiooni...")

# 4. Käime kõik kategooriad läbi
for cat in categories:
    cat_name = cat["name"]
    cat_id = cat["id"]
    articles = all_articles_by_category.get(cat_name, [])
    
    if not articles:
        continue
        
    html += f"""
        <section id="{cat_id}">
            <div class="flex items-center gap-4 mb-10">
                <h2 class="font-serif text-4xl md:text-5xl font-bold uppercase text-elegant-dark">{cat_name}</h2>
                <div class="flex-grow h-px bg-gray-200"></div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
    """
    
    for art in articles:
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

        img_url = art['image'] or 'https://via.placeholder.com/1000x800?text=ELYNE+NEWS'
        
        html += f"""
                <article class="article-card bg-white rounded-2xl overflow-hidden border border-gray-100 flex flex-col group h-full">
                    <div class="relative h-64 overflow-hidden">
                        <img src="{img_url}" alt="Uudise pilt" class="w-full h-full object-cover image-zoom">
                        <div class="absolute top-4 left-4 bg-elegant-pink text-elegant-dark text-xs font-bold uppercase tracking-widest py-1 px-3 rounded-full shadow-md">{est_region}</div>
                    </div>
                    <div class="p-8 flex flex-col flex-grow">
                        <h3 class="font-serif text-2xl font-bold leading-snug mb-4 text-elegant-dark group-hover:text-pink-400 transition-colors">{est_title}</h3>
                        <p class="text-gray-700 leading-relaxed mb-8 flex-grow font-light text-sm">{est_summary}</p>
                        <a href="{art['url']}" target="_blank" class="inline-flex items-center text-xs font-semibold uppercase tracking-widest text-elegant-dark hover:text-pink-500 transition-colors mt-auto">
                            Loe originaali (ENG) 
                            <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                        </a>
                    </div>
                </article>
        """
    html += """
            </div>
        </section>
    """

# 5. Jalus vastavalt uuele disainile
html += """
    </main>

    <footer class="bg-elegant-dark text-white pt-24 pb-12 mt-12 relative overflow-hidden">
        <div class="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
            
            <h2 class="font-serif font-black uppercase footer-title text-elegant-pink opacity-90 tracking-tighter mb-8">
                Elyne <br><span class="text-white opacity-20">Päevaleht</span>
            </h2>
            
            <div class="max-w-xl mx-auto space-y-6">
                <p class="text-gray-400 font-light text-lg">
                    Sinu kureeritud igapäevane ülevaade olulisimatest sündmustest. 
                    <br>Disainitud puhtalt, loetavus fookuses.
                </p>
                
                <div class="w-16 h-px bg-elegant-pink mx-auto my-8 opacity-50"></div>
                
                <div class="flex flex-col md:flex-row justify-center items-center gap-4 text-xs tracking-widest uppercase text-gray-500">
                    <a href="https://www.elyne.ee" class="hover:text-elegant-pink transition-colors">www.elyne.ee</a>
                    <span class="hidden md:inline-block">•</span>
                    <span>&copy; 2026 Kõik õigused kaitstud</span>
                    <span class="hidden md:inline-block">•</span>
                    <span>Automaatselt genereeritud</span>
                </div>
            </div>
        </div>
        <!-- Dekratiivne taustaelement jaluses -->
        <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-elegant-pink rounded-full blur-3xl opacity-10 pointer-events-none"></div>
    </footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Kõik uudised koos uue ELYNE disainiga töödeldud ja salvestatud!")
