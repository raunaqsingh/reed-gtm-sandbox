#!/usr/bin/env python3
import csv
import html
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO.parent
OUTPUT = ROOT / "demand_agents" / "output"
DEAL_CHECKS = OUTPUT / "reed_listing_deal_check_queue.csv"
SEO_SPECS = OUTPUT / "reed_local_seo_deal_check_specs.csv"
PAGE_LEDGER = OUTPUT / "reed_owned_deal_check_pages_ledger.csv"
DASHBOARD = OUTPUT / "reed_real_distribution_dashboard.csv"
SITE_ROOT = "https://raunaqsingh.github.io/reed-gtm-sandbox"

BANNED = (
    "instant price",
    "automated price report",
    "ai appraisal",
    "automated valuation report",
)


def clean(value):
    value = (value or "").strip()
    value = value.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", value)


def esc(value):
    return html.escape(clean(value), quote=True)


def slug(value):
    value = clean(value).lower().replace("/", " ")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "home"


def short(value, limit=120):
    value = clean(value)
    if len(value) <= limit:
        return value
    return value[: limit - 1].rsplit(" ", 1)[0] + "..."


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def page_shell(title, description, canonical_path, body, css_prefix="../.."):
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{SITE_ROOT}/{canonical_path}/">
    <link rel="stylesheet" href="{css_prefix}/assets/styles.css">
  </head>
  <body>
    <div class="site-shell">
      <header class="topbar">
        <a class="brand" href="{css_prefix}/"><span class="brand-mark">R</span><span>Reed sandbox</span></a>
        <nav class="nav" aria-label="Primary">
          <a href="{css_prefix}/deal-checks/">Deal checks</a>
          <a href="{css_prefix}/memo/">Paste a listing</a>
          <a href="{css_prefix}/audit/">Seller audit</a>
        </nav>
      </header>
{body}
      <footer class="footer">
        <div class="footer-inner">
          <span>Reed GTM sandbox</span>
          <span>For buyer research only. Not an appraisal, offer, loan quote, legal advice, or agency agreement.</span>
        </div>
      </footer>
    </div>
  </body>
</html>
"""


def page_tracking(deal):
    params = {
        "utm_source": "github_pages",
        "utm_medium": "owned_deal_check_page",
        "utm_campaign": "buyer_ai_demand",
        "utm_content": clean(deal["deal_check_id"]),
        "intent": "buy",
        "entry": "listing_deal_check_page",
        "market": slug(deal["market"]),
        "listing_url": clean(deal["source_url"]),
        "asset_id": clean(deal["asset_id"]),
    }
    return "https://www.withreed.com/?" + urlencode(params)


def deal_check_page(deal):
    deal_id = clean(deal["deal_check_id"])
    path = f"deal-checks/{deal_id}"
    headline = clean(deal["headline"])
    listing_title = short(deal["listing_title"], 108)
    market = clean(deal["market"])
    state = clean(deal["state"])
    source_url = clean(deal["source_url"])
    tracking_url = page_tracking(deal)
    body = f"""
      <main>
        <section class="hero compact-hero">
          <div class="hero-grid">
            <div>
              <p class="eyebrow">{esc(market)} deal check</p>
              <h1>{esc(headline)}</h1>
              <p class="lede">{esc(deal["quick_take"])}</p>
              <div class="pill-row">
                <span>{esc(market)}, {esc(state)}</span>
                <span>{esc(deal["hook_type"]).replace("_", " ")}</span>
                <span>Buyer research</span>
              </div>
              <div class="cta-row">
                <a class="button" href="{esc(tracking_url)}">Ask Reed about this home</a>
                <a class="button secondary" href="{esc(source_url)}" rel="nofollow">View public listing</a>
              </div>
              <p class="fine-print">Use this to decide what to ask before touring, comparing homes, or making an offer. Reed does not replace inspection, lending, legal, or licensed local advice.</p>
            </div>
            <aside class="memo-visual" aria-label="Deal check summary">
              <div class="memo-header">
                <div>
                  <p class="eyebrow">Listing</p>
                  <h3>{esc(listing_title)}</h3>
                </div>
                <span class="memo-chip">Deal check</span>
              </div>
              <div class="memo-body">
                <div class="finding-list">
                  <div class="finding">{esc(deal["payment_reality"])}</div>
                  <div class="finding">{esc(deal["comp_price_question"])}</div>
                  <div class="finding">{esc(deal["offer_leverage"])}</div>
                </div>
              </div>
            </aside>
          </div>
        </section>
        <section class="section band">
          <div class="grid-3">
            <div class="card"><h3>Payment reality</h3><p>{esc(deal["payment_reality"])}</p></div>
            <div class="card"><h3>Price sanity</h3><p>{esc(deal["comp_price_question"])}</p></div>
            <div class="card"><h3>Inspection risk</h3><p>{esc(deal["inspection_risks"])}</p></div>
            <div class="card"><h3>Offer leverage</h3><p>{esc(deal["offer_leverage"])}</p></div>
            <div class="card"><h3>Homes like this</h3><p>{esc(deal["homes_like_this_cta"])}</p></div>
            <div class="card"><h3>Next step</h3><p>Open this in Reed to pressure-test the home and compare alternatives before spending time on the wrong tour.</p></div>
          </div>
        </section>
      </main>
"""
    return path, tracking_url, page_shell(
        f"{headline} | Reed deal check",
        f"Check payment, price, inspection risk, and offer leverage before touring this {market} home.",
        path,
        body,
    )


def list_page(deals):
    rows = []
    for deal in deals:
        rows.append(
            f"""          <a class="list-row" href="{esc(clean(deal["deal_check_id"]))}/">
            <span>{esc(deal["headline"])}</span>
            <small>{esc(deal["market"])}</small>
          </a>"""
        )
    body = f"""
      <main>
        <section class="hero compact-hero">
          <div>
            <p class="eyebrow">Buyer demand rail</p>
            <h1>Listing deal checks that send buyers into Reed.</h1>
            <p class="lede">Each page gives buyers a concrete reason to start a Reed chat: payment reality, price sanity, inspection risk, offer leverage, and homes like this.</p>
            <div class="cta-row">
              <a class="button" href="../memo/">Paste another listing</a>
              <a class="button secondary" href="../">Back to sandbox</a>
            </div>
          </div>
        </section>
        <section class="section">
          <div class="page-list">
{chr(10).join(rows)}
          </div>
        </section>
      </main>
"""
    return page_shell(
        "Reed listing deal checks",
        "Public Reed deal checks for buyer demand testing across live markets.",
        "deal-checks",
        body,
        css_prefix="..",
    )


def seo_page(spec, deal_by_id):
    deal = deal_by_id[clean(spec["deal_check_id"])]
    path = f"deal-checks/local/{slug(spec['slug'])}"
    tracking_url = page_tracking(deal)
    body = f"""
      <main>
        <section class="hero compact-hero">
          <div>
            <p class="eyebrow">{esc(spec["market"])} buyer research</p>
            <h1>{esc(spec["h1"])}</h1>
            <p class="lede">{esc(deal["quick_take"])}</p>
            <div class="cta-row">
              <a class="button" href="{esc(tracking_url)}">Ask Reed about this home</a>
              <a class="button secondary" href="../../{esc(clean(deal["deal_check_id"]))}/">Open deal check</a>
            </div>
          </div>
        </section>
        <section class="section band">
          <div class="grid-3">
            <div class="card"><h3>Payment reality</h3><p>{esc(deal["payment_reality"])}</p></div>
            <div class="card"><h3>What to compare</h3><p>{esc(deal["comp_price_question"])}</p></div>
            <div class="card"><h3>What to ask</h3><p>{esc(deal["inspection_risks"])}</p></div>
          </div>
        </section>
      </main>
"""
    return path, tracking_url, page_shell(
        clean(spec["title"]),
        clean(spec["meta_description"]),
        path,
        body,
        css_prefix="../../..",
    )


def write_sitemap(paths):
    now = datetime.now(timezone.utc).date().isoformat()
    urls = ["", "memo", "audit", "deal-checks"] + sorted(paths)
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path in urls:
        loc = SITE_ROOT if not path else f"{SITE_ROOT}/{path}/"
        xml.append(f"  <url><loc>{esc(loc)}</loc><lastmod>{now}</lastmod></url>")
    xml.append("</urlset>")
    write(REPO / "sitemap.xml", "\n".join(xml) + "\n")
    write(REPO / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_ROOT}/sitemap.xml\n")


def write_ledger(rows):
    fields = [
        "page_type",
        "id",
        "market",
        "headline",
        "public_url",
        "tracking_url",
        "source_url",
        "status",
        "published_at",
    ]
    with PAGE_LEDGER.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def update_dashboard(summary):
    rows = [
        {
            "metric": "owned_deal_check_pages_ready",
            "value": str(summary["deal_pages"]),
            "source": "reed-gtm-sandbox/deal-checks",
            "updated_at": summary["timestamp"],
        },
        {
            "metric": "owned_local_seo_pages_ready",
            "value": str(summary["seo_pages"]),
            "source": "reed-gtm-sandbox/deal-checks/local",
            "updated_at": summary["timestamp"],
        },
        {
            "metric": "external_actions_taken",
            "value": "0",
            "source": "no cold email, no social posts, no public replies from this generator",
            "updated_at": summary["timestamp"],
        },
    ]
    with DASHBOARD.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "value", "source", "updated_at"])
        writer.writeheader()
        writer.writerows(rows)


def validate_text(paths):
    for path in paths:
        text = path.read_text(encoding="utf-8").lower()
        for term in BANNED:
            if term in text:
                raise ValueError(f"banned copy found in {path}: {term}")


def main():
    deals = read_csv(DEAL_CHECKS)
    specs = read_csv(SEO_SPECS)
    deal_by_id = {clean(row["deal_check_id"]): row for row in deals}
    market_counts = Counter(clean(row["market"]) for row in deals)
    ledger_rows = []
    generated_paths = []
    sitemap_paths = []

    write(REPO / "deal-checks" / "index.html", list_page(deals))
    generated_paths.append(REPO / "deal-checks" / "index.html")

    for deal in deals:
        path, tracking_url, html_page = deal_check_page(deal)
        out = REPO / path / "index.html"
        write(out, html_page)
        generated_paths.append(out)
        sitemap_paths.append(path)
        ledger_rows.append(
            {
                "page_type": "deal_check",
                "id": clean(deal["deal_check_id"]),
                "market": clean(deal["market"]),
                "headline": clean(deal["headline"]),
                "public_url": f"{SITE_ROOT}/{path}/",
                "tracking_url": tracking_url,
                "source_url": clean(deal["source_url"]),
                "status": "generated_pending_push",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    for spec in specs:
        path, tracking_url, html_page = seo_page(spec, deal_by_id)
        out = REPO / path / "index.html"
        write(out, html_page)
        generated_paths.append(out)
        sitemap_paths.append(path)
        ledger_rows.append(
            {
                "page_type": "local_seo",
                "id": clean(spec["page_id"]),
                "market": clean(spec["market"]),
                "headline": clean(spec["h1"]),
                "public_url": f"{SITE_ROOT}/{path}/",
                "tracking_url": tracking_url,
                "source_url": clean(deal_by_id[clean(spec["deal_check_id"])]["source_url"]),
                "status": "generated_pending_push",
                "published_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    write_sitemap(sitemap_paths)
    generated_paths.extend([REPO / "sitemap.xml", REPO / "robots.txt"])
    write_ledger(ledger_rows)
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "deal_pages": len(deals),
        "seo_pages": len(specs),
        "markets": dict(market_counts),
        "ledger": str(PAGE_LEDGER),
    }
    update_dashboard(summary)
    validate_text(generated_paths)
    print(summary)


if __name__ == "__main__":
    main()
