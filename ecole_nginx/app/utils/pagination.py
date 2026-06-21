import math
from sqlalchemy.orm import Query

def paginate(query: Query, page: int, per_page: int):
    total = query.count()
    last_page = math.ceil(total / per_page) if per_page else 1

    items = (
        query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return items, {
        "current_page": page,
        "last_page": last_page,
        "per_page": per_page,
        "total": total
    }
