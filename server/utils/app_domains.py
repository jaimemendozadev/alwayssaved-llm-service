import os

from server.utils.aws.ssm import get_secret

PYTHON_MODE = os.getenv("PYTHON_MODE", "DEVELOPMENT")


def get_app_domains() -> list[str]:
    app_domain_raw = (
        get_secret("/alwayssaved/FASTAPI_PRODUCTION_APP_DOMAINS")
        if PYTHON_MODE == "PRODUCTION"
        else os.getenv("FASTAPI_DEVELOPMENT_APP_DOMAIN", "http://localhost:3000")
    )

    return (
        [domain.strip() for domain in app_domain_raw.split(",") if domain.strip()]
        if app_domain_raw
        else []
    )


APP_DOMAINS = get_app_domains()
