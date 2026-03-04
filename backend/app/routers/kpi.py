from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.base import get_db
from app.models import Cage, Site
from app.routers.auth import get_current_user
from app.models.user import User
from app.schemas.kpi import SiteSummary, CageKPI, TodayTodoItem
from app.services.kpi import calc_cage_kpi, calc_today_todos

router = APIRouter(prefix="/kpi", tags=["kpi"])


@router.get("/summary", response_model=list[SiteSummary])
async def kpi_summary(
    site_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = select(Site)
    if site_id:
        q = q.where(Site.id == site_id)
    sites_result = await db.execute(q)
    sites = sites_result.scalars().all()

    summaries = []
    for site in sites:
        cages_result = await db.execute(
            select(Cage).where(Cage.site_id == site.id, Cage.is_active == True)
        )
        cages = cages_result.scalars().all()
        cage_kpis = [await calc_cage_kpi(c, db) for c in cages]
        total_biomass = sum(k.est_biomass_kg for k in cage_kpis)
        total_count = sum(k.est_count for k in cage_kpis)
        active_lots = len({k.lot_id for k in cage_kpis if k.lot_id})
        summaries.append(SiteSummary(
            site_id=site.id,
            site_name=site.name,
            total_biomass_kg=round(total_biomass, 1),
            total_est_count=total_count,
            cage_count=len(cages),
            active_lot_count=active_lots,
            cages=cage_kpis,
        ))
    return summaries


@router.get("/cage/{cage_id}", response_model=CageKPI)
async def kpi_cage(
    cage_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(Cage).where(Cage.id == cage_id))
    cage = result.scalar_one_or_none()
    if not cage:
        from fastapi import HTTPException
        raise HTTPException(404, "生簀が見つかりません")
    return await calc_cage_kpi(cage, db)


@router.get("/today/todos", response_model=list[TodayTodoItem])
async def today_todos(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await calc_today_todos(db)
