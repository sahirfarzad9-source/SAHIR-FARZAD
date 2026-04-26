// ════════════════════════════════════════════════════════════════════════════
// SearchModal.jsx — Movie search overlay (NEW in Lesson 4)
// ════════════════════════════════════════════════════════════════════════════

import { useState, useEffect, useRef } from 'react';
import { omdbSearch, omdbDetails } from '../utils/api';
import { useApp } from '../context/AppContext';

// ──────────────────── LESSON 4 ────────────────────
// Build the search overlay:
// 1. Text input + Search button → call omdbSearch() → show results grid
// 2. Each result card shows poster + title + year
// 3. Clicking a card → call omdbDetails() → call openMovie() from useApp()
// 4. Close button and Escape key both call onClose()



// ──────────────────── END ─────────────────────────
