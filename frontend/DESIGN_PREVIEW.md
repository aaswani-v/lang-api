# Frontend Design Preview

## Color Scheme

```
Primary Blue: #1e40af (header, buttons, links)
Success Green: #10b981 (genuine audio)
Warning Yellow: #f59e0b (uncertain results)
Danger Red: #ef4444 (deepfake detected)
Neutral Gray: #f3f4f6 to #1f2937 (backgrounds, text)
```

## UI Layout

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│                      वाणीCheck HEADER                            │
│              Advanced Audio Deepfake Detection                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  UPLOAD AUDIO CARD                                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              📤 UPLOAD AREA (Drag & Drop)               │ │
│  │         Or click to browse for audio files              │ │
│  │        Supports: WAV, MP3, OGG, WebM, FLAC              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Language: [English ▼]                                           │
│                                                                  │
│  ┌─ ANALYZE AUDIO ───────────────────────────────────────────┐ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  RESULTS CARD (Shows after analysis)                             │
│                                                                  │
│  Deepfake Probability                                            │
│  ████░░░░░░░░░░░░░░░░ 45%                                      │
│                                                                  │
│  ┌──────────────┐                                               │
│  │  UNCERTAIN   │   Audio may be AI-generated. Manual           │
│  └──────────────┘   review recommended.                         │
│                                                                  │
│  Details Grid:                                                  │
│  ┌─────────────────┬─────────────────┐                         │
│  │ Detection       │ Audio Duration  │                         │
│  │ 45% Confidence  │ 3.00s           │                         │
│  └─────────────────┴─────────────────┘                         │
│  ┌─────────────────┬─────────────────┐                         │
│  │ Language        │ Processing Time │                         │
│  │ English         │ 2.14s           │                         │
│  └─────────────────┴─────────────────┘                         │
│                                                                  │
│  What This Means                                                │
│  The analysis detected some unusual patterns but cannot         │
│  definitively classify the audio. Factors like background       │
│  noise, accents, or recording quality may affect accuracy.      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  HOW IT WORKS                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │    1     │  │    2     │  │    3     │  │    4     │        │
│  │ Upload   │  │ Process  │  │ Detect   │  │ Report   │        │
│  │ Audio    │  │ Features │  │ Deepfake │  │ Results  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

                    © 2026 वाणीCheck - Protecting voice authenticity
```

## Result States

### 1. Genuine Audio (Confidence < 40%)
```
┌─────────────────────────────────────┐
│ ✅ GENUINE                          │
├─────────────────────────────────────┤
│ Audio appears to be authentic       │
│ with high confidence.               │
│                                     │
│ Confidence: 15%                     │
└─────────────────────────────────────┘

Color: 🟢 Green (#10b981)
```

### 2. Uncertain (Confidence 40-70%)
```
┌─────────────────────────────────────┐
│ ⚠️ UNCERTAIN                        │
├─────────────────────────────────────┤
│ Uncertain results. Manual review     │
│ recommended.                        │
│                                     │
│ Confidence: 55%                     │
└─────────────────────────────────────┘

Color: 🟡 Yellow (#f59e0b)
```

### 3. Deepfake (Confidence > 70%)
```
┌─────────────────────────────────────┐
│ 🚨 DEEPFAKE                         │
├─────────────────────────────────────┤
│ High probability of deepfake        │
│ audio detected. Treat with caution. │
│                                     │
│ Confidence: 85%                     │
└─────────────────────────────────────┘

Color: 🔴 Red (#ef4444)
```

## Responsive Breakpoints

```
Desktop (1200px+)
├─ 2-column layout
├─ Large card padding
└─ Full info grid

Tablet (768px - 1199px)
├─ Single column layout
├─ Medium card padding
└─ 2-column info grid

Mobile (320px - 767px)
├─ Single column layout
├─ Tight card padding
└─ Stacked info grid
```

## Animation Effects

```
1. Upload Hover
   Border glow effect
   Slight scale increase
   
2. Button Hover
   Translate up (-2px)
   Shadow expansion
   
3. Result Appearance
   Slide-in animation (0.3s)
   
4. Loading Spinner
   Continuous rotation
   
5. Info Card Hover
   Translate up (-4px)
   Shadow expansion
```

## Typography

```
Header H1: 2.5rem (40px), Bold, Blue
Card Title H2: 1.5rem (24px), Bold
Subtitle: 1rem (16px), Medium
Body Text: 1rem (16px), Regular
Small Text: 0.875rem (14px), Regular
```

## Spacing

```
Card Padding: 32px (desktop), 20px (mobile)
Gap between cards: 24px
Section margin: 40px
Input padding: 10-12px
Button padding: 12px 24px
```

## Interactions

```
Upload Area
├─ Click to open file picker
├─ Drag & drop to upload
└─ Shows file name when selected

Form Select
├─ Focus: Blue border + shadow
└─ Hover: Highlight

Buttons
├─ Enabled: Full opacity, clickable
├─ Hover: Lift up, shadow grows
├─ Disabled: Half opacity, no cursor
└─ Active: Button press effect

Results
├─ Click close (X): Hide results
└─ Auto-scroll to results on show
```

## Performance

```
CSS
├─ No heavy animations
├─ GPU-accelerated transforms
└─ Minimal repaints

JavaScript
├─ No external libraries
├─ Efficient event handling
└─ Proper async/await

Loading
├─ Fast file reading
├─ Smooth API calls
└─ ~2-3 seconds processing
```

## Browser Rendering

```
Mobile First
├─ Design starts at 320px
├─ Scales up to larger screens
└─ Touch-friendly targets

Accessibility
├─ Semantic HTML
├─ Proper label associations
├─ Color contrast OK
└─ Keyboard navigable
```

---

## Summary

✨ **Modern Design**: Gradient backgrounds, smooth animations
✨ **Clean Layout**: White cards on gradient background
✨ **Color Coded**: Results instantly recognizable
✨ **Responsive**: Works on all devices
✨ **Fast**: No external CSS frameworks
✨ **Professional**: Corporate look, not template-y
✨ **User-Friendly**: Intuitive interactions

This is NOT your typical "AI app" design. It's clean, minimal, and professional! 🎨
