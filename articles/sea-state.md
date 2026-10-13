# Sea State: Measured Ocean Conditions for the Naval Community and the Coastal Public

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Sea State, an ocean-conditions layer for Orbital Network, and sets out its use cases. Sea State plots live measurements from named public instruments — the moored buoy network of the NOAA National Data Buoy Center (NDBC) and the tide and current stations of the NOAA Center for Operational Oceanographic Products and Services (CO-OPS) — on the network's real-time globe. Every reading is a measurement from a named instrument at a stated time: wave height, wave period and direction, water temperature, wind, and barometric pressure from buoys; water level, tides, and currents from coastal stations. Consistent with the network's data-provenance rules, each card names its source and timestamp, data older than six hours is labeled outdated, and where no verified measurement exists, nothing is displayed. The layer is in development as of October 2026; this document records its design and intended uses ahead of release.

## What the layer measures

**Buoys (NDBC).** A network of moored buoys and coastal stations reports hourly or better: significant wave height, dominant and average wave period, mean wave direction, water temperature, wind speed and direction, and sea-level pressure. Tapping a buoy marker opens a card with the station's latest measured values, its name and identifier, and the observation time in UTC.

**Tides and currents (CO-OPS).** Coastal stations report measured water levels and currents. Readings are shown as measured values with station name and timestamp; tide predictions, where shown, are labeled as predictions and never presented as measurements.

**Provenance rules.** Sea State follows the same four rules as every Orbital Network layer: (1) every reading is bound to a named public source; (2) every reading carries its observation timestamp; (3) data older than six hours is labeled outdated; (4) the system fails closed — an unreachable feed or a silent instrument plots nothing rather than an estimate.

## Use cases

**Mariners and boaters.** Pre-departure go/no-go decisions from the nearest buoy's measured wave height and period; fishing and dive planning from water temperature and swell direction; inlet and bar awareness from tide and current timing at nearby stations.

**The naval community.** Harbor and nearshore units can check measured conditions — not only forecasts — before small-boat and training operations. Port arrival planning benefits from measured water levels and currents around tide windows.

**Families of sailors.** Sea State gives families a factual picture of the waters where a sailor is operating: measured wave height and water temperature off a named port or coastline, with a source and a time. It carries no vessel positions and no unit information.

**The coastal public.** Beach safety decisions informed by measured surf height and period, which drive rip-current risk; storm verification, as measured wave heights at named buoys provide ground truth during hurricanes and nor'easters; and early awareness of coastal flooding from measured water levels above predicted tides.

**Professional users.** Emergency managers gain timestamped, sourced measurements of surge and wave action for situation reports. Journalists gain citable facts ("buoy 41001 is recording 6-meter seas") rather than model estimates. Educators can show a storm's wave field evolving instrument by instrument.

## Coverage and limitations

Buoy coverage is densest along the coasts of North America and Europe and thinnest in the open Pacific and the Southern Ocean; the layer's coverage is correspondingly uneven, and the map shows that honestly — instruments appear where instruments exist. Instruments also fail, drift, and go silent for maintenance; the fail-closed rule means such stations simply disappear until they report again. Sea State is an awareness product. It is not a navigation product and does not replace official charts, forecasts, or notices to mariners, which remain authoritative for safety of navigation.

## Roadmap

Sea State is the first phase of a broader maritime program for Orbital Network. Later phases, in planned order, are: live civilian vessel traffic from public AIS sources, under the same provenance rules; maritime safety alerts, including piracy and security reporting; a shore-side port picture — because no single authoritative port-status source exists, Orbital Network will build that aggregation itself over time from port authorities and Coast Guard sources; and a family layer that packages measured conditions for named ports and operating areas in plain language.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
