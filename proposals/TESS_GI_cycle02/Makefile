all: tessgi_gully_cycle2.pdf

%.pdf: %.tex
	pdflatex tessgi_gully_cycle2
	pdflatex tessgi_gully_cycle2
	bibtex tessgi_gully_cycle2
	pdflatex tessgi_gully_cycle2
	pdflatex tessgi_gully_cycle2
	rm -rf *Notes.bib
	rm -rf *.log
	rm -rf *.bbl
	rm -rf *.blg
	rm -rf *.out
	rm -rf *.dvi
	rm -rd *.aux
	rm -rd *.brf
	mv tessgi_gully_cycle2.pdf final
