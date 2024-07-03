import os
import anthropic
import requests
import PyRSS2Gen
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser as date_parser

api_key = os.environ["ANTHROPIC_API_KEY"]
client = anthropic.Anthropic(
    api_key=api_key,
)

today = datetime.today()
yesterday = today - timedelta(days=1)
query_date = yesterday.strftime("%Y-%m-%d")

url = f"https://news.ycombinator.com/front?day={query_date}"
response = requests.get(url)
html = response.text

soup = BeautifulSoup(html, "html.parser")

titles = []
for item in soup.find_all("tr", class_="athing"):
    title = item.find("span", class_="titleline").text
    link = item.find("span", class_="titleline").find("a")["href"]
    comment_link = "https://news.ycombinator.com/" + item.find_next_sibling("tr").find("span", class_="subline").find_all("a")[1]["href"]
    titles.append({"title": title, "link": link, "comment_link": comment_link})

system = "Determine which of the following Hacker News titles web developer would likely be interested in reading. Return only the related titles separated by newlines."
content = "\n\n" + "\n".join([item['title'] for item in titles])

message = client.messages.create(
    model="claude-3-5-sonnet-20240620",
    max_tokens=1000,
    temperature=0.0,
    system=system,
    messages=[
        {"role": "user", "content": content }
    ]
)

related_titles = []
for content_block in message.content:
    if content_block.type == 'text':
        related_titles.extend(content_block.text.split("\n"))

rss_items = []
for title in related_titles:
    if title:
        for item in titles:
            if item['title'] == title:
                rss_item = PyRSS2Gen.RSSItem(
                    title=title,
                    link=item['comment_link'],
                    pubDate=datetime.now()
                )
                rss_items.append(rss_item)
                break

try:
    existing_feed = feedparser.parse("gh-pages/rss.xml")
    existing_items = [PyRSS2Gen.RSSItem(
        title=item.title,
        link=item.link,
        pubDate=date_parser.parse(item.published)
    ) for item in existing_feed.entries]
except FileNotFoundError:
    existing_items = []

rss_items.extend(existing_items)

rss = PyRSS2Gen.RSS2(
    title="Hacker News web development related posts RSS",
    link="https://github.com/ktseo41/hn-webdev-news",
    description="Daily Hacker News web development related posts",
    lastBuildDate=datetime.now(),
    items=rss_items
)

with open("rss.xml", "w", encoding="utf-8") as f:
    rss.write_xml(f)
