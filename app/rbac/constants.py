from enum import Enum


class Permission(str, Enum):
    """Granular permission definitions"""
    
    # Students Management
    STUDENTS_VIEW = "students.view"
    STUDENTS_CREATE = "students.create"
    STUDENTS_EDIT = "students.edit"
    STUDENTS_DELETE = "students.delete"
    STUDENTS_EXPORT = "students.export"
    
    # Teachers Management
    TEACHERS_VIEW = "teachers.view"
    TEACHERS_CREATE = "teachers.create"
    TEACHERS_EDIT = "teachers.edit"
    TEACHERS_DELETE = "teachers.delete"
    
    # Courses Management
    COURSES_VIEW = "courses.view"
    COURSES_CREATE = "courses.create"
    COURSES_EDIT = "courses.edit"
    COURSES_DELETE = "courses.delete"
    
    # Attendance
    ATTENDANCE_VIEW = "attendance.view"
    ATTENDANCE_MARK = "attendance.mark"
    ATTENDANCE_EDIT = "attendance.edit"
    ATTENDANCE_REPORT = "attendance.report"
    
    # Grades/Marks
    MARKS_VIEW = "marks.view"
    MARKS_ENTER = "marks.enter"
    MARKS_EDIT = "marks.edit"
    MARKS_PUBLISH = "marks.publish"
    MARKS_VIEW_ALL = "marks.view_all"  # See all students' marks
    
    # Finance/Fees
    FEES_VIEW = "fees.view"
    FEES_COLLECT = "fees.collect"
    FEES_EDIT = "fees.edit"
    FEES_WAIVE = "fees.waive"
    FEES_REPORT = "fees.report"
    
    # Reports
    REPORTS_ACADEMIC = "reports.academic"
    REPORTS_FINANCIAL = "reports.financial"
    REPORTS_ATTENDANCE = "reports.attendance"
    
    # Administration
    SCHOOL_SETTINGS = "school.settings"
    USERS_MANAGE = "users.manage"
    ROLES_MANAGE = "roles.manage"
    
    # System (Super Admin only)
    SYSTEM_TENANTS_MANAGE = "system.tenants.manage"
    SYSTEM_GLOBAL_ACCESS = "system.global_access"


class Role(str, Enum):
    """Predefined user roles"""
    
    SUPER_ADMIN = "super_admin"          # Global cross-tenant access
    SCHOOL_ADMIN = "school_admin"        # Full access within school
    PRINCIPAL = "principal"              # School leadership
    TEACHER = "teacher"                  # Teaching staff
    STUDENT = "student"                  # Student portal access
    PARENT = "parent"                    # Parent/guardian access
    ACCOUNTANT = "accountant"            # Finance management
    RECEPTIONIST = "receptionist"        # Front desk operations


# Role to Permission mappings
ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: [
        Permission.SYSTEM_TENANTS_MANAGE,
        Permission.SYSTEM_GLOBAL_ACCESS,
        # Super admins have all permissions
        *[p for p in Permission]
    ],
    
    Role.SCHOOL_ADMIN: [
        Permission.STUDENTS_VIEW,
        Permission.STUDENTS_CREATE,
        Permission.STUDENTS_EDIT,
        Permission.STUDENTS_DELETE,
        Permission.STUDENTS_EXPORT,
        Permission.TEACHERS_VIEW,
        Permission.TEACHERS_CREATE,
        Permission.TEACHERS_EDIT,
        Permission.TEACHERS_DELETE,
        Permission.COURSES_VIEW,
        Permission.COURSES_CREATE,
        Permission.COURSES_EDIT,
        Permission.COURSES_DELETE,
        Permission.ATTENDANCE_VIEW,
        Permission.ATTENDANCE_REPORT,
        Permission.MARKS_VIEW_ALL,
        Permission.FEES_VIEW,
        Permission.FEES_EDIT,
        Permission.FEES_REPORT,
        Permission.REPORTS_ACADEMIC,
        Permission.REPORTS_FINANCIAL,
        Permission.REPORTS_ATTENDANCE,
        Permission.SCHOOL_SETTINGS,
        Permission.USERS_MANAGE,
        Permission.ROLES_MANAGE,
    ],
    
    Role.PRINCIPAL: [
        Permission.STUDENTS_VIEW,
        Permission.STUDENTS_EXPORT,
        Permission.TEACHERS_VIEW,
        Permission.COURSES_VIEW,
        Permission.ATTENDANCE_VIEW,
        Permission.ATTENDANCE_REPORT,
        Permission.MARKS_VIEW_ALL,
        Permission.FEES_VIEW,
        Permission.FEES_REPORT,
        Permission.REPORTS_ACADEMIC,
        Permission.REPORTS_FINANCIAL,
        Permission.REPORTS_ATTENDANCE,
    ],
    
    Role.TEACHER: [
        Permission.STUDENTS_VIEW,
        Permission.COURSES_VIEW,
        Permission.ATTENDANCE_VIEW,
        Permission.ATTENDANCE_MARK,
        Permission.ATTENDANCE_EDIT,
        Permission.MARKS_VIEW,
        Permission.MARKS_ENTER,
        Permission.MARKS_EDIT,
    ],
    
    Role.STUDENT: [
        Permission.COURSES_VIEW,
        Permission.ATTENDANCE_VIEW,  # Own attendance only
        Permission.MARKS_VIEW,        # Own marks only
        Permission.FEES_VIEW,         # Own fees only
    ],
    
    Role.PARENT: [
        Permission.STUDENTS_VIEW,     # Child's info only
        Permission.ATTENDANCE_VIEW,   # Child's attendance
        Permission.MARKS_VIEW,        # Child's marks
        Permission.FEES_VIEW,         # Child's fees
    ],
    
    Role.ACCOUNTANT: [
        Permission.STUDENTS_VIEW,
        Permission.FEES_VIEW,
        Permission.FEES_COLLECT,
        Permission.FEES_EDIT,
        Permission.FEES_WAIVE,
        Permission.FEES_REPORT,
        Permission.REPORTS_FINANCIAL,
    ],
    
    Role.RECEPTIONIST: [
        Permission.STUDENTS_VIEW,
        Permission.STUDENTS_CREATE,
        Permission.TEACHERS_VIEW,
        Permission.FEES_VIEW,
    ],
}
