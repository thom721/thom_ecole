from typing import Any

from pydantic import BaseModel

from app.Models.MBlock import BlockType, BlockRegion


class BlockCreate(BaseModel):
    block_type: BlockType
    region: BlockRegion = BlockRegion.side
    config_json: str | None = None


class BlockUpdate(BaseModel):
    region: BlockRegion | None = None
    weight: int | None = None
    is_visible: bool | None = None
    config_json: str | None = None


class BlockReorderIn(BaseModel):
    region: BlockRegion
    ordered_ids: list[str]


class BlockOut(BaseModel):
    id: str
    block_type: BlockType
    region: BlockRegion
    weight: int
    is_visible: bool
    data: dict[str, Any] = {}
