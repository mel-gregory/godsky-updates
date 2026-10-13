# Utilities & Water: Real-Time USGS Stream Gauges

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Utilities & Water, a hydrology layer for Orbital Network, and sets out its use cases. The layer plots real-time stream gauges from the United States Geological Survey's National Water Information System (NWIS) near wherever the visitor is looking: each marker is a working gauge on a real creek, river, or reservoir, carrying its latest measured discharge or gage height, with the reading's own time. The gauges are found around the globe's current center, so the layer follows the visitor anywhere the USGS network reaches. Electricity data that would complete the "utilities" name — EIA demand figures and PJM grid load — requires free registration keys a static page cannot hold, and is named in the layer's status line rather than invented. The layer is live as of October 2026.

## What the layer shows

**USGS instantaneous values.** When the layer is switched on, the page queries the USGS water-services API for gauges inside a window around the globe's current view center, requesting the two classic stream measurements — discharge (flow, parameter 00060) and gage height (stage, parameter 00065) — and plots up to 180 sites. Each marker's title is the gauge's official site name; its card gives the variable measured, the latest value and unit exactly as the service returns them, and the reading's date and time, under the source line "USGS NWIS real-time water data · live." If no view center is known, the read falls back to a Mid-Atlantic set of states (Maryland, the District of Columbia, Virginia, Pennsylvania, West Virginia, Delaware). Spinning the globe to a new place and tapping the layer off and on reloads the gauges for that place.

**What is deliberately absent.** Electricity demand (EIA) and grid load (PJM) both publish through free-but-registered APIs: the key belongs to an account holder, and a static page cannot hold it for a visitor. The layer names them — "EIA electricity + PJM grid load: free key needed, not plotted" — and shows no power data rather than estimating any. The layer also shows no water-quality data; a gauge measures the river's flow and height, not its chemistry.

**Provenance rules.** Every marker is bound to a USGS site and a timestamped reading, shown on the card. A gauge that has stopped reporting returns no current value and gets no marker. If the service cannot be reached, the layer reports that and plots nothing.

## Use cases

**River communities and flood awareness.** During heavy rain, the question "how high is the creek, and how fast is it rising" is answered by the gauge upstream with a value and a time — measured ground truth beside the forecast, from the agency that operates the national gauge network.

**Paddlers, anglers, and boaters.** Runnable water is a flow number: discharge and stage at the named gauge on the named river decide a put-in, a wading day, or a stay-home call.

**Farmers and water managers (awareness).** A regional read on streamflow during drought or deluge — the gauges farmers' and districts' own reports also cite — visible in one view around the land in question.

**Journalists.** During floods, "the gauge at ... read ... feet at ..." is the standard, citable measurement; this layer puts the nearest gauges on a globe with their readings attached.

**Educators.** The national gauge network is one of the great public instruments: thousands of unattended stations reporting a physical quantity on a rhythm. A class can watch a storm's runoff move down a watershed gauge by gauge.

## Coverage and limitations

The USGS network covers the United States and its territories, and the layer says so rather than dressing a national network as a global one: outside that footprint, the window around the globe's center returns few or no gauges, and the status line explains why. Only sites reporting a current value plot, so a silent or decommissioned gauge is absent rather than stale. Values are the service's provisional real-time data, as USGS publishes them — measurements subject to later revision, presented with their times so their freshness is judgeable. The layer reads on tap, not continuously; during a fast-rising flood, official USGS and National Weather Service channels remain the live source, and this layer is an awareness view of them.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
