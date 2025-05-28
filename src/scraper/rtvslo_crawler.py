import requests
from lxml import etree
from datetime import datetime
from db.db import get_article
import traceback

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
    try:
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
    except Exception as e:
        return "No title text found", "No subcategory found", None, "No URL found"


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
            try:
                if " ob " in detailed_date:
                    date, time = detailed_date.split(" ob ")
                    date = replace_slovenian_months(date)
                elif " - " in detailed_date:
                    date, time = detailed_date.split(" - ")
                    date = replace_slovenian_months(date)
                else:
                    date = replace_slovenian_months(detailed_date)
                    time = "00.00"  # default time if not present
                # print("Date:", date.strip())
                # print("Time:", time.strip())
                formatted_date = datetime.strptime(f"{date} {time}", "%d. %B %Y %H.%M")
            except Exception as e:
                formatted_date = None
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


def scrape_news(query, s=None, sort=1, a=1, d=-1, w=-1, per_page=10, group=1):
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

    return response


def parse_response(response):
    try:
        # 2. Parse the HTML
        root = etree.HTML(response.content)

        # 3. Find all <div> tags with that class
        #    pass class_name as a string or list of strings
        articles = root.xpath('//div[@class="md-news"]')
        fetched_articles = []
        for article in articles:
            try:
                fetched_article = {}
                title, subcategory, date_text, url = get_preview_data(article)
                existing_article = get_article(url)
                if existing_article:
                    fetched_articles.append(existing_article)
                    continue
                if "radio-si" in url or "capodistria" in url:
                    print("Skipping article", url)
                    continue
                fetched_article["title"] = title
                fetched_article["subcategory"] = subcategory
                fetched_article["date"] = date_text
                # time.sleep(1)  # be nice to the server
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
                fetched_article["url"] = url
                fetched_article["subcategory"] = subcategory
                fetched_articles.append(fetched_article)
            except Exception as e:
                print(f"Error processing article: {e}")
                traceback.print_exc()
                continue
        return fetched_articles
    except Exception as e:
        print(f"Error parsing response: {e}")
        return []
