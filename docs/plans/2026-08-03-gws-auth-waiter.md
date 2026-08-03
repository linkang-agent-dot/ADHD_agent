# GWS Authentication Waiter Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automatically detect when an interactive GWS reauthorization has completed so the calling task can continue without asking the user to reply.

**Architecture:** A small Python CLI repeatedly performs a read-only Sheets metadata request through the existing `gsheet_utils` transport. Authentication failures remain retryable; success exits 0, unexpected errors exit 1, and timeout exits 2.

**Tech Stack:** Python standard library and `scripts/gsheet_utils.py`.

---

### Task 1: Add response classification tests

**Files:**
- Create: `tests/test_wait_gws_auth.py`

Test successful authentication, expired credentials, and non-authentication errors.

### Task 2: Implement the polling CLI

**Files:**
- Create: `scripts/wait_gws_auth.py`

Add configurable spreadsheet ID, timeout, and interval arguments. Keep probes read-only.

### Task 3: Verify

Run the unit test and a live probe against the X3 `dim.iap` spreadsheet. Both must exit successfully.
