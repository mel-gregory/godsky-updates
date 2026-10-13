# Moon: The Sub-Lunar Point, Computed Live

**Melbourne Gregory**
*Orbital Network*

Version 1.0 — October 13, 2026

## Abstract

This document describes Moon, an astronomical layer for Orbital Network, and sets out its use cases. The layer plots a single glowing marker at the sub-lunar point — the spot on Earth's surface where the Moon stands directly overhead at that moment — computed live in the visitor's browser from the Moon's orbit, with no feed, no key, and nothing streamed. The marker's card gives the Moon's phase by name, the percentage of its disc lit, and its current distance from Earth; while the layer is on, the point is recomputed every few minutes, so the marker walks across the globe with the Moon. Tapping the marker also opens the page's Moon view, which pairs the computed position with a lunar atlas drawn from NASA LRO imagery. The layer is live as of October 2026.

## What the layer shows

**A computed point, honestly labeled.** The sub-lunar point is found by standard low-precision lunar mathematics — the truncated Meeus series, the same family of algorithm the widely used SunCalc library implements — evaluated for the current instant: the Moon's geocentric position from its mean orbital elements, corrected for the Sun's pull on the phase geometry, converted to the meridian it is crossing now. The implementation's own comment states its accuracy: good to a fraction of a degree. The card's source line says what the point is: "Computed live in this page · low-precision lunar orbit — no feed."

**Phase and distance from the same math.** The card names the phase from the eight traditional names (New Moon through Waning Crescent), gives the illuminated fraction as a percentage, and the Moon's distance in kilometres — all derived from the same computation as the position, so the three numbers always agree with each other. The globe dresses the marker as the Moon itself, drawn at its computed phase. While the layer is on, the whole calculation re-runs every three minutes; nothing is fetched at any point in the layer's life. The Moon view the marker opens extends the same honesty to its imagery: the atlas is identified as NASA LRO imagery, presented by an external lunar stream the page names, and the panel's own footer repeats that phase, sub-lunar point, and distance are computed in the page.

**Provenance rules.** The layer's provenance is its method, and the method is stated on the card rather than hidden: a named algorithm family, a stated precision, no source feed to cite because none exists. If the computation cannot run, there is no marker — there is nothing to fall back to, and nothing is invented.

## Use cases

**Families.** "Where is the Moon directly overhead right now?" — over an ocean, most hours, which is itself a small wonder — and "how lit is it tonight," answered with a phase name and a percentage a child can check against the sky at bedtime.

**Educators.** The sub-lunar point makes three abstractions concrete at once: that the Moon circles the Earth, that "overhead" is a place that moves, and that phase is geometry, not shadow-play. The same screen shows the computation's stated precision — a first lesson in models and their error bars.

**Photographers and skywatchers.** Phase and illumination for planning a moonrise shoot or a dark-sky night, from a card that updates as the evening does.

**Tide watchers (context).** The Moon drives the tides, and its overhead point tracks the tidal bulge's longitude loosely — offered as context and curiosity beside the network's measured water layers, not as a tide prediction, which this layer never makes.

**The simply curious.** A single breathing marker on a turning planet, answering the oldest question there is — where is the Moon? — continuously, for free, with its arithmetic showing.

## Coverage and limitations

Coverage is total and instantaneous by construction — the sub-lunar point exists at every moment — and precision is the limit instead: a fraction of a degree is hundreds of metres to tens of kilometres on the ground, ample for awareness and education and useless, as stated, for telescope pointing or occultation timing. Phase percentages and distances carry the same low-precision character. The Moon view's atlas stream depends on an external provider and NASA imagery availability; the layer's computed marker does not, and keeps walking if the stream is down. Nothing in the layer predicts eclipses, tides, or moonrise times.

## Disclosure

*Manuscript prepared with AI drafting assistance; all content was reviewed and approved by the author, who takes full responsibility for it.*

*The Orbital Network system described in this document operates at https://godsky.net. The white paper "Orbital Network: A Live Broadcast System for Real-Time Planetary Awareness" (Zenodo, DOI 10.5281/zenodo.23328433) describes the parent system.*
