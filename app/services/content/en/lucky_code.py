# app/services/content/en/lucky_code.py
"""
EN Lucky Code pack — 용신 처방 + 삶의 영역 확장.
"""

LUCKY_CODE_CONTENT = {
    "GROWTH": {
        "element": "Wood",
        "keywords": ["expansion", "direction", "initiative"],
        "colors": ["Forest green", "Jade", "Olive"],
        "numbers": [3, 8],
        "directions": ["East", "Southeast"],
        "activities": ["Morning walks", "Hiking", "Gardening", "Reading", "Starting something small"],
        "foods": ["Leafy greens", "Sour foods", "Fresh herbs"],
        "practices": [
            "Start one thing this week without a full plan.",
            "Spend 20 minutes in nature — not as fitness, just as presence.",
            "Write one direction you're moving toward, and one you're not.",
        ],
    },
    "SPARK": {
        "element": "Fire",
        "keywords": ["expression", "warmth", "visibility"],
        "colors": ["Red", "Orange", "Magenta"],
        "numbers": [2, 7],
        "directions": ["South"],
        "activities": ["Social gatherings", "Live music", "Performance", "High-intensity training"],
        "foods": ["Bitter greens", "Warm spices", "Coffee or tea"],
        "practices": [
            "Say one thing out loud this week you've been feeling quietly.",
            "Do something visible — post, present, perform. Even small.",
            "Put yourself in a room with warm people.",
        ],
    },
    "GROUND": {
        "element": "Earth",
        "keywords": ["stability", "trust", "patience"],
        "colors": ["Yellow", "Brown", "Beige", "Ochre"],
        "numbers": [5, 10],
        "directions": ["Southwest", "Northeast", "Center"],
        "activities": ["Cooking", "Pottery", "Slow walks", "Journaling", "Grounding"],
        "foods": ["Root vegetables", "Whole grains", "Sweet foods in moderation"],
        "practices": [
            "Eat one meal a week with no screen.",
            "Keep one physical object near you that reminds you of home.",
            "Do one thing this week with your hands, not your mind.",
        ],
    },
    "EDGE": {
        "element": "Metal",
        "keywords": ["clarity", "structure", "precision"],
        "colors": ["White", "Silver", "Metallic gold"],
        "numbers": [4, 9],
        "directions": ["West", "Northwest"],
        "activities": ["Strength training", "Decluttering", "Learning an instrument", "Editing something"],
        "foods": ["Pungent spices", "Nuts and seeds", "White fish"],
        "practices": [
            "Declutter one drawer, one inbox, one list.",
            "Say the direct thing this week — without softening it.",
            "Ask one question before giving the answer.",
        ],
    },
    "FLOW": {
        "element": "Water",
        "keywords": ["adaptability", "wisdom", "depth"],
        "colors": ["Black", "Navy", "Deep gray"],
        "numbers": [1, 6],
        "directions": ["North"],
        "activities": ["Swimming", "Meditation", "Journaling", "Music", "Long conversations"],
        "foods": ["Sea vegetables", "Black beans", "Salty foods in moderation"],
        "practices": [
            "Sit with one unresolved question without forcing an answer.",
            "Write a page of stream-of-consciousness this week.",
            "Say yes to one thing that has no clear plan.",
        ],
    },
}


LUCKY_CODE_DOMAINS = {
    "GROWTH": {
        "career": "Teaching, publishing, gardening, fashion, planning, education — roles where you grow people or projects.",
        "wealth": "Growth assets: equity in things you help build, long positions, income that compounds.",
        "relationships": "Peer relationships that push you forward. Find people who grow alongside you, not toward you.",
        "learning": "Deep study over fast skimming. One topic for a year beats ten for a month.",
        "everyday": "Start things small and often. Forward motion is your medicine.",
        "avoid": ["Waiting for perfect conditions", "Perfectionist paralysis", "Sitting still for too long"],
    },
    "SPARK": {
        "career": "Marketing, media, IT, energy, hospitality, entertainment — anything that needs visibility and heat.",
        "wealth": "Opportunistic, high-agility positions. Size matters less than speed.",
        "relationships": "Warm, expressive people who don't need you to be quiet. Small talk is not your enemy.",
        "learning": "Learn out loud. Teach what you're learning before you master it.",
        "everyday": "One visibly warm gesture a day. Text, call, thank someone.",
        "avoid": ["Being the only light in a dark room", "Saying yes to every invitation", "Running on empty"],
    },
    "GROUND": {
        "career": "Real estate, construction, education, brokerage, agriculture — anything with a foundation under it.",
        "wealth": "Real assets. Long holds. Savings you don't touch. Boring is your alpha.",
        "relationships": "Few, deep, steady. Loyalty over novelty. Quality time beats quality words.",
        "learning": "Structured programs. Teachers with credentials. Certifications over inspiration.",
        "everyday": "Same wake time. Same meal time. Rhythm is the whole game.",
        "avoid": ["Chasing the new thing every quarter", "Speed for its own sake", "Change without reason"],
    },
    "EDGE": {
        "career": "Finance, law, military, police, medicine, engineering — work with rules, precision, and consequence.",
        "wealth": "Disciplined portfolios. Risk-managed positions. Cutting losses clean.",
        "relationships": "Directness is your love language. People who can take your real opinion. Nothing performative.",
        "learning": "Formal training. Apprenticeships. Systems and frameworks over inspiration.",
        "everyday": "One thing cleaned, one thing said, one line drawn.",
        "avoid": ["Winning the argument at all costs", "Emotional coldness masked as honesty", "Over-structuring your life"],
    },
    "FLOW": {
        "career": "Trading, logistics, travel, consulting, research, anything that moves or connects.",
        "wealth": "Flowing assets. Multiple income streams. Money that circulates rather than sits.",
        "relationships": "Deep, quiet, unhurried. People you can think with, not just talk to.",
        "learning": "Slow, immersive study. You learn by absorbing, not by drilling.",
        "everyday": "Say yes to one unplanned thing a week. Keep the current moving.",
        "avoid": ["Committing too early", "Over-analyzing instead of acting", "Scattering focus"],
    },
}