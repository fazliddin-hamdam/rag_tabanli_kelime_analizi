# app.py
from flask import Flask, render_template, request
from vector_query import query_nearest

app = Flask(__name__)

# Available embedding models for Turkish (keep original BERT plus new ones)
MODEL_OPTIONS = {
    "bert-cased": "dbmdz/bert-base-turkish-cased",  # existing BERT model
    "roberta-uncased": "TURKCELL/roberta-base-turkish-uncased",
    "xlm-turkish-ner": "akdeniz27/xlm-roberta-base-turkish-ner"
}

# Load relationship data from text file
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

# Generate example sentence
def ornek_cumle_uret(kelime):
    return f'"{kelime}" kelimesiyle bir cümle: Dün {kelime} hakkında önemli bir konuşma yaptık.'

# Retrieve word relationships
def kelime_iliskileri(kelime):
    iliski = ILISKILER.get(kelime.lower(), {})
    hiper = iliski.get("hiperonim", [])
    hipo = iliski.get("hiponim", [])
    mero = iliski.get("meronim", [])
    return hiper, hipo, mero

@app.route("/", methods=["GET", "POST"])
def index():
    query_word = None
    selected_model = list(MODEL_OPTIONS.keys())[0]
    results = None
    hiper, hipo, mero = [], [], []

    if request.method == "POST":
        query_word = request.form.get("query_word", "").strip()
        selected_model = request.form.get("model_choice", selected_model)
        print(f"[LOG] Sorgu kelimesi: {query_word}")
        print(f"[LOG] Seçilen model: {selected_model} -> {MODEL_OPTIONS[selected_model]}")
        if query_word:
            # Pass selected model name to query_nearest
            model_name = MODEL_OPTIONS[selected_model]
            print(f"[LOG] query_nearest fonksiyonu çağrılıyor: kelime='{query_word}', model='{model_name}'")
            neighbors, distances = query_nearest(query_word, k=5)
            print(f"[LOG] query_nearest sonuçları: neighbors={neighbors}, distances={distances}")
            results = [
                (kelime, mesafe, ornek_cumle_uret(kelime))
                for kelime, mesafe in zip(neighbors, distances)
            ]
            hiper, hipo, mero = kelime_iliskileri(query_word)
            print(f"[LOG] İlişkiler: hiper={hiper}, hipo={hipo}, mero={mero}")

    return render_template(
        "index.html",
        query_word=query_word,
        results=results,
        hiper=hiper,
        hipo=hipo,
        mero=mero,
        model_options=MODEL_OPTIONS,
        selected_model=selected_model
    )

if __name__ == "__main__":
    app.run(debug=True, port=5000)
