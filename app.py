from pathlib import Path
import io
import unicodedata
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-Ticaret | RFM Yönetim Paneli", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>.stApp{background:#0b1220;color:#e5e7eb}section[data-testid='stSidebar']{background:#101b2f}div[data-testid='stMetric']{background:#17243b;border:1px solid #2b3d59;padding:16px;border-radius:14px}div[data-testid='stMetricLabel']{color:#a7b7ce}h1,h2,h3{letter-spacing:-.5px}div[data-testid='stDataFrame']{border-radius:12px;overflow:hidden}</style>""", unsafe_allow_html=True)
ROOT = Path(__file__).resolve().parent

def tr_sayi(sayi, basamak=0):
    return f"{sayi:,.{basamak}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def para(sayi):
    return f"{tr_sayi(sayi, 2)} TL"

def norm(metin):
    metin = str(metin).strip().casefold().replace("ı", "i")
    return "".join(x for x in unicodedata.normalize("NFKD", metin) if not unicodedata.combining(x) and x.isalnum())

def temiz_ad(deger, tur):
    eslesme = {
        "kategori": {"elektronik":"Elektronik","spor":"Spor","ofis":"Ofis","kozmetik":"Kozmetik","evveyasam":"Ev ve Yaşam","kitap":"Kitap"},
        "bolge": {"marmara":"Marmara","ege":"Ege","akdeniz":"Akdeniz","icanadolu":"İç Anadolu","karadeniz":"Karadeniz","doguanadolu":"Doğu Anadolu","guneydoguanadolu":"Güneydoğu Anadolu"}
    }
    if pd.isna(deger):
        return "Bilinmiyor"
    return eslesme.get(tur, {}).get(norm(deger), str(deger).strip())

@st.cache_data
def yukle():
    rfm = pd.read_csv(ROOT / "RFM_Musteri_Analizi.csv")
    segment = pd.read_csv(ROOT / "Musteri_Segment_Raporu.csv")
    ozet = pd.read_csv(ROOT / "Proje_Genel_Ozet.csv")
    ham = pd.read_csv(ROOT / "e_ticaret_veri_seti.csv")
    ham = ham.drop_duplicates().copy()
    ham["siparis_tarihi"] = pd.to_datetime(ham["siparis_tarihi"], errors="coerce")
    ham = ham.dropna(subset=["musteri_id", "siparis_id", "siparis_tarihi"])
    ham["toplam_tutar"] = pd.to_numeric(ham["toplam_tutar"], errors="coerce")
    ham["adet"] = pd.to_numeric(ham["adet"], errors="coerce")
    satis = ham[(ham["iade_durumu"].astype(str).str.strip().str.casefold() == "hayır") & (ham["toplam_tutar"] > 0)].copy()
    satis["kategori_analiz"] = satis["kategori"].map(lambda x: temiz_ad(x, "kategori"))
    satis["bolge_analiz"] = satis["bolge"].map(lambda x: temiz_ad(x, "bolge"))
    satis["sehir_analiz"] = satis["sehir"].astype(str).str.strip()
    satis["urun_analiz"] = satis["urun_adi"].astype(str).str.strip()
    satis["ay"] = satis["siparis_tarihi"].dt.to_period("M").astype(str)
    satis["yil"] = satis["siparis_tarihi"].dt.year.astype(str)
    return rfm, segment, ozet, satis, ham

def grafik(fig, anahtar):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=60,b=10), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True, key=anahtar)

def tablo(df, anahtar):
    st.dataframe(df, use_container_width=True, hide_index=True, key=anahtar)

def csv_indir(df, ad, etiket, anahtar):
    st.download_button(etiket, data=df.to_csv(index=False).encode("utf-8-sig"), file_name=ad, mime="text/csv", key=anahtar)

try:
    rfm, segment, ozet, satis, ham = yukle()
except Exception as hata:
    st.error(f"Dosyalar yüklenemedi: {hata}")
    st.info("app.py ve dört CSV dosyasının aynı klasörde olduğundan emin ol.")
    st.stop()

menu = ["🏠 Ana Panel", "👥 Müşteri Yönetimi", "🎯 RFM Segmentasyonu", "💰 Satış Analizi", "🛍️ Ürün Analizi", "🌍 Bölgesel Analiz", "📈 Müşteri Davranışları", "💡 Pazarlama Stratejileri", "📥 Rapor Merkezi"]
with st.sidebar:
    st.title("📊 RFM ANALYTICS")
    st.caption("E-Ticaret Analiz ve Yönetim Sistemi")
    sayfa = st.radio("Bölümler", menu, label_visibility="collapsed")
    st.divider()
    st.caption("Veri dönemi: " + str(satis["siparis_tarihi"].min().date()) + " — " + str(satis["siparis_tarihi"].max().date()))
    st.caption("Kaynak: proje CSV dosyaları")

st.title(sayfa)
st.caption("Müşteri segmentasyonu, satış performansı ve iş kararları için etkileşimli analiz")

if sayfa == menu[0]:
    a,b,c,d = st.columns(4)
    a.metric("👥 Müşteri", tr_sayi(rfm["musteri_id"].nunique()))
    b.metric("💰 Toplam Ciro", para(rfm["Monetary"].sum()))
    c.metric("🧾 Satış Kaydı", tr_sayi(len(satis)))
    d.metric("🎯 Segment", tr_sayi(rfm["Segment"].nunique()))
    st.divider()
    aylik = satis.groupby("ay", as_index=False)["toplam_tutar"].sum()
    col1,col2 = st.columns([1.6,1])
    with col1:
        grafik(px.line(aylik,x="ay",y="toplam_tutar",markers=True,title="Aylık Satış Performansı",labels={"ay":"Ay","toplam_tutar":"Ciro (TL)"}),"ana_aylik")
    with col2:
        adetler = rfm["Segment"].value_counts().reset_index()
        adetler.columns = ["Segment","Müşteri"]
        grafik(px.pie(adetler,names="Segment",values="Müşteri",hole=.55,title="Müşteri Segmentleri"),"ana_pie")
    c1,c2 = st.columns(2)
    with c1:
        ciro = rfm.groupby("Segment",as_index=False)["Monetary"].sum().sort_values("Monetary",ascending=False)
        grafik(px.bar(ciro,x="Segment",y="Monetary",color="Segment",title="Segment Bazında Ciro"),"ana_ciro")
    with c2:
        yillik = satis.groupby("yil",as_index=False)["toplam_tutar"].sum()
        grafik(px.bar(yillik,x="yil",y="toplam_tutar",text_auto=".2s",title="Yıllık Satış Karşılaştırması"),"ana_yil")
    st.subheader("📌 Öne Çıkan Bulgular")
    st.write(f"En fazla müşteri içeren segment: **{rfm['Segment'].value_counts().idxmax()}**")
    st.write(f"En fazla ciro sağlayan segment: **{ciro.iloc[0]['Segment']}** ({para(ciro.iloc[0]['Monetary'])})")
    st.write(f"En yüksek ciro sağlayan ürün: **{satis.groupby('urun_analiz')['toplam_tutar'].sum().idxmax()}**")

elif sayfa == menu[1]:
    a,b,c = st.columns(3)
    with a:
        arama = st.text_input("Müşteri ID",placeholder="MUS1001")
    with b:
        secim = st.multiselect("Segment",sorted(rfm["Segment"].dropna().unique()))
    with c:
        siralama = st.selectbox("Sıralama",["En yüksek harcama","En sık alışveriş","En son alışveriş","Müşteri ID"])
    filtre = rfm.copy()
    if arama:
        filtre = filtre[filtre["musteri_id"].astype(str).str.contains(arama,case=False,regex=False,na=False)]
    if secim:
        filtre = filtre[filtre["Segment"].isin(secim)]
    kolon,artan = {"En yüksek harcama":("Monetary",False),"En sık alışveriş":("Frequency",False),"En son alışveriş":("Recency",True),"Müşteri ID":("musteri_id",True)}[siralama]
    filtre = filtre.sort_values(kolon,ascending=artan)
    a,b,c = st.columns(3)
    a.metric("Filtrelenen Müşteri",len(filtre))
    b.metric("Toplam Harcama",para(filtre["Monetary"].sum()))
    c.metric("Ortalama Harcama",para(filtre["Monetary"].mean() if len(filtre) else 0))
    tablo(filtre,"musteri_tablosu")
    csv_indir(filtre,"Filtreli_Musteriler.csv","⬇️ Filtreli Müşterileri İndir","musteri_indir")
    if len(filtre):
        musteri = st.selectbox("Detayını görüntüle",filtre["musteri_id"].astype(str).tolist())
        kayit = filtre.loc[filtre["musteri_id"].astype(str)==musteri].iloc[0]
        st.info(f"**{musteri}** | Segment: {kayit['Segment']} | Son alışverişten beri: {kayit['Recency']} gün | Sipariş: {kayit['Frequency']} | Harcama: {para(kayit['Monetary'])}")
        st.write("**Pazarlama önerisi:**",kayit["Pazarlama_Onerisi"])

elif sayfa == menu[2]:
    adetler = rfm["Segment"].value_counts().reset_index()
    adetler.columns=["Segment","Müşteri"]
    gelir = rfm.groupby("Segment",as_index=False).agg(Musteri=("musteri_id","nunique"),Ciro=("Monetary","sum"),Ortalama_Harcama=("Monetary","mean"))
    gelir["Ciro_Payi_Yuzde"] = (gelir["Ciro"]/gelir["Ciro"].sum()*100).round(2)
    c1,c2=st.columns(2)
    with c1:
        grafik(px.bar(adetler,x="Segment",y="Müşteri",color="Segment",title="Segmentlerdeki Müşteri Sayısı"),"seg_adet")
    with c2:
        grafik(px.pie(adetler,names="Segment",values="Müşteri",hole=.45,title="Segment Dağılımı"),"seg_pie")
    grafik(px.bar(gelir.sort_values("Ciro",ascending=False),x="Segment",y="Ciro",color="Segment",title="Segmentlerin Toplam Cirosu"),"seg_ciro")
    grafik(px.bar(gelir.sort_values("Ortalama_Harcama",ascending=False),x="Segment",y="Ortalama_Harcama",title="Segment Başına Ortalama Müşteri Harcaması"),"seg_ort")
    tablo(gelir.sort_values("Ciro",ascending=False).round(2),"seg_tablo")
    st.subheader("RFM Puan Dağılımı")
    grafik(px.histogram(rfm,x="RFM_Score",color="Segment",title="RFM Puanları"),"seg_skor")

elif sayfa == menu[3]:
    c1,c2,c3=st.columns(3)
    c1.metric("Toplam Ciro",para(satis["toplam_tutar"].sum()))
    c2.metric("Satış Kaydı",len(satis))
    c3.metric("Ortalama Kayıt Tutarı",para(satis["toplam_tutar"].mean()))
    yillar=sorted(satis["yil"].unique())
    secilen=st.multiselect("Yıl Filtresi",yillar,default=yillar)
    veri=satis[satis["yil"].isin(secilen)]
    aylik=veri.groupby("ay",as_index=False)["toplam_tutar"].sum()
    grafik(px.line(aylik,x="ay",y="toplam_tutar",markers=True,title="Aylık Ciro",labels={"ay":"Ay","toplam_tutar":"Ciro (TL)"}),"satis_ay")
    c1,c2=st.columns(2)
    with c1:
        yillik=veri.groupby("yil",as_index=False)["toplam_tutar"].sum()
        grafik(px.bar(yillik,x="yil",y="toplam_tutar",text_auto=".2s",title="Yıllık Ciro"),"satis_yil")
    with c2:
        odeme=veri.groupby("odeme_turu",as_index=False)["toplam_tutar"].sum()
        grafik(px.pie(odeme,names="odeme_turu",values="toplam_tutar",title="Ödeme Türlerine Göre Ciro"),"satis_odeme")
    st.subheader("Aylık Satış Tablosu")
    tablo(veri.groupby("ay",as_index=False).agg(Satis_Kaydi=("siparis_id","count"),Ciro=("toplam_tutar","sum")).round(2),"satis_tablo")

elif sayfa == menu[4]:
    kategori=satis.groupby("kategori_analiz",as_index=False).agg(Ciro=("toplam_tutar","sum"),Adet=("adet","sum")).sort_values("Ciro",ascending=False)
    urun=satis.groupby("urun_analiz",as_index=False).agg(Ciro=("toplam_tutar","sum"),Adet=("adet","sum"))
    c1,c2,c3=st.columns(3)
    c1.metric("Ürün Çeşidi",satis["urun_analiz"].nunique())
    c2.metric("Kategori",satis["kategori_analiz"].nunique())
    c3.metric("Satılan Ürün Adedi",tr_sayi(satis["adet"].sum()))
    grafik(px.bar(kategori,x="kategori_analiz",y="Ciro",color="kategori_analiz",title="Kategori Bazında Ciro"),"urun_kat")
    c1,c2=st.columns(2)
    with c1:
        grafik(px.bar(urun.nlargest(10,"Adet").sort_values("Adet"),x="Adet",y="urun_analiz",orientation="h",title="En Çok Satılan 10 Ürün"),"urun_adet")
    with c2:
        grafik(px.bar(urun.nlargest(10,"Ciro").sort_values("Ciro"),x="Ciro",y="urun_analiz",orientation="h",title="En Fazla Ciro Sağlayan 10 Ürün"),"urun_ciro")
    st.subheader("Ürün Performans Tablosu")
    tablo(urun.sort_values("Ciro",ascending=False).round(2),"urun_tablo")

elif sayfa == menu[5]:
    bolge=satis.groupby("bolge_analiz",as_index=False).agg(Ciro=("toplam_tutar","sum"),Musteri=("musteri_id","nunique"),Satis_Kaydi=("siparis_id","count"))
    bolge["Musteri_Basina_Ciro"]=(bolge["Ciro"]/bolge["Musteri"]).round(2)
    sehir=satis.groupby("sehir_analiz",as_index=False).agg(Ciro=("toplam_tutar","sum"),Musteri=("musteri_id","nunique"))
    st.info("Bir müşteri birden fazla bölgede alışveriş yapmış olabilir. Bölgesel benzersiz müşteri sayıları toplanarak genel müşteri sayısı hesaplanmamalıdır.")
    grafik(px.bar(bolge.sort_values("Ciro",ascending=False),x="bolge_analiz",y="Ciro",color="bolge_analiz",title="Bölgelere Göre Ciro"),"bolge_ciro")
    c1,c2=st.columns(2)
    with c1:
        grafik(px.bar(sehir.nlargest(10,"Ciro").sort_values("Ciro"),x="Ciro",y="sehir_analiz",orientation="h",title="En Yüksek Ciroya Sahip 10 Şehir"),"sehir_ciro")
    with c2:
        grafik(px.bar(bolge.sort_values("Musteri_Basina_Ciro",ascending=False),x="bolge_analiz",y="Musteri_Basina_Ciro",title="Bölgelere Göre Müşteri Başına Ciro"),"bolge_ort")
    tablo(bolge.sort_values("Ciro",ascending=False).round(2),"bolge_tablo")

elif sayfa == menu[6]:
    c1,c2=st.columns(2)
    with c1:
        grafik(px.scatter(rfm,x="Frequency",y="Monetary",color="Segment",hover_data=["musteri_id","Recency"],title="Alışveriş Sıklığı ve Harcama"),"dav_scatter")
    with c2:
        grafik(px.histogram(rfm,x="Recency",nbins=25,title="Son Alışverişten Beri Geçen Günler"),"dav_recency")
    c1,c2=st.columns(2)
    with c1:
        grafik(px.histogram(rfm,x="Frequency",title="Sipariş Sıklığı Dağılımı"),"dav_freq")
    with c2:
        grafik(px.box(rfm,x="Segment",y="Monetary",color="Segment",title="Segmentlere Göre Harcama Dağılımı"),"dav_box")
    st.metric("Sıklık-Harcama Korelasyonu",f"{rfm['Frequency'].corr(rfm['Monetary']):.3f}")
    st.subheader("En Çok Harcama Yapan 15 Müşteri")
    tablo(rfm.nlargest(15,"Monetary")[["musteri_id","Segment","Frequency","Recency","Monetary"]],"dav_top")

elif sayfa == menu[7]:
    sec=st.selectbox("Segment seç",sorted(rfm["Segment"].dropna().unique()))
    grup=rfm[rfm["Segment"]==sec]
    c1,c2,c3=st.columns(3)
    c1.metric("Müşteri Sayısı",len(grup))
    c2.metric("Segment Cirosu",para(grup["Monetary"].sum()))
    c3.metric("Ortalama Harcama",para(grup["Monetary"].mean()))
    st.subheader("💡 Önerilen Pazarlama Yaklaşımı")
    for oner in grup["Pazarlama_Onerisi"].dropna().unique():
        st.success(oner)
    st.subheader("Bu Segmentteki Müşteriler")
    tablo(grup[["musteri_id","Recency","Frequency","Monetary","RFM_Score","Pazarlama_Onerisi"]].sort_values("Monetary",ascending=False),"paz_tablo")
    csv_indir(grup,f"{norm(sec)}_musteriler.csv","⬇️ Segment Listesini İndir","paz_indir")

elif sayfa == menu[8]:
    st.subheader("📥 Analiz Dosyaları")
    c1,c2=st.columns(2)
    with c1:
        csv_indir(rfm,"RFM_Musteri_Analizi.csv","⬇️ RFM Müşteri Analizi","rap_rfm")
        csv_indir(segment,"Musteri_Segment_Raporu.csv","⬇️ Segment Raporu","rap_seg")
    with c2:
        csv_indir(ozet,"Proje_Genel_Ozet.csv","⬇️ Proje Genel Özeti","rap_ozet")
        csv_indir(satis,"Temizlenmis_Satis_Verileri.csv","⬇️ Temizlenmiş Satış Verileri","rap_satis")
    st.subheader("📋 Proje Genel Özeti")
    tablo(ozet,"rap_ozet_tablo")
    st.subheader("🔍 Veri Kalitesi Kontrolü")
    kontroller = pd.DataFrame([
        {"Kontrol":"RFM müşteri ID benzersiz", "Durum":"BAŞARILI" if rfm["musteri_id"].is_unique else "KONTROL GEREKİYOR"},
        {"Kontrol":"RFM toplamı ile satış toplamı uyumlu", "Durum":"BAŞARILI" if abs(rfm["Monetary"].sum()-satis["toplam_tutar"].sum()) < .01 else "KONTROL GEREKİYOR"},
        {"Kontrol":"Segment müşteri sayıları uyumlu", "Durum":"BAŞARILI" if segment["Musteri_Sayisi"].sum()==len(rfm) else "KONTROL GEREKİYOR"},
        {"Kontrol":"RFM skorları 1-5 arasında", "Durum":"BAŞARILI" if rfm[["R_Score","F_Score","M_Score"]].apply(pd.to_numeric,errors="coerce").ge(1).all().all() and rfm[["R_Score","F_Score","M_Score"]].apply(pd.to_numeric,errors="coerce").le(5).all().all() else "KONTROL GEREKİYOR"}
    ])
    tablo(kontroller,"rap_kontrol")
    st.caption("Veri setinin gerçek ticari işlem kaynağı bağımsız olarak doğrulanmamıştır; örnek proje verisi olarak değerlendirilmelidir.")
