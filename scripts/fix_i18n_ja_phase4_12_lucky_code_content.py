#!/usr/bin/env python3
"""Phase 4-12: JA lucky_code.json — LUCKY_CODE_CONTENT 5 sigs."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
JA = ROOT / "app" / "services" / "content" / "data" / "ja" / "lucky_code.json"
KANA_RE = re.compile(r'[\u3040-\u30FF]')

T = {
    "GROWTH": {
        "element": "木",
        "keywords": ["拡張", "方向", "主導"],
        "colors": ["深緑", "翡翠色", "オリーブ"],
        "numbers": [3, 8],
        "directions": ["東", "東南"],
        "activities": ["朝の散歩", "ハイキング", "庭仕事", "読書", "小さなことを始める"],
        "foods": ["葉物野菜", "酸味のある食べ物", "フレッシュハーブ"],
        "practices": [
            "今週、計画なしでひとつ始めてみましょう。",
            "自然の中で20分を過ごしましょう——運動ではなく、ただ存在すること。",
            "向かっている方向をひとつ、向かっていない方向をひとつ書き出しましょう。",
        ],
    },
    "SPARK": {
        "element": "火",
        "keywords": ["表現", "温もり", "可視性"],
        "colors": ["赤", "オレンジ", "マゼンタ"],
        "numbers": [2, 7],
        "directions": ["南"],
        "activities": ["人と会う", "ライブ音楽", "発表・パフォーマンス", "高強度トレーニング"],
        "foods": ["苦味のある葉物", "温かいスパイス", "コーヒーかお茶"],
        "practices": [
            "今週、静かに抱えてきた思いをひとつ声に出しましょう。",
            "目に見えることをしましょう——投稿、発表、パフォーマンス。小さくても。",
            "温かい人がいる場に身を置きましょう。",
        ],
    },
    "GROUND": {
        "element": "土",
        "keywords": ["安定", "信頼", "忍耐"],
        "colors": ["黄色", "茶色", "ベージュ", "黄土色"],
        "numbers": [5, 10],
        "directions": ["南西", "北東", "中央"],
        "activities": ["料理", "陶芸", "ゆっくりした散歩", "日記", "グラウンディング"],
        "foods": ["根菜", "全粒穀物", "適度な甘味"],
        "practices": [
            "週に一度は画面のない食事をしましょう。",
            "家を思い出させる品をひとつ、そばに置きましょう。",
            "今週、頭ではなく手ですることをひとつしましょう。",
        ],
    },
    "EDGE": {
        "element": "金",
        "keywords": ["明晰さ", "構造", "精密さ"],
        "colors": ["白", "銀", "メタリックゴールド"],
        "numbers": [4, 9],
        "directions": ["西", "北西"],
        "activities": ["筋力トレーニング", "片づけ", "楽器を習う", "編集作業"],
        "foods": ["刺激の強いスパイス", "ナッツと種", "白身魚"],
        "practices": [
            "引き出しひとつ、受信箱ひとつ、リストひとつを整えましょう。",
            "今週、和らげずにそのまま伝えましょう。",
            "答えを出す前に質問をひとつしましょう。",
        ],
    },
    "FLOW": {
        "element": "水",
        "keywords": ["適応力", "知恵", "深さ"],
        "colors": ["黒", "ネイビー", "濃いグレー"],
        "numbers": [1, 6],
        "directions": ["北"],
        "activities": ["水泳", "瞑想", "日記", "音楽", "長い会話"],
        "foods": ["海藻", "黒豆", "適度な塩味"],
        "practices": [
            "未解決の問いをひとつ、答えを強要せずに抱えてみましょう。",
            "今週、意識の流れを1ページ書きましょう。",
            "計画のないことにひとつ「はい」と言いましょう。",
        ],
    },
}

def _ja(s): return bool(s) and bool(KANA_RE.search(s))

def main():
    print("=" * 60); print("[Phase 4-12] lucky_code LUCKY_CODE_CONTENT"); print("=" * 60)
    if not JA.exists(): print(f"❌ {JA}"); return 1
    data = json.loads(JA.read_text(encoding="utf-8"))
    data.setdefault("LUCKY_CODE_CONTENT", {})
    for sig, tr in T.items():
        data["LUCKY_CODE_CONTENT"].setdefault(sig, {}).update(tr)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(payload)
    JA.write_text(payload, encoding="utf-8")
    print(f"✅ {len(T)} sigs 저장")
    print("\n[verify]")
    ok = True
    for sig in T:
        d = data["LUCKY_CODE_CONTENT"][sig]
        if not _ja(d.get("element", "")): print(f"  [ERR] {sig}.element"); ok = False
        for key in ("keywords", "colors", "directions", "activities", "foods", "practices"):
            for i, s in enumerate(d.get(key, [])):
                if not _ja(s): print(f"  [ERR] {sig}.{key}[{i}]"); ok = False
    if ok: print("  [OK] LUCKY_CODE_CONTENT 5/5 = JA")
    print("=" * 60)
    return 0 if ok else 1

if __name__ == "__main__": sys.exit(main())