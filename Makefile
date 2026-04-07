.PHONY: tag

VERSION_ARG := $(word 2,$(MAKECMDGOALS))
VERSION_VALUE := $(if $(VERSION),$(VERSION),$(VERSION_ARG))
PREV_ARG := $(word 3,$(MAKECMDGOALS))
PREV_VALUE := $(if $(PREV),$(PREV),$(PREV_ARG))

tag:
	@if [ -z "$(VERSION_VALUE)" ]; then \
		echo "Usage: make tag VERSION=X.Y.Z [PREV=A.B.C]"; \
		echo "   or: make tag X.Y.Z [PREV=A.B.C]"; \
		echo "   or: make tag X.Y.Z [A.B.C]"; \
		exit 1; \
	fi
	@if [ -n "$(PREV_VALUE)" ]; then \
		./create_tag.sh "$(VERSION_VALUE)" "$(PREV_VALUE)"; \
	else \
		./create_tag.sh "$(VERSION_VALUE)"; \
	fi

%:
	@:
