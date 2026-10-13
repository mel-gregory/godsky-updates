# Wildlife: Recent Public Animal Observations on the Globe

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Wildlife, an animal-observations layer for Orbital Network, and sets out its use cases. Wildlife plots the most recent public, research-grade observations from iNaturalist — the citizen-science platform where naturalists and casual observers record the species they encounter — on the network's real-time globe. Each marker is an observation a person actually made and published: a species, a place, and a date. Consistent with the network's data-provenance rules, every card names its source, and data the page cannot honestly show is not shown: GPS collar studies whose owners permission their data, and a bird-sighting service that requires a personal key, are named in the layer's status line rather than approximated. The layer is live as of October 2026.

## What the layer shows

**iNaturalist observations.** When the layer is switched on, the page reads iNaturalist's public observations API for the most recent research-grade, mappable observations — sightings whose identification the iNaturalist community has corroborated and which carry coordinates their observers chose to publish — and plots up to 140 of them. A marker's title is the species' common name where one exists (its scientific name or the observer's identification otherwise); its card adds the place name and the date observed, and the source line reads "iNaturalist public observations · recent."

**What this is not.** These are sightings, not tracking. Nothing in the layer follows an individual animal: a marker says a person saw this species at this place on this date, and then the record ends. Movebank's GPS collar and tag studies — which do follow individuals — belong to the researchers who run them and are shared under study-by-study permission, so they are not plotted. eBird's sightings require each user to bring a free eBird API key, which a static page cannot hold for a visitor; the status line names both as "permission / free key needed, not plotted."

**Provenance rules.** Every plotted point is bound to the iNaturalist record it came from, with the observation's own date rather than the fetch time presented as its time. If the feed cannot be reached, the layer says so and plots nothing.

## Use cases

**Nature watchers and birders.** A living scatter of what people are actually seeing this season — migration arrivals, a rare butterfly two counties away — each point traceable to the public observation behind it.

**Families.** "What lives near us, and what have people seen lately?" A child can tap a marker near home and meet a species, a place, and a date — an invitation to go outside and add an observation of their own.

**Educators.** A classroom can watch observation density follow weekends, weather, and migration, and discuss why the map is thick near cities and thin in deserts — a first lesson in sampling bias, taught by the data itself.

**Journalists and conservation communicators.** A sudden cluster of sightings — an irruption of snowy owls, jellyfish washing up along a coast — is a story lead, each point citable to a public observation with a named observer community behind it.

**Researchers (awareness only).** The layer offers a quick qualitative sense of recent reporting activity. It is not an analysis tool and presents no abundances: iNaturalist observations record presence and effort by volunteers, never systematic counts.

## Coverage and limitations

Coverage is global in reach and uneven in fact: observations concentrate where people with phones and cameras go — near cities, trails, parks, and coasts — and thin out across oceans, deserts, and remote regions. Recency means the latest published observations, which can be hours to days old depending on observer activity; each card's date is the observation date, and nothing in the layer claims an animal is still there. Locations are plotted as iNaturalist publishes them, and iNaturalist itself coarsens or withholds exact coordinates for sensitive species — the layer inherits that protection and never sharpens it. Tapping the layer off and on re-reads the feed.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
