"""Event names (CONTRACTS §7). Payloads always include the subject id."""

COMPLAINT_SUBMITTED = "complaint.submitted"          # {sr_id}
COMPLAINT_REOPENED = "complaint.reopened"            # {sr_id, reopen_count}
COMPLAINT_STATUS_CHANGED = "complaint.status_changed"  # {sr_id, from, to}
COMPLAINT_MERGED = "complaint.merged"                # {sr_id, parent_sr_id}
WORK_ORDER_CREATED = "work_order.created"            # {wo_id, sr_id}
WORK_ORDER_COMPLETED = "work_order.completed"        # {wo_id}
WORK_ORDER_REWORK = "work_order.rework"              # {wo_id, reason}
WORK_ORDER_VERIFIED = "work_order.verified"          # {wo_id}
REFERRAL_CREATED = "referral.created"                # {referral_id, sr_id}
REFERRAL_REPLIED = "referral.replied"                # {referral_id}
ESCALATION_CREATED = "escalation.created"            # {sr_id, level}
DETECTIONS_INGESTED = "detections.ingested"          # {source_id, count}
WEATHER_ALERT_RECEIVED = "weather_alert.received"    # {alert_id}
INCIDENT_CREATED = "incident.created"                # {incident_id}
ADVISORY_PUBLISHED = "advisory.published"            # {incident_id}
AGENT_RUN_FINISHED = "agent_run.finished"            # {run_id, agent}

ALL = [v for k, v in dict(globals()).items() if k.isupper() and isinstance(v, str) and "." in v]
