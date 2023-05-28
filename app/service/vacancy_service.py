from sqlalchemy.orm import Session

from app.data import crud, schemas, models


def get_all_filters(db: Session) -> schemas.VacancyFiltersAvailable:
    # get all tags

    # get schemas from tags
    db_tags = crud.get_all_tags(db)
    tags = []
    if db_tags:
        tags = [tag[0] for tag in db_tags]
    # get all cities from vacancies
    cities = crud.get_all_cities(db)

    # # get all organisations from vacancies
    organisations = crud.get_all_organisations(db)

    return schemas.VacancyFiltersAvailable(
        tags=tags,
        city=cities,
        organisations=organisations,
    )
