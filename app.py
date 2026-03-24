import streamlit as st
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Gelişmiş İnfaz Sistemi v2", layout="wide")

# --- TCK MADDE VE ORAN SÖZLÜĞÜ ---
# Bu liste hukuk sistemindeki temel oranlara göre hazırlanmıştır
TCK_MADDELERI = {
    "Genel Suçlar (Hırsızlık, Yaralama vb.)": 0.5,           # 1/2
    "Kasten Öldürme (TCK 81, 82)": 0.666,                  # 2/3
    "Cinsel Dokunulmazlık (TCK 102, 103, 104, 105)": 0.75, # 3/4
    "Uyuşturucu Ticareti (TCK 188)": 0.75,                 # 3/4
    "Terör Suçları (3713 S.K.)": 0.75,                     # 3/4
    "Örgütlü Suçlar": 0.666,                               # 2/3
    "Devletin Güvenliğine Karşı Suçlar": 0.75              # 3/4
}

st.title("⚖️ İnfaz Hesaplama ve Denetim Takip Sistemi")
st.caption("bu site taslak olarak  Halil Yavuz tarafından hazırlanmıştır, geliştirme aşamasındadır. ")

# --- GİRİŞ PANELİ ---
with st.sidebar:
    st.header("📋 Dosya Bilgileri")
    suc_maddesi = st.selectbox("Suç Maddesi / Tipi", list(TCK_MADDELERI.keys()))
    mukerrir_durumu = st.selectbox("Mükerrirlik Durumu", 
                                  ["Yok", "1. Kez Mükerrir (1/3 İndirim)", "2. Kez Mükerrir (1/4 İndirim)"])
    
    st.divider()
    suc_tarihi = st.date_input("Suç Tarihi", date(2023, 1, 1))
    dogum_tarihi = st.date_input("Doğum Tarihi", date(1990, 1, 1))
    giris_tarihi = st.date_input("Cezaevi Giriş Tarihi", date.today())
    
    st.divider()
    st.write("**İlam Olunan Ceza**")
    c_yil = st.number_input("Yıl", 0)
    c_ay = st.number_input("Ay", 0)
    c_gun = st.number_input("Gün", 0)
    
    st.divider()
    mahsup = st.number_input("Mahsup Edilecek Süre (Gün)", 0)
    mahsup_denetim = st.number_input("Mahsup Denetim (Gün)", 0)

# --- HESAPLAMA ÇEKİRDEĞİ ---

# 1. Oran Belirleme Mantığı
# Öncelik mükerrirlik durumundadır
if mukerrir_durumu == "1. Kez Mükerrir (1/3 İndirim)":
    final_oran = 0.666  # 2/3 oranında yatış
    oran_etiket = "2/3 (Mükerrir)"
elif mukerrir_durumu == "2. Kez Mükerrir (1/4 İndirim)":
    final_oran = 0.75   # 3/4 oranında yatış
    oran_etiket = "3/4 (2. Kez Mükerrir)"
else:
    final_oran = TCK_MADDELERI[suc_maddesi]
    oran_etiket = f"{'1/2' if final_oran == 0.5 else '2/3' if final_oran == 0.666 else '3/4'}"

# 2. Toplam Ceza ve Yatılacak Süre
toplam_gun = (c_yil * 365) + (c_ay * 30) + c_gun
yatilacak_net_gun = int(toplam_gun * final_oran) - mahsup

# 3. Tarih Hesaplamaları
bihakkin = giris_tarihi + relativedelta(years=c_yil, months=c_ay, days=c_gun) - relativedelta(days=mahsup)
kosullu = giris_tarihi + relativedelta(days=yatilacak_net_gun)

# 4. 2023 ve 2025 Özel Durumları
yeni_duzenleme_2025 = suc_tarihi >= date(2025, 6, 4)
eski_suc_2023 = suc_tarihi < date(2023, 7, 31)

# --- GÖRSEL SONUÇ EKRANI ---
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Uygulanan İnfaz Oranı", oran_etiket)
    st.write(f"**Toplam Ceza:** {toplam_gun} Gün")

with col2:
    st.success(f"**Şartla Tahliye:** {kosullu.strftime('%d.%m.%Y')}")
    st.write(f"**Net Yatış:** {yatilacak_net_gun} Gün")

with col3:
    st.error(f"**Bihakkın Tahliye:** {bihakkin.strftime('%d.%m.%Y')}")

st.divider()

# --- DENETİMLİ SERBESTLİK MANTIĞI ---
st.subheader("🏁 Denetimli Serbestlik ve Tahliye Planı")

denetim_notlari = []
if eski_suc_2023:
    denetim_yil = 4 # 1+3 kuralı
    denetim_tarihi = kosullu - relativedelta(years=4)
    denetim_notlari.append("📢 31/07/2023 öncesi suç: 1+3 yıl denetim hakkı mevcuttur (1 ay kapalı - 3 ay açık şartıyla).")
elif yeni_duzenleme_2025:
    on_birde_bir = int(yatilacak_net_gun / 10)
    denetim_tarihi = giris_tarihi + relativedelta(days=on_birde_bir)
    denetim_notlari.append(f"📢 2025 Düzenlemesi: İnfazın 1/10'u ({on_birde_bir} gün) bitince denetim başlar.")
else:
    denetim_tarihi = kosullu - relativedelta(years=1) - relativedelta(days=mahsup_denetim)
    denetim_notlari.append("📢 Standart denetim süresi (1 yıl) uygulanmıştır.")

st.info(f"📅 **Tahmini Denetim Başlangıç Tarihi:** {denetim_tarihi.strftime('%d.%m.%Y')}")

for not_ in denetim_notlari:
    st.warning(not_)
