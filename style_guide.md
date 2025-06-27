# SmartDesk AI Style Guide (Inspired by Nuggetwise)

## Typography
- **Font Family:** Sans-serif (e.g., Inter, Arial, Helvetica)
- **Title Font Size:** 2rem (32px), bold
- **Subtitle/Body Font Size:** 1rem (16px)
- **Card Title Font Size:** 1.125rem (18px), bold
- **Font Weight:**
  - Title: 700
  - Card Title: 600
  - Body: 400

## Colors
- **Primary (Violet):** #a78bfa (Button, icons)
- **Secondary (Light Gray):** #f3f4f6 (Card background, cancel button)
- **Text (Dark):** #222222
- **Text (Light):** #6b7280
- **Background:** #ffffff
- **Checkbox (Checked):** #a78bfa
- **Checkbox (Unchecked):** #e5e7eb

## Buttons
- **Primary Button:**
  - Background: #a78bfa
  - Text: #fff
  - Border Radius: 12px
  - Font Weight: 600
  - Height: 48px
  - Shadow: Subtle (0 2px 8px rgba(80, 80, 120, 0.08))
- **Cancel Button:**
  - Background: #f3f4f6
  - Text: #222222
  - Border Radius: 12px
  - Font Weight: 600
  - Height: 48px

## Cards
- **Background:** #fff
- **Border Radius:** 18px
- **Shadow:** 0 2px 16px rgba(80, 80, 120, 0.08)
- **Padding:** 32px
- **Spacing Between Cards:** 16px

## Icons
- **Style:** Simple, line or filled (Material/Streamlit icons or emoji)
- **Size:** 24px
- **Color:** #a78bfa (primary), #6b7280 (secondary)
- **Feature Emoji Suggestions:**
  - Login: 🔒
  - Onboarding: 💡
  - Image/Note → Action Items: 📝
  - Chat Assistant: 💬
  - Web Research: 🔎
  - Calendar Agent: 📅

## Layout
- **Main Container:** Centered, max-width 420px
- **Vertical Spacing:** 24px between major sections
- **Horizontal Padding:** 24px
- **Checkbox/Label Gap:** 12px
- **Button Spacing:** 16px between buttons

## Other
- **Corner Radius:** 12-18px (cards, buttons)
- **Drop Shadow:** Soft, subtle
- **White Space:** Generous, especially around cards and buttons

---
**All pages and components must import and call `inject_global_styles()` from `components/style.py` to ensure the Nuggetwise style is applied throughout the app.** 