#!/usr/bin/env python3
"""Phase 4-18: JA daily.json — DAILY_THEME_CONTENT 10 + DEFAULT/HERO/GRADE."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "daily.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

THEMES = {
    "TEN_GOD_FRIEND": {
        "name": "自分に集中する日",
        "headline": "いつもよりエネルギーが強い日です。",
        "body": "自信が湧き、自分のやり方が正しいという強い感覚を持つでしょう。ただ、この高いエネルギーは他者との摩擦にもなり得ます。\n\n今日は人を説得しようとする代わりに、そのエネルギーを自分の仕事に注ぎましょう。ソロプロジェクトに取り組んだり、自分の名前がつく何かを始めるのに最適な日です。",
        "watch_for": "耳を貸さずに自分の立場を押し通さないこと。",
        "lean_into": "独立した仕事、個人プロジェクト、ルーティン。",
    },
    "TEN_GOD_ROB_WEALTH": {
        "name": "勢いを築く人",
        "headline": "あなたの推進力は爆発的ですが、せっかちさも同じです。",
        "body": "速く動きたい、競争に勝ちたい、たまっていたものを一気に片づけたいという衝動が強まる日です。競争や達成への欲求がいつもより強く湧きます。\n\nただ、全速力で走ればバッテリーはすぐに切れます。今日の目標をひとつだけ選び、そこにエネルギーを集中させましょう。それ以外は手放してください。",
        "watch_for": "ライバルではない人と競争しないこと。",
        "lean_into": "明確な目標をひとつ決める、集中する。",
    },
    "TEN_GOD_EATING_GOD": {
        "name": "創造の火花",
        "headline": "アイデアを形にするのに良い日です。",
        "body": "気分は柔らかく、何かを創り出したい、表現したいという欲求が湧きます。退屈なタスクを無理にこなすより、本当に楽しめることに集中しましょう。\n\n書くこと、描くこと、料理、新しい計画のブレインストーミング——どれも今日は追い風です。結果を気にせず、プロセスを楽しんでください。",
        "watch_for": "今日は予定を詰め込みすぎないこと。",
        "lean_into": "趣味、創作プロジェクト、アイデアの書き留め。",
    },
    "TEN_GOD_HURTING_OFFICER": {
        "name": "真実を語る人",
        "headline": "今日はシステムのほころびがいつもよりはっきり見えます。",
        "body": "非効率にもどかしさを感じたり、「何かおかしい」という違和感にイライラするかもしれません。この鋭い視点は、正しく使えば強力な武器になります。\n\nただ不満を言うだけでなく、解決策を添えてみましょう。同僚への建設的なフィードバックや改善提案に最適な日です。",
        "watch_for": "タイミングに気を配り、鋭い言葉で傷つけないこと。",
        "lean_into": "問題解決、代替案の提案、仕組みの修正。",
    },
    "TEN_GOD_INDIRECT_WEALTH": {
        "name": "機会を狩る人",
        "headline": "今日は扉が開いてはすぐ閉じます。鋭敏に。",
        "body": "新しい機会や縁がどこからともなく現れるかもしれません。直感が冴えているので、「これだ」と感じたら飛びつきましょう。\n\nただ、すべての機会を捕まえようとしてはいけません。ノイズをふるいにかけ、本当に自分と響き合うもの1〜2個に深く潜りましょう。",
        "watch_for": "FOMO（取り残される不安）に判断を委ねないこと。",
        "lean_into": "新しいことを試す、人とつながる、直感を信じる。",
    },
    "TEN_GOD_DIRECT_WEALTH": {
        "name": "ゆっくり、着実に",
        "headline": "派手ではないけれど、最も堅実な日です。",
        "body": "壮大な結果を追うよりも、必要な作業を黙々と片づけるのに向いた日です。退屈に感じるかもしれませんが、今日築いたものは将来複利で効いてきます。\n\n予算の確認、貯蓄、空間の整理に良い日です。野心より安定とルーティンに焦点を当てましょう。",
        "watch_for": "プロセスを急かしたくなる衝動。",
        "lean_into": "財務チェック、掃除、繰り返せるタスク。",
    },
    "TEN_GOD_SEVEN_KILLINGS": {
        "name": "プレッシャーテスト",
        "headline": "重く感じるかもしれませんが、あなたはより強くなって出てきます。",
        "body": "予期しない責任やプレッシャーに直面するかもしれません。息苦しく感じても、挑戦に真っ向から向き合えば大きな成長につながります。\n\n今日は「ノー」と言う練習が必要です。心身の境界を守ることが最優先。仕事が終わったら完全に切り離して休みましょう。",
        "watch_for": "自分のものではない責任を引き受けないこと。",
        "lean_into": "境界線を引く、深い睡眠、心の保護。",
    },
    "TEN_GOD_DIRECT_OFFICER": {
        "name": "スポットライト",
        "headline": "報いを受け取り、認められる良い日です。",
        "body": "ルールと構造がうまくかみ合い、仕事が滑らかに進む日です。上司への報告、契約の締結、試験にはとても有利。\n\n背景に隠れず、前に出て自分の仕事を見せましょう。今日は自分をアピールすることが強みになります。",
        "watch_for": "自己疑念で縮こまらないこと。",
        "lean_into": "公式な約束、プレゼン、面接。",
    },
    "TEN_GOD_INDIRECT_RESOURCE": {
        "name": "深く考える人",
        "headline": "外よりも内側に焦点を当てる日です。",
        "body": "人と会うよりも、静かな場所で一人で過ごしたいと感じるでしょう。外部の雑音を遮断し、内なる声に耳を傾けるのに良い日です。\n\n読書、勉強、ずっと気になっていた悩みの整理をしましょう。心が片づけば、次の一歩への明確な答えが見えてきます。",
        "watch_for": "気分が沈まないよう、軽い散歩を。",
        "lean_into": "一人の時間、学習、瞑想、リサーチ。",
    },
    "TEN_GOD_DIRECT_RESOURCE": {
        "name": "充電",
        "headline": "今日は温かい慰めと休息が必要です。",
        "body": "心身が敏感で、疲れやすく感じるかもしれません。生産性を無理に押しつける代わりに、自分をいたわる時間を過ごしましょう。\n\n良いものを食べ、温かいお茶を飲み、好きな人と気楽に話しましょう。今日は世界のペースではなく、自分のペースで動きましょう。",
        "watch_for": "休息を怠惰と取り違えないこと。",
        "lean_into": "セルフケア、滋養のある食事、メンターとの対話。",
    },
}

DEFAULT_THEME = {
    "name": "流れに乗る日",
    "headline": "特別な刺激なく、穏やかに流れる一日です。",
    "body": "今日は突出したエネルギーなく、無難に過ぎていきます。無理に何かを変えようとせず、今の流れをそのまま受け入れましょう。",
    "watch_for": "無気力に陥らないよう注意しましょう。",
    "lean_into": "日常の小さな喜びを探す、整理整頓。",
}

HERO_TEMPLATE = "{date}の運勢"

GRADE_LABEL = {
    "PEAK": "絶好調",
    "FAVORABLE": "追い風",
    "NEUTRAL": "中立",
    "CAUTION": "注意",
    "CHALLENGING": "重い",
}

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-18] daily 10 themes + defaults"); print("=" * 60)
    if not JA.exists(): print(f"❌ {JA}"); return 1
    data = json.loads(JA.read_text(encoding="utf-8"))
    data.setdefault("DAILY_THEME_CONTENT", {})
    for key, tr in THEMES.items():
        data["DAILY_THEME_CONTENT"][key] = tr
    data["DEFAULT_DAILY_THEME"] = DEFAULT_THEME
    data["DAILY_HERO_TEMPLATE"] = HERO_TEMPLATE
    data["GRADE_LABEL"] = GRADE_LABEL
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")
    print(f"✅ {len(THEMES)} themes + DEFAULT/HERO/GRADE")

    print("\n[verify]")
    ok = True
    for key, tr in THEMES.items():
        d = data["DAILY_THEME_CONTENT"][key]
        for k in ("name", "headline", "body", "watch_for", "lean_into"):
            if not _ja(d.get(k, "")):
                print(f"  [ERR] {key}.{k}"); ok = False
    for k in ("name", "headline", "body", "watch_for", "lean_into"):
        if not _ja(data["DEFAULT_DAILY_THEME"].get(k, "")):
            print(f"  [ERR] DEFAULT.{k}"); ok = False
    if not _ja(data["DAILY_HERO_TEMPLATE"]):
        print("  [ERR] HERO_TEMPLATE"); ok = False
    for g in ("PEAK", "FAVORABLE", "NEUTRAL", "CAUTION", "CHALLENGING"):
        if not _ja(data["GRADE_LABEL"].get(g, "")):
            print(f"  [ERR] GRADE_LABEL.{g}"); ok = False
    if ok: print("  [OK] daily.json 10/10 + defaults = JA 🏆")
    print("=" * 60)
    return 0 if ok else 1

if __name__ == "__main__": sys.exit(main())