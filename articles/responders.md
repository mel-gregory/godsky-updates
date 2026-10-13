# First Responders: Fire, Police, EMS and Hospital Locations

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes First Responders, a public-safety geography layer for Orbital Network, and sets out its use cases. The layer plots the locations of fire stations, police stations, hospitals, and clinics around whatever place the visitor is looking at, drawn from OpenStreetMap's worldwide mapping of the same facilities that federal structure datasets — the US HIFLD and USGS sets — publish for the United States. The layer's discipline is stated on every card: these are station locations. Live vehicle positions are not public, and local incident feeds exist only where a locality publishes one, so the layer shows where help is based — never where a truck is, and never an emergency in progress it cannot source. It is a geography layer, not an emergency tool; in an emergency, call 911 (or the local emergency number). The layer is live as of October 2026.

## What the layer shows

**Stations and hospitals around the view.** When the layer is switched on, the page asks the OpenStreetMap Overpass service for fire stations, police stations, hospitals, and clinics within 180 kilometres of the globe's current center, and plots up to 160 of them. A marker's title is the facility's mapped name, or its kind where the map carries no name; its card gives the kind in words — Fire station, Police station, Hospital, Clinic / EMS care — the city where the map records one, and the sentence "Station location — live vehicle positions are not public." The source line reads "Station locations · OpenStreetMap mapping of HIFLD/USGS-published facilities." Spinning the globe to a city and tapping the layer loads that city's stations; the layer is always centered on where the visitor is looking.

**What is deliberately absent.** No incident dots, no unit tracking, no "live calls" — because no such public feeds exist at this scope, and the layer refuses to imply otherwise. County and city incident feeds exist where a locality publishes one; they are local, not global, and this layer does not pretend to aggregate them. The word "responders" in the layer's name refers to the services whose stations these are, and every card repeats the limit in plain words.

**Provenance rules.** Every marker is bound to a mapped facility record, with its source named on the card. If the mapping service cannot be reached, the layer reports that and plots nothing. A place with no markers means the map carries no such facilities within reach — OpenStreetMap's coverage, honestly shown — not that no help exists there.

## Use cases

**Newcomers and travelers.** The first geography of a new city: where the hospital is, where the fire and police stations sit relative to home, school, or hotel — learned calmly, before the day anyone needs them.

**Families.** A parent can show a child the stations in their own town and talk about what each is for — safety education on a globe the child can spin to their own street's city, with every location traceable to the public map.

**Journalists (context).** During an incident story, the distance from a scene to the responding station or the receiving hospital is checkable context from the same public geography — stated as location, never dressed as response data.

**Emergency-preparedness educators.** Station geography is the static half of preparedness — where the infrastructure of help stands — and the layer teaches it alongside an explicit lesson in its limits: a mapped station is not a promised response time.

**Event and venue planners (awareness).** The nearest hospital and stations to a venue, for the logistics binder — orientation from public mapping, verified against local knowledge before it is relied on.

## Coverage and limitations

Coverage is OpenStreetMap's: dense and current in much of the world, thin in places with few volunteer mappers, and a facility can be missing, moved, or mislabeled in the map as in any living dataset. The 180-kilometre read and 160-point cap mean rural views show the nearest stations the read returns, not an exhaustive county roster. Above all, the limit stated on every card governs the layer's meaning: locations only. Response times, staffing, capabilities, and live status of any station are not shown and must never be inferred from a marker. In an emergency, call emergency services; this layer is for knowing your ground in advance.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*

Zenodo DOI: [10.5281/zenodo.23336832](https://doi.org/10.5281/zenodo.23336832).
