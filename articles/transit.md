# Mass Transit: Live Vehicle Positions from Open Agency Feeds

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Mass Transit, a public-transport layer for Orbital Network, and sets out its use cases. The layer plots live vehicle positions published openly by a transit agency — today, the Massachusetts Bay Transportation Authority (MBTA), whose public API streams the positions of Boston-area buses, trains, and ferries without a key. Each marker is a vehicle the agency is reporting right now, carrying its route, its status, its direction, and its speed where the feed provides them. Consistent with the network's data-provenance rules, every card names the publishing agency, and the many transit feeds that require a free developer key — most GTFS Realtime feeds worldwide, WMATA included — are named in the layer's status line rather than simulated. The layer is live as of October 2026.

## What the layer shows

**MBTA vehicle positions.** When the layer is switched on, the page reads the MBTA's public vehicles API and plots up to 170 vehicles at the latitude and longitude the agency reports for each. A marker's title names the route — the Red Line, a numbered bus route — and its card shows what the feed says about that vehicle: its current status (for example, stopped at a station or in transit), its direction, and its speed converted to miles per hour where the agency reports one. The source line reads "MBTA live vehicle positions · GTFS-family agency feed." The positions are the agency's own reports, drawn as they arrive; the page adds nothing to them.

**What is deliberately absent.** Most of the world's realtime transit data flows through GTFS Realtime feeds that require a free developer key issued to an individual — WMATA's included. A static web page cannot hold such a key for a visitor, so those systems are not plotted; the status line names them as "free developer key needed, not plotted." Nothing about their absence is filled in with estimates or schedules dressed as live positions.

**Provenance rules.** Every marker is bound to the agency feed behind it, named on the card. If the feed cannot be reached, the layer reports that and plots nothing — a vehicle never appears where the agency did not just say it is.

## Use cases

**Boston-area riders.** A system-level picture — where the fleet actually is this minute — that complements a stop-level arrival app: bunching, gaps, and a stalled line read at a glance.

**Families.** A parent can show a child "your train, right now, on the planet" — a real vehicle, on a real route, reported by the agency itself. It turns an abstract network into something a kid can watch move.

**Transit advocates and planners (awareness).** A public window onto operations as published: how much of the fleet is out, where it clusters. The layer is a view, not an operations console, and presents the feed as the agency publishes it, errors and all.

**Journalists.** During a disruption, the difference between "the agency says service is suspended" and "here is where its vehicles actually are" is visible and citable to the agency's own feed.

**Educators.** A working example of GTFS-family open data — the standard feeds agencies publish — and of why some systems can appear on a page like this keylessly while others, by their key terms, cannot.

## Coverage and limitations

Coverage today is the MBTA service area — greater Boston — because the MBTA is the agency whose realtime positions the page can read openly without a credential. The layer claims no other city. Positions refresh when the layer is re-tapped (a fresh read is used for four minutes), so the picture is as current as the last tap, not a continuous dispatch display; speeds and statuses appear only where the agency's feed reports them, and a vehicle whose transponder is silent simply has no marker. For catching an actual train, the agency's own arrival predictions remain the right tool — this layer shows the fleet, not countdowns.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
