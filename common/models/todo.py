from dataclasses import dataclass, field
from datetime import datetime

from rococo.models.versioned_model import VersionedModel, default_datetime


@dataclass(kw_only=True)
class Todo(VersionedModel):
    person_id: str = None
    title: str = None
    is_completed: bool = False
    active: bool = True
    changed_on: datetime = field(default_factory=default_datetime)

    def validate_person_id(self):
        if not self.person_id:
            return "person_id is required."

    def validate_title(self):
        if not self.title:
            return "title is required."
