import os
import time
import schedule
from plexapi.server import PlexServer
import requests

baseurl = os.getenv('PLEX_URL')
plex_token = os.getenv('PLEX_TOKEN')
ollama_url = os.getenv('OLLAMA_URL')

def get_plex_maintenance_end():
    try:
        plex = PlexServer(baseurl, plex_token)
        # Pulls the '5:00' stop time directly from your Robflix settings
        end_hour = int(plex.settings.get('butlerEndHour').value)
        start_hour = (end_hour + 1) % 24
        return f"{start_hour:02d}:00"
    except Exception as e:
        print(f"Error reading Plex schedule: {e}. Defaulting to 06:00")
        return "06:00"

def verify(t, s):
    p = f"Title: {t}\nSummary: {s}\n\nIs this a stand-up special or roast? Yes/No."
    try:
        r = requests.post(ollama_url, json={'model': 'llama3', 'prompt': p, 'stream': False}, timeout=30).json()
        return 'yes' in r.get('response', '').lower()
    except:
        return None

def run_tagger():
    print(f"--- Starting Scheduled Scan: {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    try:
        plex = PlexServer(baseurl, plex_token)
        sections = [s for s in plex.library.sections() if s.type == 'movie']
        for section in sections:
            print(f"Scanning Section: {section.title}")
            for m in section.all():
                labels = [l.tag for l in m.labels]
                if "standup" in labels or "verified_not_standup" in labels:
                    continue
                if 'comedy' in [g.tag.lower() for g in m.genres] or 'special' in m.title.lower():
                    print(f"Analyzing: {m.title}...")
                    if verify(m.title, m.summary):
                        m.addLabel('standup')
                        print(f"  [+] TAGGED: {m.title}")
                    else:
                        m.addLabel('verified_not_standup')
        print("--- Scan Complete ---")
    except Exception as e:
        print(f"Scan failed: {e}")

# Initial Setup
auto_time = get_plex_maintenance_end()
print(f"Plex maintenance ends at 05:00. Scheduling daily scan for {auto_time}.")
schedule.every().day.at(auto_time).do(run_tagger)

# Run once immediately on startup
run_tagger()

while True:
    schedule.run_pending()
    time.sleep(60)
