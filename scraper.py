from data import *

import requests
import re
import json

class Scraper:

    url_base = "https://artofproblemsolving.com/"
    url_api = url_base + "m/community/ajax.php"

    def __init__(self):
        s = requests.session()
        r = s.get(self.url_base)
        x = re.compile('AoPS.session = ({.*})')
        res = x.findall(r.text)
        data = json.loads(res[0])
        self.s = s
        self.sid = data['id']

    def get_items(self,cat_id):
        r = self.s.post(self.url_api, data={"category_id": cat_id, "a": "fetch_category_data", "fetch_all": 1, "aops_session_id": self.sid})
        data = r.json()
        return data['response']['category']['items']

    def get_multiple_items(self, parent_id, cats_id):
        r = self.s.post(self.url_api, data={"sought_category_ids": cats_id, "parent_category_id": parent_id, "a": "fetch_items_categories", "aops_session_id": self.sid})
        data = r.json()
        return data['response']['categories']

    def fetch_more_items(self, cat_id):
        r = self.s.post(self.url_api, data={"category_id": cat_id, "a": "fetch_more_items", "start_num": 0, "fetch_all": 1, "aops_session_id": self.sid})
        data = r.json()
        return data['response']['items']


gare = [
    {"nome": 'AMC 8', "id": 3413, "diff": 1},
    {"nome": 'SDML', "id": 312160, "diff": 1},
    {"nome": 'AIME', "id": 3416, "diff": 3},
    {"nome": 'AMC 10', "id": 3414, "diff": 3},
    {"nome": 'SDMO', "id": 250744, "diff": 3},
    {"nome": 'AMC 12', "id": 3415, "diff": 3},
    {"nome": 'South Africa', "id": 3387, "diff": 5},
    {"nome": 'Spain', "id": 3388, "diff": 5},
    {"nome": 'Mexico', "id": 3344, "diff": 5},
    {"nome": 'India', "id": 3309, "diff": 5},
    {"nome": 'USAJMO', "id": 3420, "diff": 5},
    {"nome": 'TSTST', "id": 3424, "diff": 6},
    {"nome": 'RMM', "id": 3238, "diff": 6},
    {"nome": 'Russia', "id": 3371, "diff": 6},
    {"nome": 'USAMO', "id": 3409, "diff": 6},
    {"nome": 'OMO', "id": 3431, "diff": 6},
    {"nome": 'IMO', "id": 3222, "diff": 6},
    {"nome": 'Balkan', "id": 3225, "diff": 6},
    {"nome": 'RMM', "id": 3238, "diff": 6}
]


# Va capito se conviene usare "multiple" o "more"
def import_gara(gara):
    print("Gara: ", gara['nome'])
    scraper = Scraper()
    session = Session()
    anni = scraper.fetch_more_items(gara['id'])
    for a in anni:
        problemi = scraper.fetch_more_items(a['item_id'])
        gara_obj = Gara(nome=gara['nome'], anno=int(a['item_text'][:4]), aops_id=int(a['item_id']))
        session.add(gara_obj)
        taken = 0
        for p in problemi:
            num = p['item_text']
            if p['item_type'] != "post" or num == "" or p['post_data']['poster_id'] == 0:
                continue
            if p['post_data']['post_number'] != 0:
                url = "https://artofproblemsolving.com/community/c{}h{}".format(p['post_data']['category_id'], p['post_data']['topic_id'])
                body = p['post_data']['post_canonical']

                m = re.findall(r"\[[^\\]+?\]", body)
                if "[list]" in m:
                    continue

                body = body.replace("[asy]\n","[asy]")
                body = body.replace("[asy]","\n\\begin{center}\n\\begin{asy}")
                body = body.replace("[/asy]","\n\\end{asy}\n\\end{center}")

                body = re.sub(r"\[i\](.*?)\[/i\]", r"\\textit{\1}", body)
                body = re.sub(r"\[u\](.*?)\[/u\]", r"\\underline{\1}", body)
                body = re.sub(r"\[b\](.*?)\[/b\]", r"\\textbf{\1}", body)
                body = re.sub(r"unitsize\(.*?\);", r"", body)
                body = re.sub(r"size\(.*?\);", r"", body)

                body = body.replace(r"\qquad", r"\\")
                if body.count("?") == 1:
                    body = body.replace("?", r"?\\")

                prob = Problema(testo=body, aops_id=int(a['item_id']), aops_link=url, gara=gara_obj, numero=num, difficolta=gara['diff'])
                session.add(prob)
                taken += 1
        print("Anno id:", a['item_id'], len(problemi), taken)

    session.commit()

for g in gare:
    import_gara(g)
