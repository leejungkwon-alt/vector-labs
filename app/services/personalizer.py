# app/services/personalizer.py
from app.services.content.loader import load_pack

def generate_personalized_notes(profile: dict, lang: str = "en") -> list[str]:
    pack = load_pack(lang, "personalization")
    insights = []
    structure = profile.get("structure", {})

    energy_sig = profile.get("energy_signature", {})
    dominant = energy_sig.get("dominant", [])
    if dominant:
        dom_note = pack.get("ELEMENT_DOMINANT", {}).get(dominant[0])
        if dom_note: insights.append(dom_note)

    deficient = energy_sig.get("deficient", [])
    missing = energy_sig.get("missing", [])
    target_def = (deficient + missing)
    if target_def:
        def_note = pack.get("ELEMENT_DEFICIENT", {}).get(target_def[0])
        if def_note: insights.append(def_note)

    gyeokguk = structure.get("gyeokguk")
    if gyeokguk:
        gyeok_note = pack.get("GYEOKGUK", {}).get(gyeokguk)
        if gyeok_note: insights.append(gyeok_note)

    traits = profile.get("special_traits", [])
    if traits:
        trait_note = pack.get("SINSAL", {}).get(traits[0])
        if trait_note: insights.append(trait_note)
            
    rel_summary = structure.get("relations", {}).get("summary", {})
    relations_pack = pack.get("RELATIONS", {})
    if rel_summary.get("day_chong") and relations_pack.get("day_chong"):
        insights.append(relations_pack["day_chong"])
    elif rel_summary.get("has_chong") and relations_pack.get("has_chong"):
        insights.append(relations_pack["has_chong"])

    special_pack = pack.get("SPECIAL_CONDITIONS", {})
    if "RESTLESS_FEET" in traits and special_pack.get("RESTLESS_FEET"):
        insights.append(special_pack["RESTLESS_FEET"])

    return insights
