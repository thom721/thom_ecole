# Point d'entrée central : chaque module de modèle doit être importé ici
# pour qu'Alembic (voir app/alembic/env.py, target_metadata = Base.metadata)
# voie l'intégralité du schéma lors d'un autogenerate.
from app.Models.MUser import User, SystemRole, MessagePrivacy
from app.Models.MPasswordReset import PasswordResetToken
from app.Models.MCourse import CourseCategory, Course, Section, CourseFormat, CourseDisplay
from app.Models.MEnrollment import Enrollment, CourseRole, EnrollmentStatus
from app.Models.MResource import Resource, ResourceFile, ResourceType
from app.Models.MAssignment import Assignment, Submission, SubmissionType, SubmissionStatus
from app.Models.MQuestion import QuestionCategory, Question, QuestionOption, QuestionAcceptedAnswer, QuestionType
from app.Models.MQuestionCalculated import QuestionCalculatedDataset
from app.Models.MQuestionCloze import QuestionClozePart
from app.Models.MQuiz import Quiz, QuizQuestion, QuizDrawRule, QuizAttempt, QuizResponse, QuizAttemptStatus
from app.Models.MGrade import GradeCategory, GradeItem, ManualGrade, GradeItemKind
from app.Models.MForum import Forum, ForumDiscussion, ForumPost, ForumSubscription, ForumReadState
from app.Models.MChoice import Choice, ChoiceOption, ChoiceAnswer, ChoiceResultsDisplay
from app.Models.MGlossary import Glossary, GlossaryEntry
from app.Models.MWiki import Wiki, Subwiki, WikiPage, WikiVersion, WikiMode
from app.Models.MGroup import Group, GroupMember, Grouping, GroupingGroup, GroupMode
from app.Models.MEnrollmentMethod import CourseEnrollmentSettings, Cohort, CohortMember, CohortSync
from app.Models.MCalendar import CalendarEvent
from app.Models.MNotification import Notification, NotificationKind
from app.Models.MCompletion import ActivityCompletion, CompletionItemType, CompletionMode, ActivityCompletionConfig
from app.Models.MAccessCondition import AccessCondition, AccessConditionType, AccessLogic
from app.Models.MScale import Scale, ScaleLevel, GradeLetter
from app.Models.MAccessLog import AccessLog, AccessItemType
from app.Models.MLesson import (
    Lesson, LessonPage, LessonAnswer, LessonAttempt, LessonPageAttempt,
    LessonPageType, LessonJumpType, LessonAttemptStatus,
)
from app.Models.MWorkshop import (
    Workshop, WorkshopDimension, WorkshopRubricLevel, WorkshopNumerrorsMap,
    WorkshopSubmission, WorkshopAssessment, WorkshopGrade,
    WorkshopPhase, WorkshopStrategy,
)
from app.Models.MMessaging import (
    Conversation, ConversationMember, Message, MessageUserAction, ConversationUserAction,
    Contact, ContactRequest, BlockedUser, ConversationType, MessageActionType, ConversationActionType,
)
from app.Models.MBadge import (
    Badge, BadgeCriterion, BadgeCriterionMet, BadgeIssued,
    BadgeStatus, BadgeCriteriaType, BadgeCriteriaLogic,
)
from app.Models.MBlock import UserBlockInstance, BlockType, BlockRegion
from app.Models.MCompetency import (
    CompetencyFramework, Competency, CourseCompetency, ModuleCompetency,
    UserCompetency, UserCompetencyCourse, CompetencyEvidence, Plan, PlanCompetency,
    CompetencyRuleType, CompetencyRuleOutcome, UserCompetencyStatus, PlanStatus, EvidenceAction,
)
from app.Models.MLiveSession import LiveSession, LiveSessionAttendance
from app.Models.MInteractiveVideo import (
    InteractiveVideo, InteractiveVideoCheckpoint, InteractiveVideoAttempt, InteractiveVideoResponse,
    InteractiveVideoSourceType, InteractiveVideoAttemptStatus,
)
from app.Models.MPermission import Permission, Role, RolePermission, UserRole
from app.Models.MStaffMeeting import StaffMeeting, StaffMeetingInvitee

__all__ = [
    "User", "SystemRole", "MessagePrivacy",
    "PasswordResetToken",
    "CourseCategory", "Course", "Section", "CourseFormat", "CourseDisplay",
    "Enrollment", "CourseRole", "EnrollmentStatus",
    "Resource", "ResourceFile", "ResourceType",
    "Assignment", "Submission", "SubmissionType", "SubmissionStatus",
    "QuestionCategory", "Question", "QuestionOption", "QuestionAcceptedAnswer", "QuestionType",
    "QuestionCalculatedDataset", "QuestionClozePart",
    "Quiz", "QuizQuestion", "QuizDrawRule", "QuizAttempt", "QuizResponse", "QuizAttemptStatus",
    "GradeCategory", "GradeItem", "ManualGrade", "GradeItemKind",
    "Forum", "ForumDiscussion", "ForumPost", "ForumSubscription", "ForumReadState",
    "Choice", "ChoiceOption", "ChoiceAnswer", "ChoiceResultsDisplay",
    "Glossary", "GlossaryEntry",
    "Wiki", "Subwiki", "WikiPage", "WikiVersion", "WikiMode",
    "Group", "GroupMember", "Grouping", "GroupingGroup", "GroupMode",
    "CourseEnrollmentSettings", "Cohort", "CohortMember", "CohortSync",
    "CalendarEvent",
    "Notification", "NotificationKind",
    "ActivityCompletion", "CompletionItemType", "CompletionMode", "ActivityCompletionConfig",
    "AccessCondition", "AccessConditionType", "AccessLogic",
    "Scale", "ScaleLevel", "GradeLetter",
    "AccessLog", "AccessItemType",
    "Lesson", "LessonPage", "LessonAnswer", "LessonAttempt", "LessonPageAttempt",
    "LessonPageType", "LessonJumpType", "LessonAttemptStatus",
    "Workshop", "WorkshopDimension", "WorkshopRubricLevel", "WorkshopNumerrorsMap",
    "WorkshopSubmission", "WorkshopAssessment", "WorkshopGrade",
    "WorkshopPhase", "WorkshopStrategy",
    "Conversation", "ConversationMember", "Message", "MessageUserAction", "ConversationUserAction",
    "Contact", "ContactRequest", "BlockedUser", "ConversationType", "MessageActionType", "ConversationActionType",
    "Badge", "BadgeCriterion", "BadgeCriterionMet", "BadgeIssued",
    "BadgeStatus", "BadgeCriteriaType", "BadgeCriteriaLogic",
    "CompetencyFramework", "Competency", "CourseCompetency", "ModuleCompetency",
    "UserCompetency", "UserCompetencyCourse", "CompetencyEvidence", "Plan", "PlanCompetency",
    "CompetencyRuleType", "CompetencyRuleOutcome", "UserCompetencyStatus", "PlanStatus", "EvidenceAction",
    "UserBlockInstance", "BlockType", "BlockRegion",
    "LiveSession", "LiveSessionAttendance",
    "InteractiveVideo", "InteractiveVideoCheckpoint", "InteractiveVideoAttempt", "InteractiveVideoResponse",
    "InteractiveVideoSourceType", "InteractiveVideoAttemptStatus",
    "Permission", "Role", "RolePermission", "UserRole",
    "StaffMeeting", "StaffMeetingInvitee",
]
