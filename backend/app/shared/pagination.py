from dataclasses import dataclass

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Query, Session


@dataclass(frozen=True)
class Pagination:
    page: int
    page_size: int
    total: int

    @property
    def pages(self) -> int:
        if self.total == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size

    def as_meta(self) -> dict[str, int]:
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
            "pages": self.pages,
        }


@dataclass(frozen=True)
class PageResult:
    items: list
    pagination: Pagination


def paginate_query(query: Query, page: int, page_size: int) -> PageResult:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return PageResult(items=items, pagination=Pagination(page, page_size, total))


def count_select(db: Session, statement: Select) -> int:
    return db.execute(select(func.count()).select_from(statement.subquery())).scalar_one()
