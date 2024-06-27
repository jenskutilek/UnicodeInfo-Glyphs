# This script loads some data from Hyperglot and stores it in a format compatible to jkUnicode

import hyperglot

# import pprint
import json
from jkUnicode.uniCase import uniLowerCaseMapping

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
languages = sorted(dict(hyperglot.languages.Languages()).items())
territory = 'dflt'
# ^ Hyperglot does not work with territories

def contains_lowercase(cp, code_points):
	try:
		if uniLowerCaseMapping[cp] in code_points:
			return True
	except KeyError:
		pass
	return False

def reduced_and_sorted(input):
	return sorted([c for c in input if not contains_lowercase(c, input)])

def code_points_reduced(str):
	code_points = set([ord(c) for c in ''.join(str.split())])
	# ^ Hyperglot sometimes contains duplicates, usually combining diacritics.
	#	Huh? Why are combining diacritics to be found in the base/auxilliary characters?
	# TODO: Tidy this up?
	return reduced_and_sorted(code_points)

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
	default_script =  script_codes[orthographies[0]['script']]
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
			orthography_dict = {'name': data['name'], 'unicodes': unicodes_dict}
			language_dict[script] = {territory: orthography_dict}
	language_characters_hyperglot[code] = language_dict
	
with open("jkUnicode/json/language_characters_hyperglot.json", "w") as text_file:
	text_file.write(json.dumps(language_characters_hyperglot, indent=4))
