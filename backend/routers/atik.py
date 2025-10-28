from fastapi import APIRouter, Query
from backend.models import Firma
from backend.optimize import optimize_waste_allocation
from backend.routers.firma import varsayilan_firmalar

router = APIRouter()

@router.get("/optimize")
def optimize(atik_turu: str = Query(...), miktar: int = Query(...)):
    eslesmeler, toplam_maliyet, toplam_alinan = optimize_waste_allocation(
        varsayilan_firmalar, atik_turu, miktar
    )
    return {
        "eslesmeler": eslesmeler,
        "toplam_maliyet": toplam_maliyet,
        "toplam_alinan": toplam_alinan
    }
