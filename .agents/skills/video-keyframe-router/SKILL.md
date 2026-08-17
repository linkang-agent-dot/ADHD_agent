---
name: video-keyframe-router
description: Route every AI-video shot to text-only, first-frame, same first-and-last frame, distinct first-and-last frames, multiple keyframes, or post-production camera motion before generation. Use for Seedance, image-to-video, product ads, ecommerce videos, character videos, try-on/garment demonstrations, before-after shots, loops, camera moves, or whenever product appearance, identity, clothing coverage, body silhouette, UI/text, spatial relationships, or the ending composition must stay controlled.
---

# Video Keyframe Router

Use this skill before generating or revising any AI-video shot. Do not treat a stronger prompt as a substitute for missing visual constraints.

This skill only decides how to anchor an individual shot. For a complete ecommerce reference-video reskin—including source analysis, complete-pain module splitting, bones-versus-skin mapping, product-reference packaging, generation, audio, assembly, QC, and cost—use `ecommerce-video-reskin`, which calls this router at its shot-routing gate.

## Required reference

Read `C:\ADHD_agent\KB\方法论\AI视频镜头首尾帧路由与验收.md` completely before choosing routes. Use `references/shot-routing-template.md` for the shot table.

## Workflow

1. Split the script into atomic shots. One shot should express one visual task.
2. Fill the routing table before any media call: goal, fixed invariants, start state, end state, subject motion, camera motion, risk, route, references, acceptance frames.
3. Choose exactly one route per shot:
   - `T` text-only: no exact external visual truth and drift is acceptable.
   - `F` first frame: start appearance/composition must be exact; end state may be open.
   - `SS` same first=last: identity, product shape, garment surface, layout, or loop must remain locked; allow only micro-motion.
   - `SE` distinct start/end: both endpoint states or compositions must be exact.
   - `MK` multiple keyframes/split shots: a critical middle state, multiple transformations, hand-object contact, or complex rotation must be controlled.
   - `PC` post-production camera: the subject must not deform, but the edit needs push-in, pan, crop, speed ramp, or reframing.
4. Generate and inspect required keyframes at original size before generating video. If visual acceptance is subjective or business-critical, wait for user confirmation.
5. Generate only after the keyframe gate passes. Use the fewest subject motions compatible with the shot goal.
6. Inspect original-size start, middle, end, and risk frames. Contact sheets locate frames; they never prove visual correctness.
7. If a locked invariant drifts, revise the static keyframe or split the shot. Do not keep stacking prompt adjectives onto a failed architecture.

## Hard routing rules

- Product SKU, color, straps, seams, packaging, logo, printed text, UI, or exact prop: never default to `T`.
- Garment concealment, compression, no-trace, fit, body silhouette, or surface flatness: require a static acceptance image first; normally use `SS` plus `PC` for energy.
- Before/after, open/close, pickup/putdown, front/back endpoints, camera landing composition: use `SE`; use `MK` if the transition itself is also critical.
- Loop or living-photo micro-motion: use `SS`.
- Exact actor identity plus free action: use at least `F`; add `SE` or `MK` when ending/intermediate states matter.
- When motion is requested but the approved subject shape must not change, keep the subject locked and move the virtual camera in post.
- Never combine multiple critical states into one long generation merely to reduce call count.

## Data boundary

Obey the active session's personal/company boundary before any call. In a personal Codex window, never upload personal content, prompts, or references to GRFal, x3-media, media-worker, Morphix, or any company endpoint. Local read-only learning from installed company prompts is allowed; submission is not.

## Completion gate

Do not report a shot as finished unless:

- its route is recorded;
- every referenced keyframe exists and was inspected at original size;
- generated video was checked at start, middle, end, and named risk moments;
- the final file passes decode/spec checks;
- user-controlled visual decisions are marked pending until the user confirms them.
