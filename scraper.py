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


ids = {'AIME': 3416, 'AMC 10': 3414, 'AMC 12': 3415, 'TSTST': 3424, 'USAJMO': 3420, 'USAMO': 3409}

# Va capito se conviene usare "multiple" o "more"

scraper = Scraper()
anni = scraper.fetch_more_items(ids['AMC 12'])
for a in anni:
    problemi = scraper.fetch_more_items(a['item_id'])
    print(a['item_text'], a['item_id'], len(problemi))
