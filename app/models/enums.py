from enum import StrEnum


class ScanStatus(StrEnum):
    QUEUED = 'QUEUED'
    PROCESSING = 'PROCESSING'
    EXTRACTED = 'EXTRACTED'
    REVIEW_REQUIRED = 'REVIEW_REQUIRED'
    APPROVED = 'APPROVED'
    FAILED = 'FAILED'


class AttemptStatus(StrEnum):
    PROCESSING = 'PROCESSING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'


class IssueSeverity(StrEnum):
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'
