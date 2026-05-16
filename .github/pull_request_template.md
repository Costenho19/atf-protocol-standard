## Summary

<!-- One sentence describing what this PR changes or adds -->

## Related invariant(s)

<!-- Which ATF invariant(s) does this affect? e.g. ATF-INV-001 -->

- [ ] ATF-INV-___
- [ ] RGC-INV-___

## Type of change

- [ ] RFC amendment (breaking — requires new version)
- [ ] ADR addition
- [ ] Conformance test
- [ ] Language port (Rust / TypeScript / other)
- [ ] Integration (FastAPI / LangChain / other)
- [ ] Bug fix in verifier or reference implementation
- [ ] Documentation only

## Checklist

- [ ] Every new test references its invariant (`# ATF-INV-XXX`)
- [ ] Hash parity confirmed: Python + modified port produce byte-identical SHA-256
- [ ] No new external dependencies added (verifier must remain zero-dep)
- [ ] `CHANGELOG.md` updated under [Unreleased]
- [ ] Example receipts valid against `schemas/`
- [ ] CI green (conformance-tests + rust-skeleton + typescript-port)

## Testing evidence

```
# paste test output here
```
