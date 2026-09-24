from fastapi import Query

from backend.app.core.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from backend.app.schemas.common import PaginationParams


def get_pagination(
    page: int = Query(DEFAULT_PAGE, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)
