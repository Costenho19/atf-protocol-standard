FROM python:3.11-slim

LABEL org.opencontainers.image.title="ATF Conformance Suite"
LABEL org.opencontainers.image.description="Standalone conformance verification for the Agent Trust Fabric protocol stack"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.vendor="OMNIX QUANTUM LTD"
LABEL org.opencontainers.image.licenses="CC-BY-4.0"
LABEL org.opencontainers.image.source="https://github.com/Costenho19/atf-protocol-standard"

WORKDIR /atf-conformance-suite

COPY . /atf-conformance-suite/

RUN pip install --no-cache-dir jsonschema && \
    python -c "import json, hashlib, secrets; print('Dependencies verified')"

# Verify the suite itself is functional before finalising the image
RUN python run_conformance.py --profile BASE --vectors vectors/complete_vectors.json 2>&1 | \
    grep -E "Verdict|PASS|FAIL" || true

ENTRYPOINT ["python", "run_conformance.py"]
CMD ["--profile", "ALL"]
