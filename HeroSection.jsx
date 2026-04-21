// ════════════════════════════════════════════════════════════════════════════
// HeroSection.jsx — Main chat interface (NEW in Lesson 3)
// ════════════════════════════════════════════════════════════════════════════

import { useState, useEffect, useRef } from 'react';
import { useApp } from '../context/AppContext';
import { parseAIText } from '../utils/textParser';
import { STAGE, AGE, CATEGORIES_BY_AGE, MOODS_BY_AGE, LANGUAGES } from '../constants';

// ──────────────────── LESSON 3 ────────────────────
// Build the full chat interface:
// 1. TypingDots — three bouncing dots while CineBot is thinking
// 2. SpecialContent — renders interactive widgets (mood-greeting, age-picker,
//    category-picker, mood-picker, language-picker, age-switch-offer)
// 3. ChatRow — renders one bot or user message bubble
// 4. ChatPage (default export) — the main component with:
//    - Welcome message on first load
//    - 6 onboarding step handlers (name → mood → age → genres → vibe → language)
//    - handleSend for free chat
//    - CHIPS quick-suggestion buttons
//    - Full JSX return with header, messages area, chips, input bar



// ──────────────────── END ─────────────────────────
