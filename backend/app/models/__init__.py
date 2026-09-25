from app.models.student import Student
from app.models.teacher import Teacher
from app.models.admin import Admin
from app.models.course import Course
from app.models.category import Category
from app.models.level import Level
from app.models.group import Group
from app.models.schedule import Schedule
from app.models.attendance import Attendance
from app.models.grade import Grade
from app.models.homework import Homework, HomeworkSubmission
from app.models.gamification import StudentGamification
from app.models.reward_transaction import RewardTransaction
from app.models.achievement import Achievement, StudentAchievement
from app.models.shop import ShopProduct, ShopOrder
from app.models.content import Content, ContentProgress
from app.models.event import Event, EventRegistration
from app.models.reward_rule import RewardRule
from app.models.notification import Notification
from app.models.course_module import CourseModule
from app.models.lead import Lead
from app.models.student_course import StudentCourse
from app.models.student_group import StudentGroup
from app.models.lesson import Lesson
from app.models.lesson_progress import LessonProgress
from app.models.lesson_quiz import LessonQuiz
from app.models.book import Book, BookOrder

from app.models.podcast import Podcast
from app.models.training import Training, TrainingRegistration
from app.models.exam import Exam, ExamRegistration

from app.models.ai_telegram_submission import AITelegramSubmission

from app.models.online_exam import OnlineExam, OnlineExamQuestion, OnlineExamAttempt

from app.models.ai_homework_state import AIHomeworkState
