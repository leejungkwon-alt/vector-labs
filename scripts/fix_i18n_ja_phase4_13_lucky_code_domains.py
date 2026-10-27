#!/usr/bin/env python3
"""Phase 4-13: JA lucky_code.json — LUCKY_CODE_DOMAINS 5 sigs. lucky_code 100%."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "lucky_code.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

T = {
    "GROWTH": {
        "career": "教育・出版・園芸・ファッション・企画・教育——人やプロジェクトを育てる役割。",
        "wealth": "新しいものを追うより、すでに持っているものを育てる。長期的思考が合います——複利を信じましょう。",
        "relationships": "あなたを前へ押し出す仲間関係。あなたのほうへ向かってくる人ではなく、一緒に育つ人を見つけましょう。",
        "learning": "速いスキミングより深い学習。1ヶ月に10テーマより、1年に1テーマ。",
        "everyday": "小さく頻繁に始めましょう。前進そのものがあなたの薬です。",
        "avoid": ["完璧な条件を待つこと", "完璧主義による麻痺", "長く立ち止まること"],
    },
    "SPARK": {
        "career": "マーケティング・メディア・IT・エネルギー・ホスピタリティ・エンタメ——可視性と熱を必要とするすべて。",
        "wealth": "機会はしばしば人を通じて訪れます。すべてに「はい」と言いたくなる衝動に注意——集中こそ本当の乗数です。",
        "relationships": "温かく表現力豊かな人。あなたに静かでいてほしいと思わない人。スモールトークは敵ではありません。",
        "learning": "声に出して学びましょう。マスターする前に教えましょう。",
        "everyday": "毎日目に見える温かい仕草をひとつ。メッセージ、電話、感謝。",
        "avoid": ["暗い部屋で唯一の光になること", "すべての誘いに「はい」と言うこと", "空っぽで走り続けること"],
    },
    "GROUND": {
        "career": "不動産・建設・教育・仲介・農業——基盤のあるすべての仕事。",
        "wealth": "安定があなたの武器。同じ小さな選択を繰り返す力を信じましょう。地味でも、うまくやれば複利で効きます。",
        "relationships": "少数・深く・着実。目新しさより忠誠。質の高い言葉より、質の高い時間。",
        "learning": "体系化されたプログラム。資格のある講師。インスピレーションより資格。",
        "everyday": "同じ起床時刻。同じ食事時刻。リズムがすべてです。",
        "avoid": ["四半期ごとに新しもの追い", "速度のための速度", "理由のない変化"],
    },
    "EDGE": {
        "career": "金融・法律・軍警・医療・エンジニアリング——ルール・精密さ・結果が伴う仕事。",
        "wealth": "明晰さがあなたの通貨。追うより理解することを選びましょう。慎重さを回避と取り違えていないか確認してください。",
        "relationships": "直接さがあなたの愛の言語。本気の意見を受け止められる人。演技のない関係。",
        "learning": "正規の訓練。徒弟制度。インスピレーションよりシステムとフレームワーク。",
        "everyday": "ひとつ片づける、ひとつ言う、ひとつ線を引く。",
        "avoid": ["何が何でも議論に勝つこと", "正直さを装った情緒的冷淡さ", "人生の過度な構造化"],
    },
    "FLOW": {
        "career": "トレーディング・物流・旅行・コンサルティング・研究——動く、あるいはつなぐすべての仕事。",
        "wealth": "資源との関係は季節と共に動きます。リズムを信じつつ、あなたを錨付けする安定した習慣をひとつ持ちましょう。",
        "relationships": "深く・静か・急がない。ただ話す相手ではなく、共に考えられる人。",
        "learning": "ゆっくりした没入型の学習。ドリルより吸収で学びます。",
        "everyday": "週に一度、予定外のことひとつに「はい」。流れを止めないでください。",
        "avoid": ["早すぎるコミット", "行動の代わりに過剰な分析", "集中の分散"],
    },
}

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-13] lucky_code LUCKY_CODE_DOMAINS"); print("=" * 60)
    if not JA.exists(): print(f"❌ {JA}"); return 1
    data = json.loads(JA.read_text(encoding="utf-8"))
    data.setdefault("LUCKY_CODE_DOMAINS", {})
    for sig, tr in T.items():
        data["LUCKY_CODE_DOMAINS"].setdefault(sig, {}).update(tr)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")
    print(f"✅ {len(T)} sigs 저장")
    print("\n[verify]")
    ok = True
    for sig in T:
        d = data["LUCKY_CODE_DOMAINS"][sig]
        for key in ("career", "wealth", "relationships", "learning", "everyday"):
            if not _ja(d.get(key, "")): print(f"  [ERR] {sig}.{key}"); ok = False
        for i, s in enumerate(d.get("avoid", [])):
            if not _ja(s): print(f"  [ERR] {sig}.avoid[{i}]"); ok = False
    # 전체 JA 커버리지 재확인
    all_ok = True
    for sig, d in data.get("LUCKY_CODE_CONTENT", {}).items():
        if not _ja(d.get("element", "")): print(f"  [잔여EN] CONTENT.{sig}"); all_ok = False
    for sig, d in data.get("LUCKY_CODE_DOMAINS", {}).items():
        if not _ja(d.get("career", "")): print(f"  [잔여EN] DOMAINS.{sig}"); all_ok = False
    if ok and all_ok: print("  [OK] lucky_code.json 100% JA 🏆")
    print("=" * 60)
    return 0 if (ok and all_ok) else 1

if __name__ == "__main__": sys.exit(main())