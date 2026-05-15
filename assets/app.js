const formEndpoint = "https://formsubmit.co/ajax/raunaq@withroam.com"
const attributionFields = [
  "utm_source",
  "utm_medium",
  "utm_campaign",
  "utm_content",
  "utm_term",
  "intent",
  "market",
  "entry"
]

function getParams() {
  return new URLSearchParams(window.location.search)
}

function captureAttribution() {
  const params = getParams()
  const attribution = {}

  attributionFields.forEach((field) => {
    const value = params.get(field)
    if (value) attribution[field] = value
  })

  attribution.landing_url = window.location.href
  attribution.referrer = document.referrer || ""

  return attribution
}

function fillHiddenFields(form) {
  const attribution = captureAttribution()

  Object.entries(attribution).forEach(([key, value]) => {
    let input = form.querySelector(`input[name="${key}"]`)
    if (!input) {
      input = document.createElement("input")
      input.type = "hidden"
      input.name = key
      form.appendChild(input)
    }
    input.value = value
  })
}

function productionUrl(intent) {
  const params = getParams()
  const output = new URLSearchParams()
  attributionFields.forEach((field) => {
    const value = params.get(field)
    if (value) output.set(field, value)
  })
  output.set("utm_source", output.get("utm_source") || "reed_gtm_sandbox")
  output.set("utm_medium", output.get("utm_medium") || "sandbox_referral")
  output.set("utm_campaign", output.get("utm_campaign") || "sandbox_gtm_validation")
  output.set("intent", output.get("intent") || intent)
  return `https://reed.withroam.com/?${output.toString()}`
}

function wireProductionLinks() {
  document.querySelectorAll("[data-production-link]").forEach((link) => {
    const intent = link.getAttribute("data-production-link") || "unknown"
    link.href = productionUrl(intent)
  })
}

function wireForms() {
  document.querySelectorAll("form[data-sandbox-form]").forEach((form) => {
    fillHiddenFields(form)
    form.action = formEndpoint
    wireMailtoFallback(form)

    form.addEventListener("submit", async (event) => {
      event.preventDefault()
      fillHiddenFields(form)
      wireMailtoFallback(form)

      const status = form.querySelector("[data-form-status]")
      if (status) status.textContent = "Sending request..."

      const payload = new FormData(form)
      payload.set("_captcha", "false")
      payload.set("_template", "table")
      payload.set("_subject", form.dataset.subject || "Reed sandbox request")

      try {
        const response = await fetch(formEndpoint, {
          method: "POST",
          headers: { Accept: "application/json" },
          body: payload
        })

        if (!response.ok) throw new Error(`FormSubmit returned ${response.status}`)

        const params = new URLSearchParams({
          type: form.dataset.sandboxForm || "request",
          intent: form.querySelector('input[name="intent"]')?.value || "",
          market: form.querySelector('input[name="market"]')?.value || getParams().get("market") || ""
        })

        window.location.href = `${basePath()}thanks/?${params.toString()}`
      } catch (error) {
        if (status) {
          status.innerHTML = "The sandbox form did not send. Use the email fallback or the live Reed link below."
        }
      }
    })
  })
}

function formToObject(form) {
  const data = new FormData(form)
  const values = {}

  for (const [key, value] of data.entries()) {
    if (key.startsWith("_")) continue
    if (value) values[key] = value
  }

  return values
}

function mailtoUrl(form) {
  fillHiddenFields(form)

  const values = formToObject(form)
  const subject = form.dataset.subject || "Reed sandbox request"
  const lines = [
    "Reed sandbox request",
    "",
    ...Object.entries(values).map(([key, value]) => `${key}: ${value}`)
  ]

  const params = new URLSearchParams({
    subject,
    body: lines.join("\n")
  })

  return `mailto:raunaq@withroam.com?${params.toString()}`
}

function wireMailtoFallback(form) {
  const link = form.querySelector("[data-mailto-fallback]")
  if (!link) return

  link.href = mailtoUrl(form)
  link.addEventListener("click", () => {
    link.href = mailtoUrl(form)
  })
}

function basePath() {
  const parts = window.location.pathname.split("/").filter(Boolean)
  if (parts[0] === "reed-gtm-sandbox") return "/reed-gtm-sandbox/"
  return "/"
}

wireProductionLinks()
wireForms()
