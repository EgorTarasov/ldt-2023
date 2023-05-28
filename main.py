from app.loader import create_app
from app.utils.settings import settings
import uvicorn

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        use_colors=True,
        host="0.0.0.0",
        port=9999,
        proxy_headers=True,
    )
