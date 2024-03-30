import feedparser
from datetime import datetime

feed = feedparser.parse("rss.xml")

html_output = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{feed.feed.title}</title>
  <meta name="description" content="{feed.feed.description}">
</head>
<body>
  <h1>{feed.feed.title}</h1>
  <p>{feed.feed.description}</p>
  <p>RSS Link: <a href="https://ktseo41.github.io/hn-webdev-news/rss.xml">https://ktseo41.github.io/hn-webdev-news/rss.xml</a></p>
  <h2>Recent Posts</h2>
  <ul>
'''

for entry in feed.entries:
    updated_time = datetime.strptime(entry.updated, "%a, %d %b %Y %H:%M:%S %Z")
    iso_time = updated_time.isoformat()
    html_output += f'    <li>\n      <a href="{entry.link}">{entry.title}</a>\n      <p>updated: <time datetime="{iso_time}">{entry.updated}</time></p>\n    </li>\n'

html_output += '''  </ul>
</body>'''

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_output)
