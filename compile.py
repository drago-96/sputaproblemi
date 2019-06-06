from data import *
import config

from instapy_cli import client
import subprocess
import argparse

def write_problem(problema, titolo):

    with open("IG_format.tex") as infile:
    	template = infile.read()

    out_str = template.replace("{{PROBLEMA}}", problema)
    out_str = out_str.replace("{{TITOLO}}", titolo)

    with open("build/to_compile.tex", "w") as outfile:
    	outfile.write(out_str)

def do_compile(path):
    f = open("compile_log","wb")
    dn = open("/dev/null","w")
    res = subprocess.call("cd build && latexmk -interaction=nonstopmode -pdf to_compile", shell=True, stdout=f, stderr=f)
    subprocess.call("cd build && latexmk -c && rm to_compile-*", shell=True, stderr=dn, stdout=dn)
    if res:
        return res
    subprocess.call("cd build && convert -density 300 to_compile.pdf -quality 100 {}".format(path), shell=True)


def upload_IG(path):
    image = 'build/'+path
    with client(config.IG_username, config.IG_password) as cli:
        cli.upload(image, story=True)


if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Compila i problemi da sputare')
    parser.add_argument('--upload', action='store_true')
    parser.add_argument('--nowrite', action='store_true')
    args = parser.parse_args()

    session = Session()

    if not args.nowrite:
        res = get_random_problem(session)
        problema = res.testo
        titolo = res.get_titolo()

        write_problem(problema, titolo)
    res = do_compile()

    if res:
        print(res)
        exit(1)


    if args.upload:
        upload_IG()

    session.close()
