import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "data" / "poems.json"
data = json.loads(p.read_text(encoding="utf-8"))

# 5가지 관계에 대한 문학 해설 번역
comm_es = {
    "same": "Este sijo canta la resonancia cuando dos fuerzas del mismo elemento se encuentran.",
    "generates_me": "Describe una fuerza nutritiva que entra desde el exterior.",
    "i_generate": "Tu energía interior se extiende hacia el mundo y florece.",
    "i_control": "Muestra tu poder gobernando y organizando el mundo que te rodea.",
    "controls_me": "Una fuerza externa te presiona y te refina."
}
comm_ja = {
    "same": "この詩は、同じ元素の二つの力が出会ったときの共鳴を歌っています。",
    "generates_me": "外から入ってくる養分となる力を描いています。",
    "i_generate": "内なるエネルギーが世界へと広がり、花開く過程を描いています。",
    "i_control": "自分の力で周囲の世界を統制し、整える姿を示しています。",
    "controls_me": "外からの強い力があなたを押し、磨き上げます。"
}
comm_zh = {
    "same": "这首诗吟唱了同源两股力量相遇时的共鸣。",
    "generates_me": "它描绘了从外部进入的滋养力量。",
    "i_generate": "你内在的能量向世界延伸并绽放。",
    "i_control": "它展现了你掌控和组织周围世界的力量。",
    "controls_me": "外部的强大力量在压迫和淬炼你。"
}

translations = {
    "mok_same": {
        "title": {"es": "El Mismo Grano", "ja": "同じ木目", "zh_cn": "同纹"},
        "sijo": {"es": "Nuevos brotes se encuentran,\\nEn silencio extienden ramas,\\nY la primavera fluye entre ellos.", "ja": "新芽が新芽に出会い\\n黙って枝を伸ばし\\n春がその間を流れる", "zh_cn": "新芽遇见新芽\\n默默伸展枝条\\n春天在它们之间流淌"},
        "interp": {"es": "Tu Madera resuena con la Madera del mes. Dos fuerzas en la misma dirección se elevan mutuamente.", "ja": "あなたの木は月建の木と同じ木目で共鳴します。同じ方向の二つの力は互いを高め合います。", "zh_cn": "你的木与月建之木同纹共鸣。同向的两股力量互相提升。"},
        "prac": {"es": "Camina 10 minutos hoy en una dirección, sin decir una palabra.", "ja": "今日は一言も発さず、同じ方向に10分歩く。", "zh_cn": "今天无目的地步行十分钟。"}
    },
    "mok_generates_me": {
        "title": {"es": "Carta del Río", "ja": "川からの手紙", "zh_cn": "来自河流的信"},
        "sijo": {"es": "El río de invierno derrite el hielo,\\nEnviando agua a las puntas de las raíces,\\nSolo entonces me convierto en hoja.", "ja": "冬の川が氷を溶かし\\n根の先に水を送る\\n私はやっと葉になる", "zh_cn": "冬河融化冰层\\n送水至根尖\\n我才化作树叶"},
        "interp": {"es": "El Agua del mes nutre tu Madera. Estás siendo apoyado silenciosamente.", "ja": "月建の水があなたの木を養います。静かに支えられている時期です。", "zh_cn": "月建的水滋养着你的木。你正受到无声的支持。"},
        "prac": {"es": "Envía un breve agradecimiento a alguien que te ayudó recientemente.", "ja": "最近助けてくれた人に短いお礼を送る。", "zh_cn": "向最近帮助过你的人发一条简短的感谢信息。"}
    },
    "mok_i_generate": {
        "title": {"es": "Al Final de la Primavera", "ja": "春の終わりに", "zh_cn": "春末"},
        "sijo": {"es": "Los nuevos brotes cruzan el río,\\nFloreciendo en llamas,\\nY yo estoy entre ellos.", "ja": "新芽が川を渡り\\n炎となって咲き\\n私はその間に立つ", "zh_cn": "新芽渡过河流\\n绽放成火焰\\n我伫立其间"},
        "interp": {"es": "Tu Madera enciende el Fuego del mes. Tu expresión es lo que ilumina el mundo ahora mismo.", "ja": "あなたの木が月建の火を灯します。あなたの表現が今、世界を照らしています。", "zh_cn": "你的木点燃了月建的火。你的表达正照亮世界。"},
        "prac": {"es": "Pon uno de tus pensamientos en palabras y envíalo a alguien hoy.", "ja": "今日、自分の考えを一つ言葉にして誰かに送る。", "zh_cn": "将你的一个想法付诸文字，今天发送给某人。"}
    },
    "mok_i_control": {
        "title": {"es": "El Trabajo de las Raíces", "ja": "根の仕事", "zh_cn": "根基的工作"},
        "sijo": {"es": "El árbol sostiene la tierra,\\nAprendiendo a mantenerse en pie,\\nY la tierra soporta el peso.", "ja": "木が土を掴み\\n自らの身を立てる\\n土はその重みに耐える", "zh_cn": "树木抓住土壤\\n学会站立\\n土壤承受重量"},
        "interp": {"es": "Tu Madera sostiene la Tierra del mes. Esta es una estación para mantener tu propio terreno.", "ja": "あなたの木が月建の土を支えます。自分の基盤を固める時期です。", "zh_cn": "你的木紧握着月建的土。这是一个坚守阵地的季节。"},
        "prac": {"es": "Finaliza una decisión que has estado posponiendo.", "ja": "先延ばしにしていた決断を一つ確定する。", "zh_cn": "敲定一个你一直在拖延的决定。"}
    },
    "mok_controls_me": {
        "title": {"es": "Poda", "ja": "剪定", "zh_cn": "修剪"},
        "sijo": {"es": "En un amanecer helado,\\nAlguien poda mis ramas,\\nLa primavera viene del corte.", "ja": "霜の降りた夜明けに\\n誰かが私の枝を剪定する\\n切り口から春が来る", "zh_cn": "霜降的黎明\\n谁在修剪我的枝条\\n春天从切口处到来"},
        "interp": {"es": "El Metal del mes poda tu Madera. El corte es el crecimiento.", "ja": "月建の金があなたの木を剪定します。切り取られることが成長です。", "zh_cn": "月建的金属修剪你的木。修剪即是成长。"},
        "prac": {"es": "Elige una cosa a la que decir que no hoy.", "ja": "今日断るべきことを一つ決める。", "zh_cn": "今天选择一件事说“不”。"}
    },
    "hwa_same": {
        "title": {"es": "La Misma Llama", "ja": "同じ炎", "zh_cn": "同焰"},
        "sijo": {"es": "La llama se encuentra con la llama,\\nArdiendo más brillante,\\nY la noche se traga la luz.", "ja": "炎が炎に出会い\\nより大きく燃え上がり\\n夜がその光を飲み込む", "zh_cn": "火焰遇见火焰\\n燃烧得更旺\\n夜晚吞噬了光芒"},
        "interp": {"es": "Tu Fuego se eleva con el Fuego del mes. Protégete contra el sobrecalentamiento, pero mantén la llama.", "ja": "あなたの火は月建の火と共に燃え上がります。過熱を避けつつ、情熱を保ちましょう。", "zh_cn": "你的火与月建的火一起升腾。提防过热，但保持火焰。"},
        "prac": {"es": "Haz una pausa a propósito, una vez hoy.", "ja": "今日は一度、意図的に休む。", "zh_cn": "今天故意停顿一次。"}
    },
    "hwa_generates_me": {
        "title": {"es": "El Corazón de la Yesca", "ja": "焚き木の心", "zh_cn": "引火之心的心意"},
        "sijo": {"es": "El árbol entrega su cuerpo,\\nAbriendo el camino al fuego,\\nY el fuego recuerda al árbol.", "ja": "木が自らを捧げ\\n火に道を開く\\n火は木を忘れない", "zh_cn": "树木献出身体\\n为火开辟道路\\n火铭记着树木"},
        "interp": {"es": "La Madera del mes alimenta tu Fuego. Estás recibiendo mucho.", "ja": "月建の木があなたの火に薪をくべます。多くを受け取っている時期です。", "zh_cn": "月建的木给你的火添柴。你正在获得很多。"},
        "prac": {"es": "Lee una página de un libro favorito, lentamente.", "ja": "お気に入りの本を一ページゆっくり読む。", "zh_cn": "慢慢读一页最喜欢的书。"}
    },
    "hwa_i_generate": {
        "title": {"es": "Donde Descansa la Ceniza", "ja": "灰の場所", "zh_cn": "灰烬之地"},
        "sijo": {"es": "Sentado donde se quemó,\\nViendo las cenizas convertirse en tierra,\\nMiré por mucho tiempo.", "ja": "燃え尽きた場所に座り\\n灰が土になるのを\\n私は長く見ていた", "zh_cn": "坐在燃尽之处\\n看着灰烬化作泥土\\n我凝望了许久"},
        "interp": {"es": "Tu Fuego deja ceniza en la Tierra del mes. Los resultados se están acumulando.", "ja": "あなたの火が月建の土に灰を残します。成果が積み上がる時期です。", "zh_cn": "你的火在月建的土中留下灰烬。成果正在积累。"},
        "prac": {"es": "Haz una revisión intermedia de algo que empezaste recientemente.", "ja": "最近始めたことの途中経過を確認する。", "zh_cn": "检查最近开始的事情的进度。"}
    },
    "hwa_i_control": {
        "title": {"es": "Mano de Fuego", "ja": "火の手", "zh_cn": "火之手"},
        "sijo": {"es": "El fuego martilla el hierro,\\nDando forma a sí mismo,\\nY el hierro recuerda el calor.", "ja": "火が鉄を打ち\\n自らの形を創り出し\\n鉄は熱さを覚えている", "zh_cn": "火锤炼铁\\n塑造出自身\\n铁铭记着热度"},
        "interp": {"es": "Tu Fuego martilla el Metal del mes. Esta es una estación para moldear lo que deseas.", "ja": "あなたの火が月建の金を打ちます。望む形を創り上げる時期です。", "zh_cn": "你的火锤炼着月建的金属。这是一个塑造你渴望之物的季节。"},
        "prac": {"es": "Haz algo con tus manos hoy: cocina, dibuja o escribe.", "ja": "今日は手を使って何か作る（料理、絵、文章）。", "zh_cn": "今天动手做点什么：做饭、画画或写字。"}
    },
    "hwa_controls_me": {
        "title": {"es": "Canción del Agua", "ja": "水の歌", "zh_cn": "水之歌"},
        "sijo": {"es": "Aunque el agua cubra mi fuego,\\nNo me convierto en ceniza,\\nMe elevo como vapor.", "ja": "水が私の火を覆っても\\n私は灰にならない\\n湯気となって空に昇る", "zh_cn": "即使水覆盖我的火\\n我也不会化为灰烬\\n我化作蒸汽升腾"},
        "interp": {"es": "El Agua del mes cubre tu Fuego. Elévate como vapor desde debajo del peso.", "ja": "月建の水があなたの火を覆います。重みの下から蒸気のように上がりましょう。", "zh_cn": "月建的水覆盖了你的火。像蒸汽一样从重压之下升腾。"},
        "prac": {"es": "Respira profundamente. Cinco minutos de silencio.", "ja": "深く呼吸する。5分間の瞑想。", "zh_cn": "深呼吸。五分钟的安静。"}
    },
    "to_same": {
        "title": {"es": "El Mismo Suelo", "ja": "同じ大地", "zh_cn": "同地"},
        "sijo": {"es": "La tierra se encuentra con la tierra,\\nFormando tranquilamente una montaña,\\nY yo me siento sobre ella.", "ja": "土が土に出会い\\n静かに山を成し\\n私はその上に座る", "zh_cn": "土遇见土\\n静静形成高山\\n我坐在其上"},
        "interp": {"es": "Tu Tierra forma una montaña con la Tierra del mes. Acumulación silenciosa.", "ja": "あなたの土は月建の土と共に山を形成します。静かに積み上がる時期です。", "zh_cn": "你的土与月建的土形成山峰。静静积累。"},
        "prac": {"es": "Date una hora hoy en la que no hacer nada sea suficiente.", "ja": "今日は何もしなくてもいい時間を1時間作る。", "zh_cn": "今天给自己一小时，什么都不做也足够。"}
    },
    "to_generates_me": {
        "title": {"es": "Suelo de Ceniza", "ja": "灰からの土", "zh_cn": "来自灰烬的土"},
        "sijo": {"es": "Desde donde el fuego ardió,\\nLa tierra se eleva lentamente,\\nApoyando mis pies.", "ja": "燃え尽きた火の場所から\\n土がゆっくりと起き上がり\\n私の足を支える", "zh_cn": "在燃尽的火烬之处\\n泥土缓缓升起\\n支撑着我的双足"},
        "interp": {"es": "El Fuego del mes calienta tu Tierra. Un fuerte apoyo te rodea.", "ja": "月建の火があなたの土を暖めます。支えが強い時期です。", "zh_cn": "月建的火温暖你的土。你被强大的支持环绕。"},
        "prac": {"es": "Sorbo de una taza de té caliente, lentamente.", "ja": "温かいお茶を一杯、ゆっくり飲む。", "zh_cn": "慢慢喝一杯热茶。"}
    },
    "to_i_generate": {
        "title": {"es": "Semilla en el Suelo", "ja": "土の中の種", "zh_cn": "土中之种"},
        "sijo": {"es": "La tierra muele su cuerpo,\\nNutriendo hierro sólido,\\nY escucho el sonido.", "ja": "土が自らを削り\\n固い鉄を育てる\\n私はその音を聞く", "zh_cn": "泥土磨砺身体\\n孕育坚硬的金属\\n我听见了那声音"},
        "interp": {"es": "Tu Tierra cría el Metal del mes. Los resultados sólidos toman forma.", "ja": "あなたの土が月建の金を育てます。確かな成果が形になります。", "zh_cn": "你的土孕育着月建的金属。坚实的成果正在成形。"},
        "prac": {"es": "Termina una cosa que decidiste hacer hoy.", "ja": "今日決めたことを一つ最後までやり遂げる。", "zh_cn": "完成你今天决定要做的一件事。"}
    },
    "to_i_control": {
        "title": {"es": "El Trabajo del Banco", "ja": "土手の仕事", "zh_cn": "堤岸的工作"},
        "sijo": {"es": "La tierra contiene el camino del agua,\\nFormando arrozales,\\nY el agua encuentra su camino.", "ja": "土が水路を掴み\\n田んぼを作る\\n水は自らの道を行く", "zh_cn": "泥土抓住水路\\n形成稻田\\n水找到了自己的路"},
        "interp": {"es": "Tu Tierra contiene el Agua del mes. Esta es una estación para canalizar el flujo.", "ja": "あなたの土が月建の水を堰き止めます。流れを整える時期です。", "zh_cn": "你的土堤坝拦住月建的水。这是一个疏导水流的季节。"},
        "prac": {"es": "Ordena un rincón desordenado de tu espacio.", "ja": "部屋の片付けられていない場所を一つ整理する。", "zh_cn": "整理你空间里的一个杂乱角落。"}
    },
    "to_controls_me": {
        "title": {"es": "Apretando la Tierra", "ja": "固められる大地", "zh_cn": "夯实大地"},
        "sijo": {"es": "Las raíces del árbol se extienden,\\nPartiendo la tierra sólida,\\nY la tierra abraza la primavera de nuevo.", "ja": "木の根が伸び\\n固い土を裂き\\n土は再び春を抱く", "zh_cn": "树根伸展\\n劈开坚硬的土壤\\n土壤再次拥抱春天"},
        "interp": {"es": "La Madera del mes atraviesa tu Tierra. Estás siendo compactado en fuerza.", "ja": "月建の木があなたの土を貫きます。強さへと固められる時期です。", "zh_cn": "月建的木穿透你的土。你正被夯实成力量。"},
        "prac": {"es": "Di no una vez hoy a una solicitud inesperada.", "ja": "今日、予期せぬ頼み事を一度断る。", "zh_cn": "今天对一次意外的请求说“不”。"}
    },
    "geum_same": {
        "title": {"es": "El Mismo Grano", "ja": "同じ木目", "zh_cn": "同纹"},
        "sijo": {"es": "El hierro se encuentra con el hierro,\\nAfiliándose mutuamente,\\nY la luz fluye entre ellos.", "ja": "鉄が鉄に出会い\\n互いを研ぎ澄まし\\n光がその間を流れる", "zh_cn": "铁遇见铁\\n互相磨砺\\n光芒在其间流淌"},
        "interp": {"es": "Tu Metal afila el Metal del mes. Esta es una estación de filo.", "ja": "あなたの金が月建の金を研ぎます。鋭さが増す時期です。", "zh_cn": "你的金与月建的金属互相磨砺。这是一个锋芒毕露的季节。"},
        "prac": {"es": "Contente una vez hoy de agudizar una conversación.", "ja": "今日、会話を鋭くしないように一度堪える。", "zh_cn": "今天克制一次，不要让对话变得尖锐。"}
    },
    "geum_generates_me": {
        "title": {"es": "Regalo de la Tierra", "ja": "土の贈り物", "zh_cn": "大地的礼物"},
        "sijo": {"es": "La tierra antigua me abraza,\\nDándome un cuerpo sólido,\\nY empiezo a recibir luz.", "ja": "古い土が私を包み\\n固い身体を与え\\n私は光を受け始める", "zh_cn": "古老的泥土拥抱我\\n赐予我坚实的身体\\n我开始接受光芒"},
        "interp": {"es": "La Tierra del mes acuna tu Metal. Estás sobre un terreno estable.", "ja": "月建の土があなたの金を包みます。安定した基盤の上に立っています。", "zh_cn": "月建的土拥抱着你的金属。你站在稳固的地基上。"},
        "prac": {"es": "Termina una tarea que has estado posponiendo.", "ja": "先延ばしにしていた片付けを一つ終わらせる。", "zh_cn": "完成一件你一直拖延的任务。"}
    },
    "geum_i_generate": {
        "title": {"es": "Sendero Helado", "ja": "霜の道", "zh_cn": "霜路"},
        "sijo": {"es": "El agua formada al final de la escarcha,\\nFluyendo hacia el río,\\nY yo guardo ese camino.", "ja": "霜の先に生まれた水が\\n川へと流れる\\n私はその道を守る", "zh_cn": "霜降尽头凝结的水\\n流入河流\\n我守护着那条路"},
        "interp": {"es": "Tu Metal da lugar al Agua del mes. Abres nuevos flujos.", "ja": "あなたの金が月建の水を生み出します。新しい流れを開く時期です。", "zh_cn": "你的金催生了月建的水。你开辟了新的水流。"},
        "prac": {"es": "Escribe una idea hoy.", "ja": "今日、アイデアを一つ書き留める。", "zh_cn": "今天写下一个想法。"}
    },
    "geum_i_control": {
        "title": {"es": "Canción de la Hoz", "ja": "鎌の歌", "zh_cn": "镰刀之歌"},
        "sijo": {"es": "La hoz corta la hierba,\\nOrdenando el campo,\\nY la hierba espera la primavera.", "ja": "鎌が草を刈り\\n畑を整える\\n草は再び春を待つ", "zh_cn": "镰刀割下草\\n整理田地\\n草等待下一个春天"},
        "interp": {"es": "Tu Metal corta la Madera del mes. Esta es una estación para despejar.", "ja": "あなたの金が月建の木を刈り取ります。整理する時期です。", "zh_cn": "你的金属砍伐月建的木。这是一个清理的季节。"},
        "prac": {"es": "Nombra tres cosas de las que te desprenderás hoy.", "ja": "今日捨てるものを三つ決める。", "zh_cn": "今天说出三件你要放下的事情。"}
    },
    "geum_controls_me": {
        "title": {"es": "Memoria de Hierro", "ja": "鉄の記憶", "zh_cn": "铁之记忆"},
        "sijo": {"es": "El fuego me martilla,\\nDando forma a sí mismo,\\nY yo recuerdo el calor.", "ja": "火が私を打ち\\n自らの形を作り\\n私は熱さを覚えている", "zh_cn": "火锤炼我\\n塑造出自身\\n我铭记着热度"},
        "interp": {"es": "El Fuego del mes martilla tu Metal. Estás siendo templado.", "ja": "月建の火があなたの金を打ちます。鍛えられる時期です。", "zh_cn": "月建的火锤炼你的金属。你正在接受淬炼。"},
        "prac": {"es": "Haz lo difícil primero, esta mañana.", "ja": "今日の午前中に、一番大変なことを先にやる。", "zh_cn": "今天上午先做最难的事。"}
    },
    "su_same": {
        "title": {"es": "La Misma Ola", "ja": "同じ波", "zh_cn": "同波"},
        "sijo": {"es": "El agua se encuentra con el agua,\\nFormando un gran río,\\nY escucho el sonido.", "ja": "水が水に出会い\\n大きな川を成し\\n私はその音を聞く", "zh_cn": "水遇见水\\n汇成大江大河\\n我听见了那声音"},
        "interp": {"es": "Tu Agua forma un río con el Agua del mes. Esta es una estación de profundidad.", "ja": "あなたの水は月建の水と共に川を形成します。深まる時期です。", "zh_cn": "你的水与月建的水汇成河流。这是一个深化的季节。"},
        "prac": {"es": "Da un paseo tranquilo de 20 minutos a solas hoy.", "ja": "今日、一人で静かに20分散歩する。", "zh_cn": "今天独自安静地散步20分钟。"}
    },
    "su_generates_me": {
        "title": {"es": "Agua de Escarcha", "ja": "霜から来た水", "zh_cn": "霜降之水"},
        "sijo": {"es": "El agua formada al final de la escarcha,\\nFluye hacia mi cuerpo,\\nY empiezo a fluir de nuevo.", "ja": "霜の先に生まれた水が\\n私の身体に流れ込み\\n私は再び流れ始める", "zh_cn": "霜降尽头凝结的水\\n流入我的身体\\n我重新开始流动"},
        "interp": {"es": "El Metal del mes da lugar a tu Agua. Un nuevo flujo está comenzando.", "ja": "月建の金があなたの水を生み出します。新しい流れが始まります。", "zh_cn": "月建的金属催生了你的水。新的水流正在开始。"},
        "prac": {"es": "Prueba una cosa nueva y pequeña hoy.", "ja": "今日、初めての小さな試みを一つする。", "zh_cn": "今天尝试一件小小的新事情。"}
    },
    "su_i_generate": {
        "title": {"es": "Agua que Llama a la Primavera", "ja": "春を呼ぶ水", "zh_cn": "唤春之水"},
        "sijo": {"es": "El agua fluye bajo tierra,\\nTocando las raíces,\\nY los nuevos brotes abren los ojos.", "ja": "水が地中を流れ\\n根を叩く\\n新芽が目を覚ます", "zh_cn": "水流过地下\\n叩击着根系\\n新芽睁开了眼睛"},
        "interp": {"es": "Tu Agua nutre la Madera del mes. Esta es una estación para brotar.", "ja": "あなたの水が月建の木を養います。芽吹く時期です。", "zh_cn": "你的水滋养着月建的木。这是一个发芽的季节。"},
        "prac": {"es": "Avanza una idea muy querida, un paso.", "ja": "長年温めてきたアイデアを一歩進める。", "zh_cn": "将一个珍藏已久的想法推进一步。"}
    },
    "su_i_control": {
        "title": {"es": "Mano de Agua", "ja": "水の手", "zh_cn": "水之手"},
        "sijo": {"es": "El agua cubre el fuego,\\nEmpapando las cenizas,\\nY el fuego se eleva como vapor.", "ja": "水が火を覆い\\n灰を濡らす\\n火は湯気となって空に昇る", "zh_cn": "水覆盖住火\\n浸湿灰烬\\n火化作蒸汽升腾"},
        "interp": {"es": "Tu Agua cubre el Fuego del mes. Esta es una estación para enfriar.", "ja": "あなたの水が月建の火を覆います。熱を冷ます時期です。", "zh_cn": "你的水覆盖了月建的火。这是一个冷却的季节。"},
        "prac": {"es": "Retrocede una vez hoy de una discusión acalorada.", "ja": "今日、熱い議論から一歩引く。", "zh_cn": "今天从激烈的争论中退后一步。"}
    },
    "su_controls_me": {
        "title": {"es": "Agua Dentro del Banco", "ja": "土手の中の水", "zh_cn": "堤岸之水"},
        "sijo": {"es": "La tierra me abraza,\\nHaciendo su propio camino,\\nY me profundizo dentro de ella.", "ja": "土が私を包み込み\\n自らの道を作り\\n私はその中で深まる", "zh_cn": "泥土拥抱住我\\n开辟出自身的道路\\n我在其中变得深邃"},
        "interp": {"es": "La Tierra del mes contiene tu Agua. Te profundizas dentro de los límites.", "ja": "月建の土があなたの水を堰き止めます。限界の中で深まる時期です。", "zh_cn": "月建的土堤坝拦住了你的水。你在界限内加深。"},
        "prac": {"es": "Posponen la respuesta. Escribe tres preguntas en su lugar.", "ja": "今日は答えを保留し、質問を三つ書く。", "zh_cn": "推迟答案。写下三个问题代替。"}
    }
}

for poem in data["poems"]:
    pid = poem["id"]
    rel = poem["relation"]
    
    if "translations" not in poem:
        poem["translations"] = {}
        
    for lang in ["es", "ja", "zh_cn"]:
        if lang not in poem["translations"]:
            poem["translations"][lang] = {}
            
        if pid in translations:
            tr_data = translations[pid]
            poem["translations"][lang]["sijo"] = tr_data["sijo"][lang]
            poem["translations"][lang]["interpretation"] = tr_data["interp"][lang]
            poem["translations"][lang]["practice"] = tr_data["prac"][lang]
            
            if "title" not in poem:
                poem["title"] = {}
            poem["title"][lang] = tr_data["title"][lang]
            
    if rel == "same":
        poem["translations"]["es"]["commentary"] = comm_es["same"]
        poem["translations"]["ja"]["commentary"] = comm_ja["same"]
        poem["translations"]["zh_cn"]["commentary"] = comm_zh["same"]
    elif rel == "generates_me":
        poem["translations"]["es"]["commentary"] = comm_es["generates_me"]
        poem["translations"]["ja"]["commentary"] = comm_ja["generates_me"]
        poem["translations"]["zh_cn"]["commentary"] = comm_zh["generates_me"]
    elif rel == "i_generate":
        poem["translations"]["es"]["commentary"] = comm_es["i_generate"]
        poem["translations"]["ja"]["commentary"] = comm_ja["i_generate"]
        poem["translations"]["zh_cn"]["commentary"] = comm_zh["i_generate"]
    elif rel == "i_control":
        poem["translations"]["es"]["commentary"] = comm_es["i_control"]
        poem["translations"]["ja"]["commentary"] = comm_ja["i_control"]
        poem["translations"]["zh_cn"]["commentary"] = comm_zh["i_control"]
    elif rel == "controls_me":
        poem["translations"]["es"]["commentary"] = comm_es["controls_me"]
        poem["translations"]["ja"]["commentary"] = comm_ja["controls_me"]
        poem["translations"]["zh_cn"]["commentary"] = comm_zh["controls_me"]

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("[OK] poems.json 다국어 업데이트 완료 (25편 전체)")
