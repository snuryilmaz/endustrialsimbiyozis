from fastapi import APIRouter
from backend.models import Firma

router = APIRouter()

# Örnek veri (ileride veritabanına geçeceğiz)
varsayilan_firmalar = [
    Firma("Firma 1", "Demir-Çelik", "Metal Talaşı", 5, 100, 7),
    Firma("Firma 2", "Demir-Çelik", "Çelik Parçaları", 4, 200, 5),
    # Diğer firmalar...
]

@router.get("/firmalar")
def get_firmalar():
    return [
        {
            "ad": f.ad,
            "sektor": f.sektor,
            "atik": f.atik,
            "fiyat": f.fiyat,
            "miktar": f.miktar,
            "lead_time_days": f.lead_time_days
        }
        for f in varsayilan_firmalar
    ]
