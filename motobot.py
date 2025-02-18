import yaml
import time
import logging
from datetime import datetime

# Updated import: use the Client class instead of AtProtocol
from atproto import Client, models


def load_config(config_file: str) -> dict:
    """
    Loads YAML configuration from a file and returns the 'bot_config' dictionary.
    """
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config["bot_config"]


def scrape_motogp_news(url: str) -> list:
    """
    Placeholder function to scrape or retrieve MotoGP news from an article or RSS feed.
    Return a list of short strings summarizing each news item or key opinion.
    """
    # In a real-world scenario, you might:
    #   1. Parse an RSS feed (using feedparser)
    #   2. Scrape a website (using requests + BeautifulSoup)
    #   3. Use an external API to fetch articles
    #
    # Below is just a hard-coded mock demonstration:
    mock_news = [
        "Ducati’s new engine update impresses during testing.",
        "Yamaha remains hopeful despite inconsistent preseason results."
    ]
    return mock_news


def gather_bluesky_conversations(query: str) -> list:
    """
    Placeholder function to gather recent posts from Bluesky containing #MotoGP or other keywords.
    This could be done by performing a search or an unofficial approach (if/when the API allows).
    """
    # For demonstration purposes, we're returning mock data.
    mock_conversations = [
        "Impressed with Marc Márquez’s pace during practice! #MotoGP",
        "Surprised to see Aprilia pushing so hard this season. #MotoGP"
    ]
    return mock_conversations


def gather_other_social_media(platform: str) -> list:
    """
    Placeholder function to fetch mentions or opinions from another social media platform.
    """
    # In practice, you'd use that platform's API or scraping tools.
    mock_social_media_posts = [
        "Rumors say KTM might have a secret aerodynamics package in the works.",
        "Honda’s track data suggests they might switch to a new chassis setup soon."
    ]
    return mock_social_media_posts


def gather_opinions_from_sources(content_sources: list) -> list:
    """
    Gathers opinions from all configured sources (RSS, Bluesky, other social media).
    Returns a combined list of short strings representing the opinions/highlights.
    """
    all_opinions = []

    for source in content_sources:
        name = source.get("name")
        if name == "rss_feed":
            url = source.get("url", "")
            all_opinions.extend(scrape_motogp_news(url))
        elif name == "bluesky_search":
            query = source.get("query", "#MotoGP")
            all_opinions.extend(gather_bluesky_conversations(query))
        elif name == "social_media":
            platform = source.get("platform", "Twitter")
            all_opinions.extend(gather_other_social_media(platform))
        else:
            # Unrecognized source type
            pass

    return all_opinions


def format_opinions_for_posting(opinions: list, hashtags: list, max_length: int) -> list:
    """
    Format each opinion by appending the default hashtags 
    and ensuring each post is within the max_length limit.
    """
    formatted_posts = []
    tag_string = " ".join(hashtags).strip()

    for opinion in opinions:
        # Combine text + hashtags
        if tag_string:
            post_text = f"{opinion} {tag_string}"
        else:
            post_text = opinion

        # Truncate if it exceeds max_length
        if len(post_text) > max_length:
            post_text = post_text[:max_length - 3] + "..."

        formatted_posts.append(post_text)

    return formatted_posts


def main():
    logging.basicConfig(level=logging.INFO)

    # 1. Load config
    config = load_config("bot_config.yaml")
    handle = config["bluesky_credentials"]["handle"]
    password = config["bluesky_credentials"]["password"]

    # 2. Initialize the Bluesky Client (formerly AtProtocol)
    client = Client()  # Defaults to bsky.social, or specify host if needed.

    # 3. Log in using your handle (or another identifier) and password
    logging.info(f"Logging in as {handle}")
    session = client.login(handle=handle, password=password)

    if not session:
        logging.error("Failed to authenticate to Bluesky. Aborting.")
        return

    # 4. Gather opinions from configured sources
    raw_opinions = gather_opinions_from_sources(config["content_sources"])

    # 5. Format them for posting
    posts_to_publish = format_opinions_for_posting(
        opinions=raw_opinions,
        hashtags=config["hashtags"],
        max_length=config["max_post_length"]
    )

    # 6. Publish each post on Bluesky
    for post_text in posts_to_publish:
        record_data = {
            "text": post_text,
            "createdAt": datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        }

        try:
            client.com.atproto.repo.createRecord(
                repo=handle,                    # Your handle
                collection="app.bsky.feed.post",
                record=record_data
            )
            logging.info(f"Posted: {post_text}")
        except Exception as e:
            logging.error(f"Error posting to Bluesky: {e}")

        # Simple rate-limiting: sleep between posts
        time.sleep(2)

    if config.get("debug_mode"):
        logging.info("Finished posting all MotoGP opinions.")


if __name__ == "__main__":
    main()
