def optimize_waste_allocation(firmalar, atik_turu, talep_miktari):
    uygunlar = []
    for firma in firmalar:
        if firma.atik == atik_turu and firma.miktar > 0:
            uygunlar.append({
                "Firma": firma.ad,
                "Fiyat": firma.fiyat,
                "Miktar": firma.miktar
            })
    uygunlar.sort(key=lambda x: x["Fiyat"])
    kalan = talep_miktari
    toplam_maliyet = 0
    toplam_alinan = 0
    eslesmeler = []
    for u in uygunlar:
        alinacak = min(u["Miktar"], kalan)
        if alinacak <= 0:
            continue
        toplam_maliyet += alinacak * u["Fiyat"]
        toplam_alinan += alinacak
        eslesmeler.append({
            "Gonderen": u["Firma"],
            "Alici": "Siz",
            "Miktar": alinacak,
            "Fiyat (TL/kg)": u["Fiyat"],
            "Tutar": alinacak * u["Fiyat"]
        })
        kalan -= alinacak
        if kalan <= 0:
            break
    if toplam_alinan == 0:
        return None, 0, 0
    return eslesmeler, toplam_maliyet, toplam_alinan
