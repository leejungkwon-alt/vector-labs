# app/services/content/en/energy.py
"""
Energy Signature content.

5 오행 시그니처 × 3 역할(dominant / deficient / missing).
"""

ELEMENT_DISPLAY = {
    "GROWTH": "Growth",
    "SPARK": "Spark",
    "GROUND": "Ground",
    "EDGE": "Edge",
    "FLOW": "Flow",
}

ELEMENT_KEYWORDS = {
    "GROWTH": ["expansion", "direction", "initiative"],
    "SPARK": ["expression", "warmth", "visibility"],
    "GROUND": ["stability", "trust", "patience"],
    "EDGE": ["clarity", "structure", "precision"],
    "FLOW": ["adaptability", "wisdom", "depth"],
}

ELEMENT_CONTENT = {
    "GROWTH": {
        "on_dominant": "You have an overabundance of growth energy. It shows up as relentless forward motion — you start things easily, and you rarely feel finished.",
        "on_deficient": "Growth is one of your scarcest energies. You can struggle to start things without a clear reason, or to keep growing something once the novelty fades.",
        "on_missing": "You have almost no growth energy in your chart. This isn't a flaw — it means you operate from a different center, and 'expansion for its own sake' will never motivate you.",
    },
    "SPARK": {
        "on_dominant": "Your chart is fire-heavy. You run hot, you radiate visibly, and you don't do subtle. The risk is burnout — everyone wants a piece of the warmth.",
        "on_deficient": "Spark is one of your scarcest energies. You don't perform enthusiasm, and you're not here for volume. Your warmth is quieter than most.",
        "on_missing": "You have almost no spark energy. You're drawn to people who carry it — they're the light that makes your own quiet work visible.",
    },
    "GROUND": {
        "on_dominant": "You have deep ground energy. You're the person others anchor to, and you don't even notice you're doing it. The risk is holding too much for too long.",
        "on_deficient": "Ground is one of your scarcest energies. You can struggle to stay still, or to make peace with slow progress. You probably move more than you'd admit.",
        "on_missing": "You have almost no ground energy. Stability isn't your default state — you find your footing by moving, not by settling.",
    },
    "EDGE": {
        "on_dominant": "Your chart is metal-heavy. You cut through the noise. You'd rather be right than liked, and you're usually right. The risk is losing the room while winning the point.",
        "on_deficient": "Edge is one of your scarcest energies. You can avoid conflict even when it's the right call, and you soften things that don't need softening.",
        "on_missing": "You have almost no edge energy. Structure and precision aren't what you lead with — you lead with something warmer, and that's not a weakness.",
    },
    "FLOW": {
        "on_dominant": "Your chart is water-heavy. You move easily, adapt easily, and know when to wait. The risk is never quite committing to anything because everything is possible.",
        "on_deficient": "Flow is one of your scarcest energies. You can struggle to go with the current — you want to know where things are going before you move.",
        "on_missing": "You have almost no flow energy. You don't drift; you decide. This makes you reliable in a crisis, but it can feel rigid when the situation calls for adaptability.",
    },
}