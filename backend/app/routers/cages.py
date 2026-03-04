from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import io
import qrcode

from app.db.base import get_db
from app.models import Cage, CageLot, Lot
from app.routers.auth import get_current_user
from app.models.user import User
from app.schemas.cage import CageCreate, CagePatch, CageOut

router = APIRouter(tags=["cages"])


@router.get("/cages", response_model=list[CageOut])
async def list_cages(
    site_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Cage)
    if site_id:
        q = q.where(Cage.site_id == site_id)
    q = q.order_by(Cage.id)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/cages/{cage_id}", response_model=CageOut)
async def get_cage(
    cage_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Cage).where(Cage.id == cage_id))
    cage = result.scalar_one_or_none()
    if not cage:
        raise HTTPException(404, "生簀が見つかりません")
    return cage


@router.post("/cages", response_model=CageOut, status_code=201)
async def create_cage(
    body: CageCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    cage = Cage(**body.model_dump())
    db.add(cage)
    await db.commit()
    await db.refresh(cage)
    return cage


@router.patch("/cages/{cage_id}", response_model=CageOut)
async def patch_cage(
    cage_id: int,
    body: CagePatch,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Cage).where(Cage.id == cage_id))
    cage = result.scalar_one_or_none()
    if not cage:
        raise HTTPException(404, "生簀が見つかりません")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(cage, field, value)
    await db.commit()
    await db.refresh(cage)
    return cage


@router.get("/cages/{cage_id}/qr")
async def get_cage_qr(
    cage_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Cage).where(Cage.id == cage_id))
    cage = result.scalar_one_or_none()
    if not cage:
        raise HTTPException(404, "生簀が見つかりません")
    url = f"/qr/{cage.qr_token}"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.get("/qr/{token}")
async def get_cage_by_qr(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """QRトークンから生簀情報を取得（認証不要 - モバイルスキャン用）"""
    result = await db.execute(select(Cage).where(Cage.qr_token == token))
    cage = result.scalar_one_or_none()
    if not cage:
        raise HTTPException(404, "QRコードが無効です")
    return {"cage_id": cage.id, "redirect": f"/cages/{cage.id}"}
