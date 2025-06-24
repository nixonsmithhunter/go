"""Scrape recent posts mentioning '4c' from a subreddit.

This script searches the specified subreddit for posts containing
`QUERY` and stores the submissions and all their comments in a JSON
file. Credentials are read from environment variables so the script can
be scheduled to run in cron, GitHub Actions, or other environments.
"""

import os
import json
import time
from pathlib import Path

import praw

# Read Reddit credentials from environment variables
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USER_AGENT = os.getenv("USER_AGENT", "4c-labs-scraper/1.0")

# Constants for the search
SUBREDDIT_NAME = "ukmedicalcannabis"
QUERY = "4c"
OUTPUT_DIR = Path("./data/4c_mentions")


def fetch_4c_posts():
    """Return a list of submissions matching QUERY from SUBREDDIT_NAME."""
    # Initialize the Reddit client using the provided credentials
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=USER_AGENT,
    )

    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    results = []
    # Search subreddit posts from the last week mentioning the query
    for submission in subreddit.search(QUERY, sort="new", time_filter="week", limit=None):
        # Load all comments associated with the submission
        submission.comments.replace_more(limit=None)
        record = {
            "id": submission.id,
            "title": submission.title,
            "selftext": submission.selftext,
            "created_utc": submission.created_utc,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "comments": [c.body for c in submission.comments.list()],
        }
        results.append(record)

    return results


def save_results(data):
    """Save fetched posts to OUTPUT_DIR as a JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = time.strftime("%Y%m%d")
    filename = OUTPUT_DIR / f"4c_posts_{today}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    posts = fetch_4c_posts()
    save_results(posts)
