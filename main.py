#!/usr/bin/env python3
# organizer.py (English version)
import os
import shutil
import fitz
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# -----------------------
# CONFIGURATION
# -----------------------
SOURCE_FOLDER = r"PDFsForOrganizer"
DESTINATION_FOLDER = r"OrganizerPdfs"
LOG_FOLDER = "Logs"

IGNORE_KEYWORDS = ["", ""]  # ignore files containing these terms in the filename
PAGE_EXTRACT_LIMIT = 2
MODEL_NAME = "gemini-2.0-flash"

# -----------------------
# COUNTRY NORMALIZATION (English only)
# -----------------------
COUNTRY_NORMALIZATION = {
    # United States
    "usa": "United States",
    "us": "United States",
    "u.s.": "United States",
    "u.s.a": "United States",
    "estados unidos": "United States",
    "america": "United States",
    "united states of america": "United States",

    # United Kingdom
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "england": "United Kingdom",
    "britain": "United Kingdom",
    "great britain": "United Kingdom",

    # Brazil
    "brasil": "Brazil",
    "brazil": "Brazil",

    # Argentina
    "argentina": "Argentina",

    # Chile
    "chile": "Chile",

    # Spain
    "spain": "Spain",
    "espanha": "Spain",

    # China
    "china": "China",

    # South Korea
    "korea": "South Korea",
    "south korea": "South Korea",

    # Japan
    "japan": "Japan",

    # Thailand
    "thailand": "Thailand",

    # India
    "india": "India",

    # Switzerland
    "switzerland": "Switzerland",
    "suisse": "Switzerland",
    "schweiz": "Switzerland",

    # Netherlands
    "nederland": "Netherlands",
    "holland": "Netherlands",
    "netherlands": "Netherlands",

    # UAE
    "uae": "United Arab Emirates",
    "emirates": "United Arab Emirates",
    "dubai": "United Arab Emirates",

    # Others
    "hong kong": "China"
}

def normalize_country(country: str) -> str:
    if not country:
        return ""
    key = country.strip().lower()
    key2 = "".join(ch for ch in key if ch.isalnum() or ch.isspace()).strip()
    return COUNTRY_NORMALIZATION.get(key, COUNTRY_NORMALIZATION.get(key2, country.strip().title()))

def normalize_city(city: str) -> str:
    if not city:
        return ""
    return " ".join(w.capitalize() for w in city.strip().split())

# -----------------------
# LOG SETUP
# -----------------------
os.makedirs(LOG_FOLDER, exist_ok=True)
LOG_GENERAL = os.path.join(LOG_FOLDER, "general.log")
LOG_RAW = os.path.join(LOG_FOLDER, "ia_raw_responses.log")
LOG_JSON = os.path.join(LOG_FOLDER, "ia_json_errors.log")

def log(filepath: str, msg: str):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def log_header(title: str):
    block = f"\n\n=== {title} | {datetime.now()} ===\n"
    log(LOG_GENERAL, block)
    log(LOG_RAW, block)
    log(LOG_JSON, block)

# -----------------------
# GEMINI CLIENT
# -----------------------
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

print("Gemini API successfully initialized.")

# -----------------------
# PDF TEXT EXTRACTION
# -----------------------
def extract_text(pdf_path: str, limit: int = PAGE_EXTRACT_LIMIT) -> str:
    try:
        with fitz.open(pdf_path) as doc:
            result = ""
            for i in range(min(limit, len(doc))):
                result += doc.load_page(i).get_text() + "\n"
            return result
    except Exception as e:
        log(LOG_GENERAL, f"[ERROR] Cannot read PDF '{pdf_path}': {e}")
        return ""

# -----------------------
# GEMINI ANALYSIS
# -----------------------
def analyze_text_with_gemini(text: str, filename: str):
    prompt = f"""
Analyze the travel document '{filename}' and extract all key destinations (cities and countries).

RULES:
1. Identify all travel destinations mentioned in the text.
2. Always list EVERY destination, even if the trip spans multiple countries or cities.
3. Ignore universities (e.g., "University of Missouri").
4. For each destination, specify: city, country, and continent.
5. Allowed continents are: LATAM, NORTHAM, ASIA, EUROPE, AFRICA, OCEANIA, OTHER.
6. Output ONLY a valid JSON list. Example:
   [
     {{"city": "London", "country": "United Kingdom", "continent": "EUROPE"}}
   ]
7. If nothing is found, return [].

TEXT:
---
{text}
---
"""

    log(LOG_GENERAL, f"\n[PDF] {filename}")
    log(LOG_GENERAL, f"[PROMPT]\n{prompt}")

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        raw = response.text.strip()
        log(LOG_RAW, f"\n\n[RAW - {filename}]\n{raw}")

        cleaned = raw.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(cleaned)
        except Exception as e:
            log(LOG_JSON, f"\n[JSON ERROR] {filename}")
            log(LOG_JSON, f"Parse error: {e}")
            log(LOG_JSON, f"Returned:\n{raw}\n")
            return []
    except Exception as e:
        log(LOG_GENERAL, f"[API ERROR] {filename} -> {e}")
        return []

# -----------------------
# MAIN
# -----------------------
def main():
    log_header("START")
    os.makedirs(DESTINATION_FOLDER, exist_ok=True)

    print("\nStarting intelligent organization...\n")
    copied = set()

    for filename in os.listdir(SOURCE_FOLDER):
        if not filename.lower().endswith(".pdf"):
            continue

        print(f"Processing: {filename}")
        src = os.path.join(SOURCE_FOLDER, filename)

        # keyword filter
        if any(k in filename.lower() for k in IGNORE_KEYWORDS):
            print("  -> Ignored (keyword rule).\n")
            log(LOG_GENERAL, f"[IGNORED] {filename}")
            continue

        text = extract_text(src)
        if not text.strip():
            print("  -> No readable text.\n")
            continue

        destinations = analyze_text_with_gemini(text, filename)
        if not destinations:
            print("  -> No destinations detected.\n")
            continue

        print("  -> Detected destinations:")

        for d in destinations:
            city_raw = d.get("city") or d.get("cidade") or ""
            country_raw = d.get("country") or d.get("pais") or ""
            continent_raw = d.get("continent") or d.get("continente") or ""

            print(f"     raw -> city='{city_raw}', country='{country_raw}', continent='{continent_raw}'")

            city = normalize_city(city_raw)
            country = normalize_country(country_raw)
            continent = continent_raw.upper()

            if not (city and country and continent):
                log(LOG_JSON, f"[INCOMPLETE] {filename} -> {d}")
                continue

            final_dir = os.path.join(DESTINATION_FOLDER, continent, country, city)
            os.makedirs(final_dir, exist_ok=True)

            dst = os.path.join(final_dir, filename)
            key = (os.path.abspath(src), os.path.abspath(dst))

            if key in copied:
                print("     -> Already copied (skipping).")
                continue

            try:
                shutil.copy2(src, dst)
                copied.add(key)
                print(f"     -> Copied to: {final_dir}")
            except Exception as e:
                print(f"     -> Copy error: {e}")

        print("")

    log_header("END")
    print("\n--- Done ---")

if __name__ == "__main__":
    main()
