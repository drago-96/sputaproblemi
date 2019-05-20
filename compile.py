with open("IG_format.tex") as infile:
	template = infile.read()

problema = r"Dimostrare che $e^{2\pi i}+1=0$"
titolo = "Cusumano 2018, 5."

out_str = template.replace("{{PROBLEMA}}", problema)
out_str = out_str.replace("{{TITOLO}}", titolo)

with open("build/to_compile.tex", "w") as outfile:
	outfile.write(out_str)

import subprocess
res = subprocess.call("cd build && latexmk -pdf to_compile && latexmk -c", shell=True)
print(res)
