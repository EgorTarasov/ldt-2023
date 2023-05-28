from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def get_openapi_schema(app: FastAPI):
    schema = get_openapi(
        title="Платформа для програм развития молодых специалистов и стажеров в проектах Правительства Москвы",
        version="dev:0.0.1",
        routes=app.routes,
        openapi_version="3.0.n",
    )
    schema["info"] = {
        "title": "Платформа для програм развития молодых специалистов и стажеров в проектах Правительства Москвы",
        "vesion": "prod:0.0.1",
        "description": "API для **Интерактивная платформа – сообщество для стажеров и участников молодежных карьерных проектов **",
        "license": {
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.txt",
        },
    }
    return schema
