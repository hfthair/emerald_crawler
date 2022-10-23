import copy
import bs4
import os
import json
import pickle

import pandas as pd
from unidecode import unidecode
import shortuuid


soup2 = bs4.BeautifulSoup("<section></section>", features="html.parser")
newtag = soup2.section


journal_to_category_dict = pickle.load(open('journal_to_category.pkl', 'rb'))
fix_missing = {
    "Perceptions of robotics emulation of human ethics in educational settings: a content analysis": "Journal of Research in Innovative Teaching & Learning",
    "Data competence maturity: developing data-driven decision making": "Journal of Research in Innovative Teaching & Learning",
    "Empowerment through a teacher leadership academy": "Journal of Research in Innovative Teaching & Learning",
    "Compassionate education from preschool to graduate school: Bringing a culture of compassion into the classroom": "Journal of Research in Innovative Teaching & Learning",
    "Small data as a conversation starter for learning analytics: Exam results dashboard for first-year students in higher education": "Journal of Research in Innovative Teaching & Learning",
    "Evaluating emotion visualizations using AffectVis, an affect-aware dashboard for students": "Journal of Research in Innovative Teaching & Learning",
    "Entrepreneurship students distilled their learning experience through reflective learning log": "Journal of Research in Innovative Teaching & Learning",
    "Learning analytics to improve writing skills for young children - an holistic approach": "Journal of Research in Innovative Teaching & Learning",
    "On predicting academic performance with process mining in learning analytics": "Journal of Research in Innovative Teaching & Learning",
    "Examining knowledge gap and Psychic Distance Paradox interdependence: An exploratory inquiry": "European Business Review",
    "The rise and fall of channel management": "IMP Journal",
    "The problem and awareness of liquor abuse in South Africa": "International Journal of Social Economics"
}


def has_structured_abstract(j):
    ks = j['abstract_sections_names']
    # if not [i for i in ks if i.startswith('Purpose')] or \
    #         not [i for i in ks if i.startswith('Design')] or \
    #         not [i for i in ks if i.startswith('Findings')] or\
    #         not [i for i in ks if i.startswith('Originality')]:
    #     return False
    if 'Purpose' not in ks or \
        'Design/methodology/approach' not in ks or \
        'Findings' not in ks or \
        'Originality/value' not in ks:
        return False
    ls = [len(i) for i in ks]
    if max(ls) > 100 or min(ls) < 3:
        return False
    return True

def is_english_journal(j):
    if 'Journal of Derivatives and Quantitative Studies: 선물연구' == j['journal'] or\
        'Spanish Journal' in j['journal']:
        return False
    else:
        return True

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
    newrow = row[['title', 'keywords', 'url']]

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


def fix_jour(j):
    if not j['journal'] and j['title'] in fix_missing:
        j['journal'] = fix_missing[j['title']]
    return j


def add_cat(j):
    j['category'] = journal_to_category_dict[j['journal']]
    return j


def abstract_length(j):
    abstract_sections_names = j['abstract_sections_names']
    abstract_sections = j['abstract_sections']

    section_length = {}
    for title, sec in zip(abstract_sections_names, abstract_sections):
        if title not in ('Purpose', 'Design/methodology/approach', 'Findings', 'Originality/value'):
            continue
        text = ' '.join(par for par in sec)
        section_length[title] = len(text.split())

    return sum([section_length[i] for i in ('Purpose', 'Design/methodology/approach', 'Findings', 'Originality/value')])


def main(csv_dir, jsonl_filename):
    f = open(jsonl_filename, 'w', encoding='utf8')

    total_row = 0
    for csv_file in os.listdir(csv_dir):
        if csv_file.endswith('.csv'):
            print(f"read csv: {csv_file}")
            try:
                df = pd.read_csv(os.path.join(csv_dir, csv_file), encoding='utf8').fillna('')
                print(f"shape: {df.shape}")

                dfr = df.apply(extract_helper, axis=1)

                csv_row = 0
                for j in dfr.to_dict('records'):
                    if j['id'] and is_english_journal(j) and has_structured_abstract(j):
                        ab_len = abstract_length(j)
                        if ab_len < 50 or ab_len > 500:
                            continue
                        j = fix_jour(j)
                        j = add_cat(j)
                        f.write(json.dumps(j) + '\n')

                        csv_row += 1
                        total_row += 1
                print(f"write json {csv_row} rows.")
            except:
                print(f"failed, file size {os.path.getsize(os.path.join(csv_dir, csv_file))}")
    print(f"done. total {total_row} rows")


if __name__ == '__main__':
    import fire
    # --csv_dir dirname --jsonl_filename filename
    fire.Fire(main)
