#!/usr/bin/env python3
import csv
import html
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus, urlencode


REPO = Path(__file__).resolve().parents[1]
OUTPUT = REPO.parent / "demand_agents" / "output"
BUYER_SOURCE = OUTPUT / "reed_250_buyer_memo_assets.csv"
SELLER_SOURCE = OUTPUT / "listing_activation_assets.csv"
DISTRIBUTION_LEDGER = OUTPUT / "reed_sandbox_distribution_ledger.csv"
EXECUTION_LEDGER = OUTPUT / "reed_300_start_execution_ledger_20260515.csv"
BATCH_LEDGER = OUTPUT / "reed_300_owned_sandbox_page_seeds_20260515.csv"

SITE_ROOT = "https://raunaqsingh.github.io/reed-gtm-sandbox"
COUNT_BUYER = 250
COUNT_SELLER = 50


def ascii_clean(value):
    value = (value or "").strip()
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"\s+", " ", value)
    return value


def esc(value):
    return html.escape(ascii_clean(value), quote=True)


def short(value, limit=92):
    value = ascii_clean(value)
    if len(value) <= limit:
        return value
    return value[: limit - 1].rsplit(" ", 1)[0] + "..."


def slug(value):
    value = ascii_clean(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "home"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def form_fields(intent, market, listing_url, source_id):
    return f"""
                <input type="hidden" name="intent" value="{esc(intent)}">
                <input type="hidden" name="market" value="{esc(market)}">
                <input type="hidden" name="listing_url" value="{esc(listing_url)}">
                <input type="hidden" name="source_id" value="{esc(source_id)}">
                <input type="hidden" name="_honey">
"""


def page_header(title, description, asset_path):
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{SITE_ROOT}/{asset_path}/">
    <link rel="stylesheet" href="../../assets/styles.css">
  </head>
  <body>
    <div class="site-shell">
      <header class="topbar">
        <a class="brand" href="../../"><span class="brand-mark">R</span><span>Reed sandbox</span></a>
        <nav class="nav"><a href="../../memos/">Listing memos</a><a href="../../seller/">Seller pages</a><a href="../../audit/">Seller audit</a></nav>
      </header>
"""


def page_footer(script_path="../../assets/app.js"):
    return f"""      <footer class="footer">
        <div class="footer-inner">
          <span>Reed GTM sandbox</span>
          <span>This is a sandbox intake test, not an appraisal, agency agreement, or offer to buy property.</span>
        </div>
      </footer>
    </div>
    <script src="{script_path}"></script>
  </body>
</html>
"""


def buyer_page(row):
    asset_id = row["asset_id"]
    market = ascii_clean(row["market"])
    state = ascii_clean(row["state"])
    listing_title = short(row["listing_title"], 98)
    source_url = row["source_url"]
    tracking_url = row["tracking_url"]
    path = f"memos/{asset_id}"
    page_url = f"{SITE_ROOT}/{path}/"
    page_tracking = f"{page_url}?{urlencode({'utm_source':'github_pages','utm_medium':'owned_sandbox_page','utm_campaign':'reed_300_start_batch','utm_content':asset_id,'intent':'buy','market':slug(market),'entry':'listing_memo_page'})}"
    headline = f"Should you tour {listing_title}?"
    prompt = ascii_clean(row.get("buyer_memo_prompt")) or "Ask Reed what to watch for before touring or making an offer."

    content = page_header(
        f"Reed buyer memo: {listing_title}",
        f"Ask Reed for a buyer decision memo on this {market} listing.",
        path,
    )
    content += f"""      <main>
        <section class="hero">
          <div class="hero-grid">
            <div>
              <p class="eyebrow">{esc(market)} buyer memo</p>
              <h1>{esc(headline)}</h1>
              <p class="lede">{esc(prompt)}</p>
              <div class="pill-row">
                <span>{esc(market)}, {esc(state)}</span>
                <span>Listing-specific memo</span>
                <span>Tour and offer prep</span>
              </div>
              <div class="cta-row">
                <a class="button" href="{esc(tracking_url)}">Open this in Reed</a>
                <a class="button secondary" href="{esc(source_url)}" rel="nofollow">View public listing</a>
              </div>
              <p class="fine-print">Reed reviews the public listing, comparable context, risk questions, and the next decision. It does not send offers, negotiate, or replace a licensed local professional.</p>
            </div>
            <form class="form-card" data-sandbox-form="buyer_listing_page" data-subject="Reed sandbox listing memo request">
              <h2>Request this memo</h2>
              <div class="form-grid">
                <label>Email for the sandbox memo
                  <input name="email" type="email" placeholder="you@example.com" required>
                </label>
                <label>What should Reed focus on?
                  <select name="decision">
                    <option value="tour">Should I tour it?</option>
                    <option value="price">Does the price make sense?</option>
                    <option value="risk">What risks should I check?</option>
                    <option value="offer">What should my agent review before an offer?</option>
                  </select>
                </label>
                <label>Anything specific?
                  <textarea name="notes" placeholder="Budget, timeline, inspection concern, spouse or lender question"></textarea>
                </label>
{form_fields("buy", market, source_url, asset_id)}
                <button class="button" type="submit">Send memo request</button>
                <a class="button secondary" data-mailto-fallback href="mailto:raunaq@withroam.com?subject=Reed%20sandbox%20listing%20memo">Email request instead</a>
                <p class="status" data-form-status></p>
              </div>
            </form>
          </div>
        </section>
        <section class="section band">
          <div class="grid-3">
            <div class="card"><h3>Price sanity</h3><p>Check the ask against public signals, stale-listing risk, price-cut history, and buyer leverage.</p></div>
            <div class="card"><h3>Tour filter</h3><p>Decide whether this is worth seeing before losing time on the wrong home.</p></div>
            <div class="card"><h3>Agent review</h3><p>Turn the memo into sharper questions for an agent, lender, inspector, or parent.</p></div>
          </div>
        </section>
      </main>
"""
    content += page_footer()
    return path, page_url, page_tracking, content


def seller_page(row):
    activation_id = row["activation_id"]
    market = ascii_clean(row["market"])
    state = ascii_clean(row["state"])
    listing_title = short(row["listing_title"], 98)
    source_url = row["source_url"]
    tracking_url = row["reed_listing_url"]
    path = f"seller/{activation_id}"
    page_url = f"{SITE_ROOT}/{path}/"
    page_tracking = f"{page_url}?{urlencode({'utm_source':'github_pages','utm_medium':'owned_sandbox_page','utm_campaign':'reed_300_start_batch','utm_content':activation_id,'intent':'sell','market':slug(market),'entry':'seller_activation_page'})}"
    headline = f"What could buyers ask about {listing_title}?"

    content = page_header(
        f"Reed seller memo: {listing_title}",
        f"Ask Reed for a seller pricing and buyer-objection memo for this {market} listing.",
        path,
    )
    content += f"""      <main>
        <section class="hero">
          <div class="hero-grid">
            <div>
              <p class="eyebrow">{esc(market)} seller memo</p>
              <h1>{esc(headline)}</h1>
              <p class="lede">Reed turns a public listing into a short pricing-risk and buyer-objection memo: what buyers may question, what the price needs to prove, and what to clarify before a showing.</p>
              <div class="pill-row">
                <span>{esc(market)}, {esc(state)}</span>
                <span>Seller pricing risk</span>
                <span>Buyer objection prep</span>
              </div>
              <div class="cta-row">
                <a class="button" href="{esc(tracking_url)}">Open this in Reed</a>
                <a class="button secondary" href="{esc(source_url)}" rel="nofollow">View public listing</a>
              </div>
              <p class="fine-print">This is a Reed sandbox page for GTM validation. It is not an appraisal, broker price opinion, or legal advice.</p>
            </div>
            <form class="form-card" data-sandbox-form="seller_listing_page" data-subject="Reed sandbox seller memo request">
              <h2>Request seller memo</h2>
              <div class="form-grid">
                <label>Email for the sandbox memo
                  <input name="email" type="email" placeholder="you@example.com" required>
                </label>
                <label>What should Reed focus on?
                  <select name="decision">
                    <option value="pricing">Pricing sanity</option>
                    <option value="buyer_objections">Buyer objections</option>
                    <option value="prep">Listing prep</option>
                    <option value="timeline">Timeline and next step</option>
                  </select>
                </label>
                <label>Anything specific?
                  <textarea name="notes" placeholder="Condition, upgrades, showing feedback, price cut, timeline"></textarea>
                </label>
{form_fields("sell", market, source_url, activation_id)}
                <button class="button" type="submit">Send seller memo request</button>
                <a class="button secondary" data-mailto-fallback href="mailto:raunaq@withroam.com?subject=Reed%20sandbox%20seller%20memo">Email request instead</a>
                <p class="status" data-form-status></p>
              </div>
            </form>
          </div>
        </section>
        <section class="section band">
          <div class="grid-3">
            <div class="card"><h3>Estimate gaps</h3><p>Capture condition, layout, upgrades, and timing that generic online estimates miss.</p></div>
            <div class="card"><h3>Buyer friction</h3><p>List the questions that may slow tours, offers, inspection, or financing.</p></div>
            <div class="card"><h3>Next action</h3><p>Turn the memo into an expert-review, pricing, prep, or listing-strategy conversation.</p></div>
          </div>
        </section>
      </main>
"""
    content += page_footer()
    return path, page_url, page_tracking, content


def directory_page(kind, rows):
    title = "Listing Memos" if kind == "memos" else "Seller Memo Pages"
    eyebrow = "Buyer memo pages" if kind == "memos" else "Seller audit pages"
    description = "Source-coded Reed sandbox pages for public listing memo demand tests."
    links = []
    for row in rows:
        label = row["listing_title"]
        market = row["market"]
        seed_id = row["seed_id"]
        public_url = row["public_url"]
        links.append(f"""              <a class="list-row" href="{esc(public_url)}">
                <span>{esc(short(label, 86))}</span>
                <small>{esc(market)} | {esc(seed_id)}</small>
              </a>""")
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Reed sandbox {esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="stylesheet" href="../assets/styles.css">
  </head>
  <body>
    <div class="site-shell">
      <header class="topbar">
        <a class="brand" href="../"><span class="brand-mark">R</span><span>Reed sandbox</span></a>
        <nav class="nav"><a href="../memo/">Buyer memo</a><a href="../audit/">Seller audit</a><a href="../">Home</a></nav>
      </header>
      <main>
        <section class="hero compact-hero">
          <div>
            <p class="eyebrow">{esc(eyebrow)}</p>
            <h1>{esc(title)}</h1>
            <p class="lede">Each page is a public, source-coded Reed GTM seed tied to a real public real estate surface. Engaged demand is counted only when someone replies, clicks, submits, or asks for the next step.</p>
          </div>
        </section>
        <section class="section">
          <div class="page-list">
{chr(10).join(links)}
          </div>
        </section>
      </main>
{page_footer('../assets/app.js').split('<footer',1)[1] if False else ''}
      <footer class="footer"><div class="footer-inner"><span>Reed GTM sandbox</span><span>Owned public GTM seed directory.</span></div></footer>
    </div>
  </body>
</html>
"""


def existing_execution_keys(path):
    if not path.exists():
        return set(), []
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return {r["seed_id"] for r in rows if r.get("seed_id")}, rows


def append_csv(path, fieldnames, rows, key="seed_id"):
    existing_keys = set()
    existing_rows = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_rows = list(reader)
            existing_keys = {r.get(key) for r in existing_rows}
            if reader.fieldnames and reader.fieldnames != fieldnames:
                fieldnames = reader.fieldnames
    new_rows = [r for r in rows if r.get(key) not in existing_keys]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_rows)
        writer.writerows(new_rows)
    return len(new_rows)


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    buyer_rows = read_csv(BUYER_SOURCE)[:COUNT_BUYER]
    seller_rows = read_csv(SELLER_SOURCE)[:COUNT_SELLER]
    seed_rows = []
    buyer_index_rows = []
    seller_index_rows = []

    for source in buyer_rows:
        path, page_url, page_tracking, content = buyer_page(source)
        write(REPO / path / "index.html", content)
        seed_id = f"owned_page_{source['asset_id']}"
        row = {
            "seed_id": seed_id,
            "created_at_utc": now,
            "channel": "github_pages",
            "rail": "owned_sandbox_listing_memo_page",
            "market": ascii_clean(source["market"]),
            "intent": "buyer_start",
            "destination": page_url,
            "status": "published_owned_page_pending_http_verify",
            "evidence": page_url,
            "notes": f"Buyer listing memo page generated from {ascii_clean(source['source_url'])}",
            "public_url": page_url,
            "tracking_url": page_tracking,
            "source_url": ascii_clean(source["source_url"]),
            "listing_title": ascii_clean(source["listing_title"]),
        }
        seed_rows.append(row)
        buyer_index_rows.append(row)

    for source in seller_rows:
        path, page_url, page_tracking, content = seller_page(source)
        write(REPO / path / "index.html", content)
        seed_id = f"owned_page_{source['activation_id']}"
        row = {
            "seed_id": seed_id,
            "created_at_utc": now,
            "channel": "github_pages",
            "rail": "owned_sandbox_seller_activation_page",
            "market": ascii_clean(source["market"]),
            "intent": "seller_start",
            "destination": page_url,
            "status": "published_owned_page_pending_http_verify",
            "evidence": page_url,
            "notes": f"Seller memo page generated from {ascii_clean(source['source_url'])}",
            "public_url": page_url,
            "tracking_url": page_tracking,
            "source_url": ascii_clean(source["source_url"]),
            "listing_title": ascii_clean(source["listing_title"]),
        }
        seed_rows.append(row)
        seller_index_rows.append(row)

    write(REPO / "memos" / "index.html", directory_page("memos", buyer_index_rows))
    write(REPO / "seller" / "index.html", directory_page("seller", seller_index_rows))

    sitemap_urls = [SITE_ROOT + "/", SITE_ROOT + "/memo/", SITE_ROOT + "/audit/", SITE_ROOT + "/memos/", SITE_ROOT + "/seller/"]
    sitemap_urls += [row["public_url"] for row in seed_rows]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in sitemap_urls:
        sitemap.append(f"  <url><loc>{esc(url)}</loc></url>")
    sitemap.append("</urlset>")
    write(REPO / "sitemap.xml", "\n".join(sitemap) + "\n")
    write(REPO / "robots.txt", "User-agent: *\nAllow: /\nSitemap: https://raunaqsingh.github.io/reed-gtm-sandbox/sitemap.xml\n")

    batch_fields = [
        "seed_id", "created_at_utc", "channel", "rail", "market", "intent", "destination",
        "status", "evidence", "notes", "public_url", "tracking_url", "source_url", "listing_title"
    ]
    write_csv(BATCH_LEDGER, batch_fields, seed_rows)

    execution_fields = ["seed_id", "created_at_utc", "channel", "rail", "market", "intent", "destination", "status", "evidence", "notes"]
    execution_rows = [{k: r[k] for k in execution_fields} for r in seed_rows]
    append_csv(EXECUTION_LEDGER, execution_fields, execution_rows)

    distribution_fields = [
        "timestamp_et", "placement_id", "channel", "market", "status", "public_url", "tracking_url",
        "utm_source", "utm_medium", "utm_campaign", "utm_content", "intent", "demand_count_rule", "notes"
    ]
    distribution_rows = []
    for r in seed_rows:
        distribution_rows.append({
            "timestamp_et": "2026-05-15 20:45:00 EDT",
            "placement_id": r["seed_id"],
            "channel": "github_pages",
            "market": r["market"],
            "status": "published_owned_page_pending_http_verify",
            "public_url": r["public_url"],
            "tracking_url": r["tracking_url"],
            "utm_source": "github_pages",
            "utm_medium": "owned_sandbox_page",
            "utm_campaign": "reed_300_start_batch",
            "utm_content": r["seed_id"].replace("owned_page_", ""),
            "intent": "buy" if r["intent"] == "buyer_start" else "sell",
            "demand_count_rule": "form submission, email request, tracked Reed click/start, or explicit next-step ask",
            "notes": f"Owned public sandbox page generated from public source URL: {r['source_url']}",
        })
    append_csv(DISTRIBUTION_LEDGER, distribution_fields, distribution_rows, key="placement_id")

    print(f"generated_seed_pages={len(seed_rows)}")
    print(f"buyer_pages={len(buyer_index_rows)} seller_pages={len(seller_index_rows)}")
    print(f"batch_ledger={BATCH_LEDGER}")


if __name__ == "__main__":
    main()
