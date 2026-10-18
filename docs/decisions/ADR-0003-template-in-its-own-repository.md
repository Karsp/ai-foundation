# ADR-0003: The foundation lives in its own template repository

- **Status:** Accepted
- **Date:** 2026-10-18
- **Deciders:** Karsp
- **Issue:** #4

## Context

The first version of the foundation was committed inside `Karsp/FinTrack`, an application. Other planned projects (Otto, Wardrobe, FlowBoard) need the same base. Copying it from one app into another would leave several drifting versions.

## Decision

The foundation lives in `Karsp/ai-foundation`, marked as a GitHub template repository. New projects are created from it with "Use this template". Each project keeps only its own decisions (architecture guide answers, ADRs, stack-specific config), and improvements to the shared rules go back to this repository through Issues.

## Alternatives considered

- **Keep it inside FinTrack:** couples the template's history to one app.
- **Git submodule or package:** keeps projects in sync automatically, but adds tooling friction to documentation that each project needs to adapt.

## Consequences

- Projects can fall behind the template; the pilot retro (#16) should define how to pull updates (e.g. a periodic "sync with foundation" Issue).
- FinTrack's copy of the files is removed or reduced in the pilot (#16).
