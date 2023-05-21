from enum import Enum


class UserRole(int, Enum):
    """
    role_id:
    0 - Наставник -> mentor
    1 - Куратор -> curator
    2 - Кадр -> hr
    3 - Кандидат -> candidate
    4 - Стажер -> intern
    """

    mentor = 0
    curator = 1
    hr = 2
    candidate = 3
    intern = 4


class FeedbackType(str, Enum):
    received = "received"
    sent = "sent"


class MailingType(str, Enum):
    received = "received"
    sent = "sent"
