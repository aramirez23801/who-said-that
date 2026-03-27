import os
import re
import time
import urllib.request

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.person import Person
from backend.models.quote import Quote
from backend.seed_data import PERSONS, QUOTES

_IMAGES_DIR = "static/images"
_BASE_URL = "http://localhost:8000/static/images"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _download_image(name: str, url: str) -> str:
    """Download image to static/images/, return local URL. Falls back to original on error."""
    ext = url.split("?")[0].rsplit(".", 1)[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "webp"):
        ext = "jpg"
    filename = f"{_slug(name)}.{ext}"
    dest = os.path.join(_IMAGES_DIR, filename)

    if os.path.exists(dest):
        return f"{_BASE_URL}/{filename}"

    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                with open(dest, "wb") as f:
                    f.write(resp.read())
            print(f"[seed] Downloaded image: {filename}")
            time.sleep(1.5)
            return f"{_BASE_URL}/{filename}"
        except Exception as e:
            wait = 5 * (attempt + 1)
            if attempt < 4:
                print(f"[seed] Retry {attempt + 1}/5 for {name} (waiting {wait}s): {e}")
                time.sleep(wait)
            else:
                print(f"[seed] WARNING: Failed all retries for {name}: {e}")
    return url  # fall back to original URL only after all retries exhausted


async def seed_database(db: AsyncSession) -> None:
    result = await db.execute(select(Person).limit(1))
    if result.scalar_one_or_none() is not None:
        return  # already seeded

    os.makedirs(_IMAGES_DIR, exist_ok=True)

    # Insert persons and build name -> id map
    name_to_id: dict[str, int] = {}
    for data in PERSONS:
        local_url = _download_image(data["name"], data["image_url"])
        person = Person(
            name=data["name"],
            image_url=local_url,
            short_bio=data["short_bio"],
        )
        db.add(person)
        await db.flush()  # populate person.id before using it
        name_to_id[person.name] = person.id

    # Insert quotes, resolving person_name -> person_id
    for data in QUOTES:
        person_id = name_to_id.get(data["person_name"])
        if person_id is None:
            raise ValueError(f"Seed error: person '{data['person_name']}' not found in PERSONS list")
        db.add(Quote(text=data["text"], person_id=person_id))

    await db.commit()
    print(f"[seed] Inserted {len(PERSONS)} persons and {len(QUOTES)} quotes.")
