download-data: data/skbl.json

data/skbl.json: data/skbl.raw.json
	jq --compact-output '.entries' $< > $@

data/skbl.raw.json:
	wget https://svn.spraakdata.gu.se/sb-arkiv/pub/skbl/skbl.json -O $@

install-python: .venv
	.venv/bin/pip install json-streams

install-memory-profiler: .venv
	.venv/bin/pip install memory-profiler

.venv:
	@test -d $@ || python -m venv $@
