import re
import os
from TexSoup import TexSoup

from data import *

def read_source_cese(path):
    print(path)
    with open(path) as infile:
        soup = TexSoup(infile)
        #print(list(soup.enumerate.contents))
    return [str(c).replace("\item","") for c in soup.enumerate.children]

def read_source_gas(path):
    print(path)
    regex = r"\\begin{gasex}\[\d+\](?:{.*?})+(.*?)\\end{gasex}"
    with open(path) as infile:
        doc = str(infile.read())
    res = []
    for p in re.finditer(regex, doc, re.DOTALL):
        res.append(p.groups()[0].strip())
    return res


def read_source_febb(path):
    print(path)
    regex = r"\\item(.*?)% Risposta"
    with open(path) as infile:
        doc = str(infile.read())
    res = []
    for p in re.finditer(regex, doc, re.DOTALL):
        testo = p.groups()[0].strip()
        idx = testo.find("\A")
        if idx != -1:
            testo = testo[:idx]
        res.append(testo.strip())
    return res


def import_gara(root, gara):
    session = Session()
    path = os.path.join(root, gara['dir'])
    for root, dirs, files in os.walk(path):
        for fn in files:
            anno = re.match(gara['regex'], fn)
            if not anno:
                continue
            anno = int(anno.groups()[0])
            if anno < 50:
                anno += 2000
            elif anno < 100:
                anno += 1900

            gara_obj = Gara(nome=gara['nome'], anno=anno, nazione="ITA")
            session.add(gara_obj)

            testi = gara['fun'](os.path.join(path, fn))
            for i, t in enumerate(testi):
                prob = Problema(testo=t, gara=gara_obj, numero=(i+1))
                session.add(prob)

            print(gara_obj, len(testi))

    session.commit()






gare = {"ITA": [
    {"nome": "Cesenatico", "regex": "ces(\d+).tex", "fun": read_source_cese, "dir": "Cesenatico"},
    {"nome": "Febbraio", "regex": "testo(\d+).tex", "fun": read_source_febb, "dir": "Febbraio"},
    {"nome": "Finale a squadre", "regex": "Fgas(\d+)_ITA.tex", "fun": read_source_gas, "dir": "GaS"},
    {"nome": "Semifinale", "regex": "Agas(\d+)_ITA.tex", "fun": read_source_gas, "dir": "GaS"}]}


#import_gara("gare", gare['ITA'][0])
