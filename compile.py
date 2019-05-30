from data import *
import config

from instapy_cli import client
import subprocess
import argparse

image = 'build/problema.jpg'

def write_problem():
    res = get_random_problem()
    problema = res.testo
    titolo = res.get_titolo()

    with open("IG_format.tex") as infile:
    	template = infile.read()

    out_str = template.replace("{{PROBLEMA}}", problema)
    out_str = out_str.replace("{{TITOLO}}", titolo)

    with open("build/to_compile.tex", "w") as outfile:
    	outfile.write(out_str)

def do_compile():
    res = subprocess.call("cd build && latexmk -interaction=nonstopmode -pdf to_compile", shell=True)
    if res:
        return res
    subprocess.call("cd build && latexmk -c && rm to_compile-*", shell=True)
    subprocess.call("cd build && convert -density 300 to_compile.pdf -quality 100 problema.jpg", shell=True)


parser = argparse.ArgumentParser(description='Compila i problemi da sputare')
parser.add_argument('--upload', action='store_true')
args = parser.parse_args()


write_problem()
res = do_compile()

if res:
    print(res)
    exit(1)


if args.upload:
    with client(config.IG_username, config.IG_password) as cli:
        cli.upload(image, story=True)
