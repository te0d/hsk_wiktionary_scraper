import logging

import pywikibot
import mwparserfromhell
import wikitextparser

# took this from https://en.wiktionary.org/wiki/Module:zh-new, removed duplicates, and added Definitions (which characters often have)
pos_titles = [
    "Definitions",
    "Noun",
    "Proper noun",
    "Pronoun",
    "Verb",
    "Adjective",
    "Adverb",
    "Preposition",
    "Postposition",
    "Conjunction",
    "Particle",
    "Suffix",
    "Proverb",
    "Idiom",
    "Phrase",
    "Interjection",
    "Classifier",
    "Numeral",
    "Abbreviation",
    "Determiner"
]
title_pattern = r"({})".format("|".join(pos_titles))

sitename = "wiktionary:en"
wiktionary = pywikibot.Site(sitename)

def get_parsed(name):
    page = pywikibot.Page(wiktionary, name)
    parsed = mwparserfromhell.parse(page.text)
    return parsed

def extract_definition(parsed):
    # yeah, grab the def section via mwparserfromhell, use wikitextparser to get the first list item,
    # then input into mwparserfromhell again to strip wikitext markup, templates, etc. fixme
    # while characters have a definitions section typically, words may have a pos title which is also checked
    wt_meaning = ''
    try:
        mw_meanings = parsed.get_sections(matches="Chinese")[0].get_sections(matches=title_pattern, flat=True, include_headings=False)[0]
        wt_meaning = wikitextparser.parse(str(mw_meanings)).get_lists()[0].items[0]
    except:
        pass

    return wt_meaning

def get_info(simplified):
    parsed = get_parsed(simplified)
    templates = parsed.filter_templates()

    # Traditional Character
    # try to find the traditional word, not sure how reliable this is
    # or rather I know there's nuance where a single simplified character
    # can simplify multiple traditional characters with different meanings
    # so that should be handled; fixme
    zh_see_values = [t.get(1).value for t in parsed.filter_templates() if t.name.strip() == 'zh-see' and (not t.has(2) or t.get(2) in ['s', 'sv', 'svt'])]
    trad_character = None
    trad_parsed = None
    trad_templates = None
    for value in zh_see_values:
        new_parsed = get_parsed(value)
        new_templates = new_parsed.filter_templates()
        new_zh_forms = [t for t in new_templates if t.name.strip() == 'zh-forms']
        if new_zh_forms and new_zh_forms[0].has('s') and new_zh_forms[0].get('s').value.strip() == simplified:
            # hopefully this means we found the matching traditional page for the simplified input,
            # with which we can grab the appropriate pronunciation and definition;
            # takes the first match it finds
            trad_character = value
            trad_parsed = new_parsed
            trad_templates = new_templates
            logging.info("Found traditional page.")
            break

    # Pinyin Pronunciation
    zh_pron = [t for t in templates if t.name.strip() == 'zh-pron']
    trad_pron = [t for t in trad_templates if t.name.strip() == 'zh-pron'] if trad_templates else None
    # there are some trad characters that are not the "main" definition, so I assume simplified and traditional
    # are the same if both pronunciation and meaning are availabile on the simplified character page
    used_trad_info = False

    if zh_pron and zh_pron[0].has('m'):
        pronunciation = zh_pron[0].get('m').value.split(',')[0].strip()
    elif trad_pron and trad_pron[0].has('m'):
        pronunciation = trad_pron[0].get('m').value.split(',')[0].strip()
        used_trad_info = True
    else:
        pronunciation = ''

    # Meaning
    # just take the first meaning (really should be cross-referenced with desired HSK3.0 pronunciation); fixme
    logging.info("Looking for definition '{}'.".format(simplified))
    wt_meaning = extract_definition(parsed)
    if not wt_meaning and trad_parsed:
        logging.info("Checking Traditional for definition '{}'.".format(simplified))
        wt_meaning = extract_definition(trad_parsed)

    if not wt_meaning:
        logging.warning("Could not find meaning '{}'.".format(simplified))

    # there's numerous templates I'm not familiar with, but if I don't get any text from the first meaning
    # after it's stripped, I try again but keeping the template arguments for characters like '们'
    meaning = mwparserfromhell.parse(wt_meaning).strip_code().strip()
    if len(meaning) == 0:
        meaning = mwparserfromhell.parse(wt_meaning).strip_code(keep_template_params=True).strip()

    # Output
    logging.info("'{}' has meaning '{}'.".format(simplified, meaning))
    info = {
        "simplified": simplified,
        "traditional": str(trad_character) if trad_character and used_trad_info else simplified,
        "pinyin_accent": pronunciation,
        "meaning": meaning
    }

    return info
