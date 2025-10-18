
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Document:
    id: str
    title: str
    date_published: Optional[str]
    url: str
    category: Optional[str]
    summary: Optional[str]
    file_links: List[str]
    hash: Optional[str] = None
