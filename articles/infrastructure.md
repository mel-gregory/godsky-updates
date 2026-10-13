# Roads & Bridges: Mapped Bridges and Disaster-Impact Alerts Near Where You Look

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Roads & Bridges, an infrastructure layer for Orbital Network, and sets out its use cases. The layer answers two questions about the place the visitor is looking at: what bridges are mapped there, and what severe-weather disaster-impact alerts are active there. Bridges come from OpenStreetMap's volunteer-mapped road network, read around the globe's current center; alerts come live from the National Weather Service's active-alerts service, plotted at the centers of their warning polygons. The layer is equally explicit about the famous dataset it does not show: bridge condition ratings live in the National Bridge Inventory, a bulk federal file rather than a live point feed, and are named as such instead of being attached to bridges the file never geocoded for this page. The layer is live as of October 2026.

## What the layer shows

**Mapped bridges around the view.** When the layer is switched on, the page asks the OpenStreetMap Overpass service for ways tagged as bridges within 300 kilometres of the globe's current center (up to 90 in the read) and plots each at its mapped center. A marker's title is the bridge's mapped name, or simply "Bridge" where the map carries none; its card says what road it carries where OpenStreetMap records one, and that it is a mapped bridge near the globe's current center. The source line credits OpenStreetMap bridge mapping and notes the National Bridge Inventory's bulk-file status.

**Active NWS alerts.** In the same read, the page takes the National Weather Service's currently active alerts and updates — the live national list, capped at the service's first hundred — and plots each alert that carries a polygon at that polygon's center point. The card names the event (a flood warning, a tornado watch, and so on), the area description, and the severity where the alert carries one, under the source line "NOAA / National Weather Service active alerts · live." Together the layer holds up to 150 points. Spinning the globe and re-tapping reloads both halves for the new view.

**What the markers do not claim.** A bridge marker claims a bridge exists there in the map — nothing about its condition, load rating, age, or safety, because the page does not hold that data and says so. An alert marker sits at the center of a warning polygon; the warned area is the polygon, which can be far larger than the marker's neighborhood, and the card's area description is the authority, not the dot.

**Provenance rules.** Every point names its source — OpenStreetMap mapping or the National Weather Service — on its card. If both services are unreachable, the layer reports that and plots nothing; if one answers, its half still plots.

## Use cases

**Travelers and road-trippers.** Crossing a region means crossing its bridges; seeing them mapped around the route — and seeing an active flood or storm alert plotted in the same view — is trip context from named sources.

**Local journalists.** During a storm, the pairing is the story's skeleton: the warning in force, and the crossings inside it. Each half cites its own source — the Weather Service for the alert, the map for the bridge.

**Emergency managers (awareness).** A quick orientation view: warned polygons' centers against the mapped crossing points near them, before turning to operational systems for the full polygons and road status.

**Infrastructure watchers and civic technologists.** An honest demonstration of what open data does and does not carry: the world's volunteers have mapped where the bridges are; the federal condition file exists but ships as a bulk download, and this page says so instead of faking a join it has not done.

**Educators.** A two-source layer is a clean lesson in data provenance — one point from a crowd-mapped database, one from a federal live service, each labeled, neither pretending to be the other.

## Coverage and limitations

Bridge coverage is OpenStreetMap's coverage: superb in much of Europe and North America, patchier elsewhere, and the 300-kilometre read around the current view means the layer is always local to where the visitor is looking — spin and re-tap to move it. Alert coverage is the National Weather Service's: the United States and its territories, and only alerts carrying polygons plot as points. The hundred-alert read can truncate the list on a major outbreak day. Nothing in the layer reports bridge condition, closures, or inspections; for those, state DOTs and the National Bridge Inventory itself are the sources, and the layer names the Inventory rather than impersonating it.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*

Zenodo DOI: [10.5281/zenodo.23336788](https://doi.org/10.5281/zenodo.23336788).
