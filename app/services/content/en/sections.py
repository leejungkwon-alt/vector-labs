# app/services/content/en/sections.py
SECTION_TITLES = {"cover": "Your Chart", "core": "Your Core", "energy": "Your Energy Signature", "lucky_code": "Your Lucky Code", "health": "Body & Wellness", "money": "Money & Wealth", "work": "Work & Craft", "bonds": "Bonds & Belonging", "year": "This Year", "timeline": "Your Timeline", "monthly": "Your Monthly Calendar", "chart": "Your Four Faces", "sinsal": "Special Traits"}
SUMMARY_LABELS = {"core": "Core", "energy": "Energy", "lucky_code": "Lucky Code", "health": "Body", "money": "Money Mode", "bonds": "Bonds", "year": "This Year", "monthly": "Monthly"}
INTENSITY_LABELS = {"SELF_SOURCED": "Self-Sourced", "BALANCED_CORE": "Balanced Core", "ENVIRONMENT_TUNED": "Environment-Tuned"}
MODE_DISPLAY = {
    "THE_STEWARD": "Steward", "THE_OPERATOR": "Operator", "THE_FLOW": "Flow",
    "THE_CREATOR": "Creator", "THE_CHALLENGER": "Challenger", "THE_OFFICER": "Officer",
    "THE_SURVIVOR": "Survivor", "THE_MYSTIC": "Mystic", "THE_MENTOR": "Mentor", "THE_GENERALIST": "Generalist",
    "THE_TWIN": "Twin", "THE_RIVAL": "Rival", "THE_ALLY": "Ally", "THE_EMPATH": "Empath",
}
ENERGY_HERO_TEMPLATES = {"missing": "You run on {dominant} — with almost no {missing}.", "deficient": "You lead with {dominant}, but carry a quiet lack of {deficient}.", "default": "You run on {dominant}."}
TIMELINE_HERO = "Your strongest decade starts around age {best_age} ({best_pillar}). Your most challenging starts around age {worst_age}."
TIMELINE_GRADE_BLURB = {"PEAK": "A rare window. Use it deliberately.", "FAVORABLE": "Tailwinds. Move with them.", "NEUTRAL": "Mixed. Pay attention to what's actually working.", "CAUTION": "Slower season. Prioritize rest and boundaries.", "CHALLENGING": "Heavy period. Survive it well and you'll grow."}
LUCKY_CODE_HERO_TEMPLATE = "Your power element is {element} — lean into it."
WATCH_OUT_LABEL = "Watch out"
HEALTH_HERO_TEMPLATES = {"missing": "{dominant} dominates — you have almost no {missing}.", "deficient": "{dominant} shapes you most; {deficient} runs low.", "default": "{dominant} shapes you."}
CHART_POSITION_TEMPLATES = {
    "year_pillar":  "In your origins, {archetype} shaped how you first met the world.",
    "month_pillar": "In your public work, {archetype} is how you show up.",
    "day_pillar":   "{archetype} is your core — this is who you are.",
    "hour_pillar":  "In your legacy, {archetype} will define what you leave behind.",
}

CHART_NOTE_TEMPLATE = "Your {a} and {b} share the same '{archetype}' energy. This means they're inseparable — your public life and your core are one."

DISCLAIMER = (
    "Note: This report combines astronomical calculations with modern coaching "
    "frameworks for personal insight and entertainment. It is not medical, financial, "
    "or psychological advice. Traditional Four Pillars analysis is school-dependent — "
    "different lineages can reach different conclusions from the same chart, in the "
    "same way different therapists can describe the same person differently. Treat "
    "this as one thoughtful reading, not a verdict. Your decisions remain your own."
)

MONEY_CONTENT = {
    "THE_STEWARD": {
        "headline": "You have a natural gift for building wealth slowly.",
        "body": (
            "You'd rather compound something boring than gamble on a hype. Money, for you, is a tool that rewards patience and discipline.\n\n"
            "You are drawn to tangible assets and stable systems that grow in value over time. While others chase quick wins, you quietly build real, lasting wealth through saving and reinvesting.\n\n"
            "However, playing it too safe might mean missing out on life-changing opportunities. Allowing yourself a small, calculated risk occasionally can make your portfolio even more resilient."
        ),
        "action": "Review one 'safe' asset this month. Not to change it, just to know exactly what you own.",
    },
    "THE_OPERATOR": {
        "headline": "You see money as energy that needs to move.",
        "body": (
            "You spot opportunities where others just see noise. You've probably made money in surprising ways. This isn't just luck; it's instinct.\n\n"
            "You hate seeing money stuck. You instinctively know that money creates value when it circulates. You excel at creating multiple income streams and taking bold risks to grow your wealth.\n\n"
            "But when money flows too fast, the leaks are usually just as big. Build a safety net when cash flow is good. What you need isn't speed, but a brake."
        ),
        "action": "Pick one flowing asset and let it settle this month. You need a boring anchor to balance your dynamic nature.",
    },
    "THE_FLOW": {
        "headline": "Your money moves when your life moves.",
        "body": (
            "You don't have a fixed relationship with money. When your life is aligned, money follows. When it's not, things feel stuck no matter what you do.\n\n"
            "Your financial sense is highly intuitive. Rather than rigid budgets, you care more about where your energy is going today. When you stop chasing money and flow with your inner rhythm, opportunities naturally find you.\n\n"
            "But this flexibility can sometimes lead to a lack of planning. You must set up a minimum emergency fund for tough times."
        ),
        "action": "Look at your three biggest expenses this month. Do they actually reflect who you are right now?",
    },
}


WORK_CONTENT = {
    "THE_CREATOR": {
        "headline": "You thrive when you can see your own mark on the work.",
        "body": (
            "You're allergic to meaningless busywork. You need to build something from scratch or add your unique voice to it.\n\n"
            "Your mind is always swirling with ideas. You feel the greatest sense of achievement when you bring them into the world and inspire others. You shine in autonomous environments where you can express your creativity.\n\n"
            "But you must also accept the pain of being a creator. You are easily hurt when your ideas run dry or your work is undervalued. Learn to detach from the outcome and enjoy the process itself."
        ),
        "action": "Block out 90 minutes this week for pure creation, with zero interruptions.",
    },
    "THE_CHALLENGER": {
        "headline": "You're at your best when things are broken and need fixing.",
        "body": (
            "You don't need a perfect system; you need a real problem. You see what's not working before anyone else does.\n\n"
            "You are an innovator who hates the status quo. You ask 'Why do we do it this way?' and find better paths. You become a true leader in a crisis.\n\n"
            "But if criticizing becomes a habit, people might see you as negative. Don't just point out the problems; offer solutions and alternatives."
        ),
        "action": "Speak up about one quiet frustration to someone who actually has the power to change it.",
    },
    "THE_OFFICER": {
        "headline": "You do your best work inside a structure worth believing in.",
        "body": (
            "You need rules that make sense. In the right team, you are the rock. In the wrong one, you just burn out.\n\n"
            "You value principles and fairness. You have the ability to build and maintain systems that allow others to work safely. You earn trust through your strong sense of responsibility and reliability.\n\n"
            "But being too attached to the rules can make you seem inflexible. Remember that sometimes people matter more than the protocol."
        ),
        "action": "Write down three values your work should embody. Are you currently in a place that shares them?",
    },
    "THE_SURVIVOR": {
        "headline": "You grow under pressure, but the pressure has to have a point.",
        "body": (
            "You have a high tolerance for hard work, but you know when the cost is too high. You've walked away from things that would break others.\n\n"
            "You instinctively enter survival mode in a crisis. You have the energy to break through when others say it's impossible. You turn adversity into a stepping stone for growth.\n\n"
            "But your toughness can be seen as cold or ruthless by those around you. Don't forget that showing vulnerability is also a form of true strength."
        ),
        "action": "Remember the last time you chose yourself over a deadline. Remember why you did it.",
    },
    "THE_MYSTIC": {
        "headline": "You think sideways, and that's your superpower.",
        "body": (
            "You see connections others miss. Your best work takes the long way around. When it lands, it lands differently.\n\n"
            "Your intuition and insight are exceptional. You see the essence behind surface phenomena. Deep focus work — research, analysis, strategy — is where you excel.\n\n"
            "But thinking too deeply can delay action. Start before the perfect picture is formed. The path opens as you walk."
        ),
        "action": "Give yourself one unstructured hour this week. Follow whatever thread pulls you without a goal.",
    },
    "THE_MENTOR": {
        "headline": "You thrive when you're helping someone else grow.",
        "body": (
            "You don't just want to be good; you want to make others good. Your best work is often invisible, happening inside someone else.\n\n"
            "You have a natural talent for sharing knowledge and experience. You recognize the potential in juniors or peers and nurture them to flourish.\n\n"
            "But helping others grow might cause you to neglect your own. Show that you are still learning and growing yourself; it will inspire others even more."
        ),
        "action": "Reach out to someone you've helped and tell them what potential you saw in them.",
    },
    "THE_GENERALIST": {
        "headline": "You're the person who can do a little of everything.",
        "body": (
            "You aren't a specialist, and that's your strength. You hold projects together across different fields. You're needed exactly where the seams are.\n\n"
            "You prefer broad experiences over digging deep into one thing. You are actually a 'T-shaped' talent who connects different domains to create new value.\n\n"
            "You might be told you lack depth. For your breadth to be a true strength, you need to build at least one 'spike' — an area where no one can match you."
        ),
        "action": "Pick two skills you usually keep separate and find one project that requires both.",
    },
}


BONDS_CONTENT = {
    "THE_TWIN": {
        "headline": "You bond through equals, not audiences.",
        "body": (
            "You don't want a leader or a follower; you want a partner walking in the same direction. You don't need to be needed — you need to be met.\n\n"
            "You maintain a horizontal perspective with people. You value relationships where you both acknowledge differences and grow together.\n\n"
            "But seeking only 'cool' relationships can make deep intimacy hard. You need to learn to lean on each other occasionally to truly get close."
        ),
        "action": "Text someone who meets you at your level. Not to ask for anything, just to connect.",
    },
    "THE_RIVAL": {
        "headline": "You bond through friction as much as warmth.",
        "body": (
            "You need people who push back. Your best relationships have a competitive edge to them, and that's exactly what keeps them alive.\n\n"
            "You find inspiration in conversations with people who have different opinions. You enjoy relationships where you exchange sharp feedback and refine each other.\n\n"
            "But not every conversation needs to be an argument. You need the empathy to understand if the other person is looking for comfort or advice right now."
        ),
        "action": "Reach out to someone you've had productive tension with and ask for their real opinion.",
    },
    "THE_ALLY": {
        "headline": "You bond through loyalty and shared standards.",
        "body": (
            "You don't collect people. You choose them carefully, and then you stay. Your loyalty is quiet but unmistakable.\n\n"
            "You value loyalty very highly. You are the first to rush to help a friend or family member in trouble. Your steadfastness makes many people trust and rely on you.\n\n"
            "But your loyalty can sometimes be a burden to the other person. Letting go of the obsession to solve everything for them and watching them stand up on their own is also a form of love."
        ),
        "action": "Check in on someone you've been meaning to talk to. Not because you have to, but because you want to.",
    },
    "THE_EMPATH": {
        "headline": "You bond by feeling what the other person feels.",
        "body": (
            "You read people fast and accurately. You know when someone is off before they do. This makes you a rare friend — but protect your own energy.\n\n"
            "You have a deep empathy that feels others' pain as your own. People gather around you because you understand their hearts without them speaking.\n\n"
            "But over-empathizing means you often neglect your own feelings and get exhausted. You must practice setting healthy psychological boundaries."
        ),
        "action": "Once this week, check: 'Is this emotion mine, or am I carrying someone else's?'",
    },
}


# 위기 안내 (append by _fix_compliance_gaps)
DISCLAIMER = DISCLAIMER + (
    " If you are in crisis, contact local emergency services or a suicide "
    "prevention hotline. If you are outside the US, see https://findahelpline.com/."
)
