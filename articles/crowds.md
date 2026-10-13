# Crowds & Gatherings: Protest and Gathering Signals from the World's News

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Crowds & Gatherings, a public-events layer for Orbital Network, and sets out its use cases. The layer plots gathering signals from GDELT, the Global Database of Events, Language, and Tone, which monitors the world's news media and codes reported events to the places they name. When news coverage reports a protest, demonstration, or rally at a place, GDELT's geographic feed carries a point for it, and this layer plots those points from the last 24 hours on the network's real-time globe. Consistent with the network's data-provenance rules, every card names its source and describes the point as what it is — a news-reported event location — never as a measured crowd. Scheduled-event listings that require their own keys are named in the layer's status line rather than filled in from other data. The layer is live as of October 2026.

## What the layer shows

**GDELT gathering signals.** When the layer is switched on, the page queries GDELT's open GEO API for items matching "protest OR demonstration OR rally" in point-data form over a 24-hour timespan, and plots up to 120 of the returned points at the coordinates GDELT itself attached to them. A marker's title is the place name from the feed; its card states how many times the event was reported in the last 24 hours, as coded by GDELT, and the source line reads "GDELT GEO · protests & gatherings, last 24h." Only signals that arrive carrying real coordinates are plotted — a report whose location GDELT could not place never becomes a guessed pin.

**What a signal means, and does not.** A point means news media reported a gathering at that place within the last day. It is not a headcount, not a crowd-size estimate, and not confirmation that a gathering is still underway; the layer measures media reporting about gatherings, and says so. Scheduled future events are a different kind of data: Eventbrite and Ticketmaster listings require each user to bring a free API key, which a static page cannot hold on a visitor's behalf, so they are named in the status line as "free key needed, not plotted."

**Provenance rules.** Every point is bound to the GDELT record behind it, with the 24-hour reporting window stated on the card. If the feed cannot be reached, the layer reports that and plots nothing.

## Use cases

**Journalists.** A same-day world map of where demonstrations are being reported — a starting point for assignment decisions, with each point traceable to the news-coded record that produced it.

**Travelers and families.** Before a trip or a downtown visit, a check of whether large gatherings are being reported near the destination — context for planning a route or a day, drawn from published reporting rather than rumor.

**Researchers and students of public life.** A qualitative sense of where protest activity is being reported on a given day, suitable for forming questions — and a clear example of media-derived data, whose strengths and biases can be discussed openly.

**Event-aware businesses and venues.** Awareness that a gathering is being reported nearby today, in time to plan staffing, deliveries, and access around it.

**The general public.** A calmer way to learn "something is happening in my city" — a sourced signal on a map, with the reporting count visible, instead of an unsourced claim moving through a feed.

## Coverage and limitations

Coverage follows the world's news media, not the world's gatherings: places with heavy press coverage produce more signals, and gatherings that no outlet reports do not appear at all. GDELT's coding is automated — it reads news text and attaches places — so a point can reflect a planned, past, or mis-geocoded event; the card's wording ("reported ... by GDELT-coded news") is the honest description, and the layer never upgrades a signal into a verified crowd. The 24-hour window is the feed's own; tapping the layer off and on re-reads it. Nothing in the layer identifies individuals, and no scheduled-event data is shown without its key.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*

Zenodo DOI: [10.5281/zenodo.23336655](https://doi.org/10.5281/zenodo.23336655).
