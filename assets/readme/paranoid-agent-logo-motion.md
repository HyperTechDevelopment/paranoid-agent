# Motion Spec — paranoid-agent-logo

Renderer-independent contract. GitHub does not play SVG animation; this spec drives the optional GIF export, with the static SVG as fallback and the `prefers-reduced-motion` state equal to frame 0.

## Layers

| Layer | Content | Animates |
|---|---|---|
| `bg` | Rounded square `#070b11`, border `#1c2635` | No |
| `rings` | 3 concentric circles `#00ff41` | Opacity pulse, staggered |
| `sweep` | Wedge `opacity 0.22` | Rotates 360° around (256,232) |
| `ticks` | 4 outer tick marks | No |
| `cross` | Red crosshair + center dot | Dot blink |
| `wordmark` | PARANOID / AGENT text | No |

## Keyframes (loop 2400ms, linear sweep, ease-in-out pulse)

- `0ms`: sweep angle 0°, rings opacity 1.0/0.6/0.35, dot opacity 1
- `1200ms`: sweep angle 180°, rings 0.7/0.45/0.25, dot opacity 0.35
- `2400ms` = `0ms` (seamless loop)

## Easing / duration

- Sweep: linear, 2400ms, infinite
- Rings pulse: ease-in-out, 2400ms, infinite, 200ms stagger per ring
- Dot blink: steps(2), 1100ms period

## Reduced motion

Static first frame. No rotation, no pulse, no blink.

## Export

Static PNG = frame 0 at 512px. Animated GIF = 2400ms loop, 12fps, GitHub-safe size. See `animated-readme-logo` exporter workflow; GIF generation needs explicit approval + tooling.
