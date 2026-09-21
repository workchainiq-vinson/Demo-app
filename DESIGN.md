---
version: "alpha"
name: Bio Green Operations
description: Visual identity for the Bio Green Processing and Manufacturing Inc. HR & Payroll System — a clean, functional operations dashboard for a Philippine manufacturing plant.
colors:
  primary: "#557a00"
  primary-hover: "#45640a"
  primary-container: "#e2f0c6"
  on-primary-container: "#45640a"
  accent: "#00a83c"
  neutral: "#fafaf9"
  surface: "#ffffff"
  surface-muted: "#e7e5e4"
  border-subtle: "#f5f5f4"
  text-primary: "#1c1917"
  text-emphasis: "#44403c"
  text-secondary: "#57534e"
  text-tertiary: "#78716c"
  text-muted: "#a8a29e"
  warning: "#d97706"
  warning-container: "#fffbeb"
  danger: "#ef4444"
  danger-text: "#b91c1c"
  danger-container: "#fef2f2"
typography:
  h1:
    fontFamily: system-ui
    fontSize: 1.25rem
    fontWeight: 600
  data-value:
    fontFamily: system-ui
    fontSize: 1.5rem
    fontWeight: 600
  label-caps:
    fontFamily: system-ui
    fontSize: 0.6875rem
    fontWeight: 600
    letterSpacing: 0.05em
  label-table:
    fontFamily: system-ui
    fontSize: 0.75rem
    fontWeight: 600
  body-md:
    fontFamily: system-ui
    fontSize: 0.875rem
    fontWeight: 400
  body-sm:
    fontFamily: system-ui
    fontSize: 0.75rem
    fontWeight: 400
rounded:
  sm: 6px
  md: 8px
  lg: 12px
  full: 9999px
spacing:
  xs: 4px
  sm: 6px
  md: 10px
  lg: 12px
  xl: 16px
components:
  page:
    backgroundColor: "{colors.neutral}"
  heading:
    textColor: "{colors.text-primary}"
    typography: "{typography.h1}"
  page-subtitle:
    textColor: "{colors.text-tertiary}"
    typography: "{typography.body-md}"
  label-section:
    textColor: "{colors.text-muted}"
    typography: "{typography.label-caps}"
  table-header:
    textColor: "{colors.text-tertiary}"
    typography: "{typography.label-table}"
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#ffffff"
    rounded: "{rounded.md}"
    padding: 8px 16px
    typography: "{typography.body-md}"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.md}"
    padding: 8px 16px
  nav-link:
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.md}"
    padding: 8px 12px
  nav-link-active:
    backgroundColor: "{colors.primary-container}"
    textColor: "{colors.on-primary-container}"
    rounded: "{rounded.md}"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: 16px
  chip-neutral:
    backgroundColor: "{colors.border-subtle}"
    textColor: "{colors.text-emphasis}"
    rounded: "{rounded.full}"
  badge-active:
    backgroundColor: "{colors.primary-container}"
    textColor: "{colors.on-primary-container}"
    rounded: "{rounded.full}"
  badge-inactive:
    backgroundColor: "{colors.surface-muted}"
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.full}"
  action-accent:
    textColor: "{colors.accent}"
  action-warning:
    textColor: "{colors.warning}"
  action-warning-hover:
    backgroundColor: "{colors.warning-container}"
  action-danger:
    textColor: "{colors.danger}"
  action-danger-hover:
    backgroundColor: "{colors.danger-container}"
  banner-error:
    backgroundColor: "{colors.danger-container}"
    textColor: "{colors.danger-text}"
---

## Overview

Functional Operations, not decoration. The Bio Green HR & Payroll System is an
internal tool for plant HR staff running payroll, logging attendance, and
tracking piece-rate output — the UI should read as calm, legible, and
trustworthy, closer to a well-organized spreadsheet than a marketing product.
The palette is sampled directly from the company logo (leaf olive-green, the
vivid emerald glow around the wordmark, true-black text) rather than a
generic Tailwind/SaaS blue-gray, and the whole interface runs tight and dense
— small paddings, small gaps — closer to a ledger than a marketing site.
Flat color only: no gradients, anywhere, on any surface or control.

## Colors

The palette is built on a warm neutral (stone) scale — chosen over the
cooler blue-gray "slate" default specifically to avoid the generic-SaaS
look — with a single green drawn from the logo, plus two semantic colors
reserved for destructive/cautionary actions.

- **Primary (#557a00):** The logo's leaf olive-green, darkened slightly off
  the raw sampled hue (~#78a800) for AA contrast with white button text.
  The single primary call-to-action color ("Add Employee", "Generate
  Payroll", "Log Attendance").
- **Primary Container (#e2f0c6) / On-Primary-Container (#45640a):** The
  active-state pair. "Active" status badges and the selected sidebar tab
  both sit on this light olive field with dark olive text (the sidebar's
  selected tab uses a marginally deeper variant, #33480a, for a touch more
  emphasis).
- **Accent (#00a83c):** The vivid emerald glow sampled from the outline
  around the logo's wordmark, darkened slightly for AA. A brighter,
  single-purpose green reserved for the "Reactivate" row action — never
  used for surfaces or primary buttons.
- **Neutral (#fafaf9):** The page canvas — warm off-white (Tailwind
  `stone-50`), not the cool blue-tinted gray typical of generic dashboard
  templates, so white cards still visibly lift off it.
- **Surface (#ffffff) / Surface Muted (#e7e5e4):** Surface is the default
  card/sidebar/table background and doubles as the base for secondary
  buttons; surface-muted (the same warm-gray tone also used to outline
  cards and the data table) fills an "Inactive" status pill.
- **Border Subtle (#f5f5f4):** Separates items inside a card (e.g. the
  sidebar's logo block from its nav list) and fills neutral chips.
- **Text Primary (#1c1917):** Page and section headings only — a warm
  near-black, echoing the logo's true-black wordmark rather than a cool
  slate-900.
- **Text Emphasis (#44403c):** Short inline labels that need to stand out
  from body copy without being a heading (employment-type chips).
- **Text Secondary (#57534e):** The workhorse secondary tone — form labels,
  buttons, nav links, and primary table-cell data.
- **Text Tertiary (#78716c):** Supporting copy one step quieter than
  secondary — page subtitles, table column headers, KPI card captions.
- **Text Muted (#a8a29e):** The faintest tone — empty-state placeholders,
  disabled icons, and the sidebar's uppercase system labels.
- **Warning (#d97706):** The "Deactivate" action only — amber signals a
  reversible, cautionary state change, never an error. Deliberately *not*
  drawn from the logo — semantic colors stay outside the brand palette so
  they never get confused with a brand accent.
- **Danger (#ef4444) / Danger Text (#b91c1c):** Danger is reserved for the
  "Delete" action; danger-text is the darker red used for inline error
  banner copy on the matching danger-container background.

## Typography

A single system font stack (`system-ui`) throughout — no custom webfonts.
Hierarchy is built with size and weight, not typeface changes, keeping the
tool feeling native and fast rather than "designed."

- **H1 (1.25rem / 600):** Page titles ("Employee Directory", "Dashboard").
- **Data Value (1.5rem / 600):** The large number in a KPI card.
- **Label Caps (0.6875rem / 600, tracked):** The sidebar's uppercase system
  labels ("MENU", "HR & Payroll System") — tracked letter-spacing signals
  "structural chrome," not content.
- **Label Table (0.75rem / 600, untracked):** Uppercase data-table column
  headers — bolder than body text but without the sidebar's tracking, so
  tables don't feel like navigation.
- **Body MD (0.875rem):** Default body copy, form inputs, page subtitles.
- **Body SM (0.75rem):** Secondary/supporting text — helper captions, dense
  button labels, timestamps.

## Layout

A fixed 240px sidebar (logo + nav) beside a fluid main content area with
16px page padding — tight by design, not an oversight. Content within a
page stacks in a single column of cards/sections with 12-16px vertical
rhythm; cards themselves use 10-12px internal padding, not the airier
16-24px common in generic dashboard templates. Multi-column layouts (KPI
card rows, report panels) use CSS grid that collapses to a single column
below the medium breakpoint. Tables are the default way to present list
data — prefer a table over a card grid whenever rows share the same fields.

## Elevation & Depth

Depth is minimal and functional: a single subtle `shadow-sm` lifts cards and
the data table off the neutral background. Modals (e.g. the Add/Edit
Employee dialog) sit on a `black/30` scrim. There is no multi-level elevation
system — everything is either "flat page background" or "one card layer"
above it.

## Shapes

Rounded corners are moderate, never sharp and never pill-shaped except for
status badges and chips:

- **sm (6px):** Small inline elements.
- **md (8px):** The default — buttons, inputs, selects, nav links.
- **lg (12px):** Cards, modals, the table container.
- **full:** Status badges ("Active"/"Inactive"), employment-type chips.

## Components

- **button-primary:** Solid primary-green background, white text, `md`
  radius. The single loudest element on any page — one per page/toolbar,
  used for the page's main creation/generation action.
- **nav-link / nav-link-active:** Sidebar items are plain text+icon by
  default; the active route gets the primary-container background and
  on-primary-container text, never an underline or border.
- **card:** White surface, `lg` radius, `shadow-sm`. The
  universal container for KPI tiles, forms, and grouped content.
- **badge-active / badge-inactive:** Pill-shaped, small, used only for
  employee/record status — never for arbitrary tagging.
- **chip-neutral:** Pill-shaped, quiet gray fill — used for descriptive
  chips (e.g. an employment-type label) that aren't a status.
- **action-accent / action-warning / action-danger:** Icon-only buttons in a
  table's Actions column. Color is the only differentiator between
  "reactivate" (accent green), "cautionary/reversible" (warning amber), and
  "destructive" (danger red) row actions — no icon shape substitutes for
  this color meaning.
- **banner-error:** Full-width inline banner for page-level load/save
  failures — danger-container background, danger-text copy. Distinct from
  the danger *action* color, which is reserved for the Delete button itself.

## Do's and Don'ts

- **Do** use green only for the primary action and active/healthy states.
  **Don't** use green as a general accent or apply it to more than one
  element's background per view.
- **Do** pair the danger color exclusively with the Delete action.
  **Don't** reuse it for validation errors or informational banners — those
  use the separate banner-error component instead.
- **Do** keep every page's header to a title + one-line description, with at
  most one primary button. **Don't** stack multiple prominent CTAs in a
  page header.
- **Do** default to a data table for any list of records with shared fields.
  **Don't** reach for card grids or custom list layouts when a table would
  do — this keeps HR/payroll data scannable and exportable-feeling.
- **Do** use Label Caps only for the sidebar's structural chrome. **Don't**
  apply tracked uppercase styling to table headers — use Label Table (no
  tracking) so tables read as data, not navigation.
- **Do** keep every surface a single flat color. **Don't** use a gradient
  anywhere — not on buttons, headers, cards, or backgrounds — even a subtle
  one. Flat color is what keeps this reading as an operations tool instead
  of a generic SaaS marketing page.
- **Do** keep paddings and gaps tight (see Layout) — this is a dense,
  ledger-like tool. **Don't** default to Tailwind's larger spacing steps
  (`p-6`, `gap-6`, gap-based `space-y-6` and above) just because they're the
  common default elsewhere; they read as too loose for this product.
