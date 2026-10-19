# app/services/content/en/health.py
"""
EN Health section — 오행 과다/부족 → 신체 부위 매핑.

전통 황제내경(黃帝內經) 오행-장부 매핑을 사용. 의학적 진단이 아니라
"이런 경향이 있다" 수준의 참고 정보.
"""

HEALTH_DISPLAY = {
    "GROWTH": "Growth",
    "SPARK":  "Spark",
    "GROUND": "Ground",
    "EDGE":   "Edge",
    "FLOW":   "Flow",
}

# 오행 → 신체 부위 (황제내경 기준)
ELEMENT_ORGANS = {
    "GROWTH": {
        "zang": "Liver",
        "fu": "Gallbladder",
        "openings": ["eyes", "sinews"],
        "emotion": "anger",
    },
    "SPARK": {
        "zang": "Heart",
        "fu": "Small intestine",
        "openings": ["tongue", "blood vessels"],
        "emotion": "overexcitement",
    },
    "GROUND": {
        "zang": "Spleen",
        "fu": "Stomach",
        "openings": ["mouth", "muscle"],
        "emotion": "rumination",
    },
    "EDGE": {
        "zang": "Lungs",
        "fu": "Large intestine",
        "openings": ["nose", "skin and hair"],
        "emotion": "grief",
    },
    "FLOW": {
        "zang": "Kidneys",
        "fu": "Bladder",
        "openings": ["ears", "bones"],
        "emotion": "fear",
    },
}

HEALTH_CONTENT = {
    "GROWTH": {
        "over_pattern": (
            "With growth energy in excess, the liver–gallbladder system and nervous system "
            "run hot. You may notice tension in the neck and shoulders, headaches from stress, "
            "or a mind that won't slow down at night."
        ),
        "under_pattern": (
            "With growth energy scarce, you can struggle to *start* — physically and mentally. "
            "Stiffness, low motivation, and a sense of being stuck tend to cluster."
        ),
        "practices": [
            "A daily 10-minute walk with no goal. Movement, not exercise.",
            "One 'no' this week to something you'd normally say yes to.",
            "Stretch your neck, jaw, and hips before bed. Holding stress there is a pattern.",
        ],
    },
    "SPARK": {
        "over_pattern": (
            "Excess spark energy can overload the heart and vascular system. "
            "Watch for racing thoughts, trouble falling asleep, or a nervous system that "
            "runs hot even when you're sitting still."
        ),
        "under_pattern": (
            "Scarce spark energy often shows up as low motivation, cold hands and feet, "
            "or feeling emotionally flat for no clear reason."
        ),
        "practices": [
            "Ten minutes of silence before you check your phone in the morning.",
            "Notice one small pleasure today. Name it out loud.",
            "Don't schedule anything after 9pm for one week.",
        ],
    },
    "GROUND": {
        "over_pattern": (
            "Excess ground energy can slow digestion and dull the appetite for change. "
            "You might feel heavy, sluggish, or 'not in the mood' for weeks at a time."
        ),
        "under_pattern": (
            "Scarce ground energy often means unstable digestion, low blood sugar dips, "
            "or feeling ungrounded — like your body isn't fully yours."
        ),
        "practices": [
            "One warm meal a day, eaten slowly, sitting down.",
            "Take your shoes off and stand on real ground for 5 minutes.",
            "Eat at the same time for three days in a row.",
        ],
    },
    "EDGE": {
        "over_pattern": (
            "Excess edge energy hits the lungs and skin first. You may notice tightness in "
            "the chest, dry cough, or a habit of holding your breath under stress."
        ),
        "under_pattern": (
            "Scarce edge energy often shows as shallow breathing, weak immunity, or a "
            "hard time setting boundaries that protect your own energy."
        ),
        "practices": [
            "Three slow, deep breaths before opening email.",
            "One thing you clean up today — a desk, a drawer, a list.",
            "Spend 10 minutes outside, even if it's cold.",
        ],
    },
    "FLOW": {
        "over_pattern": (
            "Excess water energy can drag the kidneys and bladder into overdrive. "
            "Watch for fatigue that sleep doesn't fix, coldness in the lower body, "
            "or a tendency to feel everything everyone else feels."
        ),
        "under_pattern": (
            "Scarce water energy often shows as low reserves — dry skin, aching lower back, "
            "or a deep tiredness that sits in your bones."
        ),
        "practices": [
            "Drink a full glass of water before every meal.",
            "One full rest day this month with no output.",
            "Sit quietly for 5 minutes with an unresolved question. No answer required.",
        ],
    },
}


HEALTH_DISCLAIMER = (
    "This section draws on traditional East Asian medicine's Five Elements-organ "
    "mapping. It is not a medical diagnosis or treatment plan. Consult a qualified "
    "healthcare professional for any health concern."
)

HEALTH_FRAMEWORK_NOTE = (
    "Framework: Huangdi Neijing (Yellow Emperor's Inner Canon). Traditional theory, "
    "not clinical guidance. Individual results vary; schools of interpretation differ."
)