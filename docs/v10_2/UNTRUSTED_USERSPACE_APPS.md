# TS-Reasoner v10.2: Untrusted Userspace Apps

v10.2 adds protocol-sandboxed subprocess proposer apps. Apps receive sanitized
JSON on stdin and return JSON candidates on stdout using
`ts_os_userspace_app_v1`.

Run:

```bash
python3 -m ts_reasoner.runtime_os_cli run-userspace --app '<cmd>' --session @data/v10_2/userspace_session.json
```

Malformed JSON, timeouts, unsupported claims, and budget changes are verifier
gated and receipt-backed.
