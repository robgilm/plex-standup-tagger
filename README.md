# 🎭 Plex Stand-up Tagger

A dockerized Python tool that leverages Local LLM power (**Ollama**) to accurately identify and tag stand-up comedy specials and roasts in your Plex library.

---

## ⚙️ How It Works
Managing stand-up comedy in Plex can be difficult as they are often mixed into general movie libraries. This tool automates that organization:

1. **Library Scan**: The script connects to your configured Plex server and identifies items categorized as "Comedy."
2. **AI Verification**: It sends the title and summary of each item to **Ollama (Llama 3)** to verify if it is truly a stand-up special or roast.
3. **Automated Tagging**: 
   - **Matched**: Applies a `standup` label in Plex metadata.
   - **Unmatched**: Applies a `verified_not_standup` label to prevent redundant processing in future scans.

## ⏰ Smart Scheduling
The script is designed for "set it and forget it" automation:
- **Maintenance Awareness**: Upon startup, the script queries your Plex server's `butlerEndHour` (currently set to **05:00**).
- **Conflict Avoidance**: It automatically calculates and schedules its own daily scan for **06:00** (one hour after maintenance ends) to ensure no resource conflicts during Plex's database backups.

## 📋 Requirements
* **Plex Media Server**: Access to your server and a valid [Plex Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
* **Ollama**: A running instance with the `llama3` model pulled.
* **Docker**: Recommended for deployment via Portainer.

## 🚀 Setup
Create a `.env` file with your credentials:

PLEX_URL=http://YOUR_PLEX_IP:32400
PLEX_TOKEN=YOUR_TOKEN
OLLAMA_URL=http://YOUR_OLLAMA_IP:11434/api/generate



Deploy via Docker:


docker build -t standup-tagger .
docker run -d --name standup-tagger --env-file .env --network host standup-tagger

---
## 🧹 Automated Lifecycle & Deletion (Maintainerr)

To keep your library fresh, use [Maintainerr](https://github.com/jorenn92/Maintainerr) to automatically curate the collection and delete specials 60 days after they are added.

### 1. Create the Rule Group
In Maintainerr, navigate to **Rules** > **New Rule** and use these settings:

* **Name**: `Stand-up Specials`
* **Description**: `A premium, AI-curated collection of stand-up comedy and roasts. Powered by the [Plex Stand-up Tagger](https://github.com/robgilm/plex-standup-tagger) repository, this library is automatically audited daily using local LLM analysis (Llama 3) to ensure only genuine specials are featured.`
* **Library**: Select your `Movies` library.
* **Radarr Server**: Select your active Radarr instance.
* **Plex Action**: `Delete`
* **Take Action After Days**: `60`

### 2. Configure the Rule Logic
Add the following condition to target the AI-generated tags:

* **First Value**: `Plex - [list] Labels`
* **Action**: `Contains (Partial list match)`
* **Custom Value**: `standup`

### 3. Deployment
Once saved, Maintainerr will sync with your Plex server. It will automatically build the collection on your home screen and permanently delete the files from your storage 60 days after they were first tagged by the AI.


### 🧠 Credits

Architected and co-authored by **Gemini**, an AI thought partner from Google, to help automate Plex library management.

