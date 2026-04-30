# DocuAgent AI — Business Pitch & Go-to-Market

> **The honest framing:** NotebookLM is excellent, free, and built by Google. You are not going to win by being a slightly nicer NotebookLM clone. You win by serving the customers who **cannot use NotebookLM**, and by going **deeper** than it does for the customers who can.

This document is the strategic spine for DocuAgent AI — not marketing copy. Read it, argue with it, then write the pitch deck from it.

---

## 1. The problem worth solving

NotebookLM solved a real problem for *individuals* — it made it cheap to query a stack of documents in natural language. It did **not** solve the problem for organizations, because every business interaction with an AI tool runs into the same five questions:

1. **Where does our data go?** (Google's terms allow training-exclusion, but legal teams have to read and trust them.)
2. **Can we use this with regulated data?** (HIPAA, GDPR, SEC 17a-4, CMMC, attorney-client privilege.)
3. **Can we put it on data the cloud can't see?** (R&D documents, M&A diligence, source code, classified networks.)
4. **Can we shape it to our domain?** (Custom prompts, custom workflows, custom file formats, integration with our document store.)
5. **Will it still be there next year, on our terms?** (Vendor lock-in, pricing changes, deprecation cycles.)

NotebookLM answers these with "trust us." That answer is sufficient for a journalist organising research notes. It is **categorically insufficient** for a law firm reviewing privileged contracts, a hospital reading patient records, a defense contractor handling controlled unclassified information, a consultant working under an NDA, or any organisation in the EU under GDPR's Article 28 processor obligations.

**Our product answers all five with: "the model and your data both live on hardware you control."** That is the single sentence the entire pitch hangs on.

---

## 2. The five-second positioning

> **DocuAgent AI is the on-premise NotebookLM for organisations that can't put their documents in the cloud.**

Subhead variants by audience:

- *For legal:* "NotebookLM with privilege intact — verified citations, zero cloud exposure."
- *For healthcare:* "Document AI that's HIPAA by design — because your patient data never leaves the building."
- *For defense / gov:* "An air-gappable research assistant for classified and CUI workflows."
- *For finance:* "The research workstation your compliance team already approved — because there's nothing to approve."
- *For consulting / professional services:* "Per-engagement document AI with cryptographic client segregation."
- *For regulated enterprises:* "Enterprise RAG that passes security audits on day one."

---

## 3. Who buys this — and who doesn't

### The "yes" buyers (rank-ordered by ease of close)

| Segment | Trigger | Budget owner | Deal size feel |
| --- | --- | --- | --- |
| **Mid-size law firms (20–200 lawyers)** | Litigation discovery, contract review, due diligence — privileged content cannot legally go to a third-party AI provider. | Managing partner / IT director | $20–80k/yr per firm, deployed on existing partner laptops |
| **Hospital systems & medical research groups** | Clinical trial documents, patient records research, grant compilation under HIPAA. | CIO or research IT | $50k–$300k/yr |
| **Defense contractors / federal SIs** | CUI and classified document workflows. ITAR-restricted IP. | Program manager / security officer | $100k+ per program; long sales cycle but sticky |
| **Wealth managers, family offices, boutique IBs** | Deal docs, personal financial records. | Managing director | $30–100k/yr |
| **Consulting firms (Big-4 down to 50-person boutiques)** | Per-engagement client confidentiality, SOC2 audits. | Engagement partner | $25–150k/yr depending on rollout |
| **In-house R&D / patent groups (pharma, semis, manufacturing)** | Trade secret and patentable invention disclosure documents. | R&D director or CTO | $50–250k/yr |

### The "no" buyers — be ruthless about this

- Consumer users. NotebookLM exists, is free, and is good enough for them.
- Organisations whose compliance posture is "we put it in Google Drive anyway." If they don't already feel pain about cloud AI, you cannot manufacture that pain in a 30-minute pitch.
- Companies that need 100B+ parameter reasoning on day one. An 8B model is not your differentiator — privacy is. Be honest that complex multi-step reasoning is better elsewhere; that's a feature of your honesty, not a bug.

---

## 4. The pricing & packaging that actually works

| Tier | Price | What's included | Who it's for |
| --- | --- | --- | --- |
| **Personal Pro** | $29 / month or $290 / year | Full app, signed Mac binary, model auto-installer, priority email support, local workspace encryption. | Solo professionals: solo lawyers, doctors, analysts, journalists, consultants. |
| **Team** | $49 / seat / month, 3-seat min | Personal Pro + shared workspaces over local network, role-based access, audit log, document versioning, central deployment. | 3–50 person firms and departments. |
| **Enterprise** | $35–120k flat per year | On-prem server deployment (any GPU box), model upgrades (70B+), custom document format adapters, integration with NetDocuments / iManage / SharePoint / EHR, SLA, named TAM, security review. | Regulated firms 50+ users, compliance-heavy industries. |
| **Sovereign / Air-Gap** | Six-figure annual contract | Fully offline build, on-site deployment, model fine-tuning on customer corpus, security certification support, FedRAMP/IL5 audit trail, dedicated support. | Defense, federal, life-critical infrastructure, classified networks. |

**Critical pricing insight:** do **not** price below ChatGPT Team ($25/seat). Pricing low signals "consumer toy." Customers in this space treat low prices as a red flag. Match or exceed enterprise SaaS pricing — your differentiator is risk reduction, not cost.

The economic argument to the buyer is not "we're cheaper than Google." It's "one breach, one regulator letter, or one disqualified expert opinion costs you 50–500x our annual fee. We are insurance."

---

## 5. Differentiation & Features (what enterprise requires)

Anything below this line is what makes Enterprise contracts close. DocuAgent AI's moats vs. NotebookLM:

### Core differentiators (table stakes in regulated industries)

1. **Zero cloud / full on-prem deployment** — no API calls, no cloud tenancy, no shared infrastructure. Compliance by default.
2. **Cryptographic workspace separation** — Engagement A's data is cryptographically distinct from Engagement B's. Different users cannot see each other's work.
3. **Audit log of every query, answer, and data access** — legal hold compatible, discoverable, compliant with SEC 17a-4, FINRA, HIPAA.
4. **Source citation with document-level provenance** — verify every claim in seconds. Cite exact page, section, and line. No hallucination risk on sources.
5. **Role-based and document-level access controls** — paralegals see litigation docs; R&D sees trade secrets; not both.
6. **Export to all practice formats** — Word, PDF with citations, Bates numbers, privileged marking, .eml, DOCX templates.

### Tier-1 features (before first sales call)

7. **Custom prompt templates per workflow** — "deposition prep," "10-K analysis," "clinical adverse event," "contract red-flags." Domain-specific reasoning.
8. **Document version diff with reasoning** — show what changed between contract draft v1 → v2 and explain legal consequences in plain language.
9. **Cross-document timeline extraction** — build chronologies from 200+ emails and contracts automatically.
10. **Numerical reasoning over spreadsheets & data tables** — spot inconsistencies, reconcile figures, flag anomalies.
11. **Multi-language ingestion & cross-language queries** — most law and pharma corpora span English, German, French, Japanese, Chinese.

### Tier-2 / Moat features (build during growth)

12. **Fine-tuning on customer corpus** — a model that speaks in the customer's house style. That's a +3-year lock-in, and NotebookLM cannot offer it.
13. **Adversarial review mode** — given a document or position, generate the strongest counter-arguments. Legal, medical, and investment professionals pay 10x for this kind of "stress test" tooling.
14. **Custom file format support** — Bloomberg terminal exports, Bates-numbered PDFs, EHR formats (HL7, FHIR), CAD files, Salesforce exports. Each one is an integration moat.
15. **Integration w/ firm systems** — NetDocuments, iManage, SharePoint, Slack, Teams, Relativity. Embed DocuAgent into their workflow, not the other way around.
15. **Federated search across local + corporate knowledge base** — no document leaves its home, but a single query gets answered.

---

## 6. The objection handling cheat sheet

| Prospect says | You say |
| --- | --- |
| *"NotebookLM is free."* | "It is — for individuals. For your firm, the question isn't price, it's whether your privileged documents can legally go to Google's servers. Read your engagement letters and your client's NDA." |
| *"The model isn't as good as GPT-5 / Gemini Ultra."* | "Correct. We optimise for the cases where you need a *defensible* answer over a brilliant one. For boilerplate research, our 8B model is as good as anything; for complex multi-step reasoning, we'll always recommend a human. We tell you which is which." |
| *"What about hallucinations?"* | "Every answer is grounded in retrieved passages and cites the source. You verify before quoting — same as a paralegal's brief. We make verification a one-click action, not a hope." |
| *"We don't have GPUs."* | "Mac Studio M4 Max runs the 70B variant comfortably. Or buy one $4k box and serve 50 users. We size it for you in the discovery call." |
| *"What if our IT can't deploy this?"* | "Single-installer Mac binary; one-line Docker for Linux; we have a deployment engineer on the Enterprise tier." |
| *"How do we know the model itself isn't biased?"* | "Same way you know your interns aren't — you spot-check. We give you a built-in eval harness so your team can run regression tests on prompts you care about." |
| *"What if Llama gets deprecated?"* | "The whole runtime is interchangeable. You can swap to Mistral, Qwen, or any future model in a config line. Your data, your prompts, your workspace are model-agnostic." |

---

## 7. Go-to-market sequencing (the next 90 days)

**Days 1–14 — Sharpen the wedge.** Pick *one* vertical. Not "regulated industries" — pick "20–80 lawyer commercial litigation firms in your home metro." Build the product story for them only.

**Days 15–45 — Manual founder-led sales.**
- LinkedIn-message 200 managing partners and IT directors. Offer a no-cost 30-minute walkthrough on their laptop, with their own (anonymised) document.
- Aim for 10 walkthroughs. Expect 2–3 paid pilots at $5k each for 90 days.

**Days 45–75 — Earn one logo.** Your first reference customer is worth more than $50k of marketing. Ship features they ask for. Get a quote you can put on the website.

**Days 75–90 — Repeat the wedge in an adjacent vertical.** Healthcare research groups in the same metro. Same playbook.

**Do not** build a "platform." Do not write a generic landing page. Do not buy ads. Talk to humans whose job is at risk if their documents leak.

---

## 8. The defensibility argument (for investors, not customers)

If you fundraise, the question every investor will ask is: "what stops Google from launching NotebookLM Enterprise tomorrow?"

The honest answer:

1. **Distribution.** Google's enterprise sales motion is poorly suited to the regulated, distrustful mid-market. They have to sell to your IT director's IT director's boss. You sell to the partner.
2. **Integration depth.** NotebookLM is a finished product with a controlled feature set. You are a *workbench* for industry-specific workflows. The first three custom file-format adapters and prompt libraries you ship for a vertical compound into a moat.
3. **Trust capital.** A boutique vendor that signs a BAA, runs on-prem, and answers email in two hours from a real human builds a kind of trust Google literally cannot manufacture. (See: every successful enterprise software company that beat a hyperscaler — Snowflake, Databricks, Atlassian, GitLab.)
4. **The model commoditisation tailwind.** The 8B/70B open-weight class will keep getting better. Google's advantage at the model layer is shrinking. The differentiation moves to the *application layer* — the prompts, integrations, workflows, and trust that you own.

---

## 9. Three honest weaknesses you must own

A pitch that ignores its weaknesses sounds like marketing. A pitch that names them sounds like an operator. Name these:

1. **An 8B model is not GPT-5.** Multi-step reasoning, math, code generation will be weaker. Mitigation: route those tasks to bigger local models (70B+) when GPU is available; be transparent in the UI when you're working at the edge of the model's competence.
2. **You will lose deals where the buyer's compliance team is content with cloud AI.** That's fine. Don't try to win them — lower CAC, focus on the segment where the win is structural, not preference-based.
3. **Your support burden grows linearly with deployment count.** On-prem software has a real cost-to-serve. Price for it. Build a reliable installer. Hire a deployment engineer before you hire a third salesperson.

---

## 10. The one slide

If the entire pitch had to be one slide:

> **Most knowledge work happens on documents that legally cannot go to a third-party AI service.**
>
> **DocuAgent AI is the secure document intelligence platform that runs entirely on your own hardware — with on-prem deployment, custom prompts, role-based controls, and integrations no cloud product can match.**
>
> **We're not competing with NotebookLM on features. We're competing on the principle that your documents stay yours, and every query leaves an audit trail.**

---

*This document is a living draft. The numbers above are starting hypotheses, not validated truths. Each customer conversation should change at least one of them.*
