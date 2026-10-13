# Transmitters: NOAA Weather Radio, Town by Town

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Transmitters, a public-warning geography layer for Orbital Network, and sets out its use cases. The layer plots the places of NOAA Weather Radio — the National Weather Service's voice network that broadcasts watches, warnings, and emergency information around the clock — from the Weather Service's own transmitter directory. The directory ships with the page as a snapshot file and is read only when the layer is tapped. Transmitters that share a town share one dot, and the dot's card names every transmitter there by callsign and frequency. Every surface of the layer repeats its central fact: the coordinates are town-level — the place, not the exact tower. The layer is live as of October 2026.

## What the layer shows

**The NWS transmitter directory, plotted at town level.** The snapshot bundled with the page was built from the National Weather Service's transmitter directory (published through api.weather.gov's radio service) and holds 1,027 transmitter records; the towns of 937 of them could be geocoded, and those are what plot — the remaining places, whose towns could not be resolved to coordinates, do not appear and are not placed by guesswork. Records are grouped by their coordinates, so a town with three transmitters shows one dot whose card lists all three: callsign, frequency in MHz, and the network name, with the town and state. The source line on every card reads "NOAA Weather Radio · National Weather Service (api.weather.gov/radio) · Locations are town-level." The layer holds up to a thousand dots.

**A snapshot, called a snapshot.** Unlike the network's feed layers, this one does not re-read its source when tapped: the directory rides with the page and is fetched from the page's own files at first tap, so the landing globe pays nothing for it and the layer works at the speed of a local file. The cost of that design is freshness of a different kind — the directory changes when the site republishes its snapshot, not when the Weather Service edits a record — and this document and the layer's design state that trade openly rather than letting a bundled file wear a live feed's clothes.

**Provenance rules.** Every dot is bound to named transmitter records from the Weather Service's directory, reproduced on the card by callsign and frequency. No transmitter is plotted without a directory record and a geocoded town; no tower coordinate is ever synthesized from a town's.

## Use cases

**Weather-radio owners.** Programming a receiver starts with knowing which transmitters serve a town: the card's frequencies and callsigns are exactly the facts a new owner needs, organized by the place they live in rather than by a tower they will never visit.

**Emergency preparedness.** NOAA Weather Radio is the alerting channel that works when phones and power fail; seeing its town-level footprint — including the gaps between towns — is preparedness geography a household can act on, by siting a receiver and testing which transmitters it hears.

**Travelers and newcomers.** Arriving in tornado or hurricane country, a visitor can learn which Weather Radio transmitters cover the town they are sleeping in, from the Weather Service's own directory.

**Journalists.** During severe weather, "the transmitter serving this county, on this frequency" is checkable background from the primary directory — with the town-level caveat intact when it is cited.

**Educators.** A national warning infrastructure made visible: a thousand transmitters, town by town, each with a voice frequency — and a clean lesson in the difference between a place-level directory and an engineering map.

## Coverage and limitations

Coverage is the NOAA Weather Radio network: the United States and its territories. Locations are town-level by design and by labeling — the dot marks the community a transmitter serves, and the actual tower may stand miles from it, typically on high ground outside town; never navigate to a dot expecting a tower. Frequencies and callsigns are as the directory snapshot carries them; the Weather Service adds, moves, and retires transmitters, and the snapshot follows on the site's republication cycle, not in real time. The 84 directory places that could not be geocoded are absent, so a missing town means an unresolved place name, not a missing transmitter. The layer shows where warnings are broadcast from, town by town — reception at any given house depends on terrain and the receiver, and only a listening test settles it.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
