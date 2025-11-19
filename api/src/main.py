# main.py
import os
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, HttpUrl

LINKEDIN_BASE_URL = "https://api.linkedin.com/rest/posts"
LINKEDIN_API_VERSION = os.getenv("LINKEDIN_API_VERSION", "202510")  # YYYYMM
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")  # put your token here
PINKCC_HASHTAG = "#PINKCCWeb"

if not LINKEDIN_ACCESS_TOKEN:
    raise RuntimeError("LINKEDIN_ACCESS_TOKEN env var is not set.")

app = FastAPI(title="PINKCC LinkedIn Hashtag API")


# ---------- Models ----------

class RawLinkedInPost(BaseModel):
    id: str
    author: str
    commentary: Optional[str] = None
    createdAt: Optional[int] = None
    publishedAt: Optional[int] = None
    visibility: Optional[str] = None
    # Add more fields if needed (content, media, etc.)


class PINKCCPost(BaseModel):
    post_id: str
    author_urn: str
    commentary: str
    published_at: Optional[int]
    created_at: Optional[int]
    visibility: Optional[str]
    permalink: Optional[HttpUrl] = None


# ---------- Helpers ----------

def _linkedin_headers() -> dict:
    return {
        "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Linkedin-Version": LINKEDIN_API_VERSION,
        "Accept": "application/json",
    }


def _build_permalink(post_id: str) -> Optional[str]:
    """
    Very rough permalink builder.
    For UGC posts: urn:li:ugcPost:123  → https://www.linkedin.com/feed/update/urn:li:ugcPost:123
    For shares:    urn:li:share:456   → https://www.linkedin.com/feed/update/urn:li:share:456
    """
    if not post_id.startswith("urn:li:"):
        return None
    return f"https://www.linkedin.com/feed/update/{post_id}"


async def fetch_posts_for_author(
    client: httpx.AsyncClient,
    author_urn: str,
    count: int = 20,
) -> List[RawLinkedInPost]:
    """
    Call LinkedIn /rest/posts finder for a given author.
    Docs: GET /rest/posts?author={encodedUrn}&q=author&count=...
    """
    params = {
        "author": author_urn,
        "q": "author",
        "count": count,
        "sortBy": "LAST_MODIFIED",
    }
    resp = await client.get(LINKEDIN_BASE_URL, headers=_linkedin_headers(), params=params)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"LinkedIn API error for author {author_urn}: {resp.text}",
        )

    data = resp.json()
    elements = data.get("elements", [])
    return [RawLinkedInPost(**e) for e in elements]


def filter_and_format_pinkcc(posts: List[RawLinkedInPost]) -> List[PINKCCPost]:
    out: List[PINKCCPost] = []
    for p in posts:
        text = (p.commentary or "").strip()
        if PINKCC_HASHTAG.lower() in text.lower():
            permalink = _build_permalink(p.id)
            out.append(
                PINKCCPost(
                    post_id=p.id,
                    author_urn=p.author,
                    commentary=text,
                    created_at=p.createdAt,
                    published_at=p.publishedAt,
                    visibility=p.visibility,
                    permalink=permalink,
                )
            )
    return out


# ---------- API endpoints ----------

@app.get("/api/linkedin/posts", response_model=List[PINKCCPost])
async def get_pinkcc_posts(
    authors: List[str] = Query(
        ...,
        description="List of LinkedIn author URNs (person or organization). "
                    "Example: urn:li:organization:123456, urn:li:person:abcdef",
    ),
    max_posts_per_author: int = Query(20, ge=1, le=100),
):
    """
    Fetch posts from given LinkedIn authors, keep only posts containing #PINKCCWeb,
    and return formatted information.
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        all_raw: List[RawLinkedInPost] = []
        for author in authors:
            author_posts = await fetch_posts_for_author(
                client, author_urn=author, count=max_posts_per_author
            )
            all_raw.extend(author_posts)

    return filter_and_format_pinkcc(all_raw)