# Schema versioning

Endpoint catalog entries carry a source schema version and fingerprint. Raw Pydantic models
allow additive fields so the SDK can report them; missing required fields and changed types
fail validation. Canonical schemas are strict and independently versioned.

`SchemaPolicy.REPORT`, `QUARANTINE`, and `ERROR` describe the configured response to drift.
Schema fingerprints are deterministic SHA-256 hashes over recursive JSON type signatures.
