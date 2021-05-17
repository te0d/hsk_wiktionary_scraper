# HSK 3.0 Wiktionary Scraper

This is something I put together to build a vocab list for the new HSK 3.0 words. Beside not being able to find all the
words, there are numerous errors. The bot simply looks for the first matching definition, but this is frequently not the
meaning of interest. It also doesn't handle various templates used in the meaning.

I went through the json output in the assets/ folder and manually updated some meanings after quickly looking through
earlier words.

## Install

Set up a python3 venv for the pip dependencies. Then install the following dependencies:


```
pip install pywikibot mwparserfromhell wikitextbot
```

## Usage

```
python build_dict.py
```

## Contributing

PRs accepted.

## License

Data under:

CC BY-SA 3.0

Code under:

ISC © Tom O'Donnell
