genpod_env.sif: genpod_env.def genpod_env.tar
	apptainer build -F $@ $<
genpod_env.tar: Dockerfile pyproject.toml poetry.lock
	podman build --pull --target=runtime -t genpod_env .
	rm -f $@
	podman save -o $@ genpod_env

.PHONY: genpod_env.tar
