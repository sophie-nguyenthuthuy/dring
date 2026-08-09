# ◎ dring — a decoder ring for opaque strings

**[Try the live demo →](https://sophie-nguyenthuthuy.github.io/dring/)**
Paste any opaque string and find out what it is: JWT, ULID, UUID, base64
protobuf, a cron expression, magic bytes, a Kubernetes pod name, a stack trace
from a language you don't write. Fully offline, stdlib-only, single command —
also a [static web page](docs/index.html) with the same detectors in vanilla JS.

```console
$ dring eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
1. jwt           98%  JWT signed with HS256, sub=1234567890
     alg: HS256
     typ: JWT
     claims: {"sub": "1234567890", "name": "John Doe", "iat": 1516239022}
     iat_human: 2018-01-18T01:30:22Z

$ dring nginx-7d9fd8c5b7-2xkq9
1. k8s           75%  Kubernetes pod: Deployment 'nginx' -> ReplicaSet 'nginx-7d9fd8c5b7' -> pod '2xkq9'
     deployment: nginx
     pod_template_hash: 7d9fd8c5b7
     pod_suffix: 2xkq9

$ dring "*/5 * * * *"
1. cron          85%  cron expression: every 5 minutes
     minute: */5 (every 5)
     ...
```

No answer is forced: dring returns **ranked candidates**, because a 32-char hex
string really might be an MD5 *or* base64 — you get both, ordered by confidence.

## Install / run

Stdlib only — nothing to install:

```bash
python3 -m dring <string>        # from a clone
echo "01ARZ3NDEKTSV4RRFFQ69G5FAV" | dring   # stdin works too
dring --json <string>            # machine-readable
dring --list                     # what's registered
```

Or `pip install .` to get the `dring` entry point. The web page is
`docs/index.html` — a single self-contained file, GitHub-Pages-ready, nothing
leaves the browser.

## Detectors

| detector    | identifies                              | extracts |
|-------------|------------------------------------------|----------|
| `jwt`       | JSON Web Tokens                          | alg, claims, humanized iat/exp/nbf |
| `ulid`      | ULIDs (Crockford base32)                 | 48-bit ms timestamp |
| `uuid`      | UUIDs v1–v8                              | version, v1/v7 timestamps |
| `unixtime`  | epoch timestamps (s/ms/µs/ns)            | UTC time, unit |
| `snowflake` | Discord/Twitter snowflake IDs            | timestamp, worker, sequence |
| `objectid`  | MongoDB ObjectIds                        | creation time |
| `hexdigest` | MD5/SHA-1/SHA-256/SHA-512 digests        | algorithm by length |
| `base64`    | base64/base64url                         | payload class: JSON, text, gzip, PNG, protobuf… |
| `protobuf`  | protobuf wire format (hex dumps)         | field numbers, wire types, values |
| `cron`      | cron expressions (5/6 fields, @aliases)  | per-field description |
| `magicbytes`| file magic (PNG, ELF, ZIP, PEM, 20+)     | file type |
| `k8s`       | Kubernetes pod names                     | deployment, pod-template-hash, suffix |
| `stacktrace`| Python/Java/JS/Go/Rust stack traces      | language, error line, frame count |
| `semver`    | semantic versions                        | major/minor/patch/prerelease |

## Contributing: one detector = one file + one fixture

That's the whole contributor unit. To add, say, KSUID:

1. **`dring/detectors/ksuid.py`** — a module with `NAME = "ksuid"` and
   `detect(text) -> dict | list[dict] | None` returning
   `{"type": NAME, "confidence": 0.0–1.0, "summary": str, "details": dict}`.
   Regex to rule it out fast, parser to extract what's inside.
2. **`tests/fixtures/ksuid/basic.json`** — a real sample:
   ```json
   {"input": "…", "expect_type": "ksuid", "summary_contains": ["KSUID"]}
   ```
3. `python3 -m unittest discover -s tests` — the fixture walker auto-discovers
   both, and *fails* if a detector has no fixture (or a fixture no detector).
4. Optionally port it to `docs/index.html` (one `reg("ksuid", fn)` block).

Rules: stdlib only, fully offline, never raise on weird input, return `None`
rather than guessing wildly — and prefer *ranked honesty* (0.5 confidence) over
false certainty.

**Wanted:** KSUID, nanoid, cuid2, IPv6, MAC address, AWS ARN, S3 presigned URL,
git object headers, ASN.1/DER, msgpack, CBOR, base58 (bitcoin/IPFS CID),
hashids, punycode, JWE, SSH public keys, TOTP otpauth:// URIs, EXIF dates.

## Design rules

- **Offline, always.** No network, no lookups, nothing leaves your machine.
- **Ranked candidates, not verdicts.** Ambiguity is surfaced, not hidden.
- **Detectors are independent.** One broken detector can't take down the ring.
- **Zero dependencies.** `python3 -m dring` works on a bare 3.10+.

## License

MIT
