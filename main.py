from app.loader import create_app
from app.utils.settings import settings
import uvicorn

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host=settings.DOMAIN, port=8000, reload=True, use_colors=True
    )
