# Water Temperature: NOAA's Coastal Stations, Measured Live

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Water Temperature, a measured-ocean layer for Orbital Network, and sets out its use cases. The layer plots the latest measured water temperature at each station of NOAA's Center for Operational Oceanographic Products and Services (CO-OPS) that carries a water-temperature sensor — the actual instrument reading, its station, and its time — on the network's real-time globe. Every card shows the measured value in Fahrenheit and Celsius, the station's name and identifier, and the reading's own timestamp; a reading more than 24 hours old is labeled OUTDATED on its card, and on the layer's status line when the newest reading in hand has aged past that mark. The layer is live as of October 2026.

## What the layer shows

**CO-OPS measured water temperature.** When the layer is switched on, the page reads NOAA's station directory for stations carrying a water-temperature sensor, then reads each station's latest measured water-temperature value from NOAA's CO-OPS data service. Only readings NOAA actually returns are plotted — a station whose sensor is quiet simply has no marker. A marker's title gives the station name and state with its temperature; its card gives the measured value in both Fahrenheit and Celsius, the time NOAA measured it and how old that is, the station number, and the station's coordinates. The source line reads "NOAA CO-OPS water temperature · tidesandcurrents.noaa.gov," with the reading time repeated in it. While the layer stays on, the read repeats every 15 minutes, matching the stations' reporting rhythm.

**Measurements, labeled as such.** These are instrument readings at a sensor — typically at a tide station, on a pier or bulkhead, at the sensor's depth — not a modeled sea-surface temperature field and not a beach-wide average. Predictions play no part in this layer: nothing plotted is a forecast, an interpolation, or a satellite estimate.

**Provenance rules.** Every marker is bound to a named NOAA station and a stated measurement time. Freshness is judged against the reading's own timestamp, never the fetch: past 24 hours, the card opens with "OUTDATED" and the status line follows when the freshest reading available has aged out. If NOAA cannot be reached, the layer reports that and plots nothing. Temperatures are never invented.

## Use cases

**Swimmers, surfers, and beach families.** The difference between a bracing 58°F and a comfortable 74°F is the difference between wetsuits and trunks — measured at the named station nearest the beach, with its time, before anyone packs a bag.

**Anglers and divers.** Water temperature drives fish behavior and dive planning alike; a line of station readings along a coast shows the warm and cold pockets the catch — and the thermocline — follow.

**The coastal and naval communities.** Harbor users and small-boat operators get measured conditions at the stations NOAA maintains for exactly this purpose, useful beside the tide tables the same network publishes.

**Journalists and communicators.** During a marine heatwave or an unusual cold snap, "the station at ... measured ... at ..." is a citable fact from a named instrument, not a color on an unattributed map.

**Educators and citizen scientists.** A coastline of real instruments reporting on a rhythm students can watch — and a clean example of the difference between measuring something and modeling it.

## Coverage and limitations

Coverage is the source's own: the CO-OPS network is NOAA's coastal station network — the coasts of the US states and territories and the Great Lakes — plotted exactly where NOAA measures, and no wider coverage is claimed for it. A station reading describes the water at that sensor; conditions a mile away, at another depth, or after a wind shift can differ. Stations go quiet for maintenance and damage; when one does, its marker vanishes rather than going stale silently, and the readings that remain carry their ages on their cards. The layer is an awareness product, not a safety product: rip currents, water quality, and beach advisories come from local authorities.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
