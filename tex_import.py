import re
import os
from TexSoup import TexSoup

from data import *

def read_source_cese(path):
    print(path)
    with open(path) as infile:
        soup = TexSoup(infile)
        #print(list(soup.enumerate.contents))
    return [str(c).replace("\item","", 1) for c in soup.enumerate.children]

def read_source_archi1(path):
    print(path)
    testi = []
    with open(path) as infile:
        soup = TexSoup(infile)
        for it in soup.find_all('item'):
            if "epsfig" in str(it) or "includegraphics" in str(it):
                testi.append(None)
            else:
                t = str(it)
                t = t.replace("\item","", 1)
                t = re.sub(r"\\begin{minipage}\[.\]{.*?}", "", t)
                t = re.sub(r"\\end{minipage}", "", t)
                testi.append(t)
    return testi

def read_source_archi2(path):
    print(path)
    testi = []
    regex = r"^(?:| |  )(?:\\si{)?\\def\\arc..{\\item \\dom{((?:(?!\\risp).)*)}"
    with open(path) as infile:
        doc = str(infile.read())
    for p in re.finditer(regex, doc, re.DOTALL | re.MULTILINE):
        t = p.groups()[0].strip()
        t = re.sub(r"\\begin{minipage}\[.\]{.*?}", "", t)
        t = re.sub(r"\\end{minipage}", "", t)
        t = re.sub(r"\\begin{tikzpicture}\[scale=(.*?)\]", r"\\begin{tikzpicture}[scale=2]", t)
        testi.append(t)
    return testi

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
        testo = testo.replace(r"\A", r"\a")
        testo = testo.replace(r"\B", r"\b")
        testo = testo.replace(r"\C", r"\c")
        testo = testo.replace(r"\D", r"\d")
        testo = testo.replace(r"\E", r"\e")
        res.append(testo.strip())
    return res


def import_gara(root, gara, dryrun=False):
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
            if not dryrun:
                session.add(gara_obj)

            testi = gara['fun'](os.path.join(path, fn))
            cnt = 0
            for i, t in enumerate(testi):
                if t is None:
                    continue
                cnt += 1
                if not dryrun:
                    prob = Problema(testo=t, gara=gara_obj, numero=(i+1), difficolta=gara['diff'])
                    session.add(prob)

            print(gara_obj, len(testi), cnt)

    session.commit()
    session.close()






gare = [
    {"nome": "Cesenatico", "regex": "ces(\d+).tex", "fun": read_source_cese, "dir": "Cesenatico", "diff": 6},
    {"nome": "Febbraio", "regex": "testo(\d+).tex", "fun": read_source_febb, "dir": "Febbraio", "diff": 3},
    {"nome": "Finale a squadre", "regex": "Fgas(\d+)_ITA.tex", "fun": read_source_gas, "dir": "GaS", "diff": 5},
    {"nome": "Semifinale", "regex": "Agas(\d+)_ITA.tex", "fun": read_source_gas, "dir": "GaS", "diff": 5},
    {"nome": "Archimede", "regex": "(\d+).tex", "fun": read_source_archi1, "dir": "Archimede", "diff": 1},
    {"nome": "Archimede", "regex": "archimede_triennio_(\d+).tex", "fun": read_source_archi2, "dir": "Archimede", "diff": 1}]


for g in gare:
    import_gara("gare", g)
