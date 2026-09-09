from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.Models.MScale import Scale
from app.Models.MCompletion import ActivityCompletion, CompletionItemType
from app.Models.MCompetency import (
    Competency, ModuleCompetency, UserCompetency, UserCompetencyCourse, CompetencyEvidence,
    CompetencyRuleType, CompetencyRuleOutcome, EvidenceAction,
)


def resolve_scale(db: Session, competency: Competency) -> Scale | None:
    if competency.scale_id:
        return db.query(Scale).filter(Scale.id == competency.scale_id).first()
    return db.query(Scale).filter(Scale.id == competency.framework.scale_id).first()


def set_grade(
    db: Session, student_id: str, competency: Competency, course_id: str | None,
    grade_rank: int, actor_id: str | None, action: EvidenceAction, note: str | None = None,
) -> None:
    """Met à jour l'état PAR COURS et GLOBAL en une seule passe
    (simplification assumée par rapport à la cascade conditionnelle
    réelle de Moodle, voir plan Épic 13). Ajoute une preuve d'audit,
    toujours rattachée à l'enregistrement global."""
    proficient = competency.proficient_min_rank is not None and grade_rank >= competency.proficient_min_rank

    user_competency = db.query(UserCompetency).filter(
        UserCompetency.user_id == student_id, UserCompetency.competency_id == competency.id,
    ).first()
    if user_competency is None:
        user_competency = UserCompetency(user_id=student_id, competency_id=competency.id)
        db.add(user_competency)
        db.flush()
    user_competency.grade_rank = grade_rank
    user_competency.proficiency = proficient
    user_competency.updated_at = datetime.now(timezone.utc)

    if course_id:
        ucc = db.query(UserCompetencyCourse).filter(
            UserCompetencyCourse.user_id == student_id, UserCompetencyCourse.course_id == course_id,
            UserCompetencyCourse.competency_id == competency.id,
        ).first()
        if ucc is None:
            ucc = UserCompetencyCourse(user_id=student_id, course_id=course_id, competency_id=competency.id)
            db.add(ucc)
        ucc.grade_rank = grade_rank
        ucc.proficiency = proficient
        ucc.updated_at = datetime.now(timezone.utc)

    db.add(CompetencyEvidence(
        user_competency_id=user_competency.id, action=action, actor_id=actor_id,
        note=note, grade_rank=grade_rank,
    ))
    db.commit()


def evaluate_competencies_for_activity_completion(
    db: Session, student_id: str, course_id: str | None, item_type: CompletionItemType, item_id: str,
) -> None:
    """Point de déclenchement ciblé (voir plan Épic 13) — appelé depuis
    `mark_complete_if_absent`. Contrairement aux badges (Épic 12), l'item
    est déjà connu ici : requête directe sur les compétences liées à CET
    item précis, pas un balayage de tout le cours."""
    links = db.query(ModuleCompetency).filter(
        ModuleCompetency.item_type == item_type, ModuleCompetency.item_id == item_id,
    ).all()
    for link in links:
        competency = link.competency
        if competency.rule_type == CompetencyRuleType.none or competency.rule_outcome == CompetencyRuleOutcome.none:
            continue

        all_links = competency.module_links
        completed_keys = {
            (c.item_type, c.item_id)
            for c in db.query(ActivityCompletion).filter(ActivityCompletion.student_id == student_id).all()
        }
        results = [(l.item_type, l.item_id) in completed_keys for l in all_links]
        satisfied = all(results) if competency.rule_type == CompetencyRuleType.all else any(results)
        if not satisfied:
            continue

        if competency.rule_outcome == CompetencyRuleOutcome.evidence:
            user_competency = db.query(UserCompetency).filter(
                UserCompetency.user_id == student_id, UserCompetency.competency_id == competency.id,
            ).first()
            if user_competency is None:
                user_competency = UserCompetency(user_id=student_id, competency_id=competency.id)
                db.add(user_competency)
                db.commit()
            db.add(CompetencyEvidence(user_competency_id=user_competency.id, action=EvidenceAction.log, actor_id=None))
            db.commit()
        elif competency.rule_outcome == CompetencyRuleOutcome.complete:
            scale = resolve_scale(db, competency)
            if scale is None or not scale.levels:
                continue
            max_rank = max(lvl.rank for lvl in scale.levels)
            set_grade(db, student_id, competency, course_id, max_rank, actor_id=None, action=EvidenceAction.complete)
