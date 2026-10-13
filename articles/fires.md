# Active Fires: Wildfire Events Tracked by NASA EONET

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Active Fires, a wildfire layer for Orbital Network, and sets out its use cases. The layer plots the open wildfire events tracked by NASA's Earth Observatory Natural Event Tracker (EONET) — the agency's curated register of ongoing natural events — on the network's real-time globe. Each marker stands at an event's most recently reported location and carries its name, when it was last reported, and its reported magnitude where EONET publishes one. Consistent with the network's data-provenance rules, the layer is explicit about what it is not: it plots tracked events, not individual satellite fire detections — the detection-point service, NASA FIRMS, runs on a free per-user key a static page cannot hold, and is named rather than imitated. The layer is live as of October 2026.

## What the layer shows

**EONET wildfire events.** When the layer is switched on, the page reads EONET's open wildfire category — events still open, over the last 30 days — and plots each event (up to 220) at its latest reported geometry. A marker's title is the event's name as EONET carries it; its card gives the date and time of the latest report, the event's magnitude value and unit where the register publishes one (burned area, for fires so tracked), and the upstream sources EONET lists for the event. The source line reads "NASA EONET wildfire events," with those upstream sources named.

**Events, not detections.** A satellite detection is a single overheard pixel at a single overpass; an EONET event is a fire that NASA's trackers are following as a thing with a name and a history. This layer shows the second. NASA FIRMS publishes the first — near-real-time detection points from MODIS and VIIRS — but its point feed is keyed to each user's free FIRMS MAP_KEY, which this page cannot hold on a visitor's behalf; the layer and its status line say so plainly ("FIRMS' own point feed needs FIRMS' free MAP_KEY") rather than presenting EONET events as FIRMS detections.

**Provenance rules.** Every marker is bound to an EONET event and its latest report time, both shown on the card. If EONET cannot be reached, the layer reports that and plots nothing. A fire EONET has closed leaves the map on the next read.

## Use cases

**Residents of fire country.** Which named fires are burning within reach of home, and when each was last reported — a situation picture that complements, and never replaces, the local fire authority's evacuation notices.

**Journalists.** A named incident with a last-reported time and a tracked magnitude, citable to NASA's event register — the skeleton of a fire story, distinguished honestly from the detection maps other outlets publish.

**Land and park managers (awareness).** A regional register of concurrent incidents for orientation before turning to operational systems, with each event's upstream source named for follow-up.

**Families.** When smoke is in the air or a fire is in the news near relatives, a marker with a name and a report time answers "is it still being tracked, and where" from the register itself.

**Educators.** The difference between an event and a detection — between a fire as a continuing thing and a satellite's momentary glimpse of heat — is itself a teachable idea, and this layer, read beside a detection map, teaches it.

## Coverage and limitations

EONET is a curated register, not a sensor: events enter it when NASA's trackers add them and leave when they are closed, so a small or fast-moving fire can burn without appearing, and an event's position is its latest reported point — a point, not a perimeter. Nothing here shows fire fronts, containment, or spread. Reporting cadence varies by event and by the upstream sources EONET draws on, and the card's report time is the honest freshness measure. For per-detection, near-real-time fire points, FIRMS is the right service and the layer names it; for life-safety decisions, local fire authorities and official alert systems govern.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
