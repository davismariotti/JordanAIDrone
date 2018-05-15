pdf:
	pdflatex main.tex
	makeindex main.nlo -s nomencl.ist -o main.nls
	pdflatex main.tex
git:
	git add -A
	git commit -m "$(msg)"
	git push

