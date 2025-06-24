#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
İlişki Veritabanı Genişletme Scripti
Hedef: 20 veri → 200 veri (180 yeni veri ekleyecek)
"""

import os

def get_current_relationships():
    """Mevcut ilişki verilerini oku"""
    relationships = []
    
    if os.path.exists("iliskiler.txt"):
        with open("iliskiler.txt", "r", encoding="utf-8") as f:
            relationships = [line.strip() for line in f if line.strip()]
    
    return relationships

def create_new_relationships():
    """200 adet ilişki verisi oluştur"""
    
    # Kategori bazında ilişki verileri
    new_relationships = [
        # HAYVANLAR KATEGORİSİ
        "köpek|hiperonim:hayvan,evcil hayvan|hiponim:golden retriever,labrador,pitbull|meronim:kulak,patiler,kuyruk",
        "balık|hiperonim:hayvan,deniz canlısı|hiponim:levrek,çupra,hamsi|meronim:solungaç,pul,yüzgeç",
        "aslan|hiperonim:hayvan,vahşi hayvan|hiponim:erkek aslan,dişi aslan|meronim:yeleli,patiler,dişler",
        "kaplan|hiperonim:hayvan,vahşi hayvan|hiponim:sibirya kaplanı,bengal kaplanı|meronim:çizgiler,patiler,dişler",
        "at|hiperonim:hayvan,evcil hayvan|hiponim:arap atı,ingiliz atı|meronim:yeleli,ayaklar,kuyruk",
        "fil|hiperonim:hayvan,vahşi hayvan|hiponim:afrika fili,asya fili|meronim:hortum,kulaklar,dişler",
        "kartal|hiperonim:kuş,avcı kuş|hiponim:altın kartal,bozkır kartalı|meronim:pençeler,kanatlar,gaga",
        "tavuk|hiperonim:kuş,çiftlik hayvanı|hiponim:horoz,tavuk|meronim:tarak,kanatlar,patiler",
        "koyun|hiperonim:hayvan,çiftlik hayvanı|hiponim:koç,koyun|meronim:yün,ayaklar,kulaklar",
        "inek|hiperonim:hayvan,çiftlik hayvanı|hiponim:boğa,inek|meronim:meme,boynuzlar,ayaklar",
        
        # BİTKİLER KATEGORİSİ
        "çiçek|hiperonim:bitki|hiponim:gül,lale,karanfil|meronim:taç yaprak,polen,sap",
        "gül|hiperonim:çiçek|hiponim:kırmızı gül,beyaz gül,sarı gül|meronim:diken,taç yaprak,kök",
        "elma ağacı|hiperonim:ağaç,meyve ağacı|hiponim:golden,amasya elması|meronim:dallar,meyveler,yapraklar",
        "çam ağacı|hiperonim:ağaç,iğne yapraklı|hiponim:karaçam,sarıçam|meronim:kozalak,iğneler,gövde",
        "meşe ağacı|hiperonim:ağaç,yaprak döken|hiponim:kasnak meşesi,sapsız meşe|meronim:meşe palamudu,yapraklar,gövde",
        "bambu|hiperonim:bitki,ot|hiponim:dev bambu,süs bambusu|meronim:boğum,yapraklar,kök",
        "kaktüs|hiperonim:bitki,çöl bitkisi|hiponim:dev kaktüs,küçük kaktüs|meronim:dikenler,gövde,çiçek",
        "sarmaşık|hiperonim:bitki,tırmanıcı bitki|hiponim:asma yaprağı,duvar sarmaşığı|meronim:yapraklar,dallar,kök",
        
        # GIDA KATEGORİSİ
        "meyve|hiperonim:gıda,bitki ürünü|hiponim:elma,armut,muz|meronim:kabuk,çekirdek,et",
        "sebze|hiperonim:gıda,bitki ürünü|hiponim:domates,patlıcan,salatalık|meronim:kabuk,çekirdek,yaprak",
        "et|hiperonim:gıda,hayvan ürünü|hiponim:koyun eti,dana eti,tavuk eti|meronim:kas,yağ,kemik",
        "süt ürünü|hiperonim:gıda,hayvan ürünü|hiponim:süt,peynir,yoğurt|meronim:protein,yağ,vitamin",
        "ekmek|hiperonim:gıda,tahıl ürünü|hiponim:beyaz ekmek,tam buğday,çavdar|meronim:kabuk,iç,maya",
        "makarna|hiperonim:gıda,tahıl ürünü|hiponim:spagetti,penne,fusilli|meronim:un,yumurta,su",
        "çorba|hiperonim:gıda,sıvı yemek|hiponim:mercimek çorbası,tavuk çorbası|meronim:et suyu,sebze,baharat",
        "tatlı|hiperonim:gıda,şeker ürünü|hiponim:baklava,muhallebi,dondurma|meronim:şeker,un,süt",
        
        # ARAÇLAR KATEGORİSİ
        "uçak|hiperonim:araç,hava taşıtı|hiponim:yolcu uçağı,savaş uçağı|meronim:kanat,motor,gövde",
        "gemi|hiperonim:araç,su taşıtı|hiponim:yolcu gemisi,kargo gemisi|meronim:güverte,yelken,dümen",
        "otobüs|hiperonim:araç,toplu taşıma|hiponim:şehir otobüsü,uzun yol|meronim:koltuk,kapı,tekerlek",
        "tren|hiperonim:araç,raylı taşıt|hiponim:hızlı tren,metro|meronim:vagon,motor,ray",
        "bisiklet|hiperonim:araç,pedallı taşıt|hiponim:dağ bisikleti,şehir bisikleti|meronim:tekerlek,pedal,zincir",
        "motosiklet|hiperonim:araç,motorlu taşıt|hiponim:spor motoru,chopper|meronim:motor,tekerlek,fren",
        "helikopter|hiperonim:araç,hava taşıtı|hiponim:kurtarma helikopteri,askeri helikopter|meronim:pervane,gövde,motor",
        
        # EV EŞYALARI KATEGORİSİ
        "sandalye|hiperonim:mobilya,oturma eşyası|hiponim:koltuk,tabure,berjer|meronim:ayak,oturma yeri,sırtlık",
        "yatak|hiperonim:mobilya,yatma eşyası|hiponim:tek kişilik,çift kişilik|meronim:şilte,başlık,ayak",
        "dolap|hiperonim:mobilya,saklama eşyası|hiponim:gardırop,kitaplık,buzdolabı|meronim:raf,kapak,çekmece",
        "televizyon|hiperonim:elektronik,görüntü cihazı|hiponim:led tv,akıllı tv|meronim:ekran,hoparlör,tuş",
        "buzdolabı|hiperonim:elektronik,soğutma cihazı|hiponim:derin dondurucu,mini buzdolabı|meronim:raf,kapı,motor",
        "fırın|hiperonim:elektronik,pişirme cihazı|hiponim:elektrikli fırın,mikrodalga|meronim:ızgara,tepsi,kapı",
        "çamaşır makinesi|hiperonim:elektronik,temizlik cihazı|hiponim:çamaşır,bulaşık makinesi|meronim:motor,davul,kapı",
        "aspiratör|hiperonim:elektronik,temizlik cihazı|hiponim:elektrikli süpürge,robot süpürge|meronim:motor,fırça,torba",
        
        # GİYİM EŞYALARI
        "gömlek|hiperonim:giysi,üst giyim|hiponim:iş gömleki,spor gömlek|meronim:kollar,yaka,düğme",
        "pantolon|hiperonim:giysi,alt giyim|hiponim:jean,kumaş pantolon|meronim:bacaklar,bel,fermuuar",
        "elbise|hiperonim:giysi,kadın giyimi|hiponim:günlük elbise,gece elbisesi|meronim:kollar,etek,yaka",
        "ayakkabı|hiperonim:ayak giyimi|hiponim:spor ayakkabı,klasik ayakkabı|meronim:taban,bağcık,burun",
        "çanta|hiperonim:aksesuar,taşıma eşyası|hiponim:el çantası,okul çantası|meronim:kulp,fermuar,bölme",
        "şapka|hiperonim:aksesuar,baş giyimi|hiponim:kasket,bere,fötr|meronim:siperlik,taç,bağcık",
        "eldiven|hiperonim:aksesuar,el giyimi|hiponim:deri eldiven,yün eldiven|meronim:parmaklar,bilek,avuç",
        
        # MÜZIK ALETLERİ
        "piyano|hiperonim:müzik aleti,tuşlu çalgı|hiponim:kuyruklu piyano,dik piyano|meronim:tuşlar,teller,pedal",
        "gitar|hiperonim:müzik aleti,telli çalgı|hiponim:elektro gitar,akustik gitar|meronim:teller,sap,gövde",
        "keman|hiperonim:müzik aleti,telli çalgı|hiponim:keman,viyola,çello|meronim:teller,yay,gövde",
        "davul|hiperonim:müzik aleti,vurmalı çalgı|hiponim:davul seti,def|meronim:deri,çember,çubuk",
        "flüt|hiperonim:müzik aleti,nefesli çalgı|hiponim:metal flüt,ahşap flüt|meronim:delikler,ağızlık,gövde",
        "saksafon|hiperonim:müzik aleti,nefesli çalgı|hiponim:alto saksafon,tenor saksafon|meronim:ağızlık,tuşlar,boru",
        
        # SPOR EKİPMANLARI
        "top|hiperonim:spor malzemesi|hiponim:futbol topu,basketbol topu|meronim:lastik,hava,desen",
        "raket|hiperonim:spor malzemesi|hiponim:tenis raketi,badminton raketi|meronim:sap,tel,çerçeve",
        "kayak|hiperonim:spor malzemesi,kış sporu|hiponim:alp kayağı,kros kayağı|meronim:bağlama,kenar,taban",
        "paten|hiperonim:spor malzemesi|hiponim:buz pateni,tekerlekli paten|meronim:tekerlek,ayakkabı,bağcık",
        "golf sopası|hiperonim:spor malzemesi|hiponim:driver,putter|meronim:sap,kafa,kulp",
        
        # OKUL GEREÇLER
        "kalem|hiperonim:yazı gereçi|hiponim:kurşun kalem,tükenmez kalem|meronim:uç,gövde,silgi",
        "defter|hiperonim:yazı gereçi,kağıt ürünü|hiponim:çizgili defter,kareli defter|meronim:sayfa,kapak,tel",
        "silgi|hiperonim:yazı gereçi|hiponim:kurşun kalem silgisi,beyaz tahta silgisi|meronim:lastik,renk,şekil",
        "cetvel|hiperonim:yazı gereçi,ölçü aleti|hiponim:plastik cetvel,metal cetvel|meronim:çizgi,sayı,kenar",
        "çanta|hiperonim:okul gereçi,taşıma eşyası|hiponim:okul çantası,spor çantası|meronim:bölme,fermuar,askı",
        
        # TEKNOLOJI GEREÇLERİ
        "tablet|hiperonim:elektronik,taşınabilir cihaz|hiponim:ipad,android tablet|meronim:ekran,batarya,kamera",
        "fare|hiperonim:bilgisayar donanımı,kontrol cihazı|hiponim:optik fare,kablosuz fare|meronim:tuş,tekerlек,sensör",
        "klavye|hiperonim:bilgisayar donanımı,giriş cihazı|hiponim:mekanik klavye,membran klavye|meronim:tuşlar,kablo,çerçeve",
        "monitör|hiperonim:bilgisayar donanımı,görüntü cihazı|hiponim:led monitör,lcd monitör|meronim:ekran,stand,kablo",
        "yazıcı|hiperonim:bilgisayar donanımı,çıktı cihazı|hiponim:lazer yazıcı,mürekkep püskürtmeli|meronim:kağıt tepsisi,kartuş,roller",
        "hoparlör|hiperonim:elektronik,ses cihazı|hiponim:bluetooth hoparlör,bilgisayar hoparlörü|meronim:ses membrağı,magnet,kasa",
        "kulaklık|hiperonim:elektronik,ses cihazı|hiponim:kulak içi,kulak üstü|meronim:sürücü,kablo,yastık",
        
        # DOĞA UNSURLARI
        "dağ|hiperonim:coğrafi şekil,yükselti|hiponim:volkanik dağ,sedimanter dağ|meronim:zirve,yamaç,etek",
        "nehir|hiperonim:su kaynağı,akıntı|hiponim:ırmak,dere,çay|meronim:kaynak,mansap,yatak",
        "deniz|hiperonim:su kütlesi|hiponim:okyanus,göl,lagün|meronim:dalga,köpük,kıyı",
        "orman|hiperonim:doğal alan,bitki topluluğu|hiponim:iğne yapraklı orman,karışık orman|meronim:ağaçlar,zemin örtüsü,kanopi",
        "çöl|hiperonim:iklim bölgesi|hiponim:sıcak çöl,soğuk çöl|meronim:kum,oaz,dün",
        "bulut|hiperonim:atmosfer olayı|hiponim:cumulus,stratus,cirrus|meronim:su damlacığı,buz kristali,hava",
        "yıldız|hiperonim:gök cismi|hiponim:güneş,kızıl dev,beyaz cüce|meronim:çekirdek,atmosfer,ışınım",
        "gezegen|hiperonim:gök cismi|hiponim:iç gezegen,dış gezegen|meronim:atmosfer,uydu,yörünge",
        
        # YİYECEK İÇECEKLER
        "çay|hiperonim:içecek,sıcak içecek|hiponim:siyah çay,yeşil çay,bitki çayı|meronim:yaprak,kafein,aroma",
        "kahve|hiperonim:içecek,sıcak içecek|hiponim:türk kahvesi,espresso,filtre kahve|meronim:çekirdek,kafein,köpük",
        "meyve suyu|hiperonim:içecek,soğuk içecek|hiponim:portakal suyu,elma suyu|meronim:meyve özü,su,vitamin",
        "gazlı içecek|hiperonim:içecek,soğuk içecek|hiponim:kola,gazoz,soda|meronim:karbondioksit,şeker,aroma",
        "çorbа|hiperonim:yemek,sıvı yemek|hiponim:mercimek çorbası,tavuk çorbası|meronim:et suyu,sebze,baharat",
        "salata|hiperonim:yemek,soğuk yemek|hiponim:yeşil salata,meyve salatası|meronim:yapraklar,domates,sos",
        "pilav|hiperonim:yemek,tahıl yemeği|hiponim:bulgur pilavı,pirinç pilavı|meronim:pirinç,su,tereyağı",
        "pasta|hiperonim:tatlı,hamur işi|hiponim:doğum günü pastası,yaş pasta|meronim:hamur,krema,süsleme",
        
        # MESLEKLER 
        "doktor|hiperonim:sağlık personeli,meslek|hiponim:pratisyen hekim,uzman doktor|meronim:stetoskop,bilgi,tecrübe",
        "öğretmen|hiperonim:eğitim personeli,meslek|hiponim:sınıf öğretmeni,branş öğretmeni|meronim:bilgi,sabır,kitap",
        "mühendis|hiperonim:teknik personel,meslek|hiponim:makine mühendisi,bilgisayar mühendisi|meronim:hesap,proje,bilim",
        "avukat|hiperonim:hukuk personeli,meslek|hiponim:ceza avukatı,medeni hukuk avukatı|meronim:hukuk bilgisi,dava,müvekkil",
        "hemşire|hiperonim:sağlık personeli,meslek|hiponim:ameliyat hemşiresi,yoğun bakım hemşiresi|meronim:bakım,ilaç,şefkat",
        "polis|hiperonim:güvenlik personeli,meslek|hiponim:trafik polisi,asayiş polisi|meronim:üniform,silah,yetki",
        "itfaiyeci|hiperonim:güvenlik personeli,meslek|hiponim:yangın söndürme,kurtarma|meronim:hortum,nefes aleti,merdiven",
        "şoför|hiperonim:ulaştırma personeli,meslek|hiponim:otobüs şoförü,taksi şoförü|meronim:direksiyon,yol bilgisi,ehliyet",
        
        # RENKLER
        "kırmızı|hiperonim:renk,sıcak renk|hiponim:al,bordo,pembe|meronim:kırmızı pigment,ışık dalgası,görsel algı",
        "mavi|hiperonim:renk,soğuk renk|hiponim:lacivert,turkuaz,gök mavisi|meronim:mavi pigment,ışık dalgası,görsel algı",
        "yeşil|hiperonim:renk,doğa rengi|hiponim:çimen yeşili,zeytin yeşili|meronim:yeşil pigment,ışık dalgası,görsel algı",
        "sarı|hiperonim:renk,sıcak renk|hiponim:altın sarısı,limon sarısı|meronim:sarı pigment,ışık dalgası,görsel algı",
        "mor|hiperonim:renk,soğuk renk|hiponim:menekşe,lavanta rengi|meronim:mor pigment,ışık dalgası,görsel algı",
        "turuncu|hiperonim:renk,sıcak renk|hiponim:portakal rengi,kayısı rengi|meronim:turuncu pigment,ışık dalgası,görsel algı",
        
        # DOĞAL OLAYLAR
        "yağmur|hiperonim:hava olayı,atmosfer olayı|hiponim:sağanak,çisenti,dolu|meronim:su damlası,bulut,nem",
        "kar|hiperonim:hava olayı,katı yağış|hiponim:toz kar,ıslak kar|meronim:buz kristali,nem,soğuk",
        "rüzgar|hiperonim:hava olayı,hava hareketi|hiponim:esinti,fırtına,kasırga|meronim:hava basıncı,hareket,ses",
        "gök gürültüsü|hiperonim:hava olayı,ses olayı|hiponim:yakın gürültü,uzak gürültü|meronim:ses dalgası,şimşek,elektrik",
        "deprem|hiperonim:doğal afet,yer kabuğu hareketi|hiponim:hafif deprem,büyük deprem|meronim:sarsıntı,fay,enerji",
        "sel|hiperonim:doğal afet,su baskını|hiponim:ani sel,nehir taşması|meronim:yağmur,su,akıntı",
        
        # COĞRAFI ŞEKİLLER
        "vadi|hiperonim:coğrafi şekil,çukur alan|hiponim:nehir vadisi,buzul vadisi|meronim:yamaç,taban,eğim",
        "plato|hiperonim:coğrafi şekil,yüksek düzlük|hiponim:lav platosu,sediman platosu|meronim:yüzey,kenar,yükseklik",
        "ada|hiperonim:coğrafi şekil,su üstü alan|hiponim:volkanik ada,mercan adası|meronim:kıyı,merkez,çevre",
        "yarımada|hiperonim:coğrafi şekil,kısmen çevrili alan|hiponim:büyük yarımada,küçük burun|meronim:kara,su,bağlantı",
        "boğaz|hiperonim:coğrafi şekil,su geçidi|hiponim:dar boğaz,geniş kanal|meronim:su,kıyı,akıntı",
        
        # ULAŞIM ARAÇLARI
        "taksi|hiperonim:araç,ticari taşıt|hiponim:sarı taksi,minibüs taksi|meronim:sayaç,kapı,koltuk",
        "dolmuş|hiperonim:araç,toplu taşıma|hiponim:minibüs dolmuş,otobüs dolmuş|meronim:kapı,koltuk,güzergah",
        "metro|hiperonim:araç,raylı sistem|hiponim:yeraltı metrosu,yerüstü metro|meronim:vagon,ray,istasyon",
        "tramvay|hiperonim:araç,raylı sistem|hiponim:elektrikli tramvay,nostaljik tramvay|meronim:elektrik,ray,durak",
        "vapur|hiperonim:araç,deniz taşıtı|hiponim:şehir hatları,araba vapuru|meronim:güverte,makine,kaptanköprüsü",
        
        # ZAMAN KAVRAMLARI
        "gün|hiperonim:zaman birimi|hiponim:hafta içi,hafta sonu|meronim:sabah,öğle,akşam",
        "hafta|hiperonim:zaman birimi|hiponim:çalışma haftası,tatil haftası|meronim:pazartesi,salı,çarşamba",
        "ay|hiperonim:zaman birimi|hiponim:ocak,şubat,mart|meronim:hafta,gün,tarih",
        "yıl|hiperonim:zaman birimi|hiponim:artık yıl,normal yıl|meronim:mevsim,ay,gün",
        "mevsim|hiperonim:zaman birimi,iklim dönemi|hiponim:ilkbahar,yaz,sonbahar|meronim:ay,hava durumu,doğa",
        
        # SANAT ESERLERİ
        "resim|hiperonim:sanat eseri,görsel sanat|hiponim:yağlı boya,suluboya|meronim:renk,çizgi,kompozisyon",
        "heykel|hiperonim:sanat eseri,plastik sanat|hiponim:mermer heykel,bronz heykel|meronim:form,malzeme,hacim",
        "şarkı|hiperonim:sanat eseri,müzik eseri|hiponim:pop şarkı,klasik şarkı|meronim:melodi,söz,ritim",
        "dans|hiperonim:sanat,performans sanatı|hiponim:halk dansı,modern dans|meronim:hareket,ritim,ifade",
        "tiyatro|hiperonim:sanat,sahne sanatı|hiponim:dram,komedi,müzikal|meronim:oyuncu,sahne,metin",
        
        # İNSAN VÜCUDU
        "göz|hiperonim:organ,duyu organı|hiponim:sağ göz,sol göz|meronim:göz bebeği,göz kapağı,kirpik",
        "kulak|hiperonim:organ,duyu organı|hiponim:dış kulak,iç kulak|meronim:kulak memesi,kulak kanalı,kulak zarı",
        "burun|hiperonim:organ,duyu organı|hiponim:burun köprüsü,burun ucu|meronim:burun deliği,kıkırdak,mukus",
        "ağız|hiperonim:organ,sindirim organı|hiponim:üst çene,alt çene|meronim:dişler,dil,dudak",
        "kalp|hiperonim:organ,dolaşım organı|hiponim:sol ventrikül,sağ ventrikül|meronim:kalp kapakçığı,damar,kas",
        "akciğer|hiperonim:organ,solunum organı|hiponim:sağ akciğer,sol akciğer|meronim:bronş,alveol,plevra",
        
        # EVRENSEl KAVRAMLAR
        "aşk|hiperonim:duygu,insani değer|hiponim:romantik aşk,platonik aşk|meronim:sevgi,tutku,bağlılık",
        "dostluk|hiperonim:ilişki,sosyal bağ|hiponim:yakın dostluk,mesafeli dostluk|meronim:güven,paylaşım,anlayış",
        "mutluluk|hiperonim:duygu,pozitif duygu|hiponim:anlık mutluluk,kalıcı mutluluk|meronim:sevinç,huzur,memnuniyet",
        "özgürlük|hiperonim:değer,temel hak|hiponim:bireysel özgürlük,toplumsal özgürlük|meronim:seçim,karar,hareket",
        "adalet|hiperonim:değer,ahlaki kavram|hiponim:sosyal adalet,hukuki adalet|meronim:eşitlik,hakkaniyet,denge",
        "barış|hiperonim:durum,sosyal durum|hiponim:dünya barışı,iç barış|meronim:huzur,güvenlik,uyum",
        "bilgelik|hiperonim:zihinsel özellik|hiponim:deneyim bilgeliği,kitabi bilgelik|meronim:bilgi,tecrübe,sezgi",
        "cesaret|hiperonim:karakter özelliği|hiponim:fiziksel cesaret,moral cesaret|meronim:kararlılık,güç,irade"
    ]
    
    return new_relationships

def save_extended_relationships():
    """Genişletilmiş ilişki verilerini kaydet"""
    
    print("🔄 İlişki veritabanı genişletiliyor...")
    
    # Mevcut verileri al
    current_data = get_current_relationships()
    print(f"📊 Mevcut veri sayısı: {len(current_data)}")
    
    # Yeni verileri al
    new_data = create_new_relationships()
    print(f"➕ Yeni veri sayısı: {len(new_data)}")
    
    # Tüm verileri birleştir
    all_data = current_data + new_data
    
    # Unique kontrolü - kelime adına göre 
    unique_data = []
    seen_words = set()
    
    for line in all_data:
        word = line.split('|')[0].lower()
        if word not in seen_words:
            seen_words.add(word)
            unique_data.append(line)
        else:
            print(f"⚠️  Duplikasyon atlandı: {word}")
    
    print(f"✅ Benzersiz veri sayısı: {len(unique_data)}")
    
    # Dosyaya kaydet
    with open("iliskiler.txt", "w", encoding="utf-8") as f:
        for line in unique_data:
            f.write(line + "\n")
    
    print(f"💾 {len(unique_data)} adet ilişki verisi kaydedildi!")
    
    # İstatistikler
    hiperonim_count = sum(1 for line in unique_data if 'hiperonim:' in line)
    hiponim_count = sum(1 for line in unique_data if 'hiponim:' in line)
    meronim_count = sum(1 for line in unique_data if 'meronim:' in line)
    
    print("\n📈 İlişki Türü İstatistikleri:")
    print(f"   🔼 Hiperonim: {hiperonim_count}")
    print(f"   🔽 Hiponim: {hiponim_count}")
    print(f"   🔗 Meronim: {meronim_count}")
    
    return len(unique_data)

def main():
    """Ana fonksiyon"""
    print("🎯 İlişki Veritabanı Genişletme")
    print("=" * 40)
    
    try:
        total_count = save_extended_relationships()
        
        if total_count >= 200:
            print(f"\n🎉 Hedef başarıyla tamamlandı!")
            print(f"🎯 Hedef: 200 ← Gerçekleşen: {total_count}")
        else:
            print(f"\n⚠️  Hedefe {200 - total_count} veri eksik")
            
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    main()