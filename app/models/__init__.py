"""Model package — import order matters for SQLAlchemy relationship resolution."""
from app.db.base import Base  # noqa: F401
from app.models.feedback import Feedback  # noqa: F401
from app.models.prediction import Prediction  # noqa: F401
from app.models.risk_factor import RiskFactor  # noqa: F401
from app.models.scam_category import ScamCategory  # noqa: F401
from app.models.scan import Scan  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = [
    "Base",
    "User",
    "Scan",
    "Prediction",
    "RiskFactor",
    "Feedback",
    "ScamCategory",
]
