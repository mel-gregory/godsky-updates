# Traffic: Road Incidents and Closures from Open Agency Feeds

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Traffic, a road-conditions layer for Orbital Network, and sets out its use cases. Traffic plots live road incidents and construction closures from Ontario 511, the Ontario Ministry of Transportation's open traveller-information service, on the network's real-time globe. Each marker is an event the agency itself is publishing — a collision, a closure, a construction zone — shown with the roadway, the event type, and the agency's own description. Consistent with the network's data-provenance rules, every card names its source, and where no agency publishes openly, nothing is plotted: commercial traffic-flow feeds and ship positions that require their own keys are named in the layer's status line rather than simulated. The layer is live as of October 2026.

## What the layer shows

**Ontario 511 incidents and construction.** When the layer is switched on, the page reads Ontario 511's two open feeds — current events and construction — and plots each mappable event (up to 140) at the latitude and longitude the agency publishes for it. A marker's title names the roadway and event type; its card carries the agency's description or headline, the direction of travel where the feed gives one, and the source line "Ontario 511 DOT · live incident feed." These are reported incidents and closures, not traffic speeds: the layer shows where something has happened or a road is closed, not how fast traffic is moving.

**What is deliberately absent.** TomTom and HERE traffic-flow data and AIS ship positions are not plotted. Those services give every user their own free key, and a static web page cannot hold a key on the visitor's behalf; the layer's status line names them as "free key needed, not plotted" instead of dressing other data up as theirs.

**Provenance rules.** Traffic follows the same rules as every Orbital Network layer: every reading is bound to a named public source; the card shows what the source published; and the system fails closed — if the 511 feeds cannot be reached, the layer reports that and plots nothing rather than estimating road conditions.

## Use cases

**Drivers and commuters in Ontario.** A closure or collision on a planned route is visible before departure, in the agency's own words, instead of being discovered at the ramp.

**Road-trippers and families.** On a long drive day, a glance at the globe shows whether the corridor ahead carries active closures or construction, and the card's direction field tells whether it affects the way the family is travelling.

**Emergency managers and road agencies.** A regional picture of concurrent incidents and closures, timestamped by the publishing agency, complements official dashboards — awareness, not a replacement for them.

**Journalists.** A reported closure is citable to the DOT feed that published it, with the agency's description intact, rather than paraphrased from a scanner or a social post.

**Educators.** The layer is a clean demonstration of open government data: one province publishing machine-readable road events that any citizen's page can plot the moment they are issued.

## Coverage and limitations

Coverage today is Ontario, because Ontario 511 is the road feed the page reads openly and keylessly; the layer claims no other geography. Most other road data is either commercial, key-gated per user, or published in formats a static page cannot hold a credential for — those sources are named in the status line, never faked. The layer shows incidents and closures only: it carries no speed, congestion, or travel-time data, and an empty map means the feed reported no mappable events, not that every road is clear. Events appear and clear on the agency's schedule; tapping the layer off and on re-reads the feeds.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*

Zenodo DOI: [10.5281/zenodo.23336357](https://doi.org/10.5281/zenodo.23336357).
