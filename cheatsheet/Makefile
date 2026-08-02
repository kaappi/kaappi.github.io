# Builds the Kaappi A4 cheatsheet PDF with XeLaTeX.
#
# Run as `make -C cheatsheet` (or `make` from this directory) — fontspec's
# Path= options resolve relative to the compile cwd, so running xelatex
# from anywhere else will not find the fonts. Body font is reused from the
# sibling checkout ../../kaappi-book/fonts/ (workspace layout assumption,
# same as scripts/generate-book-3d.py).
#
# The version stamped on the sheet comes from kaappi_version in ../mkdocs.yml.

VER := $(shell sed -n 's/^  kaappi_version: //p' ../mkdocs.yml)
OUT := ../docs/assets/kaappi-cheatsheet.pdf

all:
	mkdir -p build
	latexmk -xelatex -output-directory=build -interaction=nonstopmode \
	  -halt-on-error -usepretex='\def\KpVersion{$(VER)}' kaappi-cheatsheet.tex
	cp build/kaappi-cheatsheet.pdf $(OUT)

# Render both pages to build/preview-N.png for visual inspection.
preview: all
	pdftoppm -png -r 150 build/kaappi-cheatsheet.pdf build/preview

clean:
	rm -rf build

.PHONY: all preview clean
