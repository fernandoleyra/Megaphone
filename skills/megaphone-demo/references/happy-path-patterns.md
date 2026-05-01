# Happy-path patterns for demo GIFs

A demo GIF is a 5–10-second story. It has a beginning (the user arrives), a middle (they do one specific thing), and an end (they get value). Most demos fail because they try to show three things at once. This file documents the patterns that actually work.

## The shapes

### 1. The "click → result" GIF (most common)

Land on the page → click one CTA → the result appears → end on the result.

```json
{"steps": [
  {"kind": "wait", "seconds": 1},
  {"kind": "click", "text": "Generate"},
  {"kind": "wait", "selector": ".result", "state": "visible", "seconds": 6},
  {"kind": "screenshot", "label": "value-lands"},
  {"kind": "wait", "seconds": 1}
]}
```

Best for: tools where the value is one click away.

### 2. The "type → submit → see" GIF

Land on the page → type in an input → submit → result appears.

```json
{"steps": [
  {"kind": "wait", "seconds": 0.5},
  {"kind": "type", "selector": "textarea", "text": "Summarize this in 3 bullets", "delay": 60},
  {"kind": "click", "text": "Submit"},
  {"kind": "wait", "selector": ".result", "state": "visible", "seconds": 8},
  {"kind": "scroll", "selector": ".result"},
  {"kind": "wait", "seconds": 1}
]}
```

Best for: AI tools, search interfaces, anything chat-like.

### 3. The "before / after" comparison GIF

Show the before state → take an action → show the after.

```json
{"steps": [
  {"kind": "screenshot", "label": "before"},
  {"kind": "wait", "seconds": 0.6},
  {"kind": "click", "text": "Format"},
  {"kind": "wait", "selector": ".formatted", "state": "visible", "seconds": 4},
  {"kind": "screenshot", "label": "after"},
  {"kind": "wait", "seconds": 1}
]}
```

Best for: formatters, transformers, "ugly thing in / pretty thing out" tools.

### 4. The "tour" GIF (use sparingly)

Quick pan over multiple sections of the app to show what's there.

```json
{"steps": [
  {"kind": "wait", "seconds": 0.5},
  {"kind": "scroll", "y": 600},
  {"kind": "wait", "seconds": 0.6},
  {"kind": "scroll", "y": 1200},
  {"kind": "wait", "seconds": 0.6},
  {"kind": "scroll", "y": 1800},
  {"kind": "wait", "seconds": 1}
]}
```

Best for: marketing site tours. Worst for: showing a working product. Tours don't show value; they show layout.

## Timing rules

- **First frame should breathe.** Open with at least 0.5s of "the user has just landed" before anything moves. This establishes context.
- **Typed text needs `delay: 60–80ms`.** Faster looks like an autofill; slower looks slow. 60ms reads as fluent typing.
- **Click → render gap.** After any click that triggers a re-render, add `wait: 600ms` so the next frame captures the changed UI, not the in-flight UI.
- **End on the result, hold for 1s.** The last frame is what people remember. Pause on it.
- **Total length: 5–8 seconds.** GIFs longer than 10 seconds get scrolled past.

## Selectors that survive

- ✅ `data-testid="..."` — the gold standard. Add these to the components in your demo path.
- ✅ Visible text via `getByText(...)` — works for buttons, links, headings.
- ⚠️ Class names like `.btn-primary` — break when you redesign.
- ❌ Auto-generated CSS Modules class names like `.styles__btn--abc123` — guaranteed to break.

If your demo's selectors are class-based, expect to re-record after every UI change. The skill tells the user when it spots fragile selectors.

## Things that look bad on the recording

- **Native browser dialogs** (alert, confirm, browser-permission popups). Disable them in the app or accept programmatically before the demo runs.
- **Loading spinners that take >2s.** Either pre-warm the data or screen-grab a faster step.
- **Lazy-loaded images.** Add a `wait` after scroll to let images decode.
- **Animations that loop forever.** They make the GIF size balloon. Use a single static screenshot instead.
- **Empty states.** If your demo accidentally shows a "no data" screen for 2 frames, the GIF makes the app look broken. Pre-populate state.

## Scenarios that need pre-work

If your demo path requires any of the following, prep the app before running the recorder:

- **Authentication:** include a `prelogin` step or have the user log in once and pass `--auth-storage <file>` (Playwright storageState).
- **Specific data:** seed the app with the data you want to show. Don't rely on demo data being "there" by chance.
- **Time-of-day-specific UI** (greetings, etc.): the recorder runs at whatever time it runs; don't rely on "Good morning."

## Re-recording

A demo GIF lives in your repo as a JSON config + a generated PNG/GIF. When the UI changes:

1. The selectors may break. Run with `--debug` to see which step failed, fix the selector, re-run.
2. The visual style may have changed. The GIF will still produce, just with the new look.
3. The happy path itself may have shifted. Edit the JSON, re-run.

This is the whole reason this skill exists. Manual screen-recording is a one-time artifact that goes stale; a JSON-defined demo is a living spec.

## When NOT to make a demo GIF

- The product is **terminal-only** — record the terminal directly with `vhs` or `asciinema`, not Playwright.
- The product is **mobile-only** — Playwright can emulate, but for real mobile feel use the device's screen recorder.
- The value is **invisible** (background sync, observability, anything that runs without UI feedback) — make a diagram or animation, not a screen recording.
- The product is **pre-launch with no UI** — there's nothing to record. Wait until the UI exists.
