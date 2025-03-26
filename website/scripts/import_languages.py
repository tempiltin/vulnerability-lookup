#! /usr/bin/python
import json
from pathlib import Path

from website.web.bootstrap import db
from website.models import get_or_create
from website.models import Language


def import_languages(file_path: str) -> None:
    """Imports a list of programming languages from a JSON file."""
    with open(Path(file_path)) as json_file:
        languages = json.loads(json_file.read())
        for language in languages:
            get_or_create(db.session, Language, **language)
