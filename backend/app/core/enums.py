"""Shared enums (CONTRACTS §2). Stored as plain strings in the database."""
from enum import StrEnum


class Role(StrEnum):
    CITIZEN = "CITIZEN"
    WARD_OFFICER = "WARD_OFFICER"
    FIELD_TEAM = "FIELD_TEAM"
    CONTROL_ROOM = "CONTROL_ROOM"
    AGENCY = "AGENCY"


class SRStatus(StrEnum):
    SUBMITTED = "SUBMITTED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    WORK_COMPLETED = "WORK_COMPLETED"
    VERIFIED = "VERIFIED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    MERGED = "MERGED"
    REJECTED = "REJECTED"
    REOPENED = "REOPENED"


OPEN_SR_STATUSES = {SRStatus.SUBMITTED, SRStatus.ASSIGNED, SRStatus.IN_PROGRESS, SRStatus.ON_HOLD,
                    SRStatus.WORK_COMPLETED, SRStatus.VERIFIED, SRStatus.REOPENED}


class WOStatus(StrEnum):
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    REWORK = "REWORK"
    VERIFIED = "VERIFIED"


class Priority(StrEnum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Category(StrEnum):
    POTHOLE = "POTHOLE"
    ROAD_DAMAGE = "ROAD_DAMAGE"
    STREETLIGHT = "STREETLIGHT"
    GARBAGE = "GARBAGE"
    WATER_LEAK = "WATER_LEAK"
    SEWAGE_OVERFLOW = "SEWAGE_OVERFLOW"
    BLOCKED_DRAIN = "BLOCKED_DRAIN"
    WATERLOGGING = "WATERLOGGING"
    TREE_FALL = "TREE_FALL"
    OPEN_MANHOLE = "OPEN_MANHOLE"
    OTHER = "OTHER"


SURGE_CATEGORIES = {Category.WATERLOGGING, Category.BLOCKED_DRAIN, Category.TREE_FALL, Category.SEWAGE_OVERFLOW}


class Source(StrEnum):
    CITIZEN_WEB = "CITIZEN_WEB"
    VEHICLE_FEED = "VEHICLE_FEED"
    HELPDESK = "HELPDESK"
    CSV_IMPORT = "CSV_IMPORT"


class SLAState(StrEnum):
    ON_TRACK = "ON_TRACK"
    AT_RISK = "AT_RISK"
    BREACHED = "BREACHED"
    PAUSED = "PAUSED"


class HoldReason(StrEnum):
    MATERIAL = "MATERIAL"
    AGENCY = "AGENCY"
    WEATHER = "WEATHER"
    ACCESS = "ACCESS"
    CITIZEN = "CITIZEN"


# Hold reasons that pause the SLA clock (deterministic rule, BUILD_PLAN §6 Agent 2).
SLA_PAUSING_REASONS = {HoldReason.AGENCY, HoldReason.WEATHER, HoldReason.CITIZEN}


class RejectReason(StrEnum):
    NOT_CIVIC_ISSUE = "NOT_CIVIC_ISSUE"
    OUTSIDE_JURISDICTION = "OUTSIDE_JURISDICTION"
    INSUFFICIENT_INFO = "INSUFFICIENT_INFO"
    DUPLICATE_SPAM = "DUPLICATE_SPAM"


class AssetOwner(StrEnum):
    MUNICIPAL = "MUNICIPAL"
    BESCOM = "BESCOM"
    BWSSB = "BWSSB"


class Agency(StrEnum):
    BESCOM = "BESCOM"
    BWSSB = "BWSSB"


class AgencyStatus(StrEnum):
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    NOT_OURS = "NOT_OURS"


class AttachmentKind(StrEnum):
    CITIZEN = "CITIZEN"
    BEFORE = "BEFORE"
    AFTER = "AFTER"


class ActorType(StrEnum):
    HUMAN = "HUMAN"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


class ClosureType(StrEnum):
    CITIZEN = "CITIZEN"
    AUTO = "AUTO"


class AgentName(StrEnum):
    CASE_INVESTIGATOR = "case_investigator"
    FOLLOWUP_ESCALATION = "followup_escalation"
    ROAD_HAZARD_SENSING = "road_hazard_sensing"
    EVIDENCE_AUDITOR = "evidence_auditor"
    SURGE_COMMANDER = "surge_commander"


class RunStatus(StrEnum):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FALLBACK = "FALLBACK"
    FAILED = "FAILED"


class Verdict(StrEnum):
    PASS = "PASS"
    FLAG = "FLAG"
    FAIL = "FAIL"


class ClusterDecision(StrEnum):
    CREATE = "CREATE"
    CORROBORATE = "CORROBORATE"
    REPAIR_FAILURE = "REPAIR_FAILURE"
    DISMISS = "DISMISS"
    REVIEW = "REVIEW"


class ProposalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class HazardType(StrEnum):
    POTHOLE = "POTHOLE"
    DAMAGED_ROAD = "DAMAGED_ROAD"
    ROUGH_SURFACE = "ROUGH_SURFACE"


class RoadClass(StrEnum):
    ARTERIAL = "ARTERIAL"
    LOCAL = "LOCAL"


class RoadFeature(StrEnum):
    SPEED_BREAKER = "SPEED_BREAKER"
    RAIL_CROSSING = "RAIL_CROSSING"


class Language(StrEnum):
    EN = "en"
    KN = "kn"
