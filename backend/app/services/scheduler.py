"""Background scheduler for proactive daily reporting."""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.analytics import run_all_daily_reports

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _scheduled_job() -> None:
    """Job executed by the scheduler — generates daily reports for all users."""
    db: Session = SessionLocal()
    try:
        run_all_daily_reports(db)
        logger.info("Daily report job completed successfully.")
    except Exception as exc:
        logger.error("Daily report job failed: %s", exc, exc_info=True)
    finally:
        db.close()


def start_scheduler() -> None:
    """Start the background scheduler if not already running."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone="UTC")
    # Run every day at 23:00 UTC
    _scheduler.add_job(
        _scheduled_job,
        trigger=CronTrigger(hour=23, minute=0),
        id="daily_report_job",
        name="Daily Report Generation",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info("Background scheduler started — daily report job scheduled at 23:00 UTC.")


def shutdown_scheduler() -> None:
    """Gracefully shut down the scheduler."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Background scheduler shut down.")


def get_scheduler() -> BackgroundScheduler | None:
    return _scheduler
