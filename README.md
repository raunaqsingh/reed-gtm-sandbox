# Reed GTM Sandbox

Standalone static sandbox for Reed GTM validation. This is intentionally outside the core Reed app so public demand tests can run without interrupting engineering.

Live target:

https://raunaqsingh.github.io/reed-gtm-sandbox/

Guardrails:

- Public-only distribution.
- No paid spend.
- No cold email, calls, texts, or DMs.
- No generic inbox blasting.
- No phone verification, CAPTCHA bypass, or generic inbox scraping.
- Demand counts only when a user starts a tracked Reed flow, submits a form, gives a qualified public reply, or explicitly asks for a next step.

Forms use FormSubmit AJAX to route sandbox requests to `raunaq@withroam.com`.

## Deal Check Rail

The current buyer-led test publishes listing-specific deal checks under `/deal-checks/`.

Run:

```sh
python3 scripts/generate_deal_check_pages.py
```

Outputs:

- 100 listing deal-check pages across Houston, Dallas/Fort Worth, Austin, Phoenix, and Atlanta.
- 25 local search-style pages under `/deal-checks/local/`.
- `../demand_agents/output/reed_owned_deal_check_pages_ledger.csv`
- `../demand_agents/output/reed_real_distribution_dashboard.csv`

Every deal-check CTA routes to `withreed.com` with `utm_campaign=buyer_ai_demand`, `intent=buy`, `entry=listing_deal_check_page`, `market`, `listing_url`, and `asset_id`.
