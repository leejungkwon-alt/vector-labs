"""
fix_zh_cn_retranslation.py

- C-1: zh_cn core_pillars 36개 narrative[0] 재번역
- C-2: element "四"/"Cuatro" -> "火"/"Fuego"
- C-3: element "木材"/"地球"/"金属" -> "木"/"土"/"金"
- C-4: 辛巳 이름 "发情"/"celo" -> 정정

사용:
    python fix_zh_cn_retranslation.py
    python -m pytest -q
    git add -A
    git commit -m "i18n(zh_cn,es): retranslate 36 pillar narratives and fix element/name errors"
"""
import json
import pathlib

DATA = pathlib.Path(__file__).resolve().parent / "app" / "services" / "content" / "data"


# ── C-1: narrative[0] 재번역 ─────────────────────────────
NARRATIVE_ZH = {
    # 甲
    "甲子": "你是一棵在月光下生长的树。即使身处黑暗，你也不会迷失方向——你依然静静地向上生长。",
    "甲寅": "你是森林里那棵参天大橡树。无论狂风如何肆虐，你都岿然不动，朝着属于自己的方向直指苍穹。",
    "甲午": "你就像一棵燃烧的树。你用你的热情点亮了整个房间——真是个极具魅力的人。",
    "甲辰": "你是一片龙栖之林。表面看似平凡，但其下正孕育着一幅足以撼动世界的宏大图景。",
    "甲申": "你是一棵扎根于岩石中的树。在恶劣的环境中，你会将根系扎得更深，变得更加坚韧。",
    "甲戌": "你就像一棵扎根于干涸土地上的树。你是一个负责任的人，凭借原则和决断坚守立场。",
    # 乙
    "乙丑": "你就像是冻土之下生机勃勃的藤蔓。地表是坚实的土壤——而地下，正为下一个春天默默做着准备。",
    "乙亥": "你是一株水边的垂柳。轻轻摇曳，而正是这份摇曳，触动了人们的心弦。",
    "乙卯": "你就像春日原野上的一朵野花。虽小，却比任何春花都开得更盛。",
    "乙巳": "你就像一片盛开的花坛。你用丰富多彩的色调装点着周围的一切——你是一个富有创造力的人。",
    "乙未": "你就像一株蔓延在干涸草地上的藤蔓。即使在贫瘠的土地上，你也能生存下来——你是一个充满生命力的人。",
    "乙酉": "你就像是整洁花园里的一朵花，是一位为了美丽而精心修饰自己的优雅之人。",
    # 己
    "己丑": "你是一片地下蕴藏着春天的原野。表面冰冷坚硬，而地下却仍沉睡着尚未苏醒的生命力。",
    "己亥": "你是一片浸透了水的沃土。深邃、宁静，蕴藏着你从不炫耀的丰饶。",
    "己卯": "你是一片田野，泉水正悄然渗入其中。树根从土壤中破土而出，而你正是孕育生机的通道。",
    "己巳": "你是一座沐浴在阳光下的花园。在你周围，一切都毫不费力地成熟——无论是人、项目，还是微小的生命。",
    "己未": "你是一片夏日的草地。在阳光下被晒得坚硬，也因此变得更加坚实。",
    "己酉": "你就像一片精心照料的花坛。你有着一双细腻的手，总是寻找真正能带来益处的美。",
    # 辛
    "辛丑": "你就像一颗镶嵌在冬日花园里的宝石。虽深埋于寒冷的土壤之中，但一旦光芒照耀到你身上，便无人能比你更璀璨夺目。",
    "辛亥": "你就像水中的宝石。静静地闪耀在深水中，照亮周围的真相。",
    "辛卯": "你就像是春日花园里的一块翡翠。在生机勃勃的万物间静静闪耀，并温柔地助它们成长。",
    "辛巳": "你是高温锻造而成的宝石。压力让你更加精炼，而非变得脆弱。",
    "辛未": "你是一颗镶嵌在干涸土地上的宝石。周遭虽已荒芜，你的轮廓却依然清晰分明。",
    "辛酉": "你是一颗完美切割的宝石。辛的能量凝聚为最纯粹的形态——一种不可动摇的美。",
    # 壬
    "壬子": "你是一片冬日大海。表面坚如冰层，而冰层之下，却有一股永不停息的暗流。",
    "壬寅": "你宛如大海与春天的交汇。融化的水滋养着树木——你的智慧正是那种能让人茁壮成长的智慧。",
    "壬辰": "你是一片龙栖之海。表面看似平凡，但深处却蕴藏着足以撼动世界的潜力。",
    "壬午": "你就像一片蕴藏着火焰的大海。表面清凉而深邃，深处却流淌着热量。",
    "壬申": "你就像那能穿透岩石的水。外表温和，但只要给它时间，就无人能挡。",
    "壬戌": "你就像渗入干涸土地的水。从表面看不见——但你流经之处，生命便悄然生长。",
    # 癸
    "癸丑": "你就像是冻土之下的一口井。表面冰冷坚硬，但地下却有永不干涸的水源。",
    "癸亥": "你就像一条深冬的河流。水面平静，水下却暗流涌动。",
    "癸卯": "你就像春雨中的花园。雨水静静地渗入——而正是这种静谧，让你帮助万物茁壮成长。",
    "癸巳": "你是一片雾气蒙蒙的湖。湖面朦胧，湖底却流淌着热流。",
    "癸未": "你就像夏日干涸的大地上的一缕露珠。如此珍贵——哪怕只有几滴，也足以让生命延续。",
    "癸酉": "你被月光照得通亮。静静地闪耀着，你的光芒让别人看清了自己的内心。",
}


def _save(path: pathlib.Path, data: dict) -> None:
    """JSON 저장 + 후행 개행 (git diff 최소화)."""
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def fix_c1() -> int:
    fixed = 0
    base = DATA / "zh_cn" / "core_pillars"
    for pillar, new_text in NARRATIVE_ZH.items():
        path = base / f"{pillar}.json"
        if not path.exists():
            print(f"  [SKIP] {pillar}.json 없음")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        narr = data.get("narrative")
        if not isinstance(narr, list) or not narr:
            print(f"  [WARN] {pillar}: narrative 배열 없음")
            continue
        if narr[0] == new_text:
            print(f"  [OK]   {pillar}: 이미 정상")
            continue
        narr[0] = new_text
        _save(path, data)
        fixed += 1
        print(f"  [FIX]  {pillar}")
    return fixed


ELEMENT_ZH_CORE = {
    "THE_PIONEER":    "木",
    "THE_ADAPTER":    "木",
    "THE_RADIATOR":   "火",
    "THE_KEEPER":     "火",
    "THE_ANCHOR":     "土",
    "THE_CULTIVATOR": "土",
    "THE_BLADE":      "金",
    "THE_GEM":        "金",
}


def fix_c2_c3() -> int:
    fixed = 0

    # zh_cn/core.json
    p = DATA / "zh_cn" / "core.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    arch = d.get("ARCHETYPE_CONTENT", {})
    changed = False
    for key, new in ELEMENT_ZH_CORE.items():
        if key in arch and arch[key].get("element") != new:
            print(f"  [FIX]  zh_cn/core.json {key}.element: "
                  f"{arch[key].get('element')!r} -> {new!r}")
            arch[key]["element"] = new
            changed = True
            fixed += 1
    if changed:
        _save(p, d)

    # es/core.json
    p = DATA / "es" / "core.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    arch = d.get("ARCHETYPE_CONTENT", {})
    changed = False
    for key in ("THE_RADIATOR", "THE_KEEPER"):
        if key in arch and arch[key].get("element") != "Fuego":
            print(f"  [FIX]  es/core.json {key}.element: "
                  f"{arch[key].get('element')!r} -> 'Fuego'")
            arch[key]["element"] = "Fuego"
            changed = True
            fixed += 1
    if changed:
        _save(p, d)

    # es/lucky_code.json SPARK
    p = DATA / "es" / "lucky_code.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    lc = d.get("LUCKY_CODE_CONTENT", {})
    if "SPARK" in lc and lc["SPARK"].get("element") != "Fuego":
        print(f"  [FIX]  es/lucky_code.json SPARK.element: "
              f"{lc['SPARK'].get('element')!r} -> 'Fuego'")
        lc["SPARK"]["element"] = "Fuego"
        _save(p, d)
        fixed += 1

    return fixed


def fix_c4() -> int:
    fixed = 0

    pairs = [
        # (path, key_path_list, bad_value, good_value, log_label)
        (DATA / "zh_cn" / "pillar_names.json",
         ["辛巳", "name"], "《发情中的珍宝》", "烈火中的宝玉",
         "zh_cn/pillar_names.json"),
        (DATA / "es" / "pillar_names.json",
         ["辛巳", "name"], "Jewel en celo", "Joya en el fuego",
         "es/pillar_names.json"),
    ]
    for path, keys, bad, good, label in pairs:
        if not path.exists():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        node = d
        for k in keys[:-1]:
            node = node.get(k, {})
        if node.get(keys[-1]) == bad:
            node[keys[-1]] = good
            _save(path, d)
            print(f"  [FIX]  {label} 辛巳.name -> {good!r}")
            fixed += 1

    # core_pillars/辛巳.json 은 이름을 최상위 "name" 에 보관
    for lang, bad, good in [
        ("zh_cn", "《发情中的珍宝》", "烈火中的宝玉"),
        ("es",    "Jewel en celo",   "Joya en el fuego"),
    ]:
        p = DATA / lang / "core_pillars" / "辛巳.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("name") == bad:
            d["name"] = good
            _save(p, d)
            print(f"  [FIX]  {lang}/core_pillars/辛巳.json name -> {good!r}")
            fixed += 1

    return fixed


if __name__ == "__main__":
    print("── C-1: 36개 narrative[0] 재번역 ──")
    n1 = fix_c1()
    print(f"\n── C-2/C-3: element 수정 ──")
    n2 = fix_c2_c3()
    print(f"\n── C-4: 辛巳 오역 수정 ──")
    n3 = fix_c4()
    print(f"\n완료: C-1={n1} / C-2·C-3={n2} / C-4={n3}")