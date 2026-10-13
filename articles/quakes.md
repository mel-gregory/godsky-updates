# Earthquakes: The USGS Feed, Magnitude 2.5 and Up

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Earthquakes, a seismic layer for Orbital Network, and sets out its use cases. The layer plots every earthquake of magnitude 2.5 and above recorded in the last 24 hours in the United States Geological Survey's public GeoJSON summary feed, on the network's real-time globe. Each marker is sized by magnitude and carries the Survey's own account of the event: its magnitude, depth, location name, and time, plus the feed's tsunami flag where one is raised. Consistent with the network's data-provenance rules, every card names the USGS as its source and shows the event's own time rather than the fetch time. The layer is live as of October 2026.

## What the layer shows

**USGS earthquakes, last 24 hours.** When the layer is switched on, the page reads the USGS summary feed for magnitude 2.5+ events over the past day and plots them — up to 300, largest first, so the most significant events are never crowded out by the smallest. Marker size grows with magnitude. A marker's title is the USGS place description ("12 km SSE of ..."), and its card lists the magnitude, the depth in kilometres, the event time in UTC, and "tsunami flag raised" when the feed carries that flag. The source line reads "USGS earthquake feed · magnitude 2.5+, last 24 hours."

**What the numbers are.** Magnitudes, depths, and locations are the USGS's published solutions for each event. Seismic solutions are revised as more station data arrives — an event's magnitude or depth can change after it first appears — and the layer shows the feed as published at the moment it is read, neither freezing the first estimate nor presenting any value as final.

**Provenance rules.** Every marker is bound to a USGS event, with the event's own timestamp on the card. If the feed cannot be reached, the layer reports that and plots nothing; an empty globe under this layer means the feed reported no qualifying events, and the status line says which of those happened.

## Use cases

**Residents of seismic regions.** A same-day picture of the ground's activity near home — whether the jolt felt an hour ago was local or distant, large or small — answered by the agency charged with measuring it.

**Families with members in quake country.** After news of an earthquake, a marker with a magnitude, a depth, and a time replaces rumor with the Survey's account, within the hour it is published.

**Journalists.** Magnitude, depth, place, and time, citable to the USGS feed directly — the standard first facts of any earthquake story, visible in one view alongside every other event of the day for scale.

**Educators.** A day of global seismicity makes plate boundaries visible without a diagram: the ring of fire draws itself. Students can compare depth and magnitude across subduction zones and mid-ocean ridges from real events.

**Travelers.** A quick check of recent activity at a destination — an aftershock sequence still running, a volcano-adjacent swarm — as one input among official advisories.

## Coverage and limitations

The feed is global, but detection is not uniform: the worldwide network reliably catches magnitude 2.5 events in well-instrumented regions (the United States, Japan, Europe) while an event of the same size under an ocean or a sparsely instrumented continent may be recorded late, at a higher threshold, or by regional solutions the summary feed carries differently. Events below magnitude 2.5 — the great majority of the planet's earthquakes — are excluded by the layer's stated threshold, so a quiet map never means a motionless Earth. The layer reads the feed when tapped; it is an awareness view, not an alerting service, and official channels (USGS ENS, local authorities) remain the source for warnings and safety guidance.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*

Zenodo DOI: [10.5281/zenodo.23335777](https://doi.org/10.5281/zenodo.23335777).
