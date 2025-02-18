import feedparser
import json
from transformers import pipeline

def store_articles_as_json(articles, filename="articles.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(articles)} articles to {filename}")

def fetch_motogp_news(feed_url="https://www.motorsport.com/rss/motogp/news/"):
    """
    Fetch MotoGP articles and summaries from the given RSS feed URL.
    
    :param feed_url: The RSS feed URL for MotoGP news (default points to motorsport.com's feed).
    :return: A list of dictionaries, each with 'title' and 'summary' keys.
    """
    feed = feedparser.parse(feed_url)
    articles = []
    
    for entry in feed.entries:
        title = entry.get('title', 'No Title')
        summary = entry.get('summary', 'No Summary')
        
        articles.append({
            'title': title,
            'summary': summary
        })
    
    return articles

def interpret_articles(articles):
    """
    Takes a list of dicts with 'title' and 'summary',
    and returns short interpretation strings for each article.
    """
    # Example: Summarization pipeline (free model)
    summarizer = pipeline(
        "summarization",
        model="google/flan-t5-base",  # Or pick another summarization model
    )

    interpreted_texts = []

    for article in articles:
        # Combine title and summary for input
        combined_text = f"{article['title']}. {article['summary']}"

        # Run the summarization
        # Adjust max_length, min_length, etc. as needed
        result = summarizer(
            combined_text,
            max_length=60,
            min_length=20,
            do_sample=False
        )

        # Extract the summarized text
        short_interpretation = result[0]["summary_text"]
        interpreted_texts.append(short_interpretation)

    return interpreted_texts

if __name__ == "__main__":
    # Fetch articles from the RSS feed
    motogp_articles = fetch_motogp_news()

    # (Optional) Store the raw articles in a JSON file
    store_articles_as_json(motogp_articles, filename="articles.json")

    # Interpret or summarize each article using the new function
    interpreted = interpret_articles(motogp_articles)

    # Print or store the interpreted text
    print("\n--- Interpreted (Summarized) Articles ---")
    output_filename = "interpreted_summaries.txt"

    with open(output_filename, 'w', encoding='utf-8') as f:
        for i, text in enumerate(interpreted, start=1):
            # Print to console
            print(f"{i}. {text}")

            # Write to file
            f.write(f"{i}. {text}\n")

    print(f"\nAll interpreted summaries have also been written to '{output_filename}'.")

