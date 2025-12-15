# @design-rules.md
**Logistics Twin Design System - V5.7.0**

Centralized design tokens & component guidelines for frontend consistency.

---

## 🎨 1. COLOR PALETTE

### Primary Colors
```css
/* Core Brand */
--color-primary: #667eea;        /* Purple gradient start */
--color-primary-dark: #764ba2;   /* Purple gradient end */
--color-primary-hover: rgba(102, 126, 234, 0.1);

/* Agent Colors (Fixed) */
--color-agent-ql: #3498db;       /* Blue - Q-Learning */
--color-agent-sarsa: #27ae60;    /* Green - SARSA */
--color-agent-mc: #c0392b;       /* Red - Monte Carlo */
--color-agent-td: #f39c12;       /* Orange - TD-Lambda */
--color-agent-dyna: #8e44ad;     /* Purple - Dyna-Q */
```

### Semantic Colors
```css
/* Status */
--color-success: #27ae60;
--color-danger: #c0392b;
--color-warning: #f39c12;
--color-info: #3498db;

/* Financial */
--color-profit: #27ae60;
--color-loss: #c0392b;

/* City Types */
--color-city-port: #2c3e50;      /* Port (⚓) */
--color-city-industry: #c0392b;  /* Industry (🏭⚙️) */
--color-city-office: #8e44ad;    /* Office (🏢) */
--color-city-default: #3498db;   /* Default */
```

### Neutral Colors
```css
--color-gray-50: #f8f9fa;
--color-gray-100: #e9ecef;
--color-gray-200: #dee2e6;
--color-gray-300: #ced4da;
--color-gray-700: #495057;
--color-gray-900: #212529;
```

### Background & Surfaces
```css
/* Light Mode */
--bg-sidebar: rgba(255, 255, 255, 0.96);
--bg-sidebar-border: rgba(255, 255, 255, 0.5);
--bg-card: #ffffff;

/* Dark Mode */
[data-bs-theme="dark"] {
  --bg-sidebar: rgba(33, 37, 41, 0.96);
  --bg-sidebar-border: rgba(255, 255, 255, 0.1);
  --bg-card: #212529;
}
```

---

## 📏 2. SPACING SCALE

```css
/* 8px base scale */
--space-1: 4px;     /* 0.25rem */
--space-2: 8px;     /* 0.5rem */
--space-3: 12px;    /* 0.75rem */
--space-4: 16px;    /* 1rem */
--space-5: 24px;    /* 1.5rem */
--space-6: 32px;    /* 2rem */
--space-8: 48px;    /* 3rem */
--space-10: 64px;   /* 4rem */
```

**Usage:**
- Card padding: `--space-3` (12px)
- Button padding: `--space-2 --space-3` (8px 12px)
- Section margin: `--space-4` (16px)
- Modal padding: `--space-5` (24px)

---

## 🔤 3. TYPOGRAPHY

### Font Families
```css
--font-primary: 'Segoe UI', 'Roboto', sans-serif;
--font-mono: 'JetBrains Mono', 'Consolas', monospace;
```

### Font Sizes
```css
--text-xs: 9px;      /* Labels, badges */
--text-sm: 10px;     /* Descriptions */
--text-base: 11px;   /* Body text */
--text-lg: 14px;     /* Subheadings */
--text-xl: 16px;     /* Headings */
--text-2xl: 20px;    /* Page titles */
```

### Font Weights
```css
--font-normal: 400;
--font-medium: 600;
--font-bold: 700;
```

---

## 🎭 4. SHADOWS & ELEVATION

```css
/* Card Shadows */
--shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 10px rgba(0, 0, 0, 0.15);
--shadow-lg: 0 10px 40px rgba(0, 0, 0, 0.25);

/* Active State */
--shadow-active: 0 4px 15px rgba(102, 126, 234, 0.5);

/* Hover State */
--shadow-hover: 4px 4px 12px rgba(0, 0, 0, 0.1);
```

---

## 📐 5. BORDER RADIUS

```css
--radius-sm: 6px;    /* Small elements */
--radius-md: 8px;    /* Buttons, inputs */
--radius-lg: 10px;   /* Cards, nav pills */
--radius-xl: 12px;   /* Modals, sidebar */
--radius-full: 9999px; /* Pills, badges */
```

---

## ⏱️ 6. TRANSITIONS & ANIMATIONS

```css
/* Timing Functions */
--ease-standard: cubic-bezier(0.4, 0, 0.2, 1);
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);

/* Durations */
--duration-fast: 150ms;
--duration-normal: 250ms;
--duration-slow: 400ms;
```

**Standard Transition:**
```css
transition: all var(--duration-normal) var(--ease-standard);
```

---

## 🧩 7. COMPONENT PATTERNS

### Agent Card
```html
<div class="agent-card" style="border-left-color: {agentColor}">
  <div class="agent-header">...</div>
  <div class="agent-metrics">...</div>
  <div class="agent-progress">...</div>
</div>
```

**Styles:**
- Border-left: 4px agent color
- Padding: 10px 12px
- Margin-bottom: 8px
- Shadow: `--shadow-sm`
- Hover: `translateX(-3px)` + `--shadow-hover`

### Button Variants
```css
/* Primary */
.btn-primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  box-shadow: var(--shadow-active);
}

/* Sizes */
.btn-sm: padding 8px 10px
.btn-md: padding 10px 14px
.btn-lg: padding 12px 20px
```

### Nav Pills (Tabs)
```css
.nav-pills {
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-lg);
  padding: 4px;
}

.nav-pills .nav-link.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  box-shadow: var(--shadow-active);
}
```

### Modal
```css
.modal-header {
  background: var(--color-primary);
  color: white;
}

.modal-footer {
  background: var(--color-gray-50);
}
```

---

## 🎯 8. Z-INDEX SCALE

```css
--z-base: 1;           /* Map layer */
--z-overlay: 10;       /* Overlays */
--z-sticky: 100;       /* Sticky headers */
--z-sidebar: 1000;     /* Sidebar */
--z-modal: 1050;       /* Modals */
--z-toast: 1100;       /* Notifications */
```

---

## 🔧 9. COMPONENT SIZING

### Sidebar
- Width: 400px
- Max-height: 96vh
- Top/Right offset: 15px
- Collapsed transform: `translateX(420px)`

### Agent Card
- Min-height: auto
- Border-left-width: 4px
- Padding: 10px 12px
- Margin-bottom: 8px

### Buttons
- Height (sm): 32px
- Height (md): 38px
- Height (lg): 44px
- Min-width: 80px

### Inputs
- Height: 38px
- Padding: 8px 12px
- Border: 1px solid

---

## 🎨 10. ICON SYSTEM

**Framework:** Bootstrap Icons (`bi-*`)

**Common icons:**
- Play: `bi-play-circle-fill`
- Stop: `bi-pause-circle-fill`
- Save: `bi-save`, `bi-floppy`
- Delete: `bi-trash`
- Settings: `bi-sliders`, `bi-gear`
- Chart: `bi-bar-chart-fill`, `bi-graph-up`
- Disaster: `bi-exclamation-triangle-fill`
- Info: `bi-question-circle`
- Success: `bi-check-circle`
- Error: `bi-x-circle`

**Sizing:**
```css
.fs-1: 2.5rem
.fs-5: 1.25rem (default icon size)
.fs-6: 1rem (small icons)
```

---

## ✅ 11. DESIGN PRINCIPLES

### 1. Consistency
- Use design tokens, never hardcode values
- Follow 8px spacing grid
- Maintain color palette

### 2. Accessibility
- Min touch target: 44x44px
- Color contrast ratio: 4.5:1 minimum
- Focus visible states
- ARIA labels for interactive elements

### 3. Performance
- CSS transitions < 400ms
- Avoid layout thrashing
- Use `transform` over `top/left`
- Debounce animations

### 4. Responsiveness
- Mobile-first approach
- Breakpoints: 576px, 768px, 992px, 1200px
- Touch-friendly targets
- Fluid typography

---

## 🚫 12. ANTI-PATTERNS (Avoid!)

❌ **Inline styles** (use CSS variables)
```html
<!-- BAD -->
<div style="color: #3498db; padding: 12px;">

<!-- GOOD -->
<div class="text-primary p-3">
```

❌ **Hardcoded colors**
```css
/* BAD */
background-color: #667eea;

/* GOOD */
background-color: var(--color-primary);
```

❌ **Magic numbers for spacing**
```css
/* BAD */
margin-bottom: 13px;

/* GOOD -->
margin-bottom: var(--space-3); /* 12px */
```

❌ **Non-semantic class names**
```html
<!-- BAD -->
<div class="blue-box-123">

<!-- GOOD -->
<div class="agent-card">
```

---

## 📝 13. NAMING CONVENTIONS

### CSS Classes (BEM-inspired)
```css
.block {}
.block__element {}
.block--modifier {}
.block__element--modifier {}
```

**Examples:**
```css
.agent-card {}
.agent-card__header {}
.agent-card__metrics {}
.agent-card--hidden {}
```

### CSS Variables
```css
--{category}-{property}-{variant}
```

**Examples:**
```css
--color-agent-ql
--space-4
--shadow-active
```

---

## 🎯 14. COMPONENT CHECKLIST

When creating new components, ensure:

- [ ] Uses design tokens (no hardcoded values)
- [ ] Follows spacing scale (8px grid)
- [ ] Has hover/active/focus states
- [ ] Responsive on mobile
- [ ] Dark mode compatible
- [ ] Touch-friendly (44x44 min)
- [ ] Semantic HTML
- [ ] ARIA labels if interactive
- [ ] Consistent with existing patterns

---

## 📊 15. CURRENT METRICS

**Current State (V5.7):**
- Total inline styles: ~50 instances
- Hardcoded colors: ~15 instances
- Magic numbers: ~30 instances
- Design token coverage: 20%

**V6.0 Target:**
- Inline styles: 0
- Design token coverage: 90%+
- Component library: 10 reusable components
- Documentation: 100% components documented

---

## 🔄 16. MIGRATION GUIDE

### Phase 1: Audit (Current)
- Document existing patterns
- Identify hardcoded values
- Create design token inventory

### Phase 2: Tokenization
- Extract all colors to CSS variables
- Standardize spacing values
- Create component classes

### Phase 3: Refactoring
- Replace inline styles with classes
- Migrate colors to tokens
- Extract reusable components

### Phase 4: Documentation
- Document all components
- Create usage examples
- Establish review process

---

**Last Updated:** 2025-12-15 (V5.7.0)  
**Owner:** Design System Team  
**Status:** 🟡 In Progress (20% token coverage)
