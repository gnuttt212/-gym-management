"""Import all models so that Flask-Migrate can detect them."""

from .user import User  # noqa: F401
from .member import Member  # noqa: F401
from .trainer import Trainer  # noqa: F401
from .membership_plan import MembershipPlan  # noqa: F401
from .subscription import Subscription  # noqa: F401
from .invoice import Invoice  # noqa: F401
from .exercise import Exercise  # noqa: F401
from .workout_plan import WorkoutPlan, WorkoutPlanItem  # noqa: F401
from .setting import Setting  # noqa: F401
from .email_log import EmailLog  # noqa: F401
