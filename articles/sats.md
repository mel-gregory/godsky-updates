# Satellites: The Station Group, Propagated in Your Browser

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Satellites, an orbital layer for Orbital Network, and sets out its use cases. The layer plots the crewed-station group of satellites catalogued by CelesTrak — the International Space Station first among them — as markers that move across the globe in near-real time. Nothing is streamed and no radar tracks anything: when the layer is switched on, the page fetches the group's published two-line element sets (TLEs) from CelesTrak once, then computes each satellite's position from those elements with standard orbital mechanics, in the visitor's browser, advancing the markers every twenty seconds while the layer is on. Each card states the satellite's computed altitude and speed and names the element set it came from. The layer is live as of October 2026.

## What the layer shows

**Element sets, propagated locally.** A two-line element set is the standard public description of a satellite's orbit, published by the tracking community from the US Space Force's catalogue and redistributed by CelesTrak. This layer reads the "stations" group — the ISS and its fellow crewed and station-class objects — parses each element set, and propagates it with a two-body Kepler solver: the same class of math the globe's own station feed uses. While the layer is on, positions are recomputed on a twenty-second clock, so the markers genuinely advance; the elements themselves refresh only when the layer is tapped off and on again. The ISS marker is drawn larger than the rest.

**Cards that say "computed."** A marker's title is the satellite's catalogue name; its card gives the computed altitude in kilometres and an approximate orbital speed, and its source line reads "CelesTrak TLE · propagated in your browser." The word "propagated" is the honest verb: the position is a calculation from the last published elements, presented as a calculation, not dressed up as a live observation.

**Provenance rules.** The elements come from a named public source, fetched once per activation; the computation happens on the visitor's machine, so the layer works with no key and no stream. If CelesTrak cannot be reached or returns no usable elements, the layer reports that and plots nothing — a satellite never appears from memory or invention.

## Use cases

**Families and space enthusiasts.** The station, right now, over a real Earth: where the ISS is during a school-night pass, which ocean it crosses while dinner cooks — the hook that turns "space is up there" into "space is over the Atlantic, moving at orbital speed, this minute."

**Educators.** Orbital mechanics with the mathematics exposed: inclination, period, and ground tracks can be discussed against markers whose positions students know are being computed from published elements in their own browser — the model and its limits are the curriculum.

**Amateur radio operators.** The ISS carries amateur radio equipment and is a first satellite contact for many operators; a moving marker propagated from the same elements operators themselves use supports planning the next pass window (pass prediction itself belongs to dedicated tools, and the layer does not pretend to it).

**Journalists.** During dockings, spacewalks, and re-entries, "where is the station now" is answered with a sourced, computed position whose basis can be stated in one line.

**Photographers and observers.** A sense of the station's current ground track for stepping outside at the right pass — with the honest caveat, below, about precision.

## Coverage and limitations

The layer covers one catalogue group — stations — not the tens of thousands of tracked objects in orbit; other groups are not plotted and their absence is not a gap in the sky, just in this layer's scope. Positions are estimates from element sets that age between publications, computed with a two-body model that ignores atmospheric drag and gravitational perturbations: good enough to watch the station cross an ocean and to find it in the sky at a bright pass, not good enough — and not claimed — for conjunction warnings, docking, or precise pointing. Element-set epochs are days-scale stale by nature; the longer since publication, the further a computed position can drift from the satellite's true one, which is why the cards credit the elements rather than assert a tracking fix.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*

Zenodo DOI: [10.5281/zenodo.23336126](https://doi.org/10.5281/zenodo.23336126).
