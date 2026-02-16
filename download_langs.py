import os
import urllib.request
from tqdm import tqdm

# Папка с языками
TESSDATA_DIR = r"C:\Program Files\Tesseract-OCR\tessdata"
BASE_URL = "https://github.com/tesseract-ocr/tessdata/raw/main/"

# Языки для скачивания
LANGUAGES = {
    # Основные
    'eng': 'English',
    'rus': 'Russian',
    'chi_sim': 'Chinese Simplified',
    'chi_tra': 'Chinese Traditional',
    
    # Европа (ЕС)
    'deu': 'German',
    'fra': 'French',
    'spa': 'Spanish',
    'ita': 'Italian',
    'por': 'Portuguese',
    'pol': 'Polish',
    'nld': 'Dutch',
    'swe': 'Swedish',
    'dan': 'Danish',
    'fin': 'Finnish',
    'nor': 'Norwegian',
    'ces': 'Czech',
    'hun': 'Hungarian',
    'ron': 'Romanian',
    'bul': 'Bulgarian',
    'hrv': 'Croatian',
    'slk': 'Slovak',
    'slv': 'Slovenian',
    'ell': 'Greek',
    'lav': 'Latvian',
    'lit': 'Lithuanian',
    'est': 'Estonian',
    
    # СНГ
    'ukr': 'Ukrainian',
    'bel': 'Belarusian',
    'kaz': 'Kazakh',
    'uzb': 'Uzbek',
    'aze': 'Azerbaijani',
    'arm': 'Armenian',
    'geo': 'Georgian',
    'tgk': 'Tajik',
    'kir': 'Kyrgyz',
    'mon': 'Mongolian',
    
    # Другие важные
    'jpn': 'Japanese',
    'kor': 'Korean',
    'ara': 'Arabic',
    'heb': 'Hebrew',
    'hin': 'Hindi',
    'tha': 'Thai',
    'vie': 'Vietnamese',
    'tur': 'Turkish',
    'ind': 'Indonesian',
    'msa': 'Malay',
}

print("🌍 Downloading Tesseract language packs...\n")

os.makedirs(TESSDATA_DIR, exist_ok=True)

for lang_code, lang_name in LANGUAGES.items():
    filename = f"{lang_code}.traineddata"
    filepath = os.path.join(TESSDATA_DIR, filename)
    url = BASE_URL + filename
    
    if os.path.exists(filepath):
        print(f"✅ {lang_name} ({lang_code}) - already installed")
        continue
    
    try:
        print(f"⬇️  Downloading {lang_name} ({lang_code})...", end=" ")
        
        def download_with_progress(url, filepath):
            with urllib.request.urlopen(url) as response:
                total_size = int(response.getheader('Content-Length'))
                block_size = 8192
                downloaded = 0
                
                with open(filepath, 'wb') as f:
                    for data in iter(lambda: response.read(block_size), b''):
                        downloaded += len(data)
                        f.write(data)
                        
                        done = int(50 * downloaded / total_size)
                        print(f"\r   [{'=' * done}{' ' * (50-done)}] {downloaded/1024/1024:.1f}MB", end="")
        
        download_with_progress(url, filepath)
        print(" ✅")
        
    except Exception as e:
        print(f" ❌ Error: {e}")

print("\n🎉 Done!")
print(f"📁 Languages installed in: {TESSDATA_DIR}")