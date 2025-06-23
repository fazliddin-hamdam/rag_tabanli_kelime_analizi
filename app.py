from flask import Flask, render_template, request
from vector_query import query_nearest

app = Flask(__name__)

def iliskiler_txt_yukle(dosya_adi="iliskiler.txt"):
    iliskiler = {}
    with open(dosya_adi, "r", encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir or satir.startswith("#"):
                continue
            parcalar = satir.split("|")
            kelime = parcalar[0].strip().lower()
            iliski_dict = {}
            for parca in parcalar[1:]:
                if ":" in parca:
                    tip, degerler = parca.split(":", 1)
                    tip = tip.strip()
                    deger_list = [d.strip() for d in degerler.split(",") if d.strip()]
                    iliski_dict[tip] = deger_list
            iliskiler[kelime] = iliski_dict
    return iliskiler

ILISKILER = iliskiler_txt_yukle("iliskiler.txt")

def ornek_cumle_uret(kelime):
    return f'"{kelime}" kelimesiyle bir cümle: Dün {kelime} hakkında önemli bir konuşma yaptık.'

def kelime_iliskileri(kelime):
    iliski = ILISKILER.get(kelime.lower(), {})
    hiper = iliski.get("hiperonim", [])
    hipo = iliski.get("hiponim", [])
    mero = iliski.get("meronim", [])
    return hiper, hipo, mero

@app.route("/", methods=["GET", "POST"])
def index():
    query_word = None
    results = None
    hiper, hipo, mero = [], [], []

    if request.method == "POST":
        query_word = request.form.get("query_word", "").strip()
        if query_word:
            neighbors, distances = query_nearest(query_word, k=5)
            results = []
            for kelime, mesafe in zip(neighbors, distances):
                aciklama = ornek_cumle_uret(kelime)
                results.append((kelime, mesafe, aciklama))
            # Yalnızca sorgulanan kelime için ilişkiler
            hiper, hipo, mero = kelime_iliskileri(query_word)

    return render_template(
        "index.html",
        query_word=query_word,
        results=results,
        hiper=hiper,
        hipo=hipo,
        mero=mero,
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
