# I Built ArcKit for Myself. Thank You for Using It.

I built ArcKit for myself.

That is the honest origin story. I wanted a way to make architecture work less wasteful and more traceable. I wanted requirements, risks, ADRs, Wardley maps, business cases, procurement notes and assurance evidence to live together instead of drifting across documents, decks and half-remembered decisions. I wanted a harness that made AI useful for architecture without letting it turn governance into a pile of plausible prose.

So I built the thing I needed.

I did not expect this many people to use it.

Over the last few weeks I have been looking at the public signals around ArcKit: GitHub, the website, search data, clone activity, extension repos. They are not perfect measures. ArcKit does not phone home. There was no GA4 tag on the site until 29 June 2026. I cannot tell you how many teams have run a command or how many architecture decisions have been made with it, and I am comfortable with that. A governance toolkit should not quietly collect telemetry from the projects it helps.

But even from the public signals, one thing is now obvious: ArcKit is no longer just my local working method.

People are using it. People are cloning it. People are forking it. People are installing the assistant-specific versions. People are searching for it by name. People are reading the docs, opening the guides, inspecting the skills, and coming back to the repository from the site.

That is both wonderful and slightly unreal.

So this is mostly a thank you.

Thank you for trying it. Thank you for starring it. Thank you for cloning it. Thank you for filing issues, opening pull requests, asking questions, poking at the weird edges, and adapting it to assistants I was not originally thinking about. Thank you for treating enterprise architecture as something that can be made more open, more reproducible and more useful.

---

## The Surprise

As of 29 June 2026, the main [tractorjuice/arc-kit](https://github.com/tractorjuice/arc-kit) repository had:

- **2,039 GitHub stars**
- **253 forks**
- **1,331 commits** on the default branch history
- **197 GitHub releases**
- **304 merged pull requests**
- **197 closed issues**

Those numbers are not the point by themselves. Stars are not users. Forks are not deployments. Releases are not outcomes.

But for something I originally built to scratch my own itch, they are still startling.

The thing that surprised me most was not the stars. It was the clone activity. In GitHub's latest traffic window, covering **15 June to 28 June 2026**, the main ArcKit repository saw:

- **2,974 clone events**
- **625 unique cloners**
- **1,864 repository views**
- **642 unique repository viewers**

Clone events are imperfect too. They include repeat pulls, CI, local rebuilds, automation and people who try the project once. But cloning is still different from browsing. It means someone put ArcKit on a machine.

That is the moment where a project stops being content and starts becoming a tool.

---

## It Is Not Just the Main Repository

ArcKit now publishes assistant-specific distributions as standalone repositories:

- [arckit-codex](https://github.com/tractorjuice/arckit-codex)
- [arckit-gemini](https://github.com/tractorjuice/arckit-gemini)
- [arckit-opencode](https://github.com/tractorjuice/arckit-opencode)
- [arckit-copilot](https://github.com/tractorjuice/arckit-copilot)
- [arckit-paperclip](https://github.com/tractorjuice/arckit-paperclip)
- [arckit-vibe](https://github.com/tractorjuice/arckit-vibe)

I added those because the harness should meet people where they already work. Some people live in Claude Code. Some are using Codex CLI. Some are trying Gemini CLI, OpenCode, GitHub Copilot, Paperclip or Mistral Vibe. The governance method should not depend on one assistant winning.

The usage signal there is encouraging too. In the same GitHub traffic window, the standalone extension repositories saw:

| Repository | Clone events | Unique cloners |
| --- | ---: | ---: |
| arckit-codex | 594 | 219 |
| arckit-gemini | 151 | 64 |
| arckit-copilot | 114 | 38 |
| arckit-opencode | 81 | 42 |
| arckit-vibe | 81 | 60 |
| arckit-paperclip | 4 | 1 |

Do not read that as deduplicated users. The same person can clone more than one repo. Read it as behaviour: people are not only looking at the core project. They are pulling the distribution that fits their working environment.

That matters because ArcKit is not trying to be another AI app. It is a harness for the places where architects already work.

---

## The Website Is Doing Real Work

The public site at [arckit.org](https://arckit.org/) is also carrying more weight than I expected.

The latest Cloudflare export covers **30 May to 28 June 2026**. In that 30-day window the site served:

- **95,631 requests**
- **477 daily unique visitors on average**
- **858 daily unique visitors on the busiest day**, 28 June
- **11.31 GB total data served**
- **5.32 GB data cached**

Cloudflare's export reports unique visitors by day, not a deduplicated 30-day audience. So I am treating it as a daily attention signal, not a monthly user count. The useful point is the shape: the site is getting steady daily attention, not just a single launch spike.

That changes how I think about the docs. They are not just supporting material anymore. For many people they are the front door: what ArcKit is, which assistant it supports, which command to run first, which guide maps to their problem, and whether the project is serious enough to try.

The GitHub referrer data says the same thing. In the latest GitHub traffic window, `arckit.org` sent **243 views from 73 unique visitors** into the main repository. Google, GitHub, Medium and LinkedIn all sent traffic too, but the site is clearly part of the adoption path.

That makes the documentation site a product surface in its own right.

---

## People Are Searching for ArcKit by Name

The latest Google Search Console export was created on 29 June 2026. Its chart rows cover **15 May to 27 June 2026**.

Over that window, Google Search recorded:

- **764 clicks**
- **9,874 impressions**
- **7.74% click-through rate**
- **9.65 weighted average position**

The top query was `arckit`:

| Query | Clicks | Impressions | CTR | Position |
| --- | ---: | ---: | ---: | ---: |
| arckit | 426 | 1,943 | 21.92% | 1.9 |
| arc kit | 33 | 202 | 16.34% | 2.38 |
| arc-kit | 23 | 81 | 28.4% | 1.64 |
| archkit | 17 | 127 | 13.39% | 5.16 |
| arckit github | 15 | 222 | 6.76% | 3.58 |
| arckit ai | 12 | 19 | 63.16% | 1 |

That is another strange moment for a project that started as a personal tool: people are searching for it by name.

The home page captured most of those search clicks, with **703 clicks from 6,246 impressions**. The getting-started page had **42 clicks from 1,691 impressions**. Guides, articles, commands and use cases are showing up too, but the site still has work to do to help people move from "what is this?" to "I can use this on my project."

That is a good problem to have.

---

## It Has Travelled Further Than I Expected

ArcKit began with a strong UK public-sector centre of gravity. That is still visible: GDS, Technology Code of Practice, Green Book, Orange Book, NCSC CAF, Digital Marketplace, Service Standard, assurance, procurement and all the ceremony that real public-sector architecture has to survive.

But the search data is not only UK.

Top countries by search clicks in the latest Search Console export:

| Country | Clicks | Impressions | CTR | Position |
| --- | ---: | ---: | ---: | ---: |
| United Kingdom | 107 | 904 | 11.84% | 8.9 |
| United States | 84 | 3,814 | 2.2% | 14.41 |
| France | 81 | 298 | 27.18% | 3.87 |
| Australia | 48 | 299 | 16.05% | 5.07 |
| Netherlands | 45 | 397 | 11.34% | 5.35 |
| India | 39 | 360 | 10.83% | 8.72 |
| Germany | 38 | 616 | 6.17% | 4.57 |

That fits what ArcKit has become. The core method is general: make architecture decisions explicit, traceable and reviewable. The overlays make it local: UK, UAE, France, EU, Austria, Australia, Canada, USA and sector-specific variants.

The more people use it outside the original context, the more important that discipline becomes. ArcKit cannot just be a pile of clever prompts. It has to preserve structure, provenance, document control and judgement across jurisdictions and assistants.

---

## Why This Matters to Me

I care about enterprise architecture because I have seen how much public money and delivery time gets lost when decisions are vague, evidence is scattered, and governance arrives too late to change anything.

ArcKit was my attempt to make the boring but necessary work faster without making it sloppier.

The toolkit drafts. The architect judges.

That has always been the point. AI can help assemble the evidence, structure the artefacts, enforce naming, connect requirements to decisions, check traceability, and keep a project moving. It cannot carry the accountability. It cannot know the political context. It cannot decide what risk a department should accept. It cannot replace the judgement of someone who has to stand behind the recommendation.

So when I see clone activity, search demand and extension usage, I do not read it as "AI is replacing architects." I read it as architects, engineers, product people and delivery teams looking for a better way to do the work they already know matters.

That is the part I am grateful for.

---

## What Happens Next

I am going to keep building ArcKit in the open.

The next measurement layer will be cleaner because GA4 is now installed on the main site pages. That will help with page-level behaviour: which guides people read, where they drop out, which articles help, and whether the getting-started flow is doing its job.

But I do not want ArcKit to become telemetry-heavy. The public signals are enough for now:

- GitHub clone trends
- extension repository activity
- Search Console brand and non-brand queries
- Cloudflare site demand
- issues, pull requests and community contributions
- whether real practitioners keep finding value in the harness

The priority is still the same: make ArcKit useful.

Useful for the architect trying to get a messy programme under control.

Useful for the engineer who needs decisions written down.

Useful for the public servant who needs assurance evidence before a service assessment.

Useful for the small team that cannot afford a six-month consulting exercise just to understand what it is building.

Useful for me, still. And, unexpectedly, useful for many more people than I thought.

Thank you for that.

---

## Source Notes

Measurements in this article come from GitHub repository metadata and traffic APIs read on 29 June 2026, Cloudflare CSV exports in `data/` covering 30 May to 28 June 2026, and the Google Search Console export `arckit.org-Performance-on-Search-2026-06-29.zip`. GitHub traffic API data is limited to a short recent window. Cloudflare unique visitors are reported by day, not as a deduplicated 30-day audience. Search Console query tables can omit long-tail or anonymised queries, so query rows should not be treated as the complete set of search clicks.

---

*Published: 29 June 2026*
*Author: ArcKit Team*
*Tags: #usage #analytics #github #search-console #cloudflare #adoption*
