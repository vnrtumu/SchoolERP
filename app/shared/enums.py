from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    BRANCH_ADMIN = "branch_admin"
    BRANCH_PRINCIPAL = "branch_principal"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"


class Gender(str, Enum):
    """Gender enumeration"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class AttendanceStatus(str, Enum):
    """Attendance status enumeration"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class FeeStatus(str, Enum):
    """Fee payment status enumeration"""
    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class AcademicYear(str, Enum):
    """Academic year status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    UPCOMING = "upcoming"


class DayOfWeek(str, Enum):
    """Days of the week"""
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"
