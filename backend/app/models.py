"""Import every model so SQLAlchemy metadata (and Alembic) see all tables."""
from app.agents.store.models import AgentRun, AgentStep  # noqa: F401
from app.modules.audit.models import AuditLog, Event, StatusEvent  # noqa: F401
from app.modules.complaints.models import Attachment, Feedback, ServiceRequest, SrReporter  # noqa: F401
from app.modules.followup.models import Escalation, Referral  # noqa: F401
from app.modules.geo.models import (  # noqa: F401
    Asset, AssetEvent, Department, KnownRoadFeature, PlannedWork, RoadSegment, SensitivePlace,
    SlaPolicy, Ward,
)
from app.modules.incidents.models import Incident, WeatherAlert  # noqa: F401
from app.modules.ingestion.models import (  # noqa: F401
    DataSource, HazardCluster, IngestRequest, RawDetection, RejectedDetection, ReviewItem,
)
from app.modules.notifications.models import Notification  # noqa: F401
from app.modules.users.models import Captcha, User, Visit  # noqa: F401
from app.modules.work.models import (  # noqa: F401
    Crew, InventoryItem, MaterialRequest, ReassignmentProposal, WorkOrder,
)
from app.db import Base  # noqa: E402

metadata = Base.metadata
