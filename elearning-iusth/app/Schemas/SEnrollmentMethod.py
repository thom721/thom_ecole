from pydantic import BaseModel, ConfigDict

from app.Models.MEnrollment import CourseRole


class CourseEnrollmentSettingsUpdate(BaseModel):
    self_enrollment_enabled: bool | None = None
    self_enrollment_key: str | None = None
    guest_access_enabled: bool | None = None
    guest_access_key: str | None = None


class CourseEnrollmentSettingsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    course_id: str
    self_enrollment_enabled: bool
    self_enrollment_key: str | None = None
    guest_access_enabled: bool
    guest_access_key: str | None = None


class SelfEnrollIn(BaseModel):
    key: str | None = None


class CohortCreate(BaseModel):
    name: str
    description: str | None = None


class CohortUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class CohortMemberOut(BaseModel):
    user_id: str
    name: str
    email: str


class CohortOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str | None = None


class CohortDetailOut(CohortOut):
    members: list[CohortMemberOut] = []


class AddCohortMemberIn(BaseModel):
    user_id: str


class CohortSyncCreate(BaseModel):
    cohort_id: str
    role: CourseRole = CourseRole.student


class CohortSyncOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    course_id: str
    cohort_id: str
    cohort_name: str
    role: CourseRole
