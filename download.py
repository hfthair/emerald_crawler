import os
import random
import re
import sys
import time

import bs4
import pandas as pd
import requests

from cookies import cookies

base_url = "https://www.emerald.com"

with open('./ua.txt', 'r', encoding='utf8') as f:
    ualist = [i.strip() for i in f]


def randua():
    return {'headers': random.choice(ualist)}


def download_full_via_pitt(url):
    url = url.replace(base_url, "https://www-emerald-com.pitt.idm.oclc.org")
    r = None
    for delay in (1, 5, 10, 15):
        try:
            r = requests.get(url, headers=randua(), cookies=cookies)
            break
        except:
            print(f" !! download full text via pitt fail, wait for {delay} minutes")
            time.sleep(delay*60)
    if 'Authentication Request' in r.text:
        raise PermissionError("need login!!")
    if 'To read the full version of this content please select one of the options below' in r.text:
        raise FileNotFoundError("Not downloadable via Pitt")
    return r.text


def get_retry(url):
    for delay in (1, 2, 3, 5):
        try:
            r = requests.get(url, headers=randua())
            break
        except:
            print(f" !! general request fail, wait for {delay} minutes")
            time.sleep(delay*60)
    return r


def main(save_dir, pitt_auth=False):
    r = get_retry("https://www.emerald.com/insight/sitemap/publications")
    found = re.findall(r'<a href="/insight/publication.*</a>', r.text)
    journal_url_list = []
    for i in found:
        url = i.replace('<a href="', '')
        url = base_url + url[:35]
        journal_url_list.append(url)

    for nth_jour, j_page_url in enumerate(journal_url_list):
        if os.path.isfile(os.path.join(save_dir, f'out{nth_jour+1}.csv')):
            # resume from last point...
            print(f"skip {nth_jour} ...")
            continue
        fname = os.path.join(save_dir, f'out{nth_jour}.csv')
        if os.path.isfile(fname) and os.path.getsize(fname) > 100:
            df = pd.read_csv(fname, encoding='utf8')
        else:
            df = pd.DataFrame()

        jpage = get_retry(j_page_url)

        jpage_entries = re.findall(
            r'<a href="/insight/publication.*class="intent_tocIssueLink".*</a>', jpage.text)
        try:
            for entry in jpage_entries:
                entry_url = entry.replace('<a href="', '')
                entry_url = base_url + entry_url[:entry_url.index('"')]

                article_list_page = get_retry(entry_url)

                art_urls = re.findall(
                    r'href="/insight/content.*full/html', article_list_page.text)
                art_urls = [base_url + i[6:] for i in art_urls]

                for art_url in art_urls:
                    if df.shape[0] > 0 and art_url in set(df.url.to_list()): # df[df.url == purl].shape[0] > 0:
                        print(" # already done.")
                        continue
                    time.sleep(random.random() * 1.18)

                    art_page_public = get_retry(art_url)
                    soup = bs4.BeautifulSoup(art_page_public.text, 'html.parser')

                    row = {'url': art_url}

                    abstract = soup.find('div', {'class': 'Abstract__block'})
                    if not abstract:
                        continue
                    row['abstract'] = abstract.text.strip()

                    title = soup.find('h1', {'class': 'intent_article_title'})
                    row['title'] = ''
                    if title:
                        row['title'] = title.text.strip()

                    authors = soup.find(
                        'section', {'id': 'intent_contributors'})
                    row['authors'] = ''
                    if authors:
                        row['authors'] = authors.text.strip()

                    keyul = soup.find(
                        'ul', {'aria-labelledby': 'page__keywords-label'})
                    row['keywords'] = ''
                    if keyul:
                        row['keywords'] = ([i.text.strip()
                                            for i in keyul.findAll('li')])

                    breadcrumbs = soup.find('breadcrumbs')
                    row['path'] = ''
                    if breadcrumbs:
                        row['path'] = '/'.join(i[0]
                                               for i in eval(breadcrumbs.attrs['crumbs']) if i)

                    print(f" # trying ({nth_jour}) {row['path']}...")

                    if 'To read the full version of this content please select one of the options below' in art_page_public.text:
                        if pitt_auth:
                            full = download_full_via_pitt(art_url)
                            row['full_html'] = full
                        else:
                            raise FileNotFoundError('Journal is not publicly accessable.')
                    else:
                        row['full_html'] = art_page_public.text
                    row['short_html'] = art_page_public.text

                    df = df.append(row, ignore_index=True)

                    print(f"  | done ({df.shape[0]})")

                    if df.shape[0] % 100 == 0:
                        df.to_csv(fname, encoding='utf8', index=False)

        except FileNotFoundError as e:
            print("  ", e)
        df.to_csv(fname, encoding='utf8', index=False)
    return nth_jour


if __name__ == '__main__':
    import fire
    # --save_dir dir --pitt_auth True/False(need to set cookies.py if True)
    fire.Fire(main)
