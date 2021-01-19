all: tessgi_gully_cycle4.pdf

%.pdf: %.tex
	tectonic tessgi_gully_cycle4.tex
	#latexdiff final/old.tex new.tex > diff.tex
	#tectonic diff.tex
	#rm diff.tex
	rm -rf *Notes.bib
	rm -rf *.log
	rm -rf *.bbl
	rm -rf *.blg
	rm -rf *.out
	rm -rf *.dvi
	#rm -rd *.aux
	mv tessgi_gully_cycle4.pdf final
