# Radio Signals: Public Stations with Published Coordinates

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Radio Signals, a broadcast-geography layer for Orbital Network, and sets out its use cases. The layer plots radio stations that publish their own coordinates, drawn live from Radio Browser — the free, community-maintained directory of the world's internet radio stations — on the network's real-time globe. Each marker is a station in the directory: its name, its country and state as the directory carries them, and the format and bitrate at which it streams. The layer is candid about its kind: these are directory pins for stations that chose to publish a location, not signal measurements — and the official transmitter records of the FCC, NOAA Weather Radio, and the KiwiSDR receiver network are directory data too, listed in the layer's own description rather than dressed up as live signal pins. The layer is live as of October 2026.

## What the layer shows

**The Radio Browser directory, plotted.** When the layer is switched on, the page searches Radio Browser's public API for working stations that carry geographic coordinates — the directory's geo-bearing, non-broken entries, ordered by listener clicks — and plots up to 170 of them. A marker's title is the station's name; its card gives the country and state the station publishes, its codec and streaming bitrate where listed, and the source line "Radio Browser public station directory · station-published coordinates."

**Directory data, called directory data.** Nothing in the layer measures a signal: no field strength, no coverage contour, no reception report. A pin means a station exists in the directory with published coordinates — the station's own statement of where it is. The layer's panel description says the same of the famous neighboring datasets: FCC transmitter records, NOAA Weather Radio's transmitter list, and the KiwiSDR web-receiver directory are reference data, and they are listed as such, never plotted as if they were live signals on this layer. (NOAA Weather Radio has its own dedicated layer on this globe — Transmitters — built from the Weather Service's directory and labeled town-level there.)

**Provenance rules.** Every marker is bound to a station record in a named public directory, with the station's own published fields on the card. If the directory cannot be reached, the layer reports that and plots nothing.

## Use cases

**Radio hobbyists and DXers.** A world map of streamable stations that say where they are — a starting geography for the hobby, each pin traceable to the station's directory record, codec, and bitrate.

**Travelers and the diaspora.** The stations of a home town or a destination, visible in place: what broadcasts from there, in the directory's own listing, before a trip or from an ocean away.

**Educators.** Broadcast geography as a discussion starter — why stations cluster where people and infrastructure are, why the directory skews toward stations that self-list, and what a directory can and cannot tell you about the airwaves.

**Journalists and media researchers (awareness).** The visible skeleton of local media in a region — which towns carry stations that publish themselves — as orientation before deeper work in primary sources.

**The general public.** Serendipity with a source: spin the planet, tap a pin on another continent, and learn a station's name, place, and stream format — an invitation the page's listening features can then take further.

## Coverage and limitations

Coverage is the directory's: stations that list themselves in Radio Browser and publish coordinates, which skews toward internet-streaming stations in Europe and North America and toward the popular end of the directory, since the read is ordered by listener clicks. A missing pin says a station is not in this directory with coordinates — nothing about whether radio exists at that place, where the terrestrial airwaves are full of stations no internet directory carries. Coordinates are station-published and can be approximate — a studio address, a city center — and are plotted as given. The layer plots the directory; it does not play audio, rate audio quality, or verify that a stream is up at the moment of the tap beyond the directory's own broken-link screening at read time.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
