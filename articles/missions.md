# Space Missions: Recent and Upcoming Launches at Their Pads

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Space Missions, a launch-catalog layer for Orbital Network, and sets out its use cases. The layer plots recent and upcoming rocket launches at their launch pads, from Launch Library 2, the community-maintained launch database operated by The Space Devs. Each marker carries what the database publishes for that launch: the mission, the rocket, the date — labeled NET for upcoming launches, because a NET ("No Earlier Than") date is a target, not a promise — its status, and its place. Consistent with the network's data-provenance rules, every card names Launch Library 2 as its source, and the layer's status line repeats the database's own caution: launches slip. The layer is live as of October 2026.

## What the layer shows

**Launches at their pads.** When the layer is switched on, the page reads Launch Library 2's previous-launches and upcoming-launches lists (fourteen of each) and plots every launch whose pad carries coordinates — up to 160 markers — at the pad itself, not the agency's headquarters or the mission's destination. A marker's title is the launch's name as the database carries it; its card adds the rocket configuration, the date (with "NET" prefixed for upcoming launches), the published status abbreviation, and the pad's location name. The source line reads "Launch Library 2 · The Space Devs."

**Targets versus history.** The two halves of the layer are different kinds of fact and are worded differently. A previous launch's date is history as the database records it. An upcoming launch's NET date is the earliest the provider currently targets; weather, range, and hardware move these dates constantly, and the layer repeats the caveat in its own status line ("NET dates are published targets — launches slip") rather than letting a plotted date read as a commitment. Statuses come from the database as published; the layer adds no countdown, no probability, and no telemetry.

**Provenance rules.** Every marker is bound to a Launch Library 2 record, named on the card. Launches without pad coordinates are not placed at guessed locations. If the database cannot be reached, the layer reports that and plots nothing.

## Use cases

**Space-coast communities and viewing families.** Which pad, which rocket, NET when — the starting facts for planning a trip to watch a launch, held with the honest warning that the date can move, because with launches it so often does.

**Educators.** A globe of working spaceports — Florida, Virginia, California, Kazakhstan, French Guiana, New Zealand, and more — with the year's cadence visible in one view: who launches, from where, how often.

**Journalists.** A dated, sourced skeleton for launch coverage — mission, vehicle, pad, status — citable to the database the whole community maintains, with NET language intact for anything not yet flown.

**Space enthusiasts.** Recent history and the near future on one globe: the last fortnight's launches beside the next fortnight's targets, a cadence picture no single agency's page assembles.

**Travelers.** A launch near a planned trip is a genuine possibility worth knowing about — at NET value, which is to say with a flexible plan.

## Coverage and limitations

Coverage is Launch Library 2's coverage: comprehensive for orbital launches worldwide and for the suborbital flights the database tracks, dependent on its volunteer-maintained records being current. Only launches with pad coordinates plot. NET dates are targets as of the read; the layer refreshes when re-tapped, so a slip announced an hour ago appears on the next read, not retroactively. Nothing here is a launch provider's official manifest — providers and ranges remain authoritative — and the layer tracks no flight in progress.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
