# E222 Remaining Clips Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate clips 03, 05, and 15 through the personal Volcengine Seedance provider and complete the 16/16 delivery set.

**Architecture:** Keep 03 and 05 on their verified prompts. Rewrite only clip 15 as one continuous 15-second Seedance generation with three explicit time windows; do not split or stitch. Generate into a new version directory, run file/audio and visual QC, then subtitle and promote only passing clips.

**Tech Stack:** Python, Volcengine Seedance 2.0 mini, ffmpeg/ffprobe, JSON prompt catalog.

---

### Task 1: Lock the GRFal safety boundary

**Files:**
- Verify: `C:/Users/linkang/.claude-personal/settings.json`
- Verify: `C:/Users/linkang/.claude/hooks/block_grfal.py`
- Verify: `C:/ADHD_agent/avatar-replace/scripts/batch_t2v.py`

1. Confirm the personal PreToolUse hook invokes `block_grfal.py`.
2. Confirm `avatar-replace` is a guarded cwd keyword.
3. Confirm the runner imports `VolcProvider` and has no GRFal dependency.

### Task 2: Rewrite clip 15 as one-shot three-act generation

**Files:**
- Modify: `C:/ADHD_agent/avatar-replace/prompts/t2v_E222.json`

1. Preserve one 15-second generation (`dur: 15`).
2. Encode 0-5s color-showing comparison, 5-10s outfit invisibility proof, and 10-15s doorway mother-daughter payoff.
3. Lock each scene's outfit, prop ownership, action, and transition; prohibit split generation and stitching.
4. Validate the JSON parses successfully.

### Task 3: Generate 03, 05, and 15

**Files:**
- Read: `C:/ADHD_agent/avatar-replace/prompts/t2v_E222.json`
- Create: `E:/222/t2v_成片_v4/`

1. Run `batch_t2v.py --only 03,05,15 --workers 3` from the avatar-replace cwd.
2. Verify all three mp4 files exist, contain H.264 video and AAC audio, and match expected durations.
3. On network timeout, recover the existing task instead of resubmitting blindly.

### Task 4: QC and delivery

**Files:**
- Create: `E:/222/t2v_成片_v4_字幕/`
- Modify: `E:/222/t2v_最终交付/`
- Modify: `E:/222/样片验收反馈.md`

1. Compare original-resolution keyframes against each clip's sell-point and timeline card.
2. Reject incorrect color, outfit, reveal level, action, speaker ownership, prop ownership, or duplicated Seedance subtitles.
3. Subtitle only passing clean clips.
4. Copy passing final clips into the final delivery directory and update the delivery ledger to 16/16.

