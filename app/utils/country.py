from iso3166 import countries


def get_country_code(country_name: str) -> str | None:
    """
    https://www.iso.org/obp/ui/#search
    """
    if countries.get(country_name):
        return countries.get(country_name).alpha2
    raise ValueError(f"Invalid country name: {country_name}")
