# Storms: Tropical Cyclones Worldwide, Advisory by Advisory

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Storms, a tropical-cyclone layer for Orbital Network, and sets out its use cases. The layer plots every tropical cyclone that NOAA's National Hurricane Center (NHC) is issuing advisories on — in the Atlantic and the eastern and central Pacific — together with cyclones in the world's other basins republished by GDACS, the Global Disaster Alert and Coordination System, which carries the NHC and Joint Typhoon Warning Center (JTWC) advisories NHC does not issue itself. Each marker carries the advisory's own numbers: classification, sustained winds, central pressure, movement, and the advisory's number and age. A storm inside roughly its first 48 hours of advisories is badged NEW and pulses. An advisory more than six hours old is labeled OUTDATED on its card. The layer is live as of October 2026.

## What the layer shows

**NHC advisories, plotted as issued.** When the layer is switched on, the page reads NHC's CurrentStorms feed (reached through the network's relay, because NHC serves no browser-readable copy directly) and plots each active system at the position its latest advisory reports. The card gives the classification in words — Tropical Storm, Hurricane with its Saffir-Simpson category — maximum sustained winds in miles per hour and knots, minimum pressure in millibars where the advisory carries one, movement direction and speed (or "nearly stationary"), the advisory number, when it was issued and how old it is, and a link to the live advisory on nhc.noaa.gov. While the layer stays on, the read repeats every 15 minutes, matching NHC's advisory cadence of every six hours (more often near landfall).

**Freshness, enforced in the open.** Storm positions are only as current as the newest advisory. The layer judges freshness against each advisory's issuance time, never the fetch: an advisory older than six hours opens with "OUTDATED ADVISORY" on its card and the numbers are introduced as the last known, not current; if the newest advisory in hand is old, the status line says so too. Systems on advisory number 8 or lower — at NHC's six-hourly pace, inside about their first 48 hours of advisories — carry a pulsing NEW badge.

**Other basins, and disturbances.** Cyclones outside NHC's basins arrive via GDACS, which republishes NHC and JTWC reporting; duplicates of an NHC-plotted storm are suppressed, and GDACS cards say what GDACS is. Separately, NHC's Tropical Weather Outlook names disturbances with a high formation chance as written areas with no coordinates; the layer names them in its status line, with their formation percentages, and never pins them at a guessed spot. The layer plots where each system is per its latest advisory — it does not draw forecast tracks or cones, which live in the advisories themselves, one tap away through the card's link.

**Provenance rules.** Every marker is bound to a named advisory from a named center, with issuance time and age on the card. If neither NHC nor GDACS can be reached, the layer reports that and plots nothing.

## Use cases

**Coastal residents in storm paths.** Which system, how strong, moving which way, and how fresh that knowledge is — the advisories' own facts, with staleness labeled instead of hidden, for household decisions made alongside official evacuation guidance.

**Mariners and the naval community.** A worldwide cyclone picture — including the western Pacific and Indian Ocean basins a Pacific crossing actually meets — from the agencies issuing the warnings mariners already trust.

**Emergency managers.** A single view of every active system with advisory numbers and ages, useful for spotting the stale read in a stack of situation reports.

**Journalists.** Classification, winds, pressure, and movement citable to the specific advisory, plus one-tap access to its full text — and an honest "last known" label when NHC has not yet posted a newer one.

**Families.** When a storm is in the headlines near a relative's coast, the card answers "how strong is it, really, and as of when" from the advisory rather than from the loudest post in a feed.

## Coverage and limitations

NHC's own coverage is the Atlantic and the eastern and central North Pacific; everywhere else the layer depends on GDACS's republication of JTWC and NHC material, a secondary path that can lag or thin out, and the cards say GDACS when GDACS is the source. Positions are advisory-time positions of moving systems — between advisories a storm has travelled, and the card's stated age is the honest measure of that gap. Intensity figures are the issuing centers' estimates, chiefly from satellite analysis for systems without aircraft reconnaissance. This layer is an awareness view of official advisories; warnings, watches, and evacuation orders come from NHC and local authorities, and nothing here replaces them.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
