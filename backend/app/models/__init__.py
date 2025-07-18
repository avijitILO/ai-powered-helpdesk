from ..database import Base

# Import all models here to ensure they're registered with SQLAlchemy
try:
    from .ticket import Ticket
except ImportError:
    pass

try:
    from .knowledge import KnowledgeArticle
except ImportError:
    pass