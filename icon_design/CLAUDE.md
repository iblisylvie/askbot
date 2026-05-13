# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This directory contains the brand logo design assets for **anyseek** - an AI/education content brand with the philosophy of "finding low-dimensional structure in chaos" (混沌中找低维结构).

## Brand Design System

### Primary Color
- **Coral Orange**: `#E07A5F`
- Must remain visible on both black and white backgrounds

### Visual Hierarchy (Three Layers)
1. **Chaos (散沙)**: 80+ random dots, opacity 0.2-0.35
2. **Potential Paths (淡线)**: 3 alternate spiral paths with small nodes, opacity 0.15-0.22
3. **Main Path (主线)**: Golden spiral with gradient nodes, opacity 0.9+

### Final Logo (v2, 2026-05-13)
`anyseek_logo_v2_20260513.svg` — Concept: **Emergence（涌现）**
- Mathematically rigorous logarithmic spiral (r = a·e^(0.28·θ), ~2 turns)
- Golden spiral growing outward from center
- Open endpoint with halo ring (仍在求索)
- Sparse chaos point field as background texture
- 5 gradient nodes along the spiral marking accumulated discovery

**Full asset suite**: see [README.md](README.md). Variants: main / compact / mark / mini / mono_black / mono_white / horizontal lockup.

**v1 (deprecated)**: `anyseek_logo_5_spiral_east.svg` — earlier ink-wash + flying-white version. Retired due to concept overload and poor scalability at small sizes.

## File Naming Convention

```
anyseek_logo_{version}_{description}.svg
```

- `1_manifold` / `1_manifold_v2` - Curve manifold exploration
- `2_attractor` - Strange attractor concept
- `3_mountain` - Chinese landscape inspiration
- `4_hexagon_v2` - Hexagon honeycomb structure
- `5_spiral_v3` / `5_spiral_east` - Golden spiral (final)
- `6_mobius_v2` - Möbius strip concept
- `7_tree` - Fractal tree branching
- `8_prism` - Prism refraction concept

## Brand Narrative Keywords

- **Core Philosophy**: 混沌中找低维结构 (Finding order in chaos)
- **Tagline**: 路漫漫，求索不止 (The road is long, seeking never ends)
- **Mascot**: Nautilus (鹦鹉螺) - Golden spiral in nature
- **Target**: Content brand for AI progress tracking and education

## SVG Structure Pattern

```svg
<defs>
  - Gradients for main spiral
  - Filters for glow effects
</defs>

<g fill="#E07A5F">
  <!-- Chaos dots -->
</g>

<path> <!-- Potential paths (3 lines) -->
<circle> <!-- Small nodes on potential paths -->

<g filter="url(#glow)">
  <path> <!-- Main golden spiral -->
  <!-- Flying white strokes -->
</g>

<circle> <!-- Main path nodes (decreasing size) -->
```

## Export Requirements

When exporting for different platforms:
- **Xiaohongshu (小红书)**: 1:1 square format
- **WeChat Official**: 2.35:1 banner format
- **Avatar**: 200x200px minimum
- **PNG export**: Preserve transparency for light/dark mode adaptability
