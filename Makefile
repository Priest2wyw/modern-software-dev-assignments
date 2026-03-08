SHELL := /bin/bash

PY ?= python
HOST ?= 127.0.0.1
PORT ?= 8000
OLLAMA_HOST ?= http://127.0.0.1:8112
NO_PROXY ?= 127.0.0.1,localhost

export OLLAMA_HOST
export NO_PROXY
export no_proxy := $(NO_PROXY)

.DEFAULT_GOAL := help

.PHONY: help \
	w1-k-shot w1-k-fewshot w1-chain w1-self-consistency w1-rag w1-tool-calling w1-reflexion \
	w2-run w2-test \
	w4-run w4-test w4-format w4-lint w4-seed \
	w5-run w5-test w5-format w5-lint w5-seed \
	w6-run w6-test w6-format w6-lint w6-seed \
	w7-run w7-test w7-format w7-lint w7-seed

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Week 1 scripts:"
	@echo "  w1-k-shot            Run week1/k_shot_prompting.py"
	@echo "  w1-k-fewshot         Alias of w1-k-shot"
	@echo "  w1-chain             Run week1/chain_of_thought.py"
	@echo "  w1-self-consistency  Run week1/self_consistency_prompting.py"
	@echo "  w1-rag               Run week1/rag.py"
	@echo "  w1-tool-calling      Run week1/tool_calling.py"
	@echo "  w1-reflexion         Run week1/reflexion.py"
	@echo ""
	@echo "Week 2:"
	@echo "  w2-run               Run FastAPI app at $(HOST):$(PORT)"
	@echo "  w2-test              Run week2 tests"
	@echo ""
	@echo "Weeks 4-7:"
	@echo "  wX-run/test/format/lint/seed (X=4,5,6,7)"
	@echo ""
	@echo "Env overrides:"
	@echo "  PY=$(PY)"
	@echo "  OLLAMA_HOST=$(OLLAMA_HOST)"
	@echo "  NO_PROXY=$(NO_PROXY)"
	@echo "  Example: make PY=python3 w1-k-shot"
	@echo "  Example: OLLAMA_HOST=http://127.0.0.1:11434 make w1-k-shot"

w1-k-shot:
	cd week1 && $(PY) k_shot_prompting.py

w1-k-fewshot: w1-k-shot

w1-chain:
	cd week1 && $(PY) chain_of_thought.py

w1-self-consistency:
	cd week1 && $(PY) self_consistency_prompting.py

w1-rag:
	cd week1 && $(PY) rag.py

w1-tool-calling:
	cd week1 && $(PY) tool_calling.py

w1-reflexion:
	cd week1 && $(PY) reflexion.py

w2-run:
	$(PY) -m uvicorn week2.app.main:app --reload --host $(HOST) --port $(PORT)

w2-test:
	$(PY) -m pytest -q week2/tests

w4-run:
	$(MAKE) -C week4 run

w4-test:
	$(MAKE) -C week4 test

w4-format:
	$(MAKE) -C week4 format

w4-lint:
	$(MAKE) -C week4 lint

w4-seed:
	$(MAKE) -C week4 seed

w5-run:
	$(MAKE) -C week5 run

w5-test:
	$(MAKE) -C week5 test

w5-format:
	$(MAKE) -C week5 format

w5-lint:
	$(MAKE) -C week5 lint

w5-seed:
	$(MAKE) -C week5 seed

w6-run:
	$(MAKE) -C week6 run

w6-test:
	$(MAKE) -C week6 test

w6-format:
	$(MAKE) -C week6 format

w6-lint:
	$(MAKE) -C week6 lint

w6-seed:
	$(MAKE) -C week6 seed

w7-run:
	$(MAKE) -C week7 run

w7-test:
	$(MAKE) -C week7 test

w7-format:
	$(MAKE) -C week7 format

w7-lint:
	$(MAKE) -C week7 lint

w7-seed:
	$(MAKE) -C week7 seed
