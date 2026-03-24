import streamlit as st
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Sayfa yapılandırması
st.set_page_config(page_title="İnfaz Hesaplama Aracı", page_icon="⚖️")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2e4053; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ İnfaz ve Tahliye Hesaplama Sistemi")
st.info("Excel tablonuzdaki standart hesaplama mantığına göre uyarlanmıştır.")

# Giriş Bölümü
with st.expander("📝 Veri Girişi", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        giris_tarihi = st.date_input("Cezaevi Giriş Tarihi", datetime.now())
        oran = st.selectbox("İnfaz Oranı", ["1/2", "2/3", "3/4", "1/1"])
    with c2:
        st.write("Toplam Ceza Süresi")
        y, a, g = st.columns(3)
        yil = y.number_input("Yıl", 0)
        ay = a.number_input("Ay", 0)
        gun = g.number_input("Gün", 0)

mahsup = st.number_input("Mahsup Edilecek Gün (Gözaltı vb.)", 0)

# Hesaplama
if st.button("Hesaplamayı Başlat"):
    # Mantıksal hesaplamalar
    oran_val = {"1/2": 0.5, "2/3": 0.666, "3/4": 0.75, "1/1": 1.0}[oran]
    
    # Bihakkın Tahliye
    bihakkin = giris_tarihi + relativedelta(years=yil, months=ay, days=gun) - timedelta(days=mahsup)
    
    # Koşullu Salıverilme (Yargısal hesap: 1 ay = 30 gün kabulüyle veya takvimle)
    toplam_gun = (yil * 365) + (ay * 30) + gun
    yatilacak_gun = int(toplam_gun * oran_val) - mahsup
    kosullu = giris_tarihi + timedelta(days=yatilacak_gun)

    # Sonuç Paneli
    st.success("### Hesaplama Sonuçları")
    res1, res2 = st.columns(2)
    res1.metric("Bihakkın Tahliye", bihakkin.strftime("%d.%m.%Y"))
    res2.metric("Şartla Tahliye", kosullu.strftime("%d.%m.%Y"))
    
    st.write(f"👉 **Toplam Yatılacak Süre:** {yatilacak_gun} gün")
    
    # Yazdırma Notu
    st.caption("Not: Bu hesaplama bilgilendirme amaçlıdır. Resmi işlemlerde ilamdaki süreler esastır.")  
