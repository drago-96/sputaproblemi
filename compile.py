from data import *
from instapy_cli import client
import config

import subprocess

res = get_random_problem()
problema = res.testo
titolo = res.get_titolo()

with open("IG_format.tex") as infile:
	template = infile.read()

out_str = template.replace("{{PROBLEMA}}", problema)
out_str = out_str.replace("{{TITOLO}}", titolo)

with open("build/to_compile.tex", "w") as outfile:
	outfile.write(out_str)


res = subprocess.call("cd build && latexmk -pdf to_compile && latexmk -c", shell=True)
print(res)

subprocess.call("cd build && convert -density 300 to_compile.pdf -quality 100 problema.jpg", shell=True)



image = 'build/problema.jpg'

with client(config.IG_username, config.IG_password) as cli:
    cli.upload(image, story=True)
