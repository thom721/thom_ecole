from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.Models.MCourse import Course, Section
from app.Models.MResource import Resource
from app.Models.MAssignment import Assignment, Submission
from app.Models.MQuiz import Quiz, QuizQuestion, QuizDrawRule, QuizAttempt, QuizResponse
from app.Models.MQuestion import QuestionCategory, Question, QuestionOption, QuestionAcceptedAnswer
from app.Models.MGrade import GradeCategory, GradeItem, GradeItemKind, ManualGrade
from app.Models.MForum import Forum
from app.Models.MChoice import Choice, ChoiceOption
from app.Models.MGlossary import Glossary
from app.Models.MWiki import Wiki
from app.Models.MLesson import Lesson, LessonPage, LessonAnswer
from app.Models.MWorkshop import Workshop, WorkshopDimension, WorkshopRubricLevel, WorkshopNumerrorsMap, WorkshopSubmission, WorkshopAssessment, WorkshopGrade
from app.Models.MCompletion import ActivityCompletion, CompletionItemType
from app.Models.MEnrollment import Enrollment, CourseRole
from app.Models.MUser import User, SystemRole
from app.Schemas.SCourse import CourseOut
from app.Schemas.SCourseExport import (
    CourseExportDocument, ExportCourse, ExportSection, ExportResource, ExportResourceFileMeta,
    ExportAssignment, ExportQuiz, ExportQuizQuestion, ExportDrawRule,
    ExportForum, ExportChoice, ExportChoiceOption, ExportGlossary, ExportWiki,
    ExportLesson, ExportLessonPage, ExportLessonAnswer,
    ExportWorkshop, ExportWorkshopDimension, ExportWorkshopRubricLevel, ExportWorkshopNumerrorsMapRow,
    ExportQuestionCategory, ExportQuestion, ExportQuestionOption,
    ExportGradeCategory, ExportGradeItemManual,
    ExportSubmission, ExportQuizAttempt, ExportQuizResponse, ExportManualGradeValue,
    ExportActivityCompletion, ExportWorkshopSubmission, ExportWorkshopAssessment, ExportWorkshopGrade,
    StudentData,
    CourseImportRequest, CourseImportResult, EXPORT_VERSION,
)
from app.dependencies.auth import assert_course_role, require_role

router = APIRouter(tags=["course-export"])

_TEACHING_ROLES = [CourseRole.teacher, CourseRole.manager]
_COMPLETION_LOCAL_TYPES = {CompletionItemType.assignment, CompletionItemType.quiz, CompletionItemType.workshop}


@router.get("/courses/{course_id}/export")
def export_course(
    course_id: str,
    include_student_data: bool = Query(False),
    current_user: User = Depends(require_role([SystemRole.teacher, SystemRole.admin])),
    db: Session = Depends(get_db),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours introuvable")
    assert_course_role(db, current_user, course_id, _TEACHING_ROLES)

    sections = (
        db.query(Section)
        .options(
            joinedload(Section.resources).joinedload(Resource.files),
            joinedload(Section.assignments),
            joinedload(Section.quizzes).joinedload(Quiz.quiz_questions),
            joinedload(Section.quizzes).joinedload(Quiz.draw_rules),
            joinedload(Section.forums),
            joinedload(Section.choices).joinedload(Choice.options),
            joinedload(Section.glossaries),
            joinedload(Section.wikis),
            joinedload(Section.lessons).joinedload(Lesson.pages).joinedload(LessonPage.answers),
            joinedload(Section.workshops).joinedload(Workshop.dimensions).joinedload(WorkshopDimension.levels),
            joinedload(Section.workshops).joinedload(Workshop.numerrors_map),
        )
        .filter(Section.course_id == course_id)
        .order_by(Section.sort_order)
        .all()
    )
    questions = db.query(Question).filter(Question.course_id == course_id).all()
    question_id_to_local = {q.id: f"q{i+1}" for i, q in enumerate(questions)}
    categories = db.query(QuestionCategory).filter(QuestionCategory.course_id == course_id).all()
    category_id_to_local = {c.id: f"qc{i+1}" for i, c in enumerate(categories)}

    grade_categories = db.query(GradeCategory).filter(GradeCategory.course_id == course_id).all()
    grade_category_id_to_local = {g.id: f"gc{i+1}" for i, g in enumerate(grade_categories)}
    manual_items = (
        db.query(GradeItem)
        .filter(GradeItem.course_id == course_id, GradeItem.kind == GradeItemKind.manual)
        .all()
    )
    manual_item_id_to_local = {m.id: f"gi{i+1}" for i, m in enumerate(manual_items)}

    # Identifiants locaux pour les activités référencées par des données
    # étudiantes (voir plan Épic 16) — construits en un seul passage sur
    # toutes les sections.
    assignment_id_to_local: dict[str, str] = {}
    quiz_id_to_local: dict[str, str] = {}
    lesson_page_id_to_local: dict[str, dict[str, str]] = {}  # lesson_id -> {page_id: local}
    workshop_id_to_local: dict[str, str] = {}
    workshop_dimension_id_to_local: dict[str, dict[str, str]] = {}  # workshop_id -> {dim_id: local}
    a_ctr = q_ctr = w_ctr = 0
    for section in sections:
        for a in section.assignments:
            a_ctr += 1
            assignment_id_to_local[a.id] = f"a{a_ctr}"
        for q in section.quizzes:
            q_ctr += 1
            quiz_id_to_local[q.id] = f"quiz{q_ctr}"
        for ws in section.workshops:
            w_ctr += 1
            workshop_id_to_local[ws.id] = f"w{w_ctr}"
            workshop_dimension_id_to_local[ws.id] = {d.id: f"wd{i+1}" for i, d in enumerate(ws.dimensions)}
        for lesson in section.lessons:
            lesson_page_id_to_local[lesson.id] = {p.id: f"lp{i+1}" for i, p in enumerate(lesson.pages)}

    export_sections = []
    for i, section in enumerate(sections):
        export_sections.append(ExportSection(
            local_id=f"s{i+1}", title=section.title, summary=section.summary,
            sort_order=section.sort_order, is_visible=section.is_visible,
            resources=[
                ExportResource(
                    resource_type=r.resource_type.value, title=r.title, description=r.description,
                    external_url=r.external_url, page_content=r.page_content,
                    sort_order=r.sort_order, is_visible=r.is_visible,
                    files_meta=[ExportResourceFileMeta(original_filename=f.original_filename, mime_type=f.mime_type, size_bytes=f.size_bytes) for f in r.files],
                ) for r in section.resources
            ],
            assignments=[
                ExportAssignment(
                    local_id=assignment_id_to_local[a.id],
                    title=a.title, description=a.description, due_date=a.due_date,
                    allow_late_submissions=a.allow_late_submissions, submission_type=a.submission_type,
                    max_points=a.max_points, is_visible=a.is_visible,
                ) for a in section.assignments
            ],
            quizzes=[
                ExportQuiz(
                    local_id=quiz_id_to_local[q.id],
                    title=q.title, description=q.description, time_limit_minutes=q.time_limit_minutes,
                    max_attempts=q.max_attempts, shuffle_questions=q.shuffle_questions,
                    opens_at=q.opens_at, closes_at=q.closes_at, is_visible=q.is_visible,
                    quiz_questions=[
                        ExportQuizQuestion(question_ref=question_id_to_local[qq.question_id], points=qq.points, sort_order=qq.sort_order)
                        for qq in q.quiz_questions if qq.question_id in question_id_to_local
                    ],
                    draw_rules=[
                        ExportDrawRule(category_ref=category_id_to_local[r.category_id], question_type=r.question_type,
                                       count=r.count, points=r.points, sort_order=r.sort_order)
                        for r in q.draw_rules if r.category_id in category_id_to_local
                    ],
                ) for q in section.quizzes
            ],
            forums=[
                ExportForum(title=f.title, description=f.description, is_visible=f.is_visible, group_mode=f.group_mode)
                for f in section.forums
            ],
            choices=[
                ExportChoice(
                    title=c.title, description=c.description, is_visible=c.is_visible,
                    allow_multiple=c.allow_multiple, allow_update=c.allow_update, limit_answers=c.limit_answers,
                    results_display=c.results_display, anonymous_results=c.anonymous_results,
                    show_unanswered=c.show_unanswered, opens_at=c.opens_at, closes_at=c.closes_at,
                    group_mode=c.group_mode,
                    options=[ExportChoiceOption(option_text=o.option_text, max_answers=o.max_answers, sort_order=o.sort_order) for o in c.options],
                ) for c in section.choices
            ],
            glossaries=[
                ExportGlossary(title=g.title, description=g.description, is_visible=g.is_visible, is_main=g.is_main,
                                allow_student_entries=g.allow_student_entries, require_approval=g.require_approval,
                                allow_duplicates=g.allow_duplicates)
                for g in section.glossaries
            ],
            wikis=[
                ExportWiki(title=w.title, description=w.description, is_visible=w.is_visible, mode=w.mode, first_page_title=w.first_page_title)
                for w in section.wikis
            ],
            lessons=[
                ExportLesson(
                    local_id=f"lesson{i+1}_{j+1}", title=lesson.title, description=lesson.description,
                    is_visible=lesson.is_visible, password=lesson.password,
                    max_attempts_per_question=lesson.max_attempts_per_question,
                    time_limit_minutes=lesson.time_limit_minutes, allow_retake=lesson.allow_retake,
                    pages=[
                        ExportLessonPage(
                            local_id=lesson_page_id_to_local[lesson.id][p.id], page_type=p.page_type,
                            title=p.title, content=p.content, points=p.points, sort_order=p.sort_order,
                            answers=[
                                ExportLessonAnswer(
                                    answer_text=ans.answer_text, is_correct=ans.is_correct, tolerance=ans.tolerance,
                                    jump_type=ans.jump_type,
                                    jump_to_page_ref=lesson_page_id_to_local[lesson.id].get(ans.jump_to_page_id) if ans.jump_to_page_id else None,
                                    sort_order=ans.sort_order,
                                ) for ans in p.answers
                            ],
                        ) for p in lesson.pages
                    ],
                ) for j, lesson in enumerate(section.lessons)
            ],
            workshops=[
                ExportWorkshop(
                    local_id=workshop_id_to_local[ws.id], title=ws.title, description=ws.description,
                    is_visible=ws.is_visible, grade=ws.grade, gradinggrade=ws.gradinggrade, strategy=ws.strategy,
                    use_peer_assessment=ws.use_peer_assessment, use_self_assessment=ws.use_self_assessment,
                    comparison=ws.comparison,
                    dimensions=[
                        ExportWorkshopDimension(
                            local_id=workshop_dimension_id_to_local[ws.id][d.id], sort_order=d.sort_order,
                            description=d.description, grade=d.grade, weight=d.weight,
                            label_no=d.label_no, label_yes=d.label_yes,
                            levels=[ExportWorkshopRubricLevel(grade=l.grade, definition=l.definition, sort_order=l.sort_order) for l in d.levels],
                        ) for d in ws.dimensions
                    ],
                    numerrors_map=[ExportWorkshopNumerrorsMapRow(error_count=r.error_count, grade_percent=r.grade_percent) for r in ws.numerrors_map],
                ) for ws in section.workshops
            ],
        ))

    student_data = None
    if include_student_data:
        student_data = _export_student_data(
            db, course_id, assignment_id_to_local, quiz_id_to_local, question_id_to_local,
            manual_item_id_to_local, workshop_id_to_local, workshop_dimension_id_to_local,
        )

    document = CourseExportDocument(
        export_version=EXPORT_VERSION,
        exported_at=datetime.now(timezone.utc),
        course=ExportCourse(short_name=course.short_name, full_name=course.full_name, summary=course.summary,
                             start_date=course.start_date, end_date=course.end_date, is_visible=course.is_visible),
        sections=export_sections,
        question_categories=[ExportQuestionCategory(local_id=category_id_to_local[c.id], name=c.name) for c in categories],
        questions=[
            ExportQuestion(
                local_id=question_id_to_local[q.id],
                category_ref=category_id_to_local.get(q.category_id) if q.category_id else None,
                question_type=q.question_type, question_text=q.question_text,
                default_points=q.default_points, is_active=q.is_active,
                options=[ExportQuestionOption(option_text=o.option_text, match_text=o.match_text, is_correct=o.is_correct, sort_order=o.sort_order) for o in q.options],
                accepted_answers=[a.answer_text for a in q.accepted_answers],
            ) for q in questions
        ],
        grade_categories=[ExportGradeCategory(local_id=grade_category_id_to_local[g.id], name=g.name, weight_percent=g.weight_percent, sort_order=g.sort_order) for g in grade_categories],
        grade_items_manual=[
            ExportGradeItemManual(local_id=manual_item_id_to_local[i.id], title=i.title, max_points=i.max_points,
                                   grade_category_ref=grade_category_id_to_local.get(i.grade_category_id) if i.grade_category_id else None,
                                   sort_order=i.sort_order)
            for i in manual_items
        ],
        student_data=student_data,
    )

    body = document.model_dump_json(indent=2)
    return Response(
        content=body, media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{course.short_name}.json"'},
    )


def _export_student_data(
    db, course_id, assignment_id_to_local, quiz_id_to_local, question_id_to_local,
    manual_item_id_to_local, workshop_id_to_local, workshop_dimension_id_to_local,
) -> StudentData:
    users_by_id: dict[str, str] = {}

    def email_of(user_id: str) -> str:
        if user_id not in users_by_id:
            u = db.query(User).filter(User.id == user_id).first()
            users_by_id[user_id] = u.email if u else "?"
        return users_by_id[user_id]

    submissions = []
    for aid, aref in assignment_id_to_local.items():
        for s in db.query(Submission).filter(Submission.assignment_id == aid).all():
            submissions.append(ExportSubmission(
                assignment_ref=aref, student_email=email_of(s.student_id), submitted_text=s.submitted_text,
                has_file=bool(s.file_path), status=s.status, grade=s.grade, feedback=s.feedback,
                submitted_at=s.submitted_at, graded_at=s.graded_at,
            ))

    quiz_attempts = []
    for qid, qref in quiz_id_to_local.items():
        for att in db.query(QuizAttempt).filter(QuizAttempt.quiz_id == qid).all():
            responses = db.query(QuizResponse).filter(QuizResponse.attempt_id == att.id).all()
            quiz_attempts.append(ExportQuizAttempt(
                quiz_ref=qref, student_email=email_of(att.student_id), status=att.status,
                score=att.score, max_score=att.max_score, started_at=att.started_at,
                submitted_at=att.submitted_at, graded_at=att.graded_at,
                responses=[
                    ExportQuizResponse(
                        question_ref=question_id_to_local[r.question_id], points=r.points, answer_data=r.answer_data,
                        is_correct=r.is_correct, points_awarded=r.points_awarded, feedback=r.feedback,
                    ) for r in responses if r.question_id in question_id_to_local
                ],
            ))

    manual_grades = []
    for miid, miref in manual_item_id_to_local.items():
        for mg in db.query(ManualGrade).filter(ManualGrade.grade_item_id == miid, ManualGrade.points.isnot(None)).all():
            manual_grades.append(ExportManualGradeValue(grade_item_ref=miref, student_email=email_of(mg.student_id), points=mg.points, feedback=mg.feedback))

    completions = []
    local_maps = {
        CompletionItemType.assignment: assignment_id_to_local,
        CompletionItemType.quiz: quiz_id_to_local,
        CompletionItemType.workshop: workshop_id_to_local,
    }
    for item_type, id_map in local_maps.items():
        if not id_map:
            continue
        rows = db.query(ActivityCompletion).filter(
            ActivityCompletion.item_type == item_type, ActivityCompletion.item_id.in_(list(id_map.keys())),
        ).all()
        for c in rows:
            completions.append(ExportActivityCompletion(
                item_type=item_type, item_ref=id_map[c.item_id], student_email=email_of(c.student_id), completed_at=c.completed_at,
            ))

    workshop_submissions = []
    for wid, wref in workshop_id_to_local.items():
        dim_map = workshop_dimension_id_to_local.get(wid, {})
        for sub in db.query(WorkshopSubmission).filter(WorkshopSubmission.workshop_id == wid).all():
            assessments = []
            for a in db.query(WorkshopAssessment).filter(WorkshopAssessment.submission_id == sub.id).all():
                grades = db.query(WorkshopGrade).filter(WorkshopGrade.assessment_id == a.id).all()
                assessments.append(ExportWorkshopAssessment(
                    reviewer_email=email_of(a.reviewer_id), weight=a.weight,
                    gradinggrade_override=a.gradinggrade_override, feedback_author=a.feedback_author,
                    feedback_reviewer=a.feedback_reviewer,
                    grades=[
                        ExportWorkshopGrade(dimension_ref=dim_map[g.dimension_id], grade=g.grade, peer_comment=g.peer_comment)
                        for g in grades if g.dimension_id in dim_map
                    ],
                ))
            workshop_submissions.append(ExportWorkshopSubmission(
                workshop_ref=wref, author_email=email_of(sub.author_id), title=sub.title,
                has_file=bool(sub.file_path), content=sub.content, grade_override=sub.grade_override,
                feedback_author=sub.feedback_author, published=sub.published, late=sub.late,
                assessments=assessments,
            ))

    return StudentData(
        submissions=submissions, quiz_attempts=quiz_attempts, manual_grades=manual_grades,
        completions=completions, workshop_submissions=workshop_submissions,
    )


@router.post("/courses/import", response_model=CourseImportResult, status_code=status.HTTP_201_CREATED)
def import_course(
    data: CourseImportRequest,
    current_user: User = Depends(require_role([SystemRole.teacher, SystemRole.admin])),
    db: Session = Depends(get_db),
):
    export = data.export
    warnings: list[str] = []
    sort_order_offset = 0

    if data.target_course_id:
        course = db.query(Course).filter(Course.id == data.target_course_id).first()
        if course is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cours cible introuvable")
        assert_course_role(db, current_user, course.id, _TEACHING_ROLES)
        existing_max = db.query(Section).filter(Section.course_id == course.id).count()
        sort_order_offset = existing_max
    else:
        if not data.short_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code de cours requis pour créer un nouveau cours")
        if db.query(Course).filter(Course.short_name == data.short_name).first():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ce code de cours est déjà utilisé")

        course = Course(
            short_name=data.short_name, full_name=data.full_name or export.course.full_name,
            summary=export.course.summary, start_date=export.course.start_date, end_date=export.course.end_date,
            is_visible=export.course.is_visible, created_by=current_user.id,
        )
        db.add(course)
        db.flush()

        # Enrôle le créateur comme professeur du cours importé, même logique
        # que la création normale d'un cours (RCourses.py::create_course).
        if current_user.system_role != SystemRole.admin:
            db.add(Enrollment(course_id=course.id, user_id=current_user.id, role_in_course=CourseRole.teacher, enrolled_by=current_user.id))

    # Catégories de questions puis questions — doivent exister AVANT les
    # quiz (imbriqués dans les sections) qui les référencent.
    category_local_to_id: dict[str, str] = {}
    for c in export.question_categories:
        cat = QuestionCategory(course_id=course.id, name=c.name)
        db.add(cat)
        db.flush()
        category_local_to_id[c.local_id] = cat.id

    question_local_to_id: dict[str, str] = {}
    for q in export.questions:
        question = Question(
            course_id=course.id, category_id=category_local_to_id.get(q.category_ref) if q.category_ref else None,
            question_type=q.question_type, question_text=q.question_text,
            default_points=q.default_points, is_active=q.is_active, created_by=current_user.id,
        )
        db.add(question)
        db.flush()
        question_local_to_id[q.local_id] = question.id
        for opt in q.options:
            db.add(QuestionOption(question_id=question.id, **opt.model_dump()))
        for ans in q.accepted_answers:
            db.add(QuestionAcceptedAnswer(question_id=question.id, answer_text=ans))

    grade_category_local_to_id: dict[str, str] = {}
    for g in export.grade_categories:
        cat = GradeCategory(course_id=course.id, name=g.name, weight_percent=g.weight_percent, sort_order=g.sort_order)
        db.add(cat)
        db.flush()
        grade_category_local_to_id[g.local_id] = cat.id

    assignment_local_to_id: dict[str, str] = {}
    quiz_local_to_id: dict[str, str] = {}
    lesson_page_local_to_id: dict[str, str] = {}
    workshop_local_to_id: dict[str, str] = {}
    workshop_dimension_local_to_id: dict[str, str] = {}

    for section_data in export.sections:
        section = Section(course_id=course.id, title=section_data.title, summary=section_data.summary,
                           sort_order=section_data.sort_order + sort_order_offset, is_visible=section_data.is_visible)
        db.add(section)
        db.flush()

        for r in section_data.resources:
            resource = Resource(
                section_id=section.id, resource_type=r.resource_type, title=r.title, description=r.description,
                external_url=r.external_url, page_content=r.page_content, sort_order=r.sort_order, is_visible=r.is_visible,
            )
            db.add(resource)
            if r.files_meta:
                warnings.append(f"Ressource « {r.title} » : {len(r.files_meta)} fichier(s) non transféré(s), à réuploader manuellement")

        for a in section_data.assignments:
            assignment = Assignment(section_id=section.id, **a.model_dump(exclude={"local_id"}))
            db.add(assignment)
            db.flush()
            assignment_local_to_id[a.local_id] = assignment.id
            # Réutilise le même effet de bord que RAssignments.py::create_assignment
            db.add(GradeItem(course_id=course.id, assignment_id=assignment.id, kind=GradeItemKind.assignment))

        for q in section_data.quizzes:
            quiz = Quiz(
                section_id=section.id, title=q.title, description=q.description,
                time_limit_minutes=q.time_limit_minutes, max_attempts=q.max_attempts,
                shuffle_questions=q.shuffle_questions, opens_at=q.opens_at, closes_at=q.closes_at, is_visible=q.is_visible,
            )
            db.add(quiz)
            db.flush()
            quiz_local_to_id[q.local_id] = quiz.id
            db.add(GradeItem(course_id=course.id, quiz_id=quiz.id, kind=GradeItemKind.quiz))

            for qq in q.quiz_questions:
                if qq.question_ref not in question_local_to_id:
                    warnings.append(f"Quiz « {q.title} » : question référencée introuvable, ignorée")
                    continue
                db.add(QuizQuestion(quiz_id=quiz.id, question_id=question_local_to_id[qq.question_ref], points=qq.points, sort_order=qq.sort_order))

            for rule in q.draw_rules:
                if rule.category_ref not in category_local_to_id:
                    warnings.append(f"Quiz « {q.title} » : catégorie de tirage introuvable, ignorée")
                    continue
                db.add(QuizDrawRule(quiz_id=quiz.id, category_id=category_local_to_id[rule.category_ref],
                                     question_type=rule.question_type, count=rule.count, points=rule.points, sort_order=rule.sort_order))

        for f in section_data.forums:
            db.add(Forum(section_id=section.id, title=f.title, description=f.description, is_visible=f.is_visible, group_mode=f.group_mode))

        for c in section_data.choices:
            choice = Choice(
                section_id=section.id, title=c.title, description=c.description, is_visible=c.is_visible,
                allow_multiple=c.allow_multiple, allow_update=c.allow_update, limit_answers=c.limit_answers,
                results_display=c.results_display, anonymous_results=c.anonymous_results,
                show_unanswered=c.show_unanswered, opens_at=c.opens_at, closes_at=c.closes_at, group_mode=c.group_mode,
            )
            db.add(choice)
            db.flush()
            for o in c.options:
                db.add(ChoiceOption(choice_id=choice.id, option_text=o.option_text, max_answers=o.max_answers, sort_order=o.sort_order))

        for g in section_data.glossaries:
            db.add(Glossary(
                section_id=section.id, title=g.title, description=g.description, is_visible=g.is_visible,
                is_main=g.is_main, allow_student_entries=g.allow_student_entries,
                require_approval=g.require_approval, allow_duplicates=g.allow_duplicates,
            ))

        for w in section_data.wikis:
            # La sous-wiki partagée/individuelle est créée paresseusement
            # au premier accès (RWikis.py::_get_or_create_subwiki) — pas
            # besoin de la répliquer ici (voir plan Épic 16).
            db.add(Wiki(section_id=section.id, title=w.title, description=w.description, is_visible=w.is_visible,
                        mode=w.mode, first_page_title=w.first_page_title))

        for lesson_data in section_data.lessons:
            lesson = Lesson(
                section_id=section.id, title=lesson_data.title, description=lesson_data.description,
                is_visible=lesson_data.is_visible, password=lesson_data.password,
                max_attempts_per_question=lesson_data.max_attempts_per_question,
                time_limit_minutes=lesson_data.time_limit_minutes, allow_retake=lesson_data.allow_retake,
            )
            db.add(lesson)
            db.flush()

            page_local_to_id: dict[str, str] = {}
            for p in lesson_data.pages:
                page = LessonPage(lesson_id=lesson.id, page_type=p.page_type, title=p.title, content=p.content,
                                   points=p.points, sort_order=p.sort_order)
                db.add(page)
                db.flush()
                page_local_to_id[p.local_id] = page.id
                lesson_page_local_to_id[p.local_id] = page.id
            # 2e passe : les sauts peuvent référencer une page suivante,
            # doivent toutes exister d'abord (même raison que les
            # références de quiz/tirage, mais ici à l'intérieur d'une
            # même leçon).
            for p in lesson_data.pages:
                for ans in p.answers:
                    jump_to_id = page_local_to_id.get(ans.jump_to_page_ref) if ans.jump_to_page_ref else None
                    db.add(LessonAnswer(
                        page_id=page_local_to_id[p.local_id], answer_text=ans.answer_text, is_correct=ans.is_correct,
                        tolerance=ans.tolerance, jump_type=ans.jump_type, jump_to_page_id=jump_to_id, sort_order=ans.sort_order,
                    ))

        for ws_data in section_data.workshops:
            workshop = Workshop(
                section_id=section.id, title=ws_data.title, description=ws_data.description, is_visible=ws_data.is_visible,
                grade=ws_data.grade, gradinggrade=ws_data.gradinggrade, strategy=ws_data.strategy,
                use_peer_assessment=ws_data.use_peer_assessment, use_self_assessment=ws_data.use_self_assessment,
                comparison=ws_data.comparison,
            )
            db.add(workshop)
            db.flush()
            workshop_local_to_id[ws_data.local_id] = workshop.id
            db.add(GradeItem(course_id=course.id, workshop_id=workshop.id, kind=GradeItemKind.workshop_submission))
            db.add(GradeItem(course_id=course.id, workshop_id=workshop.id, kind=GradeItemKind.workshop_grading))

            for d in ws_data.dimensions:
                dimension = WorkshopDimension(workshop_id=workshop.id, sort_order=d.sort_order, description=d.description,
                                               grade=d.grade, weight=d.weight, label_no=d.label_no, label_yes=d.label_yes)
                db.add(dimension)
                db.flush()
                workshop_dimension_local_to_id[d.local_id] = dimension.id
                for lvl in d.levels:
                    db.add(WorkshopRubricLevel(dimension_id=dimension.id, grade=lvl.grade, definition=lvl.definition, sort_order=lvl.sort_order))

            for row in ws_data.numerrors_map:
                db.add(WorkshopNumerrorsMap(workshop_id=workshop.id, error_count=row.error_count, grade_percent=row.grade_percent))

    manual_item_local_to_id: dict[str, str] = {}
    for item in export.grade_items_manual:
        gi = GradeItem(
            course_id=course.id, kind=GradeItemKind.manual, title=item.title, max_points=item.max_points,
            grade_category_id=grade_category_local_to_id.get(item.grade_category_ref) if item.grade_category_ref else None,
            sort_order=item.sort_order,
        )
        db.add(gi)
        db.flush()
        manual_item_local_to_id[item.local_id] = gi.id

    db.commit()

    if export.student_data:
        _import_student_data(
            db, export.student_data, warnings,
            assignment_local_to_id, quiz_local_to_id, question_local_to_id,
            manual_item_local_to_id, workshop_local_to_id, workshop_dimension_local_to_id,
            course.id,
        )

    db.refresh(course)
    return CourseImportResult(course=CourseOut.model_validate(course).model_dump(mode="json"), warnings=warnings)


def _import_student_data(
    db, student_data: StudentData, warnings: list[str],
    assignment_local_to_id, quiz_local_to_id, question_local_to_id,
    manual_item_local_to_id, workshop_local_to_id, workshop_dimension_local_to_id,
    course_id: str,
):
    email_cache: dict[str, str | None] = {}
    enrolled_ids: set[str] = set()

    def resolve_student(email: str) -> str | None:
        if email not in email_cache:
            u = db.query(User).filter(User.email == email).first()
            email_cache[email] = u.id if u else None
        student_id = email_cache[email]
        if student_id is not None and student_id not in enrolled_ids:
            enrolled_ids.add(student_id)
            exists = db.query(Enrollment).filter(Enrollment.course_id == course_id, Enrollment.user_id == student_id).first()
            if exists is None:
                db.add(Enrollment(course_id=course_id, user_id=student_id, role_in_course=CourseRole.student))
                db.flush()
        return student_id

    for s in student_data.submissions:
        assignment_id = assignment_local_to_id.get(s.assignment_ref)
        student_id = resolve_student(s.student_email)
        if assignment_id is None:
            continue
        if student_id is None:
            warnings.append(f"Soumission de {s.student_email} : aucun compte trouvé, ignorée")
            continue
        db.add(Submission(assignment_id=assignment_id, student_id=student_id, submitted_text=s.submitted_text,
                           status=s.status, grade=s.grade, feedback=s.feedback, submitted_at=s.submitted_at, graded_at=s.graded_at))
        if s.has_file:
            warnings.append(f"Soumission de {s.student_email} : pièce jointe non transférée, à réuploader manuellement")

    for att in student_data.quiz_attempts:
        quiz_id = quiz_local_to_id.get(att.quiz_ref)
        student_id = resolve_student(att.student_email)
        if quiz_id is None:
            continue
        if student_id is None:
            warnings.append(f"Tentative de quiz de {att.student_email} : aucun compte trouvé, ignorée")
            continue
        attempt = QuizAttempt(quiz_id=quiz_id, student_id=student_id, status=att.status, score=att.score,
                               max_score=att.max_score, started_at=att.started_at, submitted_at=att.submitted_at, graded_at=att.graded_at)
        db.add(attempt)
        db.flush()
        for r in att.responses:
            question_id = question_local_to_id.get(r.question_ref)
            if question_id is None:
                continue
            db.add(QuizResponse(attempt_id=attempt.id, question_id=question_id, points=r.points, answer_data=r.answer_data,
                                 is_correct=r.is_correct, points_awarded=r.points_awarded, feedback=r.feedback))

    for mg in student_data.manual_grades:
        grade_item_id = manual_item_local_to_id.get(mg.grade_item_ref)
        student_id = resolve_student(mg.student_email)
        if grade_item_id is None:
            continue
        if student_id is None:
            warnings.append(f"Note manuelle de {mg.student_email} : aucun compte trouvé, ignorée")
            continue
        db.add(ManualGrade(grade_item_id=grade_item_id, student_id=student_id, points=mg.points, feedback=mg.feedback))

    completion_maps = {
        CompletionItemType.assignment: assignment_local_to_id,
        CompletionItemType.quiz: quiz_local_to_id,
        CompletionItemType.workshop: workshop_local_to_id,
    }
    for c in student_data.completions:
        id_map = completion_maps.get(c.item_type, {})
        item_id = id_map.get(c.item_ref)
        student_id = resolve_student(c.student_email)
        if item_id is None or student_id is None:
            continue
        db.add(ActivityCompletion(student_id=student_id, item_type=c.item_type, item_id=item_id, completed_at=c.completed_at or datetime.now(timezone.utc)))

    for sub in student_data.workshop_submissions:
        workshop_id = workshop_local_to_id.get(sub.workshop_ref)
        author_id = resolve_student(sub.author_email)
        if workshop_id is None:
            continue
        if author_id is None:
            warnings.append(f"Soumission d'atelier de {sub.author_email} : aucun compte trouvé, ignorée")
            continue
        submission = WorkshopSubmission(workshop_id=workshop_id, author_id=author_id, title=sub.title, content=sub.content,
                                         grade_override=sub.grade_override, feedback_author=sub.feedback_author,
                                         published=sub.published, late=sub.late)
        db.add(submission)
        db.flush()
        if sub.has_file:
            warnings.append(f"Soumission d'atelier de {sub.author_email} : pièce jointe non transférée, à réuploader manuellement")

        dim_map = workshop_dimension_local_to_id
        for a in sub.assessments:
            reviewer_id = resolve_student(a.reviewer_email)
            if reviewer_id is None:
                warnings.append(f"Évaluation d'atelier par {a.reviewer_email} : aucun compte trouvé, ignorée")
                continue
            assessment = WorkshopAssessment(submission_id=submission.id, reviewer_id=reviewer_id, weight=a.weight,
                                             gradinggrade_override=a.gradinggrade_override, feedback_author=a.feedback_author,
                                             feedback_reviewer=a.feedback_reviewer)
            db.add(assessment)
            db.flush()
            for g in a.grades:
                dimension_id = dim_map.get(g.dimension_ref)
                if dimension_id is None:
                    continue
                db.add(WorkshopGrade(assessment_id=assessment.id, dimension_id=dimension_id, grade=g.grade, peer_comment=g.peer_comment))

    db.commit()
