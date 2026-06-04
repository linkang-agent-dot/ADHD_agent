import json, subprocess, os, sys

GWS = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'
os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'

SPREADSHEET_ID = '11BIizMMOQRWzLZi9TjvxDxn_i0949wKwMX-T9_zlYTY'
TARGET_SHEET = 'HERO'

# 20列: ID_int, ID, cn, en, fr, de, po, zh, id, th, sp, ru, tr, vi, it, pl, ar, jp, kr, cns
rows = [
    [
        1011115279, "mecha_name_zhenqibazhu",
        "蒸汽霸主",
        "Steam Overlord",
        "Seigneur de la Vapeur",
        "Dampf-Overlord",
        "Senhor do Vapor",
        "蒸汽霸主",
        "Tuan Uap",
        "\u0e08\u0e2d\u0e21\u0e40\u0e1c\u0e14\u0e47\u0e08\u0e01\u0e32\u0e23\u0e44\u0e2d\u0e19\u0e49\u0e33",
        "Se\u00f1or del Vapor",
        "\u041f\u0430\u0440\u043e\u0432\u043e\u0439 \u0412\u043b\u0430\u0434\u044b\u043a\u0430",
        "Buhar H\u00fck\u00fcmdar\u0131",
        "B\u00e1 Ch\u1ee7 H\u01a1i N\u01b0\u1edbc",
        "Signore del Vapore",
        "W\u0142adca Pary",
        "\u0633\u064a\u062f \u0627\u0644\u0628\u062e\u0627\u0631",
        "\u30b9\u30c1\u30fc\u30e0\u30aa\u30fc\u30d0\u30fc\u30ed\u30fc\u30c9",
        "\uc99d\uae30 \uad70\uc8fc",
        "蒸汽霸主",
    ],
    [
        1011115280, "mecha_skin_src_zhenqibazhu",
        "全身覆满蒸汽装甲的霸主巨象，轰鸣的引擎与滚滚热气，彰显无与伦比的机械威势。",
        "The giant elephant clad in steam armor from head to toe; its roaring engines and billowing steam exude unrivaled mechanical dominance.",
        "Le g\u00e9ant \u00e9l\u00e9phant recouvert d'armure \u00e0 vapeur de la t\u00eate aux pieds ; ses moteurs rugissants et sa vapeur tourbillonnante d\u00e9gagent une domination m\u00e9canique sans \u00e9gale.",
        "Der mit Dampfpanzer von Kopf bis Fu\u00df bekleidete Riesenelefant; seine donnernden Motoren und der wirbelnde Dampf strahlen un\u00fcbertroffene mechanische Dominanz aus.",
        "O elefante gigante coberto de armadura a vapor da cabe\u00e7a aos p\u00e9s; seus motores rugindo e o vapor billowing exalam uma domina\u00e7\u00e3o mec\u00e2nica sem paralelo.",
        "全身覆滿蒸汽裝甲的霸主巨象，轟鳴的引擎與滾滾熱氣，彰顯無與倫比的機械威勢。",
        "Gajah raksasa yang diselimuti baju besi uap dari ujung kepala hingga ujung kaki; mesin-mesinnya yang menderu dan uap yang mengepul memancarkan dominasi mekanik yang tak tertandingi.",
        "\u0e0a\u0e49\u0e32\u0e07\u0e22\u0e31\u0e01\u0e29\u0e4c\u0e17\u0e35\u0e48\u0e2b\u0e48\u0e21\u0e40\u0e01\u0e23\u0e32\u0e30\u0e44\u0e2d\u0e19\u0e49\u0e33\u0e08\u0e32\u0e01\u0e2b\u0e31\u0e27\u0e16\u0e36\u0e07\u0e40\u0e17\u0e49\u0e32; \u0e40\u0e04\u0e23\u0e37\u0e48\u0e2d\u0e07\u0e22\u0e19\u0e15\u0e4c\u0e17\u0e35\u0e48\u0e04\u0e33\u0e23\u0e32\u0e21\u0e41\u0e25\u0e30\u0e44\u0e2d\u0e19\u0e49\u0e33\u0e17\u0e35\u0e48\u0e1e\u0e27\u0e22\u0e1e\u0e38\u0e48\u0e07\u0e2a\u0e30\u0e17\u0e49\u0e2d\u0e19\u0e16\u0e36\u0e07\u0e2d\u0e33\u0e19\u0e32\u0e08\u0e17\u0e32\u0e07\u0e01\u0e25\u0e44\u0e01\u0e17\u0e35\u0e48\u0e40\u0e2b\u0e19\u0e37\u0e2d\u0e01\u0e27\u0e48\u0e32\u0e43\u0e04\u0e23",
        "El elefante gigante cubierto de armadura de vapor de la cabeza a los pies; sus motores rugientes y el vapor arremolinado irradian un dominio mec\u00e1nico sin igual.",
        "\u0413\u0438\u0433\u0430\u043d\u0442\u0441\u043a\u0438\u0439 \u0441\u043b\u043e\u043d, \u0443\u043a\u0440\u044b\u0442\u044b\u0439 \u043f\u0430\u0440\u043e\u0432\u043e\u0439 \u0431\u0440\u043e\u043d\u0451\u0439 \u0441 \u0433\u043e\u043b\u043e\u0432\u044b \u0434\u043e \u043d\u043e\u0433; \u0435\u0433\u043e \u0440\u0435\u0432\u0443\u0449\u0438\u0435 \u0434\u0432\u0438\u0433\u0430\u0442\u0435\u043b\u0438 \u0438 \u043a\u043b\u0443\u0431\u044f\u0449\u0438\u0439\u0441\u044f \u043f\u0430\u0440 \u0438\u0437\u043b\u0443\u0447\u0430\u044e\u0442 \u043d\u0435\u043f\u0440\u0435\u0432\u0437\u043e\u0439\u0434\u0451\u043d\u043d\u043e\u0435 \u043c\u0435\u0445\u0430\u043d\u0438\u0447\u0435\u0441\u043a\u043e\u0435 \u0433\u043e\u0441\u043f\u043e\u0434\u0441\u0442\u0432\u043e.",
        "Ba\u015ftan a\u015fa\u011f\u0131 buhar z\u0131rh\u0131yla kapl\u0131 dev fil; g\u00fcmb\u00fcrdayan motorlar\u0131 ve t\u00fcten buhar\u0131 e\u015fsiz mekanik h\u00e2kimiyetini ortaya koyuyor.",
        "Con voi kh\u1ed3ng l\u1ed3 \u0111\u01b0\u1ee3c b\u1ecdc gi\u00e1p h\u01a1i n\u01b0\u1edbc t\u1eeb \u0111\u1ea7u \u0111\u1ebfn ch\u00e2n; ti\u1ebfng \u0111\u1ed9ng c\u01a1 g\u1ea7m r\u00fa v\u00e0 l\u00e0n h\u01a1i ng\u00fat ng\u00e0n th\u1ec3 hi\u1ec7n s\u1ee9c m\u1ea1nh c\u01a1 h\u1ecdc kh\u00f4ng ai s\u00e1nh k\u1ecbp.",
        "Il gigantesco elefante rivestito di armatura a vapore dalla testa ai piedi; i suoi motori ruggenti e il vapore vorticoso emanano un dominio meccanico senza pari.",
        "Gigantyczny s\u0142o\u0144 okryty zbroj\u0105 parow\u0105 od g\u0142owy do st\u00f3p; jego rycz\u0105ce silniki i k\u0142\u0119bi\u0105ca si\u0119 para emanuj\u0105 niezr\u00f3wnan\u0105 mechaniczn\u0105 dominacj\u0105.",
        "\u0627\u0644\u0641\u064a\u0644 \u0627\u0644\u0639\u0645\u0644\u0627\u0642 \u0627\u0644\u0645\u063a\u0637\u0649 \u0628\u062f\u0631\u0639 \u0627\u0644\u0628\u062e\u0627\u0631 \u0645\u0646 \u0627\u0644\u0631\u0623\u0633 \u062d\u062a\u0649 \u0627\u0644\u0642\u062f\u0645\u064a\u0646\u061b \u0645\u062d\u0631\u0643\u0627\u062a\u0647 \u0627\u0644\u0632\u0626\u064a\u0631\u0629 \u0648\u0628\u062e\u0627\u0631\u0647 \u0627\u0644\u0645\u062a\u0635\u0627\u0639\u062f \u064a\u064f\u062c\u0633\u0651\u062f\u0627\u0646 \u0647\u064a\u0645\u0646\u0629 \u0645\u064a\u0643\u0627\u0646\u064a\u0643\u064a\u0629 \u0644\u0627 \u0645\u062b\u064a\u0644 \u0644\u0647\u0627.",
        "\u982d\u304b\u3089\u722a\u5148\u307e\u3067\u8482\u6c17\u88c5\u7532\u306b\u899a\u308f\u308c\u305f\u9738\u738b\u30a8\u30ec\u30d5\u30a1\u30f3\u30c8\u3002\u8bd9\u304f\u6a5f\u95a2\u3068\u7acb\u3061\u8fbc\u3081\u308b\u71b1\u6c17\u304c\u3001\u6bd4\u985e\u306a\u304d\u6a5f\u68b0\u306e\u8987\u6c17\u3092\u793a\u3057\u3066\u3044\u307e\u3059\u3002",
        "\uba38\ub9ac\ubd80\ud130 \ubc1c\ub05d\uae4c\uc9c0 \uc99d\uae30 \uac11\uc637\uc73c\ub85c \ub4a4\ub36e\uc778 \ud328\uc655 \ucf54\ub07c\ub9ac. \uad89\uc74c\uc744 \ub0b4\ub3cc\ub294 \uc5d4\uc9c4\uacfc \uc6c0\uad74\uc6c0\uad61 \uc18f\uc544\uc624\ub974\ub294 \uc5f4\uae30\uac00 \ube44\ud560 \ub370 \uc5c6\ub294 \uae30\uacc4\uc801 \uc704\uc555\uac10\uc744 \ub4dc\ub7ec\ub0c5\ub2c8\ub2e4.",
        "全身覆满蒸汽装甲的霸主巨象，轰鸣的引擎与滚滚热气，彰显无与伦比的机械威势。",
    ],
    [
        1011115281, "mecha_name_zhenqibazhu_item",
        "巨象（蒸汽霸主）",
        "Giant Elephant (Steam Overlord)",
        "\u00c9l\u00e9phant G\u00e9ant (Seigneur de la Vapeur)",
        "Riesiger Elefant (Dampf-Overlord)",
        "Elefante Gigante (Senhor do Vapor)",
        "巨象（蒸汽霸主）",
        "Gajah Raksasa (Tuan Uap)",
        "\u0e0a\u0e49\u0e32\u0e07\u0e22\u0e31\u0e01\u0e29\u0e4c (\u0e08\u0e2d\u0e21\u0e40\u0e1c\u0e14\u0e47\u0e08\u0e01\u0e32\u0e23\u0e44\u0e2d\u0e19\u0e49\u0e33)",
        "Elefante Gigante (Se\u00f1or del Vapor)",
        "\u0413\u0438\u0433\u0430\u043d\u0442\u0441\u043a\u0438\u0439 \u0421\u043b\u043e\u043d (\u041f\u0430\u0440\u043e\u0432\u043e\u0439 \u0412\u043b\u0430\u0434\u044b\u043a\u0430)",
        "Dev Fil (Buhar H\u00fck\u00fcmdar\u0131)",
        "Voi Kh\u1ed3ng L\u1ed3 (B\u00e1 Ch\u1ee7 H\u01a1i N\u01b0\u1edbc)",
        "Elefante Gigante (Signore del Vapore)",
        "Gigantyczny S\u0142o\u0144 (W\u0142adca Pary)",
        "\u0641\u064a\u0644 \u0639\u0645\u0644\u0627\u0642 (\u0633\u064a\u062f \u0627\u0644\u0628\u062e\u0627\u0631)",
        "\u5dde\u5927\u306a\u30a8\u30ec\u30d5\u30a1\u30f3\u30c8\uff08\u30b9\u30c1\u30fc\u30e0\u30aa\u30fc\u30d0\u30fc\u30ed\u30fc\u30c9\uff09",
        "\uac70\ub300\ud55c \ucf54\ub07c\ub9ac (\uc99d\uae30 \uad70\uc8fc)",
        "巨象（蒸汽霸主）",
    ],
    [
        1011115282, "mecha_skin_src_zhenqibazhu_item",
        "机械之力，霸者登临。使用后可激活巨象的\u201c蒸汽霸主\u201d涂装。",
        "The power of machinery, the overlord has arrived. After use, it activates the Giant Elephant's \"Steam Overlord\" skin.",
        "La puissance de la m\u00e9canique, le seigneur est arriv\u00e9. Apr\u00e8s utilisation, il active le skin \"Seigneur de la Vapeur\" de l'\u00c9l\u00e9phant G\u00e9ant.",
        "Die Kraft der Mechanik, der Herrscher ist angekommen. Nach der Verwendung aktiviert es die \"Dampf-Overlord\"-Haut des Riesenelefanten.",
        "O poder da maquinaria, o soberano chegou. Ap\u00f3s o uso, ativa a skin \"Senhor do Vapor\" do Elefante Gigante.",
        "機械之力，霸者登臨。使用後可激活巨象的「蒸汽霸主」塗裝。",
        "Kekuatan mesin, sang penguasa telah tiba. Setelah digunakan, ini mengaktifkan skin \"Tuan Uap\" Gajah Raksasa.",
        "\u0e1e\u0e25\u0e31\u0e07\u0e41\u0e2b\u0e48\u0e07\u0e40\u0e04\u0e23\u0e37\u0e48\u0e2d\u0e07\u0e08\u0e31\u0e01\u0e23 \u0e08\u0e2d\u0e21\u0e40\u0e1c\u0e14\u0e47\u0e08\u0e01\u0e32\u0e23\u0e21\u0e32\u0e16\u0e36\u0e07\u0e41\u0e25\u0e49\u0e27 \u0e2b\u0e25\u0e31\u0e07\u0e08\u0e32\u0e01\u0e43\u0e0a\u0e49\u0e41\u0e25\u0e49\u0e27\u0e08\u0e30\u0e40\u0e1b\u0e34\u0e14\u0e43\u0e0a\u0e49\u0e07\u0e32\u0e19\u0e2a\u0e01\u0e34\u0e19 \"\u0e08\u0e2d\u0e21\u0e40\u0e1c\u0e14\u0e47\u0e08\u0e01\u0e32\u0e23\u0e44\u0e2d\u0e19\u0e49\u0e33\" \u0e02\u0e2d\u0e07\u0e0a\u0e49\u0e32\u0e07\u0e22\u0e31\u0e01\u0e29\u0e4c",
        "El poder de la maquinaria, el soberano ha llegado. Despu\u00e9s de usarlo, activa la piel \"Se\u00f1or del Vapor\" del Elefante Gigante.",
        "\u0421\u0438\u043b\u0430 \u043c\u0435\u0445\u0430\u043d\u0438\u043a\u0438, \u0432\u043b\u0430\u0441\u0442\u0438\u0442\u0435\u043b\u044c \u043f\u0440\u0438\u0431\u044b\u043b. \u041f\u043e\u0441\u043b\u0435 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u043d\u0438\u044f \u0430\u043a\u0442\u0438\u0432\u0438\u0440\u0443\u0435\u0442 \u0441\u043a\u0438\u043d \"\u041f\u0430\u0440\u043e\u0432\u043e\u0439 \u0412\u043b\u0430\u0434\u044b\u043a\u0430\" \u0434\u043b\u044f \u0413\u0438\u0433\u0430\u043d\u0442\u0441\u043a\u043e\u0433\u043e \u0421\u043b\u043e\u043d\u0430.",
        "Makinenin g\u00fc\u00e7, h\u00fck\u00fcmdar geldi. Kullan\u0131mdan sonra, Dev Fil'in \"Buhar H\u00fck\u00fcmdar\u0131\" g\u00f6r\u00fcn\u00fcm\u00fcn\u00fc etkinle\u015ftirir.",
        "S\u1ee9c m\u1ea1nh c\u01a1 kh\u00ed, b\u00e1 ch\u1ee7 \u0111\u00e3 \u0111\u1ebfn. Sau khi s\u1eed d\u1ee5ng, n\u00f3 k\u00edch ho\u1ea1t trang ph\u1ee5c \"B\u00e1 Ch\u1ee7 H\u01a1i N\u01b0\u1edbc\" c\u1ee7a Voi Kh\u1ed3ng L\u1ed3.",
        "La potenza della meccanica, il dominatore \u00e8 arrivato. Dopo l'uso, attiva la skin \"Signore del Vapore\" del Gigante Elefante.",
        "Moc mechaniki, w\u0142adca przyby\u0142. Po u\u017cyciu aktywuje sk\u00f3rk\u0119 \"W\u0142adca Pary\" Gigantycznego S\u0142onia.",
        "\u0642\u0648\u0629 \u0627\u0644\u0622\u0644\u0629\u060c \u0627\u0644\u062d\u0627\u0643\u0645 \u0642\u062f \u0648\u0635\u0644. \u0628\u0639\u062f \u0627\u0644\u0627\u0633\u062a\u062e\u062f\u0627\u0645\u060c \u064a\u0642\u0648\u0645 \u0628\u062a\u0641\u0639\u064a\u0644 \u0645\u0638\u0647\u0631 \"\u0633\u064a\u062f \u0627\u0644\u0628\u062e\u0627\u0631\" \u0644\u0644\u0641\u064a\u0644 \u0627\u0644\u0639\u0645\u0644\u0627\u0642.",
        "\u6a5f\u68b0\u306e\u529b\u3001\u8987\u8005\u304c\u767b\u5834\u3002\u4f7f\u7528\u5f8c\u3001\u30b8\u30e3\u30a4\u30a2\u30f3\u30c8\u30a8\u30ec\u30d5\u30a1\u30f3\u30c8\u306e\u300c\u30b9\u30c1\u30fc\u30e0\u30aa\u30fc\u30d0\u30fc\u30ed\u30fc\u30c9\u300d\u30b9\u30ad\u30f3\u3092\u30a2\u30af\u30c6\u30a3\u30d9\u30fc\u30c8\u3057\u307e\u3059\u3002",
        "\uae30\uacc4\uc758 \ud798, \ud328\uc655\uc774 \uc784\ud558\ub2e4. \uc0ac\uc6a9 \ud6c4, \uac70\ub300\ud55c \ucf54\ub07c\ub9ac\uc758 \"\uc99d\uae30 \uad70\uc8fc\" \uc2a4\ud0a8\uc744 \ud65c\uc131\ud654\ud569\ub2c8\ub2e4.",
        "机械之力，霸者登临。使用后可激活巨象的\u201c蒸汽霸主\u201d涂装。",
    ],
    [
        1011115283, "mecha_skin_src_zhenqibazhu_tips",
        "巨象（蒸汽霸主）已激活",
        "Giant Elephant (Steam Overlord) has been activated",
        "\u00c9l\u00e9phant G\u00e9ant (Seigneur de la Vapeur) a \u00e9t\u00e9 activ\u00e9",
        "Riesiger Elefant (Dampf-Overlord) wurde aktiviert",
        "Elefante Gigante (Senhor do Vapor) foi ativado",
        "巨象（蒸汽霸主）已啟動",
        "Gajah Raksasa (Tuan Uap) telah diaktifkan",
        "\u0e0a\u0e49\u0e32\u0e07\u0e22\u0e31\u0e01\u0e29\u0e4c (\u0e08\u0e2d\u0e21\u0e40\u0e1c\u0e14\u0e47\u0e08\u0e01\u0e32\u0e23\u0e44\u0e2d\u0e19\u0e49\u0e33) \u0e16\u0e39\u0e01\u0e40\u0e1b\u0e34\u0e14\u0e43\u0e0a\u0e49\u0e07\u0e32\u0e19\u0e41\u0e25\u0e49\u0e27",
        "Elefante Gigante (Se\u00f1or del Vapor) ha sido activado",
        "\u0413\u0438\u0433\u0430\u043d\u0442\u0441\u043a\u0438\u0439 \u0421\u043b\u043e\u043d (\u041f\u0430\u0440\u043e\u0432\u043e\u0439 \u0412\u043b\u0430\u0434\u044b\u043a\u0430) \u0431\u044b\u043b \u0430\u043a\u0442\u0438\u0432\u0438\u0440\u043e\u0432\u0430\u043d",
        "Dev Fil (Buhar H\u00fck\u00fcmdar\u0131) etkinle\u015ftirildi",
        "Voi Kh\u1ed3ng L\u1ed3 (B\u00e1 Ch\u1ee7 H\u01a1i N\u01b0\u1edbc) \u0111\u00e3 \u0111\u01b0\u1ee3c k\u00edch ho\u1ea1t",
        "L'Elefante Gigante (Signore del Vapore) \u00e8 stato attivato",
        "Gigantyczny S\u0142o\u0144 (W\u0142adca Pary) zosta\u0142 aktywowany",
        "\u062a\u0645 \u062a\u0641\u0639\u064a\u0644 \u0641\u064a\u0644 \u0639\u0645\u0644\u0627\u0642 (\u0633\u064a\u062f \u0627\u0644\u0628\u062e\u0627\u0631)",
        "\u5dde\u5927\u306a\u30a8\u30ec\u30d5\u30a1\u30f3\u30c8\uff08\u30b9\u30c1\u30fc\u30e0\u30aa\u30fc\u30d0\u30fc\u30ed\u30fc\u30c9\uff09\u304c\u30a2\u30af\u30c6\u30a3\u30d9\u30fc\u30c8\u3055\u308c\u307e\u3057\u305f",
        "\uac70\ub300\ud55c \ucf54\ub07c\ub9ac (\uc99d\uae30 \uad70\uc8fc)\uac00 \ud65c\uc131\ud654\ub418\uc5c8\uc2b5\ub2c8\ub2e4",
        "巨象（蒸汽霸主）已激活",
    ],
]

# Verify all rows have 20 columns
for i, row in enumerate(rows):
    assert len(row) == 20, f"Row {i} has {len(row)} cols, expected 20"

append_params = json.dumps({
    "spreadsheetId": SPREADSHEET_ID,
    "range": f"{TARGET_SHEET}!A1",
    "valueInputOption": "RAW",
    "insertDataOption": "INSERT_ROWS",
})

append_body = json.dumps({"values": rows}, ensure_ascii=False)

r = subprocess.run(
    [GWS, "sheets", "spreadsheets", "values", "append",
     "--params", append_params,
     "--json", append_body],
    capture_output=True, text=True, encoding="utf-8", shell=True
)

if r.returncode != 0:
    print("STDERR:", r.stderr)
    sys.exit(1)

result = json.loads(r.stdout)
print("写入页签:", TARGET_SHEET)
print("写入范围:", result["updates"]["updatedRange"])
print("写入行数:", result["updates"]["updatedRows"])
print("写入列数:", result["updates"]["updatedColumns"])
