#!/usr/bin/env python3
"""Convert legalinfo.mn detail pages (_raw/mn/html/<lawId>.html.gz) to Markdown.

legalinfo.mn renders each element of an act as
  <div class="w-100 pull-left responsive_mobile ..." data-parentid=".." id=".." data-pp="N" style="..">
with data-pp = 2 for structural headings (part / chapter titles), 1 for article headings,
0 for body text (including the consolidated-text notes "/Энэ ... хуулиар нэмсэн/").
"""
import gzip, os, re, sys, html

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
RAW = os.path.abspath(os.path.join(REPO, '..', '_raw', 'mn'))
RETRIEVED = '2026-10-12'

ITEM = re.compile(r'<div class="w-100 pull-left responsive_mobile[^"]*" data-parentid="(\d*)" id="(\d+)" '
                  r'data-pp="(\d+)"\s*style="([^"]*)">(.*?)</div>', re.S)
DIRS = {'constitution': 'undsen-khuul', 'law': 'khuul', 'presidential-decree': 'ernhiilogchiin-zarlig'}
TYPES = {'constitution': 'constitution', 'law': 'act', 'presidential-decree': 'decree'}

KINDS = ['part', 'subpart', 'chapter', 'subchapter', 'article']
PAT = {
    'part': re.compile(r'.*\bАНГИ\b', re.I),
    'subpart': re.compile(r'.*\bДЭД\s+АНГИ\b', re.I),
    'chapter': re.compile(r'.*\bБҮЛЭГ\b', re.I),
    'subchapter': re.compile(r'.*\bДЭД\s+БҮЛЭГ\b', re.I),
}

TR = dict(zip('абвгдеёжзийклмнопрстуфхцчшщъыьэюяөү',
              ['a', 'b', 'v', 'g', 'd', 'e', 'yo', 'j', 'z', 'i', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't',
               'u', 'f', 'kh', 'ts', 'ch', 'sh', 'sh', '', 'y', '', 'e', 'yu', 'ya', 'o', 'u']))


def slug(s, n=60):
    s = ''.join(TR.get(c, c) for c in s.lower())
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s[:n].rstrip('-')


def text(body):
    body = re.sub(r'<span class="icon-s".*?</span>', '', body, flags=re.S)
    body = re.sub(r'<br\s*/?>', '\n', body)
    body = re.sub(r'</p>\s*<p[^>]*>', '\n', body)
    t = html.unescape(re.sub(r'<[^>]+>', '', body)).replace('\xa0', ' ')
    t = re.sub(r'[ \t]+', ' ', t)
    return '\n'.join(l.strip() for l in t.split('\n') if l.strip())


def md_escape(t):
    t = re.sub(r'^(#+)', r'\\\1', t)
    t = re.sub(r'^(\d+)([.)]) ', r'\1\\\2 ', t)
    t = re.sub(r'^([-+*>]) ', r'\\\1 ', t)
    return t


def kind2(t):
    u = t.upper()
    if PAT['subchapter'].match(u):
        return 'subchapter'
    if PAT['subpart'].match(u):
        return 'subpart'
    if PAT['chapter'].match(u):
        return 'chapter'
    if PAT['part'].match(u):
        return 'part'
    return None


def convert(s):
    blocks = []
    for parent, iid, pp, style, body in ITEM.findall(s):
        t = text(body)
        if not t:
            continue
        if pp == '2':
            k = kind2(t)
            if k is None and blocks and blocks[-1][0] == 'h' and blocks[-1][1] != 'article' and not blocks[-1][3]:
                # title line following "НЭГДҮГЭЭР БҮЛЭГ": merge into that heading
                blocks[-1] = ('h', blocks[-1][1], blocks[-1][2] + ' ' + t.replace('\n', ' '), True)
                continue
            blocks.append(('h', k or 'chapter', t.replace('\n', ' '), k is None))
        elif pp == '1':
            blocks.append(('h', 'article', t.replace('\n', ' '), True))
        else:
            for ln in t.split('\n'):
                blocks.append(('p', ln))
    return blocks


def render(blocks):
    present = [k for k in KINDS if any(b[0] == 'h' and b[1] == k for b in blocks)]
    level = {k: min(2 + i, 6) for i, k in enumerate(present)}
    out = []
    for b in blocks:
        if b[0] == 'h':
            out.append('#' * level[b[1]] + ' ' + b[2])
        else:
            out.append(md_escape(b[1]))
    return '\n\n'.join(out) + '\n'


def yq(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def main():
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(RAW, 'list.tsv'))]
    stats, missing = {}, []
    for cat, lid, title, gazette, enacted, enforced in rows:
        fn = os.path.join(RAW, 'html', lid + '.html.gz')
        if not os.path.exists(fn):
            missing.append(lid)
            continue
        s = gzip.open(fn, 'rt', encoding='utf-8').read()
        blocks = convert(s)
        if not blocks:
            missing.append(lid)
            continue
        date = enacted if re.match(r'\d{4}-\d{2}-\d{2}$', enacted) else None
        year = date[:4] if date else 'unknown'
        name = slug(title) + '-' + lid
        if cat == 'constitution':
            rel = os.path.join(DIRS[cat], name + '.md')
        else:
            rel = os.path.join(DIRS[cat], year, name + '.md')
        fm = ['---', f'title: {yq(title)}', f'identifier: "legalinfo:{lid}"', f'type: {TYPES[cat]}',
              'jurisdiction: mn', 'language: mn']
        if date:
            fm.append(f'date: {date}')
        if re.match(r'\d{4}-\d{2}-\d{2}$', enforced):
            fm.append(f'entry_into_force: {enforced}')
        fm += ['status: in_force']
        if gazette:
            fm.append(f'publication: {yq(gazette)}')
        fm += [f'source: "https://legalinfo.mn/mn/detail?lawId={lid}"', f'retrieved: {RETRIEVED}', '---', '']
        md = '\n'.join(fm) + f'\n# {title}\n\n' + render(blocks)
        out = os.path.join(REPO, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as f:
            f.write(md)
        stats[cat] = stats.get(cat, 0) + 1
    print(stats, 'missing', len(missing))
    with open(os.path.join(RAW, 'missing.txt'), 'w') as f:
        f.write('\n'.join(missing))


if __name__ == '__main__':
    main()
