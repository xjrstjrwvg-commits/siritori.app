import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 配布用：国名データのみに限定
COUNTRIES = ["アイスランド", "アイルランド", "アゼルバイジャン", "アフガニスタン", "アメリカ", "アラブシュチョウコクレンポウ", "アルジェリア", "アルゼンチン", "アルバニア", "アルメニア", "アンゴラ", "アンティグアバーブーダ", "アンドラ", "イエメン", "イギリス", "イスラエル", "イタリア", "イラク", "イラン", "インド", "インドネシア", "ウガンダ", "ウクライナ", "ウズベキスタン", "ウルグアイ", "エクアドル", "エジプト", "エストニア", "エスワティニ", "エチオピア", "エリトリア", "エルサルバドル", "オーストラリア", "オーストリア", "オマーン", "オランダ", "ガーナ", "カーボベルデ", "ガイアナ", "カザフスタン", "カタール", "カナダ", "ガボン", "カメルーン", "ガンビア", "カンボジア", "キタマケドニア", "ギニア", "ギニアビサウ", "キプロス", "キューバ", "ギリシャ", "キリバス", "キルギス", "グアテマラ", "クウェート", "クックショトウ", "グレナダ", "クロアチア", "ケニア", "コートジボワール", "コスタリカ", "コソボ", "コモロ", "コロンビア", "コンゴキョウワコク", "コンゴミンシュキョウワコク", "サウジアラビア", "サモア", "サントメプリンシペ", "ザンビア", "サンマリノ", "シエラレオネ", "ジブチ", "ジャマイカ", "ジョージア", "シリア", "シンガポール", "ジンバブエ", "スイス", "スウェーデン", "スーダン", "スペイン", "スリナム", "スリランカ", "スロバキア", "スロベニア", "セーシェル", "セキドウギニア", "セネガル", "セルビア", "セントクリストファーネービス", "セントビンセントグレナディーンショトウ", "セントルシア", "ソマリア", "ソロモンショトウ", "タイ", "ダイカンミンコク", "タジキスタン", "タンザニア", "チェコ", "チャド", "チュウオウアフリカ", "チュウカジンミンキョウワコク", "チュニジア", "チョウセンミンシュシュギジンミンキョウワコク", "チリ", "ツバル", "デンマーク", "ドイツ", "トーゴ", "ドミニカキョウワコク", "ドミニカコク", "トリニダードトバゴ", "トルクメニスタン", "トルコ", "トンガ", "ナイジェリア", "ナウル", "ナミビア", "ニウエ", "ニカラグア", "ニジェール", "ニホン", "ニュージーランド", "ネパール", "ノルウェー", "バーレーン", "ハイチ", "パキスタン", "バチカンシコク", "パナマ", "バヌアツ", "バハマ", "パプアニューギニア", "パラオ", "パラグアイ", "バルバドス", "ハンガリー", "バングラデシュ", "ヒガシティモール", "フィジー", "フィリピン", "フィンランド", "ブータン", "ブラジル", "フランス", "ブルガリア", "ブルキナファソ", "ブルネイ", "ブルンジ", "ベトナム", "ベナン", "ベネズエラ", "ベラルーシ", "ベリーズ", "ペルー", "ベルギー", "ポーランド", "ボスニアヘルツェゴビナ", "ボツワナ", "ボリビア", "ポルトガル", "ホンジュラス", "マーシャルショトウ", "マダガスカル", "マラウイ", "マリ", "マルタ", "マレーシア", "ミクロネシアレンポウ", "ミナミアフリカキョウワコク", "ミナミスーダン", "ミャンマー", "メキシコ", "モーリシャス", "モーリタニア", "モザンビーク", "モナコ", "モルディブ", "モルドバ", "モロッコ", "モンゴル", "モンテネグロ", "ヨルダン", "ラオス", "ラトビア", "リトアニア", "リビア", "リヒテンシュタイン", "リベリア", "ルーマニア", "ルクセンブルク", "ルワンダ", "レソト", "レバノン", "ロシア"]

SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
VOICE_MAP = str.maketrans("ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ", "カキクケコサシスセソタチツテトハヒフヘホハヒフヘホ")

def get_clean_char(w, pos="head"):
    char = w if pos == "head" else w.replace("ー", "")[-1]
    return SMALL_TO_LARGE.get(char, char)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    max_len = min(int(d.get('max_len', 5)), 8) # 最大8単語に制限
    ignore_voiced = d.get('ignore_voiced', False)
    must_chars = [c.translate(VOICE_MAP if ignore_voiced else {}) for c in d.get('must_char', "")]
    limit_one = d.get('limit_one', False)

    results = []

    def solve(path):
        if len(results) >= 500: return # 500件で打ち切り
        if len(path) == max_len:
            if must_chars:
                full = "".join(path).translate(VOICE_MAP if ignore_voiced else {})
                if not all(mc in full for mc in must_chars): return
                if limit_one and not all(full.count(mc) == 1 for mc in must_chars): return
            results.append(list(path))
            return
        
        last_tail = get_clean_char(path[-1], "tail").translate(VOICE_MAP if ignore_voiced else {})
        for next_w in COUNTRIES:
            if next_w not in path:
                next_head = get_clean_char(next_w, "head").translate(VOICE_MAP if ignore_voiced else {})
                if next_head == last_tail:
                    solve(path + [next_w])

    sw = d.get('start_word')
    starts = [sw] if (sw in COUNTRIES) else COUNTRIES
    for w in starts:
        if not sw and d.get('start_char'):
            if get_clean_char(w, "head").translate(VOICE_MAP if ignore_voiced else {}) != d.get('start_char').translate(VOICE_MAP if ignore_voiced else {}): continue
        solve([w])

    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
