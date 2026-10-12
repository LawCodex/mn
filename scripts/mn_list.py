#!/usr/bin/env python3
"""List acts in force on legalinfo.mn (Unified Legal Information System of Mongolia) for the
Constitution (category 26), laws (27) and presidential decrees (30), using the site's own
list endpoint (POST /mn/ajaxList/). Output: _raw/mn/list.tsv
(category, lawId, title, gazette, enacted, enforced)"""
import os, re, sys, time, json, html, requests

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_raw', 'mn')
UA = 'LawCodex/1.0 (+https://github.com/LawCodex)'
CATS = {'26': 'constitution', '27': 'law', '30': 'presidential-decree'}
ROW = re.compile(r'detail\?lawId=(\d+)" class="act-name[^>]*>(.*?)</a></div>\s*(?:<span[^>]*>(.*?)</span>)?'
                 r'.*?data-block="enacteddate">\s*<span>(.*?)</span>.*?data-block="enforcementdate">\s*<span>(.*?)</span>', re.S)


def t(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x or ''))).strip()


def main():
    os.makedirs(RAW, exist_ok=True)
    s = requests.Session(); s.headers.update({'User-Agent': UA, 'X-Requested-With': 'XMLHttpRequest'})
    out = open(os.path.join(RAW, 'list.tsv'), 'w')
    for cat, name in CATS.items():
        page, seen, total = 1, set(), None
        while True:
            for a in range(5):
                try:
                    r = s.post('https://legalinfo.mn/mn/ajaxList/', timeout=120, data={
                        'filtercategorytypeid': cat, 'isactive': '1', 'page': str(page), 'code': '1'})
                    h = r.json()['Html']; break
                except Exception as e:
                    print('ERR', e, file=sys.stderr); time.sleep(10 * (a + 1))
            else:
                raise SystemExit('failed')
            if total is None:
                total = int((re.findall(r'Нийт (\d+)', h) or ['0'])[0])
            rows = ROW.findall(h)
            new = 0
            for lid, title, gaz, en, ef in rows:
                if lid in seen: continue
                seen.add(lid); new += 1
                out.write('\t'.join([name, lid, t(title), t(gaz), t(en)[:10], t(ef)[:10]]) + '\n')
            print(name, page, len(seen), '/', total, flush=True)
            if new == 0 or len(seen) >= total:
                break
            page += 1
            time.sleep(1)
        out.flush()


if __name__ == '__main__':
    main()
