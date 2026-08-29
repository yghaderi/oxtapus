# Security policy

Report vulnerabilities privately through the repository security advisory workflow. Do not
open a public issue containing credentials, session identifiers, proxy URLs, unpublished
endpoints, or sensitive payloads.

Oxtapus strips sensitive headers before Bronze persistence and disallows arbitrary high-level
hosts. Applications remain responsible for secure proxy configuration, filesystem permissions,
dependency updates, data-access authorization, and secret management. Supported security fixes
target the current 1.x release.
