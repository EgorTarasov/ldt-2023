from enum import Enum


class UserRole(str, Enum):
    """
    role:
    0 - Наставник -> mentor
    1 - Куратор -> curator
    2 - Кадр -> hr
    3 - Кандидат -> candidate
    4 - Стажер -> intern
    """

    mentor = "mentor"
    curator = "curator"
    hr = "hr"
    candidate = "candidate"
    intern = "intern"


class FeedbackType(str, Enum):
    received = "received"
    sent = "sent"


class MailingType(str, Enum):
    received = "received"
    sent = "sent"


class MailingTemplate(str, Enum):
    event_info = "app/templates/event_info.html"
    event_reminder = "app/templates/event_reminder.html"
    intern_school_invite = "app/templates/intern_school_invite.html"


class MentorStatus(str, Enum):
    pending = "pending"
    active = "active"
    declined = "declined"


class InternApplicationStatus(str, Enum):
    unverified = "unverified"
    verified = "verified"
    approved = "approved"
    declined = "declined"


class InternApplicationParameters(str, Enum):
    status = "status"
    age = "age"
    city = "city"
    course = "course"
    education = "education"
    citizenship = "citizenship"
    graduation_date = "graduation_date"
