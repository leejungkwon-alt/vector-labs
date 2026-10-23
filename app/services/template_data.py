# app/services/template_data.py

TEMPLATE_DATABASE = {
    "en": {
        "title": "Your Comprehensive Life Blueprint & Wellness Coaching Report",
        "intro": "Welcome to your deep-dive personal blueprint. This comprehensive report combines precise astronomical calculations with modern coaching psychology to offer profound insights into your core identity, wealth flow, career mastery, social dynamics, and energetic wellness.",
        
        "day_master_intro": "1. Core Essence: Your fundamental operating energy is represented by {day_pillar}.",
        "day_master_traits": {
            "甲": {
                "summary": "You embody the towering resilience and vertical growth of a giant oak. Naturally visionary and pioneering, you thrive when initiating new paths rather than following old tracks.",
                "strengths": ["Unwavering autonomy", "Progressive leadership", "High ideals"],
                "blind_spot": "Rigidity under pressure. Learning to bend like a flexible branch will protect you from burnout."
            },
            "乙": {
                "summary": "You flow with the agile, resilient grace of climbing ivy or wildflowers. Highly adaptable and intuitively intelligent, you navigate complex social and professional landscapes with finesse.",
                "strengths": ["Exceptional adaptability", "Empathy", "Subtle influence"],
                "blind_spot": "Over-accommodating others at the expense of your own boundary setting."
            },
            "丙": {
                "summary": "You radiate the bright, magnificent warmth of the midday sun. Naturally magnetic, optimistic, and expressive, you light up rooms and inspire collective momentum.",
                "strengths": ["Infectious passion", "Broad vision", "Generous charisma"],
                "blind_spot": "Risk of emotional exhaustion from trying to illuminate everyone else's path."
            },
            "丁": {
                "summary": "You carry the focused, warm glow of a sanctuary candle. Deeply empathetic, detail-oriented, and artistically perceptive, you notice subtle nuances that others overlook.",
                "strengths": ["Profound emotional intelligence", "Precise focus", "Artistic depth"],
                "blind_spot": "Internalizing stress and holding onto private worries."
            },
            "戊": {
                "summary": "You stand unshakeable like a majestic mountain range. Deeply grounded, reliable, and patient, you provide a stable anchor and a safe harbor for yourself and those around you.",
                "strengths": ["High trust", "Unyielding patience", "Structural reliability"],
                "blind_spot": "Resistance to sudden changes and unexpected pivots."
            },
            "己": {
                "summary": "You represent fertile, nurturing garden soil. Highly pragmatic, resourceful, and supportive, you cultivate real, tangible growth in collaborative projects and relationships.",
                "strengths": ["Practical problem-solving", "Nurturing capacity", "Quiet productivity"],
                "blind_spot": "Internalizing over-responsibility for everyone's success."
            },
            "庚": {
                "summary": "You carry the strength of refined, unyielding steel. Principled, decisive, and fiercely committed to integrity, you excel at cutting through noise to find objective truth.",
                "strengths": ["Laser-sharp focus", "Moral courage", "Decisive execution"],
                "blind_spot": "Approaching emotional situations with excessive cold logic."
            },
            "辛": {
                "summary": "You shine like precision-cut jewelry. Elegant, aesthetically refined, and intellectually sharp, you possess an exquisite eye for quality and self-mastery.",
                "strengths": ["Refined taste", "Meticulous attention to detail", "High standards"],
                "blind_spot": "Perfectionism that leads to self-criticism or harsh judgment of others."
            },
            "壬": {
                "summary": "You flow with the vast, philosophical depth of an open ocean. Wise, adaptable, and naturally drawn to big-picture horizons, you embrace major life transformations with calm.",
                "strengths": ["Strategic vision", "Deep wisdom", "Fluid resilience"],
                "blind_spot": "Getting lost in abstract over-thinking or scattering focus."
            },
            "癸": {
                "summary": "You are like morning dew or a nourishing spring rain. Gentle, quietly strategic, and profoundly intuitive, you move through life with subtle grace and deep emotional awareness.",
                "strengths": ["Stealthy problem-solving", "Deep intuition", "Quiet persistence"],
                "blind_spot": "Guarding your inner world too tightly, leading to isolation."
            }
        },

        "wealth_section": {
            "title": "2. Wealth & Money Mindset",
            "description": "Your deep-dive financial psychology, resource attraction patterns, and long-term asset management strategy.",
            "advice": {
                "TEN_GOD_DIRECT_WEALTH": "You have a natural gift for systematic, predictable asset accumulation. You view money as a structured tool that rewards discipline, steady savings routines, and risk-averse long planning. Focus on compounding, real estate, or stable, long-term portfolio foundations.",
                "TEN_GOD_INDIRECT_WEALTH": "You possess a sharp market instinct, an eye for emerging trends, and comfort with calculated risks. You see wealth as fluid and full of dynamic opportunities. Balance your adventurous enthusiasm with an ironclad risk-management framework.",
                "DEFAULT": "Your financial flow relies on intuitive adaptability rather than rigid formulas. Focus on aligning your spending habits with your deepest core values and build a resilient financial safety net."
            }
        },

        "career_section": {
            "title": "3. Career & Work Style",
            "description": "An analysis of your professional genius, ideal organizational environment, and talent monetization framework.",
            "advice": {
                "TEN_GOD_EATING_GOD": "Your professional genius lies in creative expression, turning abstract ideas into tangible value, and enjoying a sustainable, stress-free work rhythm. Avoid rigid micromanagement; design projects where your unique voice translates into value.",
                "TEN_GOD_HURTING_OFFICER": "You excel at system innovation, challenging outdated protocols, and applying sharp critical insights to complex problem-solving. Channel your rebellious intellect into constructive product design or strategic consulting.",
                "TEN_GOD_DIRECT_OFFICER": "You shine brightest in structured, ethical organizations where your commitment to rules, systemic leadership, and reliability earn deep institutional trust. Guard against bureaucratic burnout.",
                "DEFAULT": "Your career evolves by balancing independent analytical problem-solving with steady, high-trust collaborative execution."
            }
        },

        "relationship_section": {
            "title": "4. Relationship & Social Style",
            "description": "Insights into how you bond with peers, romantic partners, and professional networks while maintaining healthy boundaries.",
            "advice": {
                "TEN_GOD_FRIEND": "Collaboration, peer synergy, and mutual respect energize you. You view relationships through the lens of equals walking side by side. Cultivate communities that celebrate mutual growth.",
                "TEN_GOD_DIRECT_OFFICER": "You value mutual accountability, loyalty, and clear ethical boundaries in all interactions. Practice verbalizing your emotional needs softly with warmth.",
                "DEFAULT": "Your social style is built on empathetic adaptability. Always balance your desire to understand others with firm, loving emotional boundaries."
            }
        },

        "wellness_section": {
            "title": "5. Energy & Wellness Care",
            "description": "Tailored holistic prescriptions to protect your mental space, prevent burnout, and sustain vitality.",
            "advice": {
                "TEN_GOD_SEVEN_KILLINGS": "Because you naturally attract high-stakes responsibilities and pressure, your nervous system frequently runs on high alert. Integrate vigorous physical movement, breathwork, and absolute mental disconnect.",
                "TEN_GOD_INDIRECT_RESOURCE": "Your hyper-active mind processes vast layers of information, making mental clutter your primary source of fatigue. Dedicate daily digital detox windows and solitary walks in nature.",
                "DEFAULT": "Your overall wellness depends on rhythmic pacing and physical grounding. Prioritize consistent sleep schedules and mindful hydration."
            }
        },

        "annual_luck_title": "6. {target_year} Growth & Strategic Timing Guide",
        "annual_luck_note": "For target year {target_year}, your prevailing annual atmospheric energy is governed by {annual_pillar}.",
        "annual_luck_advice": {
            "TEN_GOD_FRIEND": "An empowering cycle to reinforce your self-worth, forge alliances with aligned peers, and expand your professional support network.",
            "TEN_GOD_ROB_WEALTH": "An ambitious period that spikes your drive and competitive energy. Channel this intensity into bold milestones while practicing strict pacing.",
            "TEN_GOD_EATING_GOD": "A golden window for creative projects, upgrading specialized skills, and enjoying the restorative comforts of life.",
            "TEN_GOD_HURTING_OFFICER": "A year of breakthrough insights and outspoken innovation. Use your sharp voice constructively to initiate positive changes.",
            "TEN_GOD_INDIRECT_WEALTH": "A dynamic season of expanded horizons and fresh market ventures. Pair your adventurous enthusiasm with disciplined risk tracking.",
            "TEN_GOD_DIRECT_WEALTH": "A grounding period where sustainable progress and structured financial habits shine. Focus on consolidating your hard-earned assets.",
            "TEN_GOD_SEVEN_KILLINGS": "A transformative year that brings major leadership challenges. Meet them head-on by prioritizing strict stress boundaries and restorative rest.",
            "TEN_GOD_DIRECT_OFFICER": "An aligned season for career milestones, public recognition, and earning deep trust through ethical execution.",
            "TEN_GOD_INDIRECT_RESOURCE": "A deep incubation period ideal for mastering specialized knowledge, intuitive self-reflection, and refining unique expertise.",
            "TEN_GOD_DIRECT_RESOURCE": "A nurturing cycle focused on personal sanctuaries, seeking mentorship, and recharging your mental reserves."
        },
        "disclaimer": "Note: This report blends astronomical calculations with modern self-reflection frameworks for personal empowerment and entertainment purposes."
    },
    
    "ko": {
        "title": "당신만의 맞춤형 성향 & 웰니스 심층 코칭 리포트",
        "intro": "이 리포트는 정밀한 천문 계산과 현대 심리 코칭 프레임워크를 결합하여, 당신의 타고난 본질 성향부터 재물 흐름, 커리어 마스터피스, 대인관계 다이내믹스, 그리고 멘탈 웰니스까지 삶의 전 영역을 입체적이고 깊이 있게 분석해 드립니다.",
        
        "day_master_intro": "1. 나의 본질 에너지: 세상을 마주하는 당신의 고유한 중심 성향은 **{day_pillar}**입니다.",
        "day_master_traits": {
            "甲": {
                "summary": "거대한 거목처럼 곧고 주체적인 성향을 지니고 있습니다. 선천적으로 남다른 비전과 개척자적 정신을 품고 있어, 익숙하고 정체된 환경보다는 새로운 가능성을 발굴하고 앞으로 나아갈 때 진정한 생명력을 발휘합니다.",
                "strengths": ["강한 독립성과 주체적인 추진력", "타인을 이끄는 진취적 리더십", "높은 이상과 비전"],
                "blind_spot": "때로는 지나친 곧음이 유연성을 해칠 수 있으므로, 주변의 피드백을 수용하고 유연하게 대처하는 지혜가 필요합니다."
            },
            "乙": {
                "summary": "유연한 덩굴과 들꽃처럼 적응력이 뛰어나고 지혜롭습니다. 복잡한 대인관계나 변화무쌍한 환경 속에서도 타인과 부드럽게 조화를 이루며 자신만의 영역을 조용히 넓혀갑니다.",
                "strengths": ["탁월한 공감 능력과 임기응변", "부드러운 설득력과 조화력", "유연한 생존 지능"],
                "blind_spot": "타인의 기대에 맞추느라 정작 자신의 에너지를 소모하지 않도록 명확한 심리적 경계를 세우는 연습이 필요합니다."
            },
            "丙": {
                "summary": "태양처럼 밝고 따뜻한 에너지를 품고 있습니다. 낙천적이고 열정적이며 매력적인 카리스마를 지니고 있어, 주변 사람들에게 긍정적인 활력과 영감을 널리 선사합니다.",
                "strengths": ["전염성 강한 열정과 에너지", "스케일 큰 비전과 통찰", "따뜻하고 매력적인 카리스마"],
                "blind_spot": "모든 사람의 어두운 곳을 밝혀주려다 스스로 에너지가 고갈될 수 있으므로, 선택과 집중을 통해 에너지를 보호하세요."
            },
            "丁": {
                "summary": "은은한 촛불이나 등대처럼 섬세한 감성을 지니고 있습니다. 깊은 통찰력과 예술적 감각으로 타인의 마음을 어루만지며, 남들이 놓치는 세밀한 디테일을 완벽하게 캐치해 냅니다.",
                "strengths": ["깊은 공감 지능과 섬세함", "남다른 집중력과 디테일", "예술적 감성과 통찰"],
                "blind_spot": "마음속에 걱정이나 스트레스를 혼자 담아두는 경향이 있으므로, 정기적인 감정 디톡스와 소통 창구가 필요합니다."
            },
            "戊": {
                "summary": "듬직한 산처럼 포용력이 넓고 신뢰감이 두텁습니다. 마음의 그릇이 크고 묵묵히 제자리를 지키기 때문에, 언제나 주변 사람들에게 든든한 안식처와 안정감을 줍니다.",
                "strengths": ["흔들리지 않는 신뢰감", "깊은 인내심과 묵직함", "포용력 있는 중심축 역할"],
                "blind_spot": "갑작스러운 변화나 예상치 못한 변수에 맞닥뜨렸을 때 유연하게 대처하는 태도를 연습하면 큰 도움이 됩니다."
            },
            "己": {
                "summary": "비옥한 정원의 밭처럼 수용성이 높고 실용적입니다. 만물을 길러내듯 타인의 재능을 북돋워 주고, 관계와 프로젝트 속에서 실질적이고 가시적인 성과를 만들어내는 데 탁월합니다.",
                "strengths": ["현실적인 문제 해결력", "헌신적인 실무 및 서포트 능력", "꾸준한 생산성과 결실"],
                "blind_spot": "모든 책임을 혼자 떠안으려는 완벽주의 성향을 내려놓고, 주변과 업무를 신뢰하며 나누는 지혜를 발휘해 보세요."
            },
            "庚": {
                "summary": "단단한 무쇠와 원광처럼 의리가 투철하고 결단력이 강합니다. 원칙과 공정함을 최우선으로 여기며, 복잡하고 혼란스러운 상황 속에서도 객관적이고 날카로운 진실을 짚어냅니다.",
                "strengths": ["흔들리지 않는 원칙주의", "명확하고 신속한 결단력", "강한 책임감과 의리"],
                "blind_spot": "지나치게 차가운 논리로만 상황을 판단하면 타인에게 상처를 줄 수 있으므로, 공감과 부드러운 소통을 함께 곁들여 보세요."
            },
            "辛": {
                "summary": "정교하게 세공된 보석처럼 예리한 미감과 완벽주의적 디테일을 지니고 있습니다. 자기관리가 철저하며 자신만의 고결한 가치를 우아하고 완벽하게 완성해 나갑니다.",
                "strengths": ["탁월한 전문성과 디테일", "세련된 미적 감각과 취향", "높은 수준의 자기 완성도"],
                "blind_spot": "스스로를 향한 엄격한 잣대가 과도한 스트레스로 이어땅의 기운 않도록, 때로는 마음의 여유를 허락해 주세요."
            },
            "壬": {
                "summary": "광활한 바다처럼 지혜의 스케일이 큽니다. 시야가 매우 넓고 변화무쌍한 세상의 흐름을 한 발 앞서 읽어내며, 거대한 삶의 변화 앞에서도 당황하지 않고 유연하게 대처합니다.",
                "strengths": ["거시적이고 입체적인 통찰", "변화에 대한 탁월한 적응력", "깊고 유연한 철학적 지혜"],
                "blind_spot": "생각의 스케일이 너무 커져 실천이 늦어질 수 있으므로, 아이디어를 작은 단위로 쪼개어 차근차근 실행하는 습관이 중요합니다."
            },
            "癸": {
                "summary": "새벽 이슬이나 잔잔한 호수처럼 조용하지만 강한 직관력을 지니고 있습니다. 겉으로는 부드러워 보이지만 내면에는 엄청난 저력과 깊은 공감 지능을 품고 물 흐르듯 지혜롭게 살아갑니다.",
                "strengths": ["뛰어난 전략적 사고와 지능", "깊고 정확한 직관력", "끈질긴 회복 탄력성과 저력"],
                "blind_spot": "내면의 고민이나 생각을 너무 꼭꼭 숨겨두기보다, 믿을 만한 사람들과 고민을 나누며 에너지를 환기해 보세요."
            }
        },

        "wealth_section": {
            "title": "2. 재물 & 자금 흐름 성향",
            "description": "재물 에너지를 다루는 당신만의 경제적 의사결정 패턴과 장기적인 부의 축적 전략을 심층 분석합니다.",
            "advice": {
                "TEN_GOD_DIRECT_WEALTH": "체계적이고 안정적인 자산 관리에 타고난 감각을 지니고 있습니다. 돈을 감정적으로 대하지 않고, 철저한 계획과 저축 루틴, 그리고 리스크가 적은 장기 투자를 통해 탄탄한 부를 일구어갑니다. 복리 효과를 누릴 수 있는 우량 자산이나 안정적인 포트폴리오 구축에 집중하세요.",
                "TEN_GOD_INDIRECT_WEALTH": "시장 흐름을 읽는 안목이 예리하고 새로운 기회를 포착하는 활동 무대가 넓습니다. 돈을 정체시키기보다 유연하게 순환시키며 키워가는 과정 자체를 즐깁니다. 과감한 도전과 함께 철저한 손절매와 리스크 관리 장치를 마련해 두세요.",
                "DEFAULT": "유연한 흐름 속에서 재정을 다루며 직관적인 경제 관념을 지니고 있습니다. 일상의 소비 패턴을 자신의 핵심 가치와 연결하고, 예상치 못한 변수에 대비한 든든한 비상금 통장을 마련해 두세요."
            }
        },

        "career_section": {
            "title": "3. 일 & 커리어 성향",
            "description": "당신의 전문성과 잠재력이 가장 폭발적으로 빛을 발하는 일의 방식, 조직 환경, 그리고 재능 수익화 구조를 제안합니다.",
            "advice": {
                "TEN_GOD_EATING_GOD": "창의적인 아이디어를 실질적인 콘텐츠나 가치로 전환하고, 타인에게 영감을 주며 지속 가능한 페이스로 일할 때 성과가 극대화됩니다. 꽉 막힌 통제형 조직보다는 자율성이 주어지는 환경이 좋으며, 나만의 전문 콘텐츠나 창의적 프로젝트를 주도해 보세요.",
                "TEN_GOD_HURTING_OFFICER": "기존의 틀을 깨는 혁신성, 날카로운 비판적 사고, 그리고 복잡한 문제를 해결하는 탁월한 기획력이 당신의 최대 무기입니다. 번뜩이는 아이디어를 제품화하거나 전략 컨설팅, 전문 테크 분야에서 날개를 펼칠 수 있습니다.",
                "TEN_GOD_DIRECT_OFFICER": "체계적인 시스템, 명확한 규범, 그리고 상식적인 원칙이 살아있는 조직에서 가장 큰 안정감과 성취감을 느낍니다. 조직 내에서 두터운 신임을 받는 리더나 핵심 중추로 성장하기 좋습니다.",
                "DEFAULT": "독립적인 문제 해결 능력과 타인과의 유연한 협업 균형을 맞추며 커리어를 탄탄하게 빌드업해 나가는 성향입니다."
            }
        },

        "relationship_section": {
            "title": "4. 대인관계 & 소통 방식",
            "description": "타인과 깊은 유대를 형성하고, 소통 속에서 건강한 심리적 경계를 지키는 맞춤형 가이드입니다.",
            "advice": {
                "TEN_GOD_FRIEND": "동반자들과 함께 시너지를 내는 평등하고 수평적인 관계를 지향합니다. 서로 영감을 주고받는 커뮤니티 속에서 큰 활력을 얻습니다. 우정과 협력을 소중히 여기되, 타인의 감정에 지나치게 몰입하지 않도록 적절한 거리를 유지하세요.",
                "TEN_GOD_DIRECT_OFFICER": "상호 책임감, 의리, 그리고 투명한 원칙을 관계의 가장 중요한 가치로 여깁니다. 상식에 어긋나는 행동에는 엄격합니다. 때로는 완벽한 원칙보다 따뜻한 포용과 유연한 농담이 유대를 깊게 만들어 줍니다.",
                "DEFAULT": "타인을 향한 깊은 공감과 유연한 적응력을 바탕으로 원만한 관계를 맺습니다. 남을 배려하느라 내 진짜 감정을 숨기지 말고 솔직하게 표현해 보세요."
            }
        },

        "wellness_section": {
            "title": "5. 에너지 충전 & 멘탈 케어",
            "description": "최상의 컨디션을 유지하고 번아웃을 사전에 예방하기 위해, 당신의 신경계에 꼭 필요한 맞춤형 웰니스 처방입니다.",
            "advice": {
                "TEN_GOD_SEVEN_KILLINGS": "선천적으로 높은 책임감과 압박감을 스스로에게 부여하는 경향이 있어, 신경계가 쉽게 긴장 상태에 놓이기 쉽습니다. 의도적인 휴식 루틴이 반드시 필요하며, 강도 높은 운동이나 디지털 디스커넥트 시간을 가져보세요.",
                "TEN_GOD_INDIRECT_RESOURCE": "지적인 호기심이 매우 깊고 생각의 회전이 빠른 만큼, 머릿속에 쌓이는 정보와 잡념이 피로의 주원인이 됩니다. 혼자만의 고요한 사색을 즐길 수 있는 '나만의 안식처'와 자연 속 산책을 실천하세요.",
                "DEFAULT": "일상의 리듬을 일정하게 유지하고 신체 감각에 집중할 때 웰니스가 유지됩니다. 피로가 몰려오기 전에 가벼운 스트레칭과 충분한 수분 섭취를 챙겨주세요."
            }
        },

        "annual_luck_title": "6. {target_year}년 성장 타이밍 & 액션 가이드",
        "annual_luck_note": "조회하신 {target_year}년의 한 해 동안 당신을 감싸는 흐름은 **{annual_pillar}** 기운입니다.",
        "annual_luck_advice": {
            "TEN_GOD_FRIEND": "나의 주체성과 자존감을 단단히 다지고, 뜻이 맞는 든든한 동반자들과 손을 잡고 네트워크를 확장하기에 더없이 좋은 해입니다.",
            "TEN_GOD_ROB_WEALTH": "도전 의식과 성취욕이 한껏 고취되는 시기입니다. 과감한 실행력으로 목표를 향해 돌파하되 마인드 밸런스를 챙기는 지혜가 동반되어야 합니다.",
            "TEN_GOD_EATING_GOD": "창의적인 프로젝트에 깊이 몰입하거나, 내면의 즐거움을 채우고 심신의 휴식과 웰니스를 가꾸기에 완벽한 타이밍입니다.",
            "TEN_GOD_HURTING_OFFICER": "기존의 틀을 깨는 혁신적인 아이디어가 샘솟습니다. 날카로운 통찰을 생산적인 기획으로 풀어내어 긍정적인 변화를 이끌어내기 좋은 해입니다.",
            "TEN_GOD_INDIRECT_WEALTH": "새로운 무대와 다채로운 기회가 넓게 열리는 흐름입니다. 활기찬 도전 정신과 함께 냉철한 리스크 관리 감각을 조화롭게 맞추세요.",
            "TEN_GOD_DIRECT_WEALTH": "성실함과 안정성이 가장 큰 무기가 되는 시기입니다. 일상의 루틴을 흐트러짐 없이 다지고 자산을 정돈하기 좋습니다.",
            "TEN_GOD_SEVEN_KILLINGS": "성장을 위한 큰 책임과 도전을 마주하는 해입니다. 철저한 바운더리와 충분한 휴식 루틴을 지킨다면 커다란 내적 성장을 이룰 수 있습니다.",
            "TEN_GOD_DIRECT_OFFICER": "사회적 신뢰와 커리어의 마일스톤이 탄탄하게 자리 잡는 시기입니다. 원칙과 책임감을 바탕으로 명예로운 성취를 누려보세요.",
            "TEN_GOD_INDIRECT_RESOURCE": "전문적인 지식을 깊게 흡수하고, 직관적인 내면 성찰과 독창적인 스킬을 연마하기에 최고의 흐름입니다.",
            "TEN_GOD_DIRECT_RESOURCE": "나만의 안식처를 단단히 돌보고 정신적인 에너지를 충전하며 장기적인 비전을 설계하기에 아주 유리한 시기입니다."
        },
        "disclaimer": "안내: 본 리포트는 전통 천문 계산과 현대적 자기 성찰 프레임워크를 결합하여 오락 및 개인 성찰 목적으로 제작되었습니다."
    }
}