# app/services/content/en/monthly.py
"""
EN monthly luck pack.

Monthly is tactical: brief, actionable.
"""

MONTHLY_THEME_CONTENT = {
    "TEN_GOD_FRIEND": {
        "name": "The Alignment Month",
        "headline": "Your own energy returns.",
        "body": "This month mirrors who you already are. Confidence comes easy — so does stubbornness. Peer dynamics surface. You'll feel like you're meeting yourself.",
        "watch_for": "Digging into a position without checking it.",
        "lean_into": "Solo work. Personal projects. Anything with your name on it.",
    },
    "TEN_GOD_ROB_WEALTH": {
        "name": "The Push Month",
        "headline": "Drive amplified. So is impatience.",
        "body": "High-output month. Move fast, but pace yourself. This month rewards boldness and punishes burnout equally. Pick your one big move.",
        "watch_for": "Competing with people who aren't your rivals.",
        "lean_into": "One ambitious target. Move with intent, not motion.",
    },
    "TEN_GOD_EATING_GOD": {
        "name": "The Creative Month",
        "headline": "Softer, generative energy.",
        "body": "Make things. Not grind — create. This month rewards play over production and gives you output that surprises even you.",
        "watch_for": "Over-scheduling. This month needs whitespace.",
        "lean_into": "Craft. Play. Get ideas out of your head.",
    },
    "TEN_GOD_HURTING_OFFICER": {
        "name": "The Breakthrough Month",
        "headline": "Sharp voice, sharp vision.",
        "body": "You'll see what's broken more clearly this month — and want to say so. Used well, this is a month you shift something real.",
        "watch_for": "Saying the true thing at the wrong moment.",
        "lean_into": "System-level change. Not complaint — the fix.",
    },
    "TEN_GOD_INDIRECT_WEALTH": {
        "name": "The Horizon Month",
        "headline": "Doors open — and close fast.",
        "body": "Opportunities appear and disappear. Your instinct is sharp; so is your urge to chase everything. Focus on one or two.",
        "watch_for": "Saying yes because FOMO is loud.",
        "lean_into": "One or two openings, done deeply.",
    },
    "TEN_GOD_DIRECT_WEALTH": {
        "name": "The Grounding Month",
        "headline": "Slow, steady, real.",
        "body": "Not a dramatic month — and that's the gift. What you build now compounds quietly. Boring is the strategy.",
        "watch_for": "Impatience. This month rewards patience, not ambition.",
        "lean_into": "Routines. Systems. Consistent, small actions.",
    },
    "TEN_GOD_SEVEN_KILLINGS": {
        "name": "The Forge Month",
        "headline": "Weight, and what you become under it.",
        "body": "This month brings pressure. Not necessarily bad — often useful — but heavy. Meet it with rest, not more force.",
        "watch_for": "Saying yes to responsibilities that aren't yours.",
        "lean_into": "Boundaries. Rest. The people who hold you steady.",
    },
    "TEN_GOD_DIRECT_OFFICER": {
        "name": "The Milestone Month",
        "headline": "Things align.",
        "body": "Structure helps this month. Promotions, commitments, recognitions — the forms of success that involve other people — are unusually available.",
        "watch_for": "Playing small to avoid being seen.",
        "lean_into": "Formal commitments. Public milestones.",
    },
    "TEN_GOD_INDIRECT_RESOURCE": {
        "name": "The Cave Month",
        "headline": "Depth before output.",
        "body": "This month pulls you inward. You'll read more, think more, want more alone time. Not depression — incubation.",
        "watch_for": "Forcing visibility before you're ready.",
        "lean_into": "Reading. Research. Solitude.",
    },
    "TEN_GOD_DIRECT_RESOURCE": {
        "name": "The Sanctuary Month",
        "headline": "Rest and rebuild.",
        "body": "This month is kind. Nourishment is available if you stop forcing productivity. Support shows up if you let it.",
        "watch_for": "Mistaking rest for laziness.",
        "lean_into": "Nourishment. Mentorship. Whatever refills your cup.",
    },
}


DEFAULT_MONTHLY_THEME = {
    "name": "The Unfolding Month",
    "headline": "A month still taking shape.",
    "body": "This month's energy is hard to pin to a single pattern. Pay attention — the theme will reveal itself.",
    "watch_for": "Assuming you already know what this month is about.",
    "lean_into": "Staying curious about what's actually happening.",
}

MONTHLY_HERO_TEMPLATE = "Your {year}, twelve doors."

GRADE_LABEL = {
    "PEAK": "Peak",
    "FAVORABLE": "Favorable",
    "NEUTRAL": "Neutral",
    "CAUTION": "Caution",
    "CHALLENGING": "Challenging",
}


MONTHLY_GRADE_CONTEXT = {
    "PEAK": "Root energy (地支) is favorable this month — separate from the theme.",
    "FAVORABLE": "Gentle tailwinds from the root energy.",
    "NEUTRAL": "Mixed root energy — the theme carries the month.",
    "CAUTION": "Root energy is cautious — keep the pace slow.",
    "CHALLENGING": "Heavy root energy — protect your margins.",
}

