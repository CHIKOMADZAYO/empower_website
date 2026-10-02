import logging

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.log_activity import ActivityLog

logger = logging.getLogger(__name__)


def record_activity(
    session: Session,
    *,
    user_id: int | None,
    action: str,
    resource: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> ActivityLog:
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    session.add(activity)
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise

    logger.info(
        "User activity | user_id=%s action=%s resource=%s resource_id=%s",
        user_id,
        action,
        resource,
        resource_id,
    )
    return activity


def record_activity_in_background(
    *,
    user_id: int | None,
    action: str,
    resource: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    """Persist best-effort activity data without reusing a request session."""
    with SessionLocal() as session:
        try:
            record_activity(
                session,
                user_id=user_id,
                action=action,
                resource=resource,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception:
            logger.exception("Failed to persist background activity log")
