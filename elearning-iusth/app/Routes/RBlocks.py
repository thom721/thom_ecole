from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.Models.MBlock import UserBlockInstance, BlockRegion
from app.Models.MUser import User
from app.Schemas.SBlock import BlockCreate, BlockUpdate, BlockReorderIn, BlockOut
from app.dependencies.auth import get_current_active_user
from app.Helper.blocks import compute_block_data

router = APIRouter(prefix="/blocks", tags=["blocks"])


def _to_out(db: Session, block: UserBlockInstance, current_user: User) -> BlockOut:
    return BlockOut(
        id=block.id, block_type=block.block_type, region=block.region,
        weight=block.weight, is_visible=block.is_visible,
        data=compute_block_data(db, block, current_user),
    )


@router.get("/mine", response_model=list[BlockOut])
def list_my_blocks(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    blocks = (
        db.query(UserBlockInstance)
        .filter(UserBlockInstance.user_id == current_user.id)
        .order_by(UserBlockInstance.region, UserBlockInstance.weight)
        .all()
    )
    return [_to_out(db, b, current_user) for b in blocks]


@router.post("/mine", response_model=BlockOut, status_code=status.HTTP_201_CREATED)
def add_block(
    data: BlockCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    max_weight = (
        db.query(UserBlockInstance)
        .filter(UserBlockInstance.user_id == current_user.id, UserBlockInstance.region == data.region)
        .count()
    )
    block = UserBlockInstance(
        user_id=current_user.id, block_type=data.block_type, region=data.region,
        weight=max_weight, config_json=data.config_json,
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return _to_out(db, block, current_user)


def _get_block_or_404(db: Session, current_user: User, block_id: str) -> UserBlockInstance:
    block = db.query(UserBlockInstance).filter(UserBlockInstance.id == block_id).first()
    if block is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bloc introuvable")
    if block.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ce bloc ne vous appartient pas")
    return block


@router.post("/mine/reorder", status_code=status.HTTP_204_NO_CONTENT)
def reorder_blocks(
    data: BlockReorderIn,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    for weight, block_id in enumerate(data.ordered_ids):
        block = db.query(UserBlockInstance).filter(UserBlockInstance.id == block_id, UserBlockInstance.user_id == current_user.id).first()
        if block is None:
            continue
        block.region = data.region
        block.weight = weight
    db.commit()


@router.patch("/mine/{block_id}", response_model=BlockOut)
def update_block(
    block_id: str, data: BlockUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    block = _get_block_or_404(db, current_user, block_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(block, field, value)
    db.commit()
    db.refresh(block)
    return _to_out(db, block, current_user)


@router.delete("/mine/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(
    block_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    block = _get_block_or_404(db, current_user, block_id)
    db.delete(block)
    db.commit()
