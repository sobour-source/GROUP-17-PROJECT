# Book Discovery & Reading Companion

A Streamlit app that lets you search for books, generate AI-powered reading
guides (summary, reading level, discussion questions), and manage a personal
reading list.

## Features
- Search Open Library by title, author, or ISBN
- View cover, authors, publish year, page count, subjects
- Generate a plain-language summary, reading level, and discussion questions via the Gemini API
- Track books as **Want to Read**, **Reading**, or **Finished**
- Get similar-book suggestions based on shared subjects/authors
- Reading list and guides are saved locally to `reading_list.json`

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your Gemini API key as an environment variable:

   **macOS/Linux:**
   ```
   export GEMINI_API_KEY="your-key-here"
   ```
   **Windows (PowerShell):**
   ```
   $env:GEMINI_API_KEY="your-key-here"
   ```

3. Run the app:
   ```
   streamlit run app.py
   ```

## Project structure
- `book.py` — `Book` class (data model, regex validation/cleaning)
- `api_client.py` — `OpenLibraryClient` (all Open Library API calls)
- `reading_list_manager.py` — `ReadingListManager` (reading list + JSON file handling)
- `reading_guide_generator.py` — `ReadingGuideGenerator` (Gemini API calls)
- `exceptions.py` — custom exception classes
- `app.py` — Streamlit UI
