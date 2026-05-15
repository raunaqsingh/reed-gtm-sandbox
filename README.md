# Reed GTM Sandbox

Standalone static sandbox for Reed GTM validation. This is intentionally outside the core Reed app so public demand tests can run without interrupting engineering.

Live target:

https://raunaqsingh.github.io/reed-gtm-sandbox/

Guardrails:

- Public-only distribution.
- No paid spend.
- No personal social.
- No DMs or direct owner outreach.
- No phone verification, CAPTCHA bypass, or generic inbox scraping.
- Demand counts only when a user submits a form, gives a qualified public reply, starts a tracked Reed flow, or explicitly asks for a next step.

Forms use FormSubmit AJAX to route sandbox requests to `raunaq@withroam.com`.
