# Mongolia — legislation as Markdown (LawCodex)

Legislation of Mongolia (Монгол Улс) as Markdown, in Mongolian (Cyrillic). Part of
[LawCodex](https://github.com/LawCodex).

Retrieved: **2026-10-12**.

## Coverage

__COUNTS__

All acts of the following categories that the Unified Legal Information System marks as **valid /
in force** (*Хүчинтэй*), in the consolidated version shown by the system (amendment notes such as
"/Энэ хэсгийг … хуулиар нэмсэн/" are part of the published text and kept):

* the **Constitution of Mongolia** (1992, with its amendments);
* all **laws** (*Монгол Улсын хууль* — in Mongolia codes are laws too: Civil Law, Criminal Law,
  General Administrative Law, Law on Tax …);
* **decrees of the President** (*Ерөнхийлөгчийн зарлиг*) in force — small volume, so included.
  Annexes (e.g. regulations approved by a decree) that the system only publishes as attachments are
  not included.

**Not covered:** resolutions of the State Great Khural (≈2,600 in force), Government resolutions
(≈5,800), ministerial orders and other subordinate acts, local acts, international treaties
(available on legalinfo.mn). Acts whose page has no structured text were skipped (see the count of
missing files below).

## Source

**Эрх зүйн мэдээллийн нэгдсэн систем — Legalinfo** (https://legalinfo.mn), Ministry of Justice and
Home Affairs / National Legal Institute. Lists from the site's own list endpoint
(`POST /mn/ajaxList/` with `filtercategorytypeid` 26 = Constitution, 27 = laws, 30 = presidential
decrees, `isactive=1`), texts from `/mn/detail?lawId=<id>`. legalinfo.mn has no `robots.txt`;
requests were made with pauses (at most two at a time).

Licence: under the Law of Mongolia on Copyright and Related Rights, laws and other official
documents of state bodies are not protected by copyright.

## Structure

```
undsen-khuul/<slug>-<lawId>.md               Constitution
khuul/<year>/<slug>-<lawId>.md               laws, by year of adoption
ernhiilogchiin-zarlig/<year>/<slug>-<lawId>.md   presidential decrees
scripts/                                     fetch + convert code
```

`<lawId>` is the legalinfo.mn identifier; `<slug>` a transliteration of the Mongolian title.
Headings: part (АНГИ) / chapter (БҮЛЭГ) / article (зүйл).

## Regenerate

```
python3 -m pip install -r scripts/requirements.txt
python3 scripts/mn_list.py       # -> ../_raw/mn/list.tsv
python3 scripts/mn_fetch.py      # -> ../_raw/mn/html/ (cached)
python3 scripts/mn_convert.py
```
