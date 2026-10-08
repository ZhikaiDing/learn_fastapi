import sys
from pathlib import Path
# 把项目根目录加入sys.path
sys.path.append(str(Path(__file__).parent.parent))

from db.session import engine, get_db
from db.models import Base
from core.settings import settings

if settings.ENVIRONMENT == "dev":
    Base.metadata.create_all(bind=engine)
    print(settings.ENVIRONMENT)

    db = get_db()
    print(db)
