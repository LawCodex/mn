#!/usr/bin/env python3
"""Download legalinfo.mn detail pages for the acts in _raw/mn/list.tsv into
_raw/mn/html/<lawId>.html.gz (re-runs skip cached files)."""
import gzip, os, sys, time, requests

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_raw', 'mn')
UA = 'LawCodex/1.0 (+https://github.com/LawCodex)'

def main():
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(RAW, 'list.tsv'))]
    os.makedirs(os.path.join(RAW, 'html'), exist_ok=True)
    s = requests.Session(); s.headers['User-Agent'] = UA
    for n, r in enumerate(rows):
        lid = r[1]
        out = os.path.join(RAW, 'html', lid + '.html.gz')
        if os.path.exists(out):
            continue
        url = f'https://legalinfo.mn/mn/detail?lawId={lid}&showType=1'
        for a in range(5):
            try:
                resp = s.get(url, timeout=180)
                if resp.status_code == 200 and 'data-pp=' in resp.text:
                    with gzip.open(out + '.tmp', 'wt', encoding='utf-8') as f:
                        f.write(resp.text)
                    os.replace(out + '.tmp', out)
                    break
                print('HTTP', resp.status_code, url, len(resp.text), file=sys.stderr, flush=True)
                if resp.status_code == 200:
                    break   # page without structured text (e.g. PDF-only act)
            except Exception as e:
                print('ERR', url, e, file=sys.stderr, flush=True)
            time.sleep(10 * (a + 1))
        time.sleep(1.5)
        if n % 100 == 0:
            print('progress', n, len(rows), flush=True)
    print('done')

if __name__ == '__main__':
    main()
