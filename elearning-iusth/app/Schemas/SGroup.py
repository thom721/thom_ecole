from pydantic import BaseModel, ConfigDict


class GroupCreate(BaseModel):
    name: str
    description: str | None = None


class GroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class GroupMemberOut(BaseModel):
    user_id: str
    name: str
    email: str


class GroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    course_id: str
    name: str
    description: str | None = None


class GroupDetailOut(GroupOut):
    members: list[GroupMemberOut] = []


class GroupingCreate(BaseModel):
    name: str
    description: str | None = None


class GroupingUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class GroupingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    course_id: str
    name: str
    description: str | None = None


class GroupingDetailOut(GroupingOut):
    groups: list[GroupOut] = []


class AddMemberIn(BaseModel):
    user_id: str


class AddGroupToGroupingIn(BaseModel):
    group_id: str
