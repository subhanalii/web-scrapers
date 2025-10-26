from youtube_search_scraper import search_videos
from video_scraper import scrape_video_info
from channel_scraper import scrape_channel_info

def get_valid_choice(prompt, options):
    while True:
        choice = input(prompt).strip()
        if choice in options:
            return choice
        print(f"Invalid choice. Choose from {', '.join(options)}.")

def get_valid_number(prompt, default=5):
    while True:
        value = input(prompt).strip()
        if not value:
            return default
        if value.isdigit() and int(value) > 0:
            return int(value)
        print(" Please enter a valid positive number.")

def get_url_list(prompt):
    urls = input(prompt).split(",")
    clean_urls = [u.strip() for u in urls if u.strip()]
    if not clean_urls:
        print(" No valid URLs provided.")
        return []
    return clean_urls

def interactive_cli():
    print("YouTube Scraper Tool")
    print("-" * 35)

    mode_choice = get_valid_choice("Choose mode:\n1. Scrape Videos\n2. Scrape Channels\nEnter choice: ", ["1", "2"])

    if mode_choice == "1":
        print("\n Video scraping selected.")
        input_choice = get_valid_choice("Input method:\n1. Search keyword\n2. Paste video URLs\nEnter choice: ", ["1", "2"])

        if input_choice == "1":
            query = input("🔎 Enter search keyword: ").strip()
            if not query:
                print("❗ Search query cannot be empty.")
                return
            limit = get_valid_number("How many videos to scrape? (default 5): ", default=5)

            try:
                video_urls = search_videos(query, limit)
                if not video_urls:
                    print("No videos found.")
                    return
                for url in video_urls:
                    scrape_video_info(url)
            except Exception as e:
                print(f"Failed to search or scrape videos: {e}")

        elif input_choice == "2":
            urls = get_url_list("Paste video URLs (comma-separated): ")
            for url in urls:
                try:
                    scrape_video_info(url)
                except Exception as e:
                    print(f" Failed to scrape video: {url}\nError: {e}")

    elif mode_choice == "2":
        print("\n Channel scraping selected.")
        urls = get_url_list("Paste channel or video URLs (comma-separated): ")
        for url in urls:
            try:
                scrape_channel_info(url)
            except Exception as e:
                print(f" Failed to scrape channel: {url}\nError: {e}")

    print("\n All tasks completed.\n")

if __name__ == "__main__":
    try:
        interactive_cli()
    except KeyboardInterrupt:
        print("\n❗ Interrupted by user. Exiting gracefully.")
