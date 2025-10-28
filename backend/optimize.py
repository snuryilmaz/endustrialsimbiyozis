import math

def get_new_coordinates(existing_coords, num_new_firms):
    center_lat = sum([coord[0] for coord in existing_coords]) / len(existing_coords)
    center_lon = sum([coord[1] for coord in existing_coords]) / len(existing_coords)
    radius = 0.03
    angle_step = 2 * math.pi / num_new_firms
    new_coords = []
    for i in range(num_new_firms):
        angle = i * angle_step
        new_lat = center_lat + radius * math.sin(angle)
        new_lon = center_lon + radius * math.cos(angle)
        new_coords.append((new_lat, new_lon))
    return new_coords

def optimize_waste_allocation(firmalar, atik_turu, talep_miktari):
    uygunlar = []
    for f_adi, f_bilgi in firmalar.items():
        if f_bilgi.get("atik") == atik_turu and f_bilgi.get("miktar", 0) > 0:
            uygunlar.append({
                "Firma": f_adi,
                "Fiyat": f_bilgi["fiyat"],
                "Miktar": f_bilgi["miktar"]
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
