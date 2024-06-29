# This script loads some data from Hyperglot and stores it in a format compatible to jkUnicode

import hyperglot

# import pprint
import json
from jkUnicode.uniCase import uniUpperCaseMapping, uniLowerCaseMapping

language_speakers_CLDR = {'aa': 2119662, 'ab': 91952, 'ace': 3738364, 'ach': 1600361, 'ada': 880206, 'ady': 444583, 'aeb': 10549080, 'af': 9318844, 'agq': 38843, 'ak': 11442678, 'aln': 1430249, 'alt': 19841, 'am': 35728475, 'an': 26008, 'ar': 351664187, 'arn': 272802, 'aro': 104, 'arq': 35667507, 'ars': 1025205, 'ary': 30938679, 'arz': 66639360, 'as': 17239170, 'asa': 702633, 'ast': 650205, 'atj': 6407, 'av': 552715, 'awa': 25862923, 'ay': 2838620, 'az': 32446679, 'ba': 1842386, 'bal': 8227886, 'ban': 4806468, 'bar': 22043626, 'bas': 332940, 'bax': 332940, 'bbc': 2456639, 'bbj': 388430, 'be': 10064517, 'bej': 2460326, 'bem': 5402246, 'bew': 5607546, 'bez': 995397, 'bfd': 158146, 'bfq': 305000, 'bg': 7878313, 'bgc': 15913080, 'bgn': 2037380, 'bho': 32934796, 'bi': 268499, 'bik': 3275430, 'bin': 1519598, 'bjn': 4010287, 'bkm': 360685, 'bla': 4900, 'blo': 51505, 'blt': 681176, 'bm': 9385632, 'bn': 267193287, 'bo': 3006695, 'bpy': 90174, 'bqi': 1188926, 'br': 563140, 'bra': 54369, 'brh': 3035513, 'brx': 1856526, 'bs': 7594468, 'bss': 149823, 'bua': 311788, 'bug': 4298211, 'bum': 1276269, 'byn': 79055, 'byv': 305195, 'ca': 8679137, 'cch': 44945, 'ccp': 729137, 'ce': 935365, 'ceb': 26203440, 'cgg': 2335662, 'ch': 46323, 'chk': 30730, 'chm': 524371, 'cho': 10977, 'chp': 12815, 'chr': 25613, 'ckb': 11086548, 'clc': 866, 'co': 162835, 'cps': 720594, 'cr': 9046, 'crg': 678, 'crh': 245968, 'crk': 4146, 'crl': 376, 'crs': 94061, 'cs': 13045532, 'csb': 49766, 'csw': 1809, 'cv': 1842386, 'cy': 884910, 'da': 7072055, 'dak': 20831, 'dar': 368477, 'dav': 438928, 'de': 136350219, 'den': 2299, 'dgr': 2110, 'dje': 3871308, 'doi': 2652180, 'dsb': 6973, 'dtp': 182851, 'dua': 133176, 'dv': 388043, 'dyo': 409146, 'dyu': 6667328, 'dz': 370341, 'ebu': 802918, 'ee': 4690856, 'efi': 2996392, 'egl': 31201, 'el': 12292235, 'en': 1636485484, 'eo': 301, 'es': 493528071, 'esu': 20956, 'et': 878448, 'eu': 1088518, 'ewo': 860095, 'ext': 245077, 'fa': 84710454, 'fan': 426450, 'ff': 7788902, 'fi': 5736840, 'fil': 67471094, 'fit': 56113, 'fj': 365029, 'fo': 71349, 'fon': 3216150, 'fr': 278611489, 'frc': 27941, 'frp': 63777, 'frr': 9619, 'frs': 2003, 'fur': 37441, 'fy': 743057, 'ga': 1237486, 'gaa': 821525, 'gag': 111028, 'gan': 23698340, 'gay': 320431, 'gbz': 7982, 'gd': 72337, 'gil': 67077, 'gl': 3515529, 'glk': 3906471, 'gn': 5827106, 'gon': 3182616, 'gor': 1094806, 'gsw': 7956950, 'gu': 61721797, 'guc': 132528, 'gur': 1026907, 'guz': 2622867, 'gv': 1719, 'gwi': 301, 'ha': 40411880, 'hak': 32062459, 'haw': 29604, 'he': 8675480, 'hi': 546882142, 'hif': 383749, 'hil': 9171204, 'hnj': 781682, 'ho': 152448, 'hr': 6813158, 'hsb': 12825, 'hsn': 40426580, 'ht': 8964918, 'hu': 12443426, 'hur': 716, 'hy': 5317267, 'hz': 239336, 'ia': 135, 'iba': 816302, 'ibb': 2996392, 'id': 171207687, 'ie': 1, 'ig': 27823640, 'ii': 8364120, 'ik': 7983, 'ilo': 10481376, 'inh': 226755, 'is': 350734, 'it': 70247055, 'iu': 90464, 'izh': 141, 'ja': 119729024, 'jam': 2668141, 'jgo': 94333, 'jmc': 433290, 'jv': 91180665, 'ka': 3543644, 'kaa': 2177222, 'kab': 3351886, 'kac': 962031, 'kaj': 449458, 'kam': 4068120, 'kbd': 1070872, 'kcg': 199046, 'kde': 1463820, 'kea': 530762, 'ken': 69362, 'kfo': 63206, 'kg': 1526700, 'kgp': 50811, 'kha': 1060872, 'khq': 332407, 'khw': 350251, 'ki': 9099743, 'kiu': 155833, 'kj': 920524, 'kk': 13637392, 'kkj': 149823, 'kl': 55440, 'kln': 4068120, 'km': 15065030, 'kmb': 8130575, 'kn': 49065330, 'ko': 78357046, 'koi': 63774, 'kok': 4243488, 'kos': 7990, 'kpe': 1186303, 'krc': 240927, 'kri': 6293683, 'krj': 425805, 'krl': 116212, 'kru': 2519571, 'ks': 5598084, 'ksb': 995397, 'ksf': 88784, 'ksh': 240479, 'ku': 6866754, 'kum': 283444, 'kv': 255099, 'kw': 1972, 'kwk': 376, 'kxv': 38456, 'ky': 3338266, 'la': 820, 'lad': 112781, 'lag': 509409, 'lah': 93433552, 'lb': 421015, 'lez': 255099, 'lg': 5622890, 'li': 950422, 'lij': 536663, 'lil': 527, 'lkt': 8315, 'lmo': 3901516, 'ln': 3514490, 'lo': 5138706, 'lol': 620858, 'loz': 1045596, 'lrc': 2020512, 'lt': 2488616, 'ltg': 167429, 'lu': 2340939, 'lua': 9770880, 'luo': 5245734, 'luy': 5888069, 'lv': 1147550, 'lzz': 22964, 'mad': 16822638, 'maf': 205313, 'mag': 15913080, 'mai': 19249149, 'mak': 1949289, 'man': 3511762, 'mas': 1734738, 'mdf': 297616, 'mdr': 245663, 'men': 1813082, 'mer': 2141116, 'mfe': 1241433, 'mg': 24260130, 'mgh': 1354419, 'mgo': 130401, 'mh': 56879, 'mi': 137913, 'mic': 7915, 'min': 8010780, 'mk': 1608562, 'ml': 43257483, 'mn': 6572844, 'mni': 1476590, 'moe': 12062, 'moh': 1771, 'mos': 8334160, 'mr': 92826300, 'mrj': 29761, 'ms': 38097304, 'mt': 457267, 'mua': 277450, 'mus': 3991, 'mwr': 15913080, 'mwv': 64086, 'my': 36559231, 'myv': 439338, 'mzn': 4246165, 'na': 6930, 'nan': 26486380, 'nap': 605306, 'naq': 289307, 'nb': 5468932, 'nd': 1745556, 'nds': 11520008, 'ne': 20903374, 'new': 1000820, 'ng': 552314, 'niu': 1120, 'njo': 305000, 'nl': 31765643, 'nmg': 8878, 'nn': 1366860, 'nnh': 388430, 'no': 5467440, 'nqo': 626370, 'nr': 903417, 'nso': 5307578, 'nus': 591427, 'nv': 166319, 'ny': 17026780, 'nym': 1932242, 'nyn': 2724939, 'nzi': 293402, 'oc': 2040397, 'oj': 23747, 'ojs': 15077, 'oka': 490, 'om': 34897120, 'or': 42434880, 'os': 541444, 'pa': 203571208, 'pag': 1528534, 'pam': 2511162, 'pap': 211640, 'pau': 16046, 'pcd': 746330, 'pcm': 44945880, 'pdc': 129729, 'pdt': 90465, 'pis': 561779, 'pl': 41077396, 'pms': 6177, 'pnt': 392462, 'pon': 23560, 'pqm': 490, 'prg': 38, 'ps': 53542641, 'pt': 237496876, 'qu': 11385851, 'quc': 1200731, 'qug': 963579, 'raj': 1326090, 'rhg': 1824081, 'rif': 3692410, 'rm': 42019, 'rn': 7475454, 'ro': 22187406, 'rof': 433290, 'rtm': 2527, 'ru': 196713954, 'rue': 527074, 'rug': 9591, 'rw': 11083625, 'rwk': 128816, 'sa': 15913, 'sah': 453510, 'saq': 246228, 'sas': 2590152, 'sat': 7293495, 'saz': 384566, 'sbp': 117105, 'sc': 1060845, 'scn': 511702, 'sco': 1644027, 'sd': 40329510, 'sdc': 106084, 'sdh': 3142162, 'se': 51528, 'seh': 1384517, 'sei': 900, 'ses': 664815, 'sg': 2935521, 'shi': 6187734, 'shn': 3687984, 'si': 15564656, 'sid': 3783955, 'sk': 6680269, 'sl': 1973177, 'sli': 11867, 'sly': 144194, 'sm': 252716, 'sma': 295, 'smj': 1530, 'smn': 612, 'sms': 612, 'sn': 11782503, 'snk': 1153650, 'so': 16911643, 'sq': 6791903, 'sr': 15602407, 'srn': 414506, 'srr': 1731004, 'ss': 2212378, 'ssy': 218923, 'st': 6390567, 'stq': 961, 'su': 32043120, 'suk': 5094093, 'sus': 1378014, 'sv': 12932870, 'sw': 171610295, 'swb': 170720, 'syr': 210657, 'szl': 497669, 'ta': 85616157, 'tcy': 1989135, 'te': 95478480, 'tem': 1722481, 'teo': 2082973, 'tet': 816394, 'tg': 9644223, 'th': 55181920, 'ti': 10145910, 'tig': 1094616, 'tiv': 3424448, 'tk': 6870837, 'tkl': 1284, 'tkr': 16329, 'tly': 1000168, 'tmh': 1776965, 'tn': 6113426, 'to': 100790, 'tog': 207726, 'tpi': 5154216, 'tr': 80408082, 'tru': 3034, 'trv': 4720, 'trw': 123755, 'ts': 4880931, 'tsd': 201, 'tt': 1984108, 'ttt': 22452, 'tum': 1780514, 'tvl': 9867, 'twq': 7970, 'ty': 91487, 'tyv': 184238, 'tzm': 3485046, 'udm': 538543, 'ug': 8052965, 'uk': 29348974, 'umb': 9431467, 'und': 323, 'ur': 290790290, 'uz': 39027133, 'vai': 131905, 've': 1391758, 'vec': 1380828, 'vep': 3543, 'vi': 86222961, 'vls': 1172070, 'vmf': 4809582, 'vmw': 3912766, 'vro': 70031, 'vun': 433290, 'wa': 679800, 'wae': 11375, 'wal': 1946034, 'war': 3166927, 'wbp': 2495, 'wo': 11025493, 'wuu': 83641200, 'xh': 10182944, 'xmf': 439670, 'xnr': 2121744, 'xog': 2292409, 'yao': 722356, 'yap': 6555, 'yav': 2302, 'ybb': 443920, 'yi': 997212, 'yo': 28685568, 'yrl': 26170, 'yue': 79654758, 'za': 4321462, 'zea': 241925, 'zgh': 7823574, 'zh': 1304678908, 'zu': 13973827, 'zza': 1148245}
ISO_3letter_to_2letter = {"aar":"aa","abk":"ab","afr":"af","aka":"ak","amh":"am","ara":"ar","arg":"an","asm":"as","ava":"av","ave":"ae","aym":"ay","aze":"az","bak":"ba","bam":"bm","bel":"be","ben":"bn","bis":"bi","bod":"bo","bos":"bs","bre":"br","bul":"bg","cat":"ca","ces":"cs","cha":"ch","che":"ce","chu":"cu","chv":"cv","cor":"kw","cos":"co","cre":"cr","cym":"cy","dan":"da","deu":"de","div":"dv","dzo":"dz","ell":"el","eng":"en","epo":"eo","est":"et","eus":"eu","ewe":"ee","fao":"fo","fas":"fa","fij":"fj","fin":"fi","fra":"fr","fry":"fy","ful":"ff","gla":"gd","gle":"ga","glg":"gl","glv":"gv","grn":"gn","guj":"gu","hat":"ht","hau":"ha","hbs":"sh","heb":"he","her":"hz","hin":"hi","hmo":"ho","hrv":"hr","hun":"hu","hye":"hy","ibo":"ig","ido":"io","iii":"ii","iku":"iu","ile":"ie","ina":"ia","ind":"id","ipk":"ik","isl":"is","ita":"it","jav":"jv","jpn":"ja","kal":"kl","kan":"kn","kas":"ks","kat":"ka","kau":"kr","kaz":"kk","khm":"km","kik":"ki","kin":"rw","kir":"ky","kom":"kv","kon":"kg","kor":"ko","kua":"kj","kur":"ku","lao":"lo","lat":"la","lav":"lv","lim":"li","lin":"ln","lit":"lt","ltz":"lb","lub":"lu","lug":"lg","mah":"mh","mal":"ml","mar":"mr","mkd":"mk","mlg":"mg","mlt":"mt","mon":"mn","mri":"mi","msa":"ms","mya":"my","nau":"na","nav":"nv","nbl":"nr","nde":"nd","ndo":"ng","nep":"ne","nld":"nl","nno":"nn","nob":"nb","nor":"no","nya":"ny","oci":"oc","oji":"oj","ori":"or","orm":"om","oss":"os","pan":"pa","pli":"pi","pol":"pl","por":"pt","pus":"ps","que":"qu","roh":"rm","ron":"ro","run":"rn","rus":"ru","sag":"sg","san":"sa","sin":"si","slk":"sk","slv":"sl","sme":"se","smo":"sm","sna":"sn","snd":"sd","som":"so","sot":"st","spa":"es","sqi":"sq","srd":"sc","srp":"sr","ssw":"ss","sun":"su","swa":"sw","swe":"sv","tah":"ty","tam":"ta","tat":"tt","tel":"te","tgk":"tg","tgl":"tl","tha":"th","tir":"ti","ton":"to","tsn":"tn","tso":"ts","tuk":"tk","tur":"tr","twi":"tw","uig":"ug","ukr":"uk","urd":"ur","uzb":"uz","ven":"ve","vie":"vi","vol":"vo","wln":"wa","wol":"wo","xho":"xh","yid":"yi","yor":"yo","zha":"za","zho":"zh","zul":"zu",}
ISO_3letter_to_2letter['cmn'] = 'zh'
# ^ Not sure whether this is correct but it helps get Hyperglot and jkUnicode in line

script_codes = {
	"Adlam": "Adlm",
	"Afaka": "Afak",
	"Caucasian Albanian": "Aghb",
	"Ahom, Tai Ahom": "Ahom",
	"Arabic": "Arab",
	"Arabic (Nastaliq variant)": "Aran",
	"Imperial Aramaic": "Armi",
	"Armenian": "Armn",
	"Avestan": "Avst",
	"Balinese": "Bali",
	"Bamum": "Bamu",
	"Bassa Vah": "Bass",
	"Batak": "Batk",
	"Bengali (Bangla)": "Beng",
	"Bengali": "Beng",
	"Bhaiksuki": "Bhks",
	"Blissymbols": "Blis",
	"Bopomofo": "Bopo",
	"Brahmi": "Brah",
	"Braille": "Brai",
	"Buginese": "Bugi",
	"Buhid": "Buhd",
	"Chakma": "Cakm",
	"Unified Canadian Aboriginal Syllabics": "Cans",
	"Ojibwe Syllabics": "Cans",
	"Cree": "Cans",
	"Inuktitut Syllabics": "Cans",
	"Carian": "Cari",
	"Cham": "Cham",
	"Cherokee": "Cher",
	"Chisoi": "Chis",
	"Chorasmian": "Chrs",
	"Cirth": "Cirt",
	"Coptic": "Copt",
	"Cypro-Minoan": "Cpmn",
	"Cypriot syllabary": "Cprt",
	"Cyrillic": "Cyrl",
	"Cyrillic (Old Church Slavonic variant)": "Cyrs",
	"Devanagari (Nagari)": "Deva",
	"Devanagari": "Deva",
	"Dives Akuru": "Diak",
	"Dogra": "Dogr",
	"Deseret (Mormon)": "Dsrt",
	"Duployan shorthand, Duployan stenography": "Dupl",
	"Egyptian demotic": "Egyd",
	"Egyptian hieratic": "Egyh",
	"Egyptian hieroglyphs": "Egyp",
	"Egyptian Hieroglyphs": "Egyp",
	"Elbasan": "Elba",
	"Elymaic": "Elym",
	"Ethiopic (Geʻez)": "Ethi",
	"Geʽez": "Ethi",
	"Garay": "Gara",
	"Khutsuri (Asomtavruli and Nuskhuri)": "Geok",
	"Georgian (Mkhedruli and Mtavruli)": "Geor",
	"Georgian": "Geor",
	"Glagolitic": "Glag",
	"Gunjala Gondi": "Gong",
	"Masaram Gondi": "Gonm",
	"Gothic": "Goth",
	"Grantha": "Gran",
	"Greek": "Grek",
	"Gujarati": "Gujr",
	"Gurung Khema": "Gukh",
	"Gurmukhi": "Guru",
	"Han with Bopomofo (alias for Han + Bopomofo)": "Hanb",
	"Hangul (Hangŭl, Hangeul)": "Hang",
	"Hangul": "Hang",
	"Han (Hanzi, Kanji, Hanja)": "Hani",
	"Kanji": "Hani",
	"Hanja": "Hani",
	"Chinese": "Hani",
	"Hanunoo (Hanunóo)": "Hano",
	"Hanunoo": "Hano",
	"Han (Simplified variant)": "Hans",
	"Han (Traditional variant)": "Hant",
	"Hatran": "Hatr",
	"Hebrew": "Hebr",
	"Hiragana": "Hira",
	"Anatolian Hieroglyphs (Luwian Hieroglyphs, Hittite Hieroglyphs)": "Hluw",
	"Pahawh Hmong": "Hmng",
	"Nyiakeng Puachue Hmong": "Hmnp",
	"Japanese syllabaries (alias for Hiragana + Katakana)": "Hrkt",
	"Old Hungarian (Hungarian Runic)": "Hung",
	"Indus (Harappan)": "Inds",
	"Old Italic (Etruscan, Oscan, etc.)": "Ital",
	"Jamo (alias for Jamo subset of Hangul)": "Jamo",
	"Javanese": "Java",
	"Japanese (alias for Han + Hiragana + Katakana)": "Jpan",
	"Jurchen": "Jurc",
	"Kayah Li": "Kali",
	"Katakana": "Kana",
	"Kawi": "Kawi",
	"Kharoshthi": "Khar",
	"Khmer": "Khmr",
	"Khojki": "Khoj",
	"Khitan large script": "Kitl",
	"Khitan small script": "Kits",
	"Kannada": "Knda",
	"Korean (alias for Hangul + Han)": "Kore",
	"Kpelle": "Kpel",
	"Kirat Rai": "Krai",
	"Kaithi": "Kthi",
	"Tai Tham (Lanna)": "Lana",
	"Tham": "Lana",
	"Lao": "Laoo",
	"Latin (Fraktur variant)": "Latf",
	"Latin (Gaelic variant)": "Latg",
	"Latin": "Latn",
	"Leke": "Leke",
	"Lepcha (Róng)": "Lepc",
	"Limbu": "Limb",
	"Linear A": "Lina",
	"Linear B": "Linb",
	"Lisu (Fraser)": "Lisu",
	"Loma": "Loma",
	"Lycian": "Lyci",
	"Lydian": "Lydi",
	"Mahajani": "Mahj",
	"Makasar": "Maka",
	"Mandaic, Mandaean": "Mand",
	"Manichaean": "Mani",
	"Marchen": "Marc",
	"Mayan hieroglyphs": "Maya",
	"Medefaidrin (Oberi Okaime, Oberi Ɔkaimɛ)": "Medf",
	"Mende Kikakui": "Mend",
	"Meroitic Cursive": "Merc",
	"Meroitic Hieroglyphs": "Mero",
	"Malayalam": "Mlym",
	"Modi, Moḍī": "Modi",
	"Mongolian": "Mong",
	"Moon (Moon code, Moon script, Moon type)": "Moon",
	"Mro, Mru": "Mroo",
	"Meitei Mayek (Meithei, Meetei)": "Mtei",
	"Multani": "Mult",
	"Myanmar (Burmese)": "Mymr",
	"Burmese": "Mymr",
	"Nag Mundari": "Nagm",
	"Nandinagari": "Nand",
	"Old North Arabian (Ancient North Arabian)": "Narb",
	"Nabataean": "Nbat",
	"Newa, Newar, Newari, Nepāla lipi": "Newa",
	"Naxi Dongba (na²¹ɕi³³ to³³ba²¹, Nakhi Tomba)": "Nkdb",
	"Naxi Geba (na²¹ɕi³³ gʌ²¹ba²¹, 'Na-'Khi ²Ggŏ-¹baw, Nakhi Geba)": "Nkgb",
	"N’Ko": "Nkoo",
	"N'Ko": "Nkoo",
	"Nüshu": "Nshu",
	"Ogham": "Ogam",
	"Ol Chiki (Ol Cemet’, Ol, Santali)": "Olck",
	"Ol Onal": "Onao",
	"Old Turkic, Orkhon Runic": "Orkh",
	"Oriya (Odia)": "Orya",
	"Oriya": "Orya",
	"Osage": "Osge",
	"Osmanya": "Osma",
	"Old Uyghur": "Ougr",
	"Palmyrene": "Palm",
	"Pau Cin Hau": "Pauc",
	"Proto-Cuneiform": "Pcun",
	"Proto-Elamite": "Pelm",
	"Old Permic": "Perm",
	"Phags-pa": "Phag",
	"Inscriptional Pahlavi": "Phli",
	"Psalter Pahlavi": "Phlp",
	"Book Pahlavi": "Phlv",
	"Phoenician": "Phnx",
	"Miao (Pollard)": "Plrd",
	"Klingon (KLI pIqaD)": "Piqd",
	"Inscriptional Parthian": "Prti",
	"Proto-Sinaitic": "Psin",
	"Reserved for private use (start)": "Qaaa",
	"Reserved for private use (end)": "Qabx",
	"Ranjana": "Ranj",
	"Rejang (Redjang, Kaganga)": "Rjng",
	"Hanifi Rohingya": "Rohg",
	"Rongorongo": "Roro",
	"Runic": "Runr",
	"Samaritan": "Samr",
	"Sarati": "Sara",
	"Old South Arabian": "Sarb",
	"Ancient South Arabian": "Sarb",
	"Saurashtra": "Saur",
	"SignWriting": "Sgnw",
	"Shavian (Shaw)": "Shaw",
	"Sharada, Śāradā": "Shrd",
	"Shuishu": "Shui",
	"Siddham, Siddhaṃ, Siddhamātṛkā": "Sidd",
	"Sidetic": "Sidt",
	"Khudawadi, Sindhi": "Sind",
	"Sinhala": "Sinh",
	"Sogdian": "Sogd",
	"Old Sogdian": "Sogo",
	"Sora Sompeng": "Sora",
	"Soyombo": "Soyo",
	"Sundanese": "Sund",
	"Sunuwar": "Sunu",
	"Syloti Nagri": "Sylo",
	"Syriac": "Syrc",
	"Syriac (Estrangelo variant)": "Syre",
	"Syriac (Western variant)": "Syrj",
	"Syriac (Eastern variant)": "Syrn",
	"Tagbanwa": "Tagb",
	"Takri, Ṭākrī, Ṭāṅkrī": "Takr",
	"Tai Le": "Tale",
	"New Tai Lue": "Talu",
	"Tamil": "Taml",
	"Tangut": "Tang",
	"Tai Viet": "Tavt",
	"Tai Yo": "Tayo",
	"Telugu": "Telu",
	"Tengwar": "Teng",
	"Tifinagh (Berber)": "Tfng",
	"Tifinagh": "Tfng",
	"Tagalog (Baybayin, Alibata)": "Tglg",
	"Baybayin": "Tglg",
	"Thaana": "Thaa",
	"Thai": "Thai",
	"Tibetan": "Tibt",
	"Tirhuta": "Tirh",
	"Tangsa": "Tnsa",
	"Todhri": "Todr",
	"Tolong Siki": "Tols",
	"Toto": "Toto",
	"Tulu-Tigalari": "Tutg",
	"Ugaritic": "Ugar",
	"Vai": "Vaii",
	"Visible Speech": "Visp",
	"Vithkuqi": "Vith",
	"Warang Citi (Varang Kshiti)": "Wara",
	"Wancho": "Wcho",
	"Woleai": "Wole",
	"Old Persian": "Xpeo",
	"Cuneiform, Sumero-Akkadian": "Xsux",
	"Sumero-Akkadian Cuneiforms": "Xsux",
	"Yezidi": "Yezi",
	"Yi": "Yiii",
	"Modern Yi": "Yiii",
	"Zanabazar Square (Zanabazarin Dörböljin Useg, Xewtee Dörböljin Bicig, Horizontal Square Script)": "Zanb",
	"Code for inherited script": "Zinh",
	"Mathematical notation": "Zmth",
	"Symbols (Emoji variant)": "Zsye",
	"Symbols": "Zsym",
	"Code for unwritten documents": "Zxxx",
	"Code for undetermined script": "Zyyy",
	"Code for uncoded script": "Zzzz",
}

with open("jkUnicode/json/ignored_languages.json", "r") as text_file:
	ignored_languages = json.load(text_file)

language_characters_hyperglot = {}
language_speakers_combined = language_speakers_CLDR
languages = sorted(dict(hyperglot.languages.Languages()).items())
territory = 'dflt'
# ^ Hyperglot does not work with territories

def contains_lowercase(cp, code_points):
	# returns True if cp exists in the mapping,
	# the LC variant exists in the font,
	# and the round-trip is correct
	try:
		return uniLowerCaseMapping[cp] in code_points and uniUpperCaseMapping[uniLowerCaseMapping[cp]] == cp
	except KeyError:
		return False

def reduced_and_sorted(input):
	return sorted([c for c in input if not contains_lowercase(c, input)])

def code_points_reduced(str):
	code_points = set([ord(c) for c in ''.join(str.split())])
	# ^ Hyperglot sometimes contains duplicates, usually combining diacritics.
	#	Huh? Why are combining diacritics to be found in the base/auxilliary characters?
	# TODO: Tidy this up?
	return reduced_and_sorted(code_points)

all_names = set()
for code, data in languages:
	try:
		code = ISO_3letter_to_2letter[code]
	except KeyError:
		pass
	if code in ignored_languages:
		continue
	try:
		orthographies = data['orthographies']
	except KeyError:
		# seems to be a macrolanguage
		continue
	for orthography in orthographies:
		if orthography['status'] == 'primary':
			default_script = script_codes[orthography['script']]
			break
	language_dict = {}
	for orthography in orthographies:
		if data['validity'] == 'draft':
			continue
		assert(data['validity'] == 'preliminary' or data['validity'] == 'verified')
		# ^ So that we catch new types of validity in case they are introduced
		script = script_codes[orthography['script']].replace(default_script, 'DFLT')
		if script in language_dict:
			# We have already added this script to the language.
			# There is no systematic way of finding out what makes this orthography
			# different from the one already processed.
			# In some cases, the only difference between two orthographies is the note.
			
			# The best we can do is to add this orthography (i.e. the possible surplus) as optional characters:
			unicodes_dict = language_dict[script][territory]['unicodes']
			combined_full = set(code_points_reduced(orthography['base']))
			if 'auxiliary' in orthography:
				combined_full.update(code_points_reduced(orthography['auxiliary']))
			if 'optional' in unicodes_dict:
				combined_full.update(unicodes_dict['optional'])
			existing_base = set(unicodes_dict['base'])
			combined_opt = combined_full - existing_base
			unicodes_dict['optional'] = reduced_and_sorted(combined_opt)
		else:
			unicodes_dict = {}
			unicodes_dict['base'] = code_points_reduced(orthography['base'])
			if 'auxiliary' in orthography:
				unicodes_dict['optional'] = code_points_reduced(orthography['auxiliary'])
			name = data['name']
			if script != 'DFLT':
				name += ' (' + orthography['script'] + ')'
				# TODO: somehow store and transfer orthography['status'],
				#       e.g. limit the number of “speakers”
				# print(orthography['status'], name, '– default script', default_script)
			assert(name not in all_names)
			all_names.add(name)
			orthography_dict = {'name': name, 'unicodes': unicodes_dict}
			language_dict[script] = {territory: orthography_dict}
	language_characters_hyperglot[code] = language_dict
	# speakers:
	try:
		speakers = data['speakers']
		# Apparently, Hyperglot counts only L1 speakers
		# so this is usually smaller than CLDR.
	except KeyError:
		continue
	if not speakers:
		# may be None or 0
		continue
	try:
		speakers_CLDR = language_speakers_combined[code]
	except KeyError:
		language_speakers_combined[code] = speakers
		continue
	if speakers > speakers_CLDR:
		# larger figure from Hyperglot, probably newer data.
		# let’s use this Hyperglot:
		language_speakers_combined[code] = speakers
	elif speakers > speakers_CLDR / 3:
		# somewhat smaller figure from Hyperglot, probably because only L1.
		# let’s use the average:
		language_speakers_combined[code] = int((speakers_CLDR + speakers) / 2)
	else:
		# much smaller figure from Hyperglot, probably because only L1.
		# let’s apply a minimum (i.e. the average of CLDR and 1/3 of it):
		language_speakers_combined[code] = int(speakers_CLDR * 2 / 3)

with open("jkUnicode/json/language_characters_hyperglot.json", "w") as text_file:
	text_file.write(json.dumps(language_characters_hyperglot, indent=4))
with open("jkUnicode/json/language_speakers.json", "w") as text_file:
	text_file.write(json.dumps(language_speakers_combined, indent=4))
