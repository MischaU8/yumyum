from datasette import hookimpl
from bs4 import BeautifulSoup as Soup
import html
import re

non_alphanumeric = re.compile(r"[^a-zA-Z0-9\s]")
multi_spaces = re.compile(r"\s+")


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
        words = list(set(text.lower().strip().split()))
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
            {"words": " OR ".join(words), "slug": video["slug"], "topic": video["topic"]},
        )
        return result.rows

    return {
        "q": request.args.get("q", ""),
        "highlight": highlight,
        "first_paragraph": first_paragraph,
        "related_videos": related_videos,
    }


@hookimpl
def prepare_connection(conn):
    conn.create_function("first_paragraph", 1, first_paragraph)
