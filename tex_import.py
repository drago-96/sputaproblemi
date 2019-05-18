import re

def read_source(path):
    with open(path) as infile:
        content = infile.read().replace('\n',' ')
    x = re.findall(r"\\begin{enumerate}(.*?)\\end{enumerate}", str(content), re.DOTALL)
    testi = x[0].split("\\item")
    return testi
