# Clouds: NOAA GOES-19 GeoColor over the Americas

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Clouds, an imagery layer for Orbital Network, and sets out its use cases. Unlike the network's point layers, Clouds paints no markers: it drapes the newest full-disc photograph from NOAA's GOES-19 (GOES-East) geostationary satellite — its ABI instrument's GeoColor product, served by NOAA NESDIS — over the globe as a translucent shell, so the clouds on the planet are the clouds the satellite is actually seeing. The imagery's own scan time is named in the layer's status line, and a frame more than six hours old is labeled OUTDATED. The layer refreshes every ten minutes while it is on, matching GOES-East's full-disc scan cadence. It is imagery — a picture of the sky, not measurements at points — and is described as exactly that. The layer is live as of October 2026.

## What the layer shows

**GOES-19 GeoColor, reprojected in the browser.** When the layer is switched on, the page reads NOAA's public GOES-19 directory for the newest ABI full-disc GeoColor frame, then redraws that photograph — taken from the satellite's fixed slot above 75.2°W — onto the globe's surface in the visitor's own browser, point by point. Places beyond the satellite's horizon stay clear; near-black night pixels become transparency, so the dark half of the disc never punches a black wedge through the planet. The result is a living cloud shell distinct from the globe's own backdrop portrait: this is the current sky, dated.

**Time, named and enforced.** Freshness is judged against the frame's own scan time — the timestamp in NOAA's filename — never against when the page fetched it. The status line names that time and the frame's age ("about 40 min old"); past six hours it leads with "OUTDATED" and advises treating the picture as the last known sky, not the current one. While the layer is on, a new frame is read every ten minutes, GOES-East's own full-disc rhythm. If NOAA's directory or frame cannot be reached, the layer reports the feed as unreachable and plots nothing — clouds are never invented to fill a gap.

**What GeoColor is.** GeoColor is NOAA's composite view of the Earth from ABI's channels, made to read the way a photograph reads — clouds, land, and ocean in natural-looking color by day. It is an image product, not a measurement series: the layer shows no temperatures, no cloud-top heights, no per-point values, and a tapped globe under this layer gives the imagery's time and source, not a reading.

## Use cases

**Weather watchers.** The day's actual cloud architecture — a hurricane's spiral, a front's long comma, a clear slot opening over a launch coast — seen as the satellite sees it, with the scan time printed on it.

**Families.** "Show me the clouds over Grandma's house right now" is a question this layer answers with a dated photograph rather than a forecast icon — and the date is part of the answer, taught by the status line itself.

**Journalists.** A storm visual whose provenance can be stated in one line — instrument, satellite, agency, scan time — instead of the unattributed satellite grabs that circulate during hurricanes.

**Educators.** Geostationary geometry made visible: why one satellite sees one disc, why the night side goes transparent, why the picture updates on a ten-minute heartbeat. The reprojection happening in the student's own browser is itself the lesson.

**Storm and fire awareness (context).** Beside the Storms layer's advisory markers, the cloud shell shows the system those advisories describe; beside the fire layer, smoke plumes can sometimes be seen in the same frame — context imagery, clearly labeled as imagery, under the sourced points.

## Coverage and limitations

Coverage is the GOES-East disc: the Americas, the Atlantic, and the Caribbean, from one satellite's vantage — the Pacific, Asia, Europe, and Africa are outside this frame, and the layer claims nothing there. Resolution is the published GeoColor frame's; reprojection onto the globe resamples it, so fine cloud detail softens, especially near the disc's edge where the satellite's view grazes. GeoColor is a composite that reads like a photograph; at night the product is not a true visible-light picture, and this layer's handling of the dark side (transparency for near-black pixels) is a display choice, stated openly. The layer is imagery for awareness — forecasts, warnings, and measurements live in the network's other layers and at NOAA.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*

Zenodo DOI: [10.5281/zenodo.23335921](https://doi.org/10.5281/zenodo.23335921).
