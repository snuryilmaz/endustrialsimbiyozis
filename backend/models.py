class Firma:
    def __init__(self, ad, sektor, atik, fiyat, miktar, lead_time_days):
        self.ad = ad
        self.sektor = sektor
        self.atik = atik
        self.fiyat = fiyat
        self.miktar = miktar
        self.lead_time_days = lead_time_days

class AtikTalep:
    def __init__(self, atik_turu, miktar):
        self.atik_turu = atik_turu
        self.miktar = miktar
