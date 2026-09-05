# Permission collection method

The nine URLs in `permission_request_manifest.csv` were registered before their corresponding HTTP GETs. Requests used the truthful user agent recorded in that manifest, no authentication, no cookies, and no personal data. Requests to the same host were spaced at least seven seconds apart. Responses were cached under `raw/permission/`, with UTC, effective URL, HTTP status, content type, byte count, and SHA-256 recorded in `permission_request_results.csv`. Host collection stopped on HTTP 401, 403, 429, CAPTCHA, or block-page evidence. No data-payload endpoint was requested.

`ADR-CORR-001` preserves a clerical timestamp correction for `ADR-PR-007` and `ADR-PR-008`; filesystem evidence showed that the manifest was written nine seconds before the first affected request.
