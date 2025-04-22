import requests
from lxml import etree
from datetime import datetime
import time
from embeddings import store_pieces
from db import get_article


def replace_slovenian_months(date_str):
    months = {
        "januar": "January",
        "februar": "February",
        "marec": "March",
        "april": "April",
        "maj": "May",
        "junij": "June",
        "julij": "July",
        "avgust": "August",
        "september": "September",
        "oktober": "October",
        "november": "November",
        "december": "December",
    }
    for slovenian, english in months.items():
        date_str = date_str.replace(slovenian, english)
    return date_str


def get_preview_data(article):
    h3 = article.xpath(".//h3")
    if h3:
        h3 = h3[0]

    link = h3.xpath("./span[@class='news-cat']/a")
    if link:
        link = link[0]
    subcategory = link.text.strip() if link.text else "No subcategory found"
    title = h3.xpath("./a")
    url = title[0].get("href") if title else "No URL found"
    title_text = title[0].text.strip() if title else "No title text found"
    date = article.xpath("./p[contains(@class, 'media-meta')]/text()")

    date_text = date[0].strip() if date else None
    return title_text, subcategory, date_text, url


def get_article_data(article_content):
    root = etree.HTML(article_content)

    section = root.xpath('//div[contains(@class, "section-heading")]/h1/a/text()')
    section_text = section[0].strip() if section else "No section found"
    # print("Section:", section_text)

    meta_container = root.xpath('//div[@class="article-meta"]')
    author_name = "No author found"
    formatted_date = None
    if meta_container and len(meta_container) > 0:
        author_divs = meta_container[0].xpath(".//div[@class='author-name']")
        if author_divs:
            div = author_divs[0]
            # see if there’s an <a> inside
            a_tags = div.xpath(".//a")
            if a_tags:
                # first <a> takes precedence
                author_name = a_tags[0].text.strip()
            else:
                # fallback to whatever text is directly in the div
                author_name = div.text.strip()
        detailed_date = meta_container[0].xpath('./div[@class="publish-meta"]/text()')
        if detailed_date:
            detailed_date = detailed_date[0].strip()
            date, time = detailed_date.split(" ob ")
            date = replace_slovenian_months(date)
            # print("Date:", date.strip())
            # print("Time:", time.strip())
            formatted_date = datetime.strptime(f"{date} {time}", "%d. %B %Y %H.%M")
        else:
            detailed_date = None
    header = root.xpath('//header[@class="article-header"]')
    subtitle = header[0].xpath('./div[@class="subtitle"]')
    recap = header[0].xpath('./p[@class="lead"]')
    recap_text = "No recap found"
    if recap:
        if recap[0].text:
            recap_text = recap[0].text.strip()
    subtitle_text = "No subtitle found"
    if subtitle:
        if subtitle[0].text:
            subtitle_text = subtitle[0].text.strip()
    # print("Recap:", recap[0].text.strip() if recap else "No recap found")

    body = root.xpath('//div[@class="article-body"]')
    article = body[0].xpath('./article[@class="article"]')
    pieces = []
    # select all direct children (elements only)
    for elem in article[0].xpath("./*"):
        tag = elem.tag.lower()

        if tag == "p":
            # grab all text nodes, join and strip
            text = "".join(elem.xpath(".//text()")).strip()
            pieces.append({"type": "paragraph", "text": text})

        elif tag == "figure":
            cls = elem.get("class", "")
            data_type = elem.get("data-type", "")

            # IMAGE FIGURE
            if "image" in cls.split():
                # find <figcaption> anywhere inside
                cap_nodes = elem.xpath(".//figcaption//text()")
                caption = (
                    "".join(cap_nodes).strip() if cap_nodes else "No caption found"
                )
                pieces.append({"type": "image", "caption": caption})

            # RTV-TABLE FIGURE
            elif data_type == "rtv-table":
                tbl = elem.xpath(".//table")
                if tbl:
                    rows = []
                    for tr in tbl[0].xpath(".//tr"):
                        row_cells = []
                        for cell in tr.xpath("./th|./td"):
                            # collect _all_ descendant text nodes
                            texts = [
                                t.strip() for t in cell.xpath(".//text()") if t.strip()
                            ]
                            cell_text = " ".join(texts)
                            row_cells.append(cell_text)
                        rows.append(row_cells)
                    pieces.append({"type": "table", "content": rows})
                else:
                    pieces.append({"type": "table", "content": []})

        else:
            # you can handle other tags here if needed
            continue
    return pieces, subtitle_text, recap_text, section_text, author_name, formatted_date


def search_news(query, s=None, sort=1, a=1, d=-1, w=-1, per_page=100, group=1):
    search_url = f"https://www.rtvslo.si/iskalnik"
    # from-to in format YYYY-MM-DD
    params = {
        "q": query,
        "s": s,  # 3 for sport, null for all
        "sort": sort,  # (1=newest, 2=popular)
        "a": a,  # Časovno obdobje (1=all, 2=last 24h, 3=last week, 4=last month, 5=last year)
        "d": d,  #
        "w": w,  #
        "per_page": per_page,  # number of results per page
        "group": group,  # (1=novice, 15=video, 16=audio)
    }
    response = requests.get(
        search_url, params=params, headers={"User-Agent": "onj-fri"}
    )
    print(f"Response URL: {response.url}")
    response.raise_for_status()  # blows up on HTTP errors

    # 2. Parse the HTML
    root = etree.HTML(response.content)

    # 3. Find all <div> tags with that class
    #    pass class_name as a string or list of strings
    articles = root.xpath('//div[@class="md-news"]')
    fetched_articles = []
    for article in articles:
        start_time = time.time()
        fetched_article = {}
        title, subcategory, date_text, url = get_preview_data(article)
        if "radio-si" in url or "capodistria" in url:
            print("Skipping article", url)
            continue
        existing_article = get_article(url)
        if existing_article:
            print(f"Article already exists in the database: {url}")
            continue
        fetched_article["title"] = title
        fetched_article["subcategory"] = subcategory
        fetched_article["date"] = date_text
        # print(f"Title: {title}")
        # print(f"Subcategory: {subcategory}")
        # print(f"Date: {date_text}")
        # print(f"URL: {url}")
        # print("-" * 40)
        time.sleep(1)  # be nice to the server
        article_response = requests.get(url, headers={"User-Agent": "onj-fri"})
        article_response.raise_for_status()
        pieces, subtitle, recap, section, author, date = get_article_data(
            article_response.content
        )
        fetched_article["pieces"] = pieces
        fetched_article["subtitle"] = subtitle
        fetched_article["recap"] = recap
        fetched_article["section"] = section
        fetched_article["author"] = author
        fetched_article["date"] = date
        meta = {
            "title": title,
            "subtitle": subtitle,
            "recap": recap,
            "published_at": date,
            "section": section,
            "author": author,
            "url": url,
            "subcategory": subcategory,
        }
        store_pieces(meta, pieces)
        # print("Subtitle:", subtitle)
        # print("Recap:", recap)
        # print("Content:")
        # for piece in pieces:
        #     if piece["type"] == "paragraph":
        #         print(piece["text"])
        #     elif piece["type"] == "image":
        #         print("Image caption:", piece["caption"])
        #     elif piece["type"] == "table":
        #         for row in piece["content"]:
        #             print("\t".join(row))
        #     else:
        #         print("Unknown content type:", piece["type"])
        # print("=" * 40)
        fetched_articles.append(fetched_article)
        end_time = time.time()
        # Minus 1 second for the sleep time
        elapsed_time = end_time - start_time
        print(f"Time taken to fetch article {title}: {elapsed_time:.2f} seconds.")
    return fetched_articles


def compare_query_results(query_1, query_2):
    articles_1 = search_news(query_1, per_page=10)
    articles_2 = search_news(query_2, per_page=10)

    # Compare the two lists of articles
    if len(articles_1) != len(articles_2):
        print(f"Number of articles for '{query_1}' and '{query_2}' are different.")
        return False

    for article_1, article_2 in zip(articles_1, articles_2):
        if article_1["title"] != article_2["title"]:
            print(
                f"Article titles do not match: '{article_1['title']}' vs '{article_2['title']}'"
            )
            return False

    print("All articles match.")
    return True
