<!-- wio
name = "feature.parent"
kind = "feature"
shape = "parent"
description = "A capability delivered by child Works, with constraints they share."

[actions]
define = "define-feature"
deliver = "integrate"
amend = "amend-contract"
ratify = "ratify-contract"

[contract]
roots = ["@descendants"]
depends_on = []
-->

# <Work name>

<!--
Write each section for the rules this stage's bundle lists.
Delete a section or a heading that has nothing under it, unless it is
required.
-->

## Purpose <!-- wio: required -->

<!-- Why this change is needed. -->

## Goals <!-- wio: required, items>=1 -->

<!-- The capabilities this Work makes possible. -->

## Glossary <!-- wio: inherit -->

<!-- Terms whose meaning in this Work could be read more than one way. -->

## Non-Goals

<!-- What this Work deliberately does not do. -->

## Assumptions <!-- wio: required -->

<!-- What this Work takes as true without having confirmed it, with ids
     (A-1, A-2, ...), or "None." -->

## Mechanisms

<!-- The tools, packages, modules or data structures central to the
     solution, and their roles. -->

## Constraints <!-- wio: inherit -->

<!-- The constraints this Work adds and its children inherit. -->

## Visuals <!-- wio: required -->

<!-- Before and after diagrams of what the Work changes. -->

## Acceptance criteria <!-- wio: required, items>=1, pattern=AC-\d+ -->

<!-- The system-level guarantees that the integrated result establishes. -->

<!-- Example:

### **AC-1** A retry remains part of its trial

A retried execution records another attempt for the same trial.

#### Purchase with fees

- **Given** a trial whose first attempt can be safely retried.
- **When** the runner executes its retry.
- **Then** both attempts belong to the same trial.
-->

## Additional context

<!-- Context, risks and links the Work needs that fit nowhere above. -->
