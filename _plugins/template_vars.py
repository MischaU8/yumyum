from datasette import hookimpl
from bs4 import BeautifulSoup as Soup
import html
import re

non_alphanumeric = re.compile(r"[^a-zA-Z0-9\s]")
multi_spaces = re.compile(r"\s+")
stopwords = set(
    [
        "a",
        "about",
        "an",
        "are",
        "as",
        "at",
        "be",
        "by",
        "com",
        "de",
        "en",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "la",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "was",
        "what",
        "when",
        "where",
        "who",
        "will",
        "with",
        "und",
        "the",
        "www",
    ]
)


def first_paragraph(html):
    soup = Soup(html, "html.parser")
    return str(soup.find("p"))


def highlight(s):
    s = html.escape(s)
    s = s.replace("b4de2a49c8", "<strong>").replace("8c94a2ed4b", "</strong>")
    return s


@hookimpl
def extra_template_vars(request, datasette):
    async def related_videos(video):
        text = video["title"] + " " + video["body"]
        text = non_alphanumeric.sub(" ", text)
        text = multi_spaces.sub(" ", text)
        words = list(set(text.lower().strip().split()) - stopwords)
        sql = """
        select
          video.topic, video.slug, video.title, video.upload_date
        from
          video
          join video_fts on video.rowid = video_fts.rowid
        where
          video_fts match :words
          and not (
            video.slug = :slug
            and video.topic = :topic
          )
        order by
          video_fts.rank
        limit
          5
        """
        result = await datasette.get_database().execute(
            sql,
            {
                "words": " OR ".join(words),
                "slug": video["slug"],
                "topic": video["topic"],
            },
        )
        return result.rows

    async def manual_pages(text):
        text = non_alphanumeric.sub(" ", text)
        text = multi_spaces.sub(" ", text)
        words = list(set(text.lower().strip().split()))
        if not len(words):
            return []
        sql = """
        select
            manual_fts.rank,
            manual.*
        from
            manual
            join manual_fts on manual.rowid = manual_fts.rowid
        where
            manual_fts match :words
        order by
            manual_fts.rank limit 5
        """
        result = await datasette.get_database().execute(
            sql,
            {
                "words": " OR ".join(words),
            },
        )
        return result.rows

    return {
        "q": request.args.get("q", ""),
        "highlight": highlight,
        "first_paragraph": first_paragraph,
        "related_videos": related_videos,
        "manual_pages": manual_pages,
    }


@hookimpl
def prepare_connection(conn):
    conn.create_function("first_paragraph", 1, first_paragraph)
