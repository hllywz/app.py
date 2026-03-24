import streamlit as st
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from fpdf import FPDF

st.set_page_config(page_title="Hukuk Otomasyon: İnfaz", layout="wide")

# --- TCK VE ORAN SÖZLÜĞÜ ---
TCK_MADDELERI = {
    "Genel Suçlar (Hırsızlık, Yaralama vb.)": 0.5,
    "Kasten Öldürme (TCK 81, 82)": 0.666,
    "Cinsel Dokunulmazlık (TCK 102, 103, 104, 105)": 0.75,
    "Uyuşturucu Ticareti (TCK 188)": 0.75,
    "Terör Suçları (3713 S.K.)": 0.75,
    "Örgütlü Suçlar": 0.666
}

st.title("⚖️  İnfaz Müddetname Sistemi PRO")
st.markdown("---")

# --- GİRİŞ PANELİ ---
with st.sidebar:
    st.header("📋 Dosya Parametreleri")
    suc_maddesi = st.selectbox("Suç Tipi", list(TCK_MADDELERI.keys()))
    mukerrir = st.selectbox("Mükerrirlik", ["Yok", "1. Kez Mükerrir", "2. Kez Mükerrir"])
    
    st.divider()
    suc_tarihi = st.date_input("Suç Tarihi", date(2025, 6, 5))
    giris_tarihi = st.date_input("Cezaevi Giriş Tarihi", date.today())
    
    st.divider()
    st.write("**İlam Cezası**")
    y, a, g = st.columns(3)
    c_yil = y.number_input("Yıl", 0)
    c_ay = a.number_input("Ay", 0)
    c_gun = g.number_input("Gün", 0)
    
    st.divider()
    st.write("**Mahsup Edilecek Süreler (Gün)**")
    mahsup_12_15 = st.number_input("12-15 Yaş Arası (3x)", 0)
    mahsup_15_18 = st.number_input("15-18 Yaş Arası (2x)", 0)
    mahsup_18_ustu = st.number_input("18+ Yaş (1x)", 0)

# --- MATEMATİKSEL HESAPLAMA ---

# 1. Mahsup Çarpan Mantığı
toplam_mahsup_gun = (mahsup_12_15 * 3) + (mahsup_15_18 * 2) + mahsup_18_ustu

# 2. İnfaz Oranı
if mukerrir == "1. Kez Mükerrir":
    infaz_orani = 0.666
    oran_text = "2/3 (Mükerrir)"
elif mukerrir == "2. Kez Mükerrir":
    infaz_orani = 0.75
    oran_text = "3/4 (2. Kez Mükerrir)"
else:
    infaz_orani = TCK_MADDELERI[suc_maddesi]
    oran_text = f"{'1/2' if infaz_orani == 0.5 else '2/3' if infaz_orani == 0.666 else '3/4'}"

# 3. Süre ve Tarih Hesaplama
toplam_ceza_gun = (c_yil * 365) + (c_ay * 30) + c_gun
indirimli_ceza_gun = int(toplam_ceza_gun * infaz_orani)

bihakkin = giris_tarihi + relativedelta(years=c_yil, months=c_ay, days=c_gun) - relativedelta(days=toplam_mahsup_gun)
kosullu = giris_tarihi + relativedelta(days=indirimli_ceza_gun) - relativedelta(days=toplam_mahsup_gun)

# 4. Denetim ve 1/10 Kuralı
denetim_yil = 4 if suc_tarihi < date(2023, 7, 31) else 1
min_yatis_tarihi = giris_tarihi # Varsayılan
if suc_tarihi >= date(2025, 6, 4):
    min_yatis_tarihi = giris_tarihi + relativedelta(days=int(indirimli_ceza_gun / 10))

tahliye_tarihi = max(kosullu - relativedelta(years=denetim_yil), min_yatis_tarihi)

# --- GÖRSEL SONUÇLAR ---
c1, c2, c3 = st.columns(3)
c1.metric("Uygulanan İnfaz Oranı", oran_text)
c2.success(f"Şartla Tahliye: {kosullu.strftime('%d.%m.%Y')}")
c3.error(f"Bihakkın Tahliye: {bihakkin.strftime('%d.%m.%Y')}")

st.divider()
st.subheader(f"🏁 Tahliye/Denetim Tarihi: {tahliye_tarihi.strftime('%d.%m.%Y')}")
st.write(f"*(Toplam Mahsup Etkisi: {toplam_mahsup_gun} gün)*")

# --- PDF İÇİN TÜRKÇE KARAKTER TEMİZLEME (Hata önleyici) ---
def tr_fix(text):
    # Standart PDF fontları Türkçe karakterlerde hata verebilir.
    # Bu fonksiyon karakterleri güvenli karşılıklarına çevirir.
    mapping = str.maketrans("ığüşöçİĞÜŞÖÇ", "igusocIGUSOC")
    return str(text).translate(mapping)

# --- PDF OLUŞTURMA FONKSİYONU ---
def generate_pdf():
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Font ayarı (Standart fontlar kullanılır)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(190, 10, "INFAZ MUDDETNAME TASLAGI", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Helvetica", size=12)
        # Verileri Türkçe karakter hatasından arındırarak yazdırıyoruz
        pdf.cell(100, 10, f"Suc Tarihi: {suc_tarihi}")
        pdf.ln(8)
        pdf.cell(100, 10, f"Giris Tarihi: {giris_tarihi}")
        pdf.ln(8)
        pdf.cell(100, 10, f"Toplam Ceza: {c_yil} Yil {c_ay} Ay {c_gun} Gun")
        pdf.ln(8)
        pdf.cell(100, 10, tr_fix(f"Infaz Orani: {oran_text}"))
        
        pdf.ln(15)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(100, 10, f"Sartla Tahliye: {kosullu.strftime('%d.%m.%Y')}")
        pdf.ln(8)
        pdf.cell(100, 10, f"Bihakkin Tahliye: {bihakkin.strftime('%d.%m.%Y')}")
        pdf.ln(8)
        pdf.cell(100, 10, f"Tahliye/Denetim Baslangic: {tahliye_tarihi.strftime('%d.%m.%Y')}")
        
        # ÇIKTIYI BYTES OLARAK AL (Kritik nokta)
        # fpdf2 kullanıyorsanız output() byte döner. 
        # Garanti olması için bytes() içine alıyoruz.
        pdf_bytes = pdf.output()
        if isinstance(pdf_bytes, str): # Eğer string dönerse (eski sürümse)
            pdf_bytes = pdf_bytes.encode('latin-1')
            
        return bytes(pdf_bytes)
    except Exception as e:
        return f"Hata oluştu: {str(e)}".encode('utf-8')

# --- PDF İNDİRME BUTONU ---
# Veriyi önce bir değişkene alıp sonra butona veriyoruz
pdf_data = generate_pdf()

st.download_button(
    label="📄 Müddetnameyi PDF Olarak İndir",
    data=pdf_data,
    file_name=f"muddetname_{datetime.now().strftime('%Y%m%d')}.pdf",
    mime="application/pdf"
)
