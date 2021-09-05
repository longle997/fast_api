import json
from sqlalchemy.ext.asyncio import AsyncSession
# ??? Path library
from pathlib import Path
from typing import Any, Dict, List, Union, Optional
from datetime import datetime

from blog_api.models import User
from blog_api.users.users_services import hash_password

DATA_ROOT = Path("tests/data")
DATA_FILES = {
    "user": "user.json"
}


def load_data(
    path: str, as_json: bool = True
) -> Union[str, List[Dict[str, Union[str, datetime, Dict[str, str]]]]]:
    if not path.endswith(".json"):
        path += ".json"

    with open(DATA_ROOT / path) as f:
        if as_json:
            data: List[Dict[str, Union[str, datetime, Dict[str, str]]]] = json.load(f)
            return data
        else:
            return f.read()


async def populate_user(session: AsyncSession):
    db_records = []
    records = load_data(DATA_FILES["user"])
    
    for record in records:
        # record.hashed_password = hash_password("password")
        new_user = User(**record, hashed_password=hash_password("password"))
        session.add(new_user)
        db_records.append(new_user)

    await session.commit()
    return db_records
