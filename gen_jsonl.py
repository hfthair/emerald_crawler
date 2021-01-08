import copy
import bs4

import pandas as pd
from unidecode import unidecode
import shortuuid

soup2 = bs4.BeautifulSoup("<section></section>", features="html.parser")
newtag = soup2.section

def remove_extra_end(r):
    return '\n'.join(i.strip() for i in r.split('\n') if i.strip())

def full_text(soup):
    body_section = soup.findAll('section', {'class': 'Body'})
    if not body_section:
        return ''
    body = body_section[-1]
    c = remove_extra_end(body.text)
    if len(c) > 300:
        return c
    else:
        return ''

def abstract(html):
    for i in (1,2,3,4):
        html = html.replace(f'</h{i}>', f'</h{i}>\n')
    soup = bs4.BeautifulSoup(html)
    abstract_section = soup.find('section', {'id': 'abstract'})
    if not abstract_section:
        print('Can not find abstract section!!!')
        return ''
    return remove_extra_end(abstract_section.text)


def extract_sections(soup):
    body_section = soup.findAll('section', {'class': 'Body'})
    if not body_section:
        return None
    body = body_section[-1]
    
    children = list(body.children)
    if not children:
        return None
    sections = body.findAll('section', recursive=False)
    if not sections:
        return ['__NO_TITLE__'], [remove_extra_end(body.text)]
    
    newtag.clear()
    for i in children[:children.index(sections[0])]:
        newtag.append(copy.copy(i))
    pre = remove_extra_end(newtag.text)
    
    newtag.clear()
    for i in children[children.index(sections[-1])+1:]:
        newtag.append(copy.copy(i))
    post = remove_extra_end(newtag.text)
    
    def extract_section(sec):
        newtag.clear()
        h2 = sec.find('h2')
        for i in sec.children:
            if i != h2:
                newtag.append(copy.copy(i))
        t = ''
        if h2:
            t = remove_extra_end(h2.text)
        c = remove_extra_end(newtag.text)
        return t, c

    extracted_sections = [extract_section(sec) for sec in sections]
    merge_extracted_sections = []
    for t, c in extracted_sections:
        if t:
            merge_extracted_sections.append([t, c])
        else:
            if merge_extracted_sections:
                merge_extracted_sections[-1][1] = '\n'.join((merge_extracted_sections[-1][1], c)).strip()
            else:
                pre = '\n'.join((pre, c)).strip()
    
    titles, content = [], []
    if merge_extracted_sections:
        titles, content = zip(*merge_extracted_sections)
        titles, content = list(titles), list(content)
    
    if pre:
        titles = ['__NO_TITLE__'] + titles
        content = [pre] + content
    if post:
        titles = titles + ['__NO_TITLE__']
        content = content + [post]

    return titles, content # [i.split('\n') for i in content]
    


def extract_abstract(soup):
    abstract_section = soup.find('section', {'id': 'abstract'})
    if not abstract_section:
        print('Can not find abstract section!!!')
        return ''
    sub_sections = abstract_section.findAll('div', {'class': 'intent_sub_item'}, recursive=False)
    def extract_div(sec):
        newtag.clear()
        h3 = sec.find('h3')
        for i in sec.children:
            if i != h3:
                newtag.append(copy.copy(i))
        t = ''
        if h3:
            t = remove_extra_end(h3.text)
            if not t:
                t = '__NO_TITLE__'
        c = remove_extra_end(newtag.text)
        return t, c
    extracted_divs = [extract_div(sec) for sec in sub_sections]
    titles, content = [], []
    if extract_div:
        titles, content = zip(*extracted_divs)
        titles, content = list(titles), list(content)
    
    return titles, content

def extract_ref(soup):
    ref_section = soup.find('section', {'class': 'References'})
    if not ref_section:
        return []
    else:
        ps = ref_section.findAll('p', {'class': 'Reference'})
        return [remove_extra_end(p.text) for p in ps]
    
def extract_appendices(soup):
    appendix_section = soup.find('section', {'class': 'Appendices'})
    if not appendix_section:
        return ''
    else:
        return remove_extra_end(appendix_section.text)

def get_jour(p):
    ps = p.split('/')
    if len(ps) >= 2:
        return ps[1].replace('\n', '')
    else:
        return ''

def extract_helper(row):
    newrow = row[['title', 'keywords']]

    newrow['title'] = unidecode(row['title'])

    if newrow['keywords']:
        newrow['keywords'] = eval(newrow['keywords'])

    html = unidecode(row['full_html'])
    for i in (1,2,3,4):
        html = html.replace(f'</h{i}>', f'</h{i}>\n')
    soup_html = bs4.BeautifulSoup(html, features="html.parser")

    ft = full_text(soup_html)

    r = extract_sections(soup_html)
    t, c = None, None
    if r:
        t, c = r
        c = [i.split('\n') for i in c]
    else:
        print("Error: ", row['path'])
    newrow['section_names'] = t
    newrow['sections'] = c
    
    r = extract_abstract(soup_html)
    t, c = None, None
    if r:
        t, c = r
        c = [i.split('\n') for i in c]
    else:
        print("Ab Error: ", row['path'])
    
    newrow['abstract_sections_names'] = t
    newrow['abstract_sections'] = c
    
    newrow['references'] = extract_ref(soup_html)
    newrow['appendix'] = extract_appendices(soup_html)

    newrow['journal'] = get_jour(row['path'])

    newrow['id'] = shortuuid.uuid()
    if len(ft) <= 300:
        newrow['id'] = ''

    return newrow

if __name__ == '__main__':
    import os
    import json

    f = open('extracted.jsonl', 'w', encoding='utf8')

    for csv_file in os.listdir('./'):
        if csv_file.startswith('out') and csv_file.endswith('.csv'):
            print(csv_file)
            df = pd.read_csv(csv_file, encoding='utf8').fillna('')
            print(df.shape)

            dfr = df.apply(extract_helper, axis=1)

            for i in dfr.to_dict('records'):
                if i['id']:
                    f.write(json.dumps(i) + '\n')
