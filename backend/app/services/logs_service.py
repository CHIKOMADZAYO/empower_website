import logging

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log_activity import ActivityLog

logger = logging.getLogger(__name__)


async def record_activity(
    session: AsyncSession,
    *,
    user_id: int | None,
    action: str,
    resource: str | None = None,
    resource_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
):
    activity = ActivityLog(
        user_id=user_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    session.add(activity)

    logger.info(
        "User activity | user_id=%s action=%s resource=%s resource_id=%s",
        user_id,
        action,
        resource,
        resource_id,
    )