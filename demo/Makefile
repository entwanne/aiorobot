PRES = pres.ipynb
SRC = $(shell find src -name "*.md" | sort -n)

GEN = $(PRES) $(NOTES)

$(PRES):	$(SRC)
		lucina -o $@ $^ --no-autolaunch

pres:		$(PRES)

clean:
		rm -f $(GEN)

re:		clean $(GEN)

.PHONY:		pres clean re
