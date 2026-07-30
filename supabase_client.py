"""
supabase_client.py
------------------
Singleton Supabase client and helper functions for the predictive maintenance system.

Provides:
  - Supabase PostgREST client (server-side, using service role key)
  - User lookup / creation helpers
  - Diagnostic log persistence
  - Work order CRUD
  - OT Security event logging

Graceful degradation: if SUPABASE_URL or SUPABASE_SERVICE_KEY are not configured,
all helpers become no-ops and the application continues to work with in-memory/
hardcoded fallbacks.
"""

import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Client initialisation
# ──────────────────────────────────────────────────────────────────────────────

_supabase = None
_supabase_enabled = False

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        from supabase import create_client, Client
        _supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        _supabase_enabled = True
        logger.info("✅ Supabase client initialised successfully.")
    except ImportError:
        logger.warning("⚠️  supabase Python package not installed. Run: pip install supabase>=2.0.0")
    except Exception as exc:
        logger.error(f"❌ Supabase client init failed: {exc}")
else:
    logger.warning(
        "⚠️  SUPABASE_URL or SUPABASE_SERVICE_KEY not set. "
        "Supabase persistence is DISABLED — falling back to in-memory operation."
    )


def is_enabled() -> bool:
    """Returns True if the Supabase client is ready."""
    return _supabase_enabled and _supabase is not None


# ──────────────────────────────────────────────────────────────────────────────
# User / Auth helpers
# ──────────────────────────────────────────────────────────────────────────────

def get_user_by_email(email: str) -> dict | None:
    """
    Look up a user from the Supabase `users` table by email.
    Returns the row dict or None if not found / Supabase is disabled.
    """
    if not is_enabled():
        return None
    try:
        res = _supabase.table("users").select("*").eq("email", email).single().execute()
        return res.data
    except Exception as exc:
        logger.error(f"Supabase get_user_by_email error: {exc}")
        return None


def list_users() -> list:
    """Return all rows from the `users` table."""
    if not is_enabled():
        return []
    try:
        res = _supabase.table("users").select("*").execute()
        return res.data or []
    except Exception as exc:
        logger.error(f"Supabase list_users error: {exc}")
        return []


# ──────────────────────────────────────────────────────────────────────────────
# Diagnostic log helpers
# ──────────────────────────────────────────────────────────────────────────────

def log_diagnostic(
    email: str,
    fault_code: int,
    fault_name: str,
    severity: str,
    confidence: float,
    mode: str,
    sensor_data: dict,
    ai_recommendation: dict,
    cii_rating: str = None,
    rul_hours: float = None,
) -> dict | None:
    """
    Persist a prediction result to the `diagnostic_logs` table.
    Returns the inserted row or None on failure / disabled.
    """
    if not is_enabled():
        return None
    try:
        row = {
            "email": email,
            "fault_code": fault_code,
            "fault_name": fault_name,
            "severity": severity,
            "confidence": round(confidence, 4),
            "mode": mode,
            "sensor_data": sensor_data,
            "ai_recommendation": ai_recommendation,
            "cii_rating": cii_rating,
            "rul_hours": rul_hours,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        res = _supabase.table("diagnostic_logs").insert(row).execute()
        return res.data[0] if res.data else None
    except Exception as exc:
        logger.error(f"Supabase log_diagnostic error: {exc}")
        return None


def get_recent_diagnostics(email: str = None, limit: int = 50) -> list:
    """Fetch the most recent diagnostic log entries, optionally filtered by user."""
    if not is_enabled():
        return []
    try:
        query = _supabase.table("diagnostic_logs").select("*").order("created_at", desc=True).limit(limit)
        if email:
            query = query.eq("email", email)
        res = query.execute()
        return res.data or []
    except Exception as exc:
        logger.error(f"Supabase get_recent_diagnostics error: {exc}")
        return []


# ──────────────────────────────────────────────────────────────────────────────
# Work order CRUD helpers
# ──────────────────────────────────────────────────────────────────────────────

def get_work_orders() -> list:
    """Fetch all work orders ordered by creation date (newest first)."""
    if not is_enabled():
        return []
    try:
        res = _supabase.table("work_orders").select("*").order("created_at", desc=True).execute()
        return res.data or []
    except Exception as exc:
        logger.error(f"Supabase get_work_orders error: {exc}")
        return []


def create_work_order(
    wo_number: str,
    fault_name: str,
    assignee: str,
    priority: str,
    status: str,
    time_logged: str,
    diagnosis: dict,
    created_by: str,
) -> dict | None:
    """Insert a new work order row. Returns the created row or None."""
    if not is_enabled():
        return None
    try:
        row = {
            "wo_number": wo_number,
            "fault_name": fault_name,
            "assignee": assignee,
            "priority": priority,
            "status": status,
            "time_logged": time_logged,
            "diagnosis": diagnosis,
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        res = _supabase.table("work_orders").insert(row).execute()
        return res.data[0] if res.data else None
    except Exception as exc:
        logger.error(f"Supabase create_work_order error: {exc}")
        return None


def update_work_order_status(wo_number: str, status: str) -> dict | None:
    """Update the status of an existing work order by wo_number."""
    if not is_enabled():
        return None
    try:
        res = (
            _supabase.table("work_orders")
            .update({"status": status})
            .eq("wo_number", wo_number)
            .execute()
        )
        return res.data[0] if res.data else None
    except Exception as exc:
        logger.error(f"Supabase update_work_order_status error: {exc}")
        return None


def delete_work_order(wo_number: str) -> bool:
    """Delete a work order by wo_number. Returns True on success."""
    if not is_enabled():
        return False
    try:
        _supabase.table("work_orders").delete().eq("wo_number", wo_number).execute()
        return True
    except Exception as exc:
        logger.error(f"Supabase delete_work_order error: {exc}")
        return False


# ──────────────────────────────────────────────────────────────────────────────
# OT Security event logging
# ──────────────────────────────────────────────────────────────────────────────

def log_ot_security_event(
    event_type: str,
    ip_address: str,
    path: str,
    reason: str,
    threat_level: str,
    payload_snapshot: dict = None,
) -> dict | None:
    """
    Persist an OT security anomaly event to the `ot_security_events` table.
    Called by ot_security.py when anomalies or access failures are detected.
    """
    if not is_enabled():
        return None
    try:
        row = {
            "event_type": event_type,
            "ip_address": ip_address,
            "path": path,
            "reason": reason,
            "threat_level": threat_level,
            "payload_snapshot": payload_snapshot or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        res = _supabase.table("ot_security_events").insert(row).execute()
        return res.data[0] if res.data else None
    except Exception as exc:
        logger.error(f"Supabase log_ot_security_event error: {exc}")
        return None


def get_ot_security_events(limit: int = 100) -> list:
    """Fetch recent OT security events from Supabase."""
    if not is_enabled():
        return []
    try:
        res = (
            _supabase.table("ot_security_events")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception as exc:
        logger.error(f"Supabase get_ot_security_events error: {exc}")
        return []
