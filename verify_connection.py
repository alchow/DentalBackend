import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings

# Force env vars to check what's actually loaded
print(f"DEBUG: settings.SQLALCHEMY_DATABASE_URI: {settings.SQLALCHEMY_DATABASE_URI}", file=sys.stderr)
print(f"DEBUG: DB_USER={os.getenv('DB_USER')}", file=sys.stderr)
print(f"DEBUG: DB_HOST={os.getenv('DB_HOST')}", file=sys.stderr)

async def check():
    engine = create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),
        echo=False,
    )
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("SUCCESS! Connected to Database.")
    except Exception as e:
        print(f"FAILURE: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    current_path = os.getcwd()
    sys.path.append(os.path.join(current_path, "backend"))
    asyncio.run(check())
