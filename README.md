# 📇 Plex Media Tagger

A powerful and modular dockerized Python tool that leverages Local LLM power (**Ollama**) and external APIs (**Trakt.tv**) to accurately identify and tag specific movie categories in your Plex library. Designed for extensibility, it automates the organization of content like stand-up comedy specials and "sappy" made-for-TV Christmas movies.

---

## ⚙️ How It Works

This tool operates as a long-running service, orchestrating multiple configurable "taggers" to keep your Plex library organized.

1.  **Modular Taggers:** Each tagging task (e.g., identifying stand-up, finding sappy Christmas movies) is defined as a separate configuration within `config.json`.
2.  **Smart Filtering:** For each tagger, the script:
    *   Connects to your configured Plex server and searches a specified movie library using genre filters (if provided in `config.json`).
    *   **Trakt.tv Integration (Configurable):** For specific taggers (e.g., `sappy_christmas`), it fetches an external list of movie identifiers from Trakt.tv (using your API credentials and list slug). Movies matching this list are immediately tagged, bypassing AI analysis for maximum accuracy and efficiency.
    *   **Keyword Pre-filtering (Configurable):** A configurable keyword filter then checks movie titles and summaries. Movies not meeting a specified keyword threshold are immediately rejected, further reducing the load on the AI.
    *   **AI Verification:** Remaining movies are sent to **Ollama (Llama 3)** with a highly specialized prompt to verify if they match the tagger's criteria.
3.  **Automated Tagging:**
    *   **Matched:** Applies a positive label (e.g., `standup`, `sappy_christmas`) in Plex metadata.
    *   **Unmatched:** Applies a negative label (e.g., `verified_not_standup`, `verified_not_sappy_christmas`) to prevent redundant processing in future scans.

## ⏰ Smart Scheduling

The script is designed for "set it and forget it" automation:
-   **Maintenance Awareness:** Upon startup, the script queries your Plex server's `butlerEndHour`.
-   **Conflict Avoidance:** It automatically calculates and schedules its own daily scan for a configurable time (defaulting to one hour after Plex's maintenance ends) to ensure no resource conflicts during Plex's database backups. All configured taggers run sequentially within this single scheduled window.

## 📋 Requirements

*   **Plex Media Server**: Access to your server and a valid [Plex Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
*   **Ollama**: A running instance with the `llama3` model pulled.
*   **Docker**: Recommended for deployment.
*   **Trakt.tv API Credentials**: For enhanced tagging (e.g., `sappy_christmas` tagger), you'll need a Trakt.tv account and API `client_id` (also known as `api_key`). The `client_secret` is also required, though it's less frequently used for public list access.

## 🛠️ Setup

1.  **`.env` File Configuration:**
    Create a `.env` file in the project root with your credentials:

    ```
    PLEX_URL=http://YOUR_PLEX_IP:32400
    PLEX_TOKEN=YOUR_TOKEN
    OLLAMA_URL=http://YOUR_OLLAMA_IP:11434/api/generate
    ```

2.  **`config.json` Configuration:**
    This file defines your taggers and API credentials. It's crucial for the tool's functionality. An example `config.json` is provided in the repository.

    ```json
    {
        "trakt_api": {
            "client_id": "YOUR_TRAKT_CLIENT_ID",
            "client_secret": "YOUR_TRAKT_CLIENT_SECRET",
            "cache_lifetime_hours": 24
        },
        "tagger_configs": {
            "standup": {
                "genres": ["Comedy"],
                "add_label": "standup",
                "reject_label": "verified_not_standup",
                "schedule_offset_hours": 1,
                "prompt": "You are a strict media analyst. Determine if the following title is a Stand-up Comedy Special..."
            },
            "sappy_christmas": {
                "add_label": "sappy_christmas",
                "reject_label": "verified_not_sappy_christmas",
                "schedule_offset_hours": 2,
                "genres": ["Holiday", "Christmas", "Romance", "Comedy", "Family", "Drama"],
                "pre_ai_keywords": ["christmas", "holiday", "winter", "snow", "santa", "mistletoe", "elf", "reindeer", "family", "love", "romance", "town", "miracle", "magic", "eve", "gift", "jingle", "bells", "cookie", "decorate"],
                "pre_ai_keyword_threshold": 2,
                "trakt_list_owner_username": "ad76",
                "trakt_list_slug": "hallmark-christmas",
                "prompt": "You are a media analyst with a knack for spotting \"sappy\" Christmas movies, like those commonly produced by Hallmark..."
            }
        }
    }
    ```
    **Important:** Replace `YOUR_TRAKT_CLIENT_ID` and `YOUR_TRAKT_CLIENT_SECRET` with your actual Trakt API credentials.

## 🚀 Deployment via Docker

1.  **Build the Docker image:**
    ```bash
    docker build -t plex-media-tagger .
    ```
2.  **Run the Docker container:**
    ```bash
    docker run -d --name plex-media-tagger --env-file .env --network host plex-media-tagger
    ```

## 📋 Usage Commands

Once the Docker container is running, it will automatically perform scheduled scans. You can also trigger actions manually:

*   **Perform an immediate orchestrated scan of all taggers:**
    ```bash
    docker exec -it plex-media-tagger python run_taggers.py --scan
    ```
*   **Reset all tags/labels created by this script across your library:**
    ```bash
    docker exec -it plex-media-tagger python run_taggers.py --reset
    ```

## 🧹 Automated Lifecycle & Deletion (Maintainerr)

To keep your library fresh, you can use [Maintainerr](https://github.com/jorenn92/Maintainerr) to automatically curate collections and delete tagged items after a certain period.

### Example Maintainerr Rule for `standup` specials:

1.  **Create the Rule Group:**
    *   **Name**: `Stand-up Specials`
    *   **Description**: `A premium, AI-curated collection of stand-up comedy and roasts. Automatically audited daily using local LLM analysis (Llama 3).`
    *   **Library**: Select your `Movies` library.
    *   **Plex Action**: `Delete` (or `Keep` if you just want the collection)
    *   **Take Action After Days**: `60` (example)
2.  **Configure the Rule Logic:**
    *   **First Value**: `Plex - [list] Labels`
    *   **Action**: `Contains (Partial list match)`
    *   **Custom Value**: `standup`

### Example Maintainerr Rule for `sappy_christmas` movies:

1.  **Create the Rule Group:**
    *   **Name**: `Sappy Christmas Movies`
    *   **Description**: `An AI & Trakt.tv curated collection of made-for-TV sappy Christmas movies. Automatically audited daily.`
    *   **Library**: Select your `Movies` library.
    *   **Plex Action**: `Delete` (to remove them after the holidays)
    *   **Take Action After Days**: `30` (example, to remove them a month after Christmas)
2.  **Configure the Rule Logic:**
    *   **First Value**: `Plex - [list] Labels`
    *   **Action**: `Contains (Partial list match)`
    *   **Custom Value**: `sappy_christmas`

---

### 🧠 Credits

Architected and co-authored by **Gemini**, an AI thought partner from Google, to help automate Plex library management.