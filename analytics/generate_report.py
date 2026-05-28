#!/usr/bin/env python3
"""
RANTUGUESSER — Analytics Report Generator
==========================================

Pulls events from Supabase and generates a single-page HTML report
suitable for client presentation.

Usage
-----
    pip install -r requirements.txt
    export SB_SERVICE_KEY="..."           # service_role key from Supabase
    python generate_report.py
    open report.html

Optional env vars
-----------------
    SB_URL          override Supabase project URL
    DATE_FROM       ISO date, e.g. 2026-04-01
    DATE_TO         ISO date, e.g. 2026-05-31
    OUTPUT_DIR      where to write report.html and events.csv (default: ./)

Security
--------
The service_role key bypasses Row Level Security. Keep it secret.
The game itself uses the public anon/publishable key (insert-only via RLS).
"""

import os
import sys
import json
import base64
import csv
from io import BytesIO
from datetime import datetime
from collections import Counter, defaultdict
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: pip install requests")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
except ImportError:
    sys.exit("Missing dependency: pip install matplotlib")


# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════
SB_URL = os.environ.get('SB_URL', 'https://pryjvqbbhzyvzonbhxmp.supabase.co')
SB_KEY = os.environ.get('SB_SERVICE_KEY', '')
DATE_FROM = os.environ.get('DATE_FROM', '')
DATE_TO = os.environ.get('DATE_TO', '')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', os.path.dirname(os.path.abspath(__file__)))
PAGE_SIZE = 1000

# Brand palette (matches the game canvas)
TEAL   = '#1D5C62'
AMBER  = '#F5A800'
CREAM  = '#F5F1E8'
MUTED  = '#7BA7AB'
GREEN  = '#5BAE7F'
CORAL  = '#C75B47'
INK    = '#222'
LINE   = '#E5E0D2'

CHALLENGE_LABEL = {
    'c1': 'C1 — Escada Analgésica',
    'c2': 'C2 — Farmacovigilância',
    'c3': 'C3 — Via Metabólica',
    'd1': 'Debrief 1',
    'd2': 'Debrief 2',
    'd3': 'Debrief 3',
}

# Funnel sequence used for completion analysis
FUNNEL_SCREENS = ['privacy', 'register', 'intro', 'c1', 'd1', 'c2', 'd2', 'c3', 'd3', 'finale']

# C1 card IDs (defined in the game) → human labels
C1_CARDS = {
    0: 'Paracetamol / AINEs',
    1: 'Opióides fracos + AINEs',
    2: 'Opióides fortes + AINEs',
    3: 'Paracetamol',
    4: 'Opióides fortes',
}
C2_TARGET = 28


# ═══════════════════════════════════════════════════════════════════════
# FETCH
# ═══════════════════════════════════════════════════════════════════════
def fetch_all_events():
    if not SB_KEY:
        print("ERROR: SB_SERVICE_KEY env var is required.")
        print("  Find it at: Supabase Dashboard → Project Settings → API → service_role")
        sys.exit(1)
    headers = {'apikey': SB_KEY, 'Authorization': f'Bearer {SB_KEY}'}
    out = []
    offset = 0
    print(f"Fetching events from {SB_URL}...")
    while True:
        params = [('select', '*'), ('order', 'server_ts.asc'),
                  ('limit', PAGE_SIZE), ('offset', offset)]
        if DATE_FROM:
            params.append(('server_ts', f'gte.{DATE_FROM}'))
        if DATE_TO:
            params.append(('server_ts', f'lte.{DATE_TO}'))
        url = f"{SB_URL}/rest/v1/events?{urlencode(params)}"
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code in (401, 403):
            sys.exit(f"ERROR: Auth failed ({r.status_code}). Check SB_SERVICE_KEY.")
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        print(f"  ...{len(out)} events fetched")
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


# ═══════════════════════════════════════════════════════════════════════
# ANALYZE
# ═══════════════════════════════════════════════════════════════════════
def organize_by_session(events):
    sessions = defaultdict(list)
    for e in events:
        sessions[e['session_id']].append(e)
    # Sort within each session by client_ts (handles batched out-of-order arrivals)
    for sid in sessions:
        sessions[sid].sort(key=lambda x: x.get('client_ts', 0))
    return sessions


def session_furthest_screen(evs):
    """Return the furthest screen reached in a single session."""
    best = -1
    for e in evs:
        if e['event_type'] == 'screen_enter':
            to = (e.get('payload') or {}).get('to')
            if to in FUNNEL_SCREENS:
                idx = FUNNEL_SCREENS.index(to)
                if idx > best:
                    best = idx
    return FUNNEL_SCREENS[best] if best >= 0 else 'privacy'


def compute_funnel(sessions):
    """For each step in FUNNEL_SCREENS, count sessions that reached it."""
    counts = Counter()
    counts['privacy'] = len(sessions)  # everyone with a session_start lands on privacy
    for sid, evs in sessions.items():
        reached = set()
        for e in evs:
            if e['event_type'] == 'screen_enter':
                reached.add((e.get('payload') or {}).get('to'))
            if e['event_type'] == 'session_complete':
                reached.add('finale')
        for s in reached:
            if s in FUNNEL_SCREENS:
                counts[s] += 1
    return [(s, counts.get(s, 0)) for s in FUNNEL_SCREENS]


def compute_screen_times(events):
    """Average ms spent on each screen, from screen_enter.prev_screen_ms."""
    sums = defaultdict(list)
    for e in events:
        if e['event_type'] != 'screen_enter':
            continue
        p = e.get('payload') or {}
        frm, ms = p.get('from'), p.get('prev_screen_ms', 0)
        if frm and ms and ms > 0 and ms < 30 * 60 * 1000:  # cap at 30 min outliers
            sums[frm].append(ms)
    return {k: (sum(v) / len(v) / 1000.0, len(v)) for k, v in sums.items() if v}


def compute_session_durations(events):
    durations = []
    for e in events:
        if e['event_type'] == 'session_complete':
            t = (e.get('payload') or {}).get('t_total_ms', 0)
            if t > 0 and t < 60 * 60 * 1000:
                durations.append(t / 1000.0)
    return durations


def compute_first_try_accuracy(events):
    """% of sessions where each challenge was correct on the first attempt."""
    # Group answers by session
    first_answers = defaultdict(dict)  # session_id → {c1: bool, c2: bool, c3: bool}
    for e in events:
        if e['event_type'] in ('c1_answer', 'c2_answer', 'c3_answer'):
            ch = e['event_type'][:2]
            sid = e['session_id']
            if ch not in first_answers[sid]:  # only first attempt
                first_answers[sid][ch] = bool((e.get('payload') or {}).get('correct'))
    result = {}
    for ch in ('c1', 'c2', 'c3'):
        attempts = [v[ch] for v in first_answers.values() if ch in v]
        if attempts:
            result[ch] = (sum(attempts) / len(attempts), len(attempts))
        else:
            result[ch] = (0.0, 0)
    return result


def compute_c1_wrong_slots(events):
    """For first-try wrong C1 attempts, count slot placements per card."""
    # slot_counts[slot_idx][card_id] = times
    slot_counts = {0: Counter(), 1: Counter(), 2: Counter()}
    seen_sessions = set()
    for e in events:
        if e['event_type'] != 'c1_answer':
            continue
        sid = e['session_id']
        if sid in seen_sessions:
            continue
        seen_sessions.add(sid)
        p = e.get('payload') or {}
        slots = p.get('slots') or []
        for i, card in enumerate(slots[:3]):
            if card is not None:
                slot_counts[i][card] += 1
    return slot_counts


def compute_c2_guesses(events):
    """First-try C2 guess distribution."""
    seen = set()
    guesses = []
    for e in events:
        if e['event_type'] != 'c2_answer':
            continue
        sid = e['session_id']
        if sid in seen:
            continue
        seen.add(sid)
        g = (e.get('payload') or {}).get('guess')
        if isinstance(g, (int, float)):
            guesses.append(int(g))
    return guesses


def compute_c3_zones(events):
    """First-try C3 zone choices."""
    seen = set()
    counts = Counter()
    for e in events:
        if e['event_type'] != 'c3_answer':
            continue
        sid = e['session_id']
        if sid in seen:
            continue
        seen.add(sid)
        z = (e.get('payload') or {}).get('zone')
        if z:
            counts[z] += 1
    return counts


def compute_register_friction(events):
    """Average friction metrics across all register_complete events."""
    samples = []
    for e in events:
        if e['event_type'] != 'register_complete':
            continue
        p = e.get('payload') or {}
        f = p.get('friction') or {}
        samples.append({
            't_total': p.get('t_register_ms', 0) / 1000.0,
            'type': f.get('typeFocusMs', 0) / 1000.0,
            'uls': f.get('ulsFocusMs', 0) / 1000.0,
            'inst': f.get('instFocusMs', 0) / 1000.0,
            'inputs': f.get('instInputCount', 0),
        })
    if not samples:
        return None
    avg = {}
    for k in ('t_total', 'type', 'uls', 'inst', 'inputs'):
        vals = [s[k] for s in samples]
        avg[k] = sum(vals) / len(vals)
    avg['n'] = len(samples)
    return avg


def compute_device_breakdown(events):
    counts = Counter()
    for e in events:
        if e['event_type'] != 'session_start':
            continue
        d = (e.get('payload') or {}).get('device') or {}
        os_ = d.get('os', 'unknown')
        form = d.get('form', 'unknown')
        counts[f"{os_} / {form}"] += 1
    return counts


def compute_institutions(sessions):
    """Top institutions by completed-session count + avg score."""
    inst_complete = Counter()
    inst_scores = defaultdict(list)
    inst_started = Counter()
    for sid, evs in sessions.items():
        inst = ''
        completed = False
        for e in evs:
            if not inst and e.get('institution'):
                inst = e['institution']
            if e['event_type'] == 'session_complete':
                completed = True
                p = e.get('payload') or {}
                ts = p.get('total_score')
                if isinstance(ts, (int, float)):
                    inst_scores[inst].append(ts)
        if inst:
            inst_started[inst] += 1
            if completed:
                inst_complete[inst] += 1
    rows = []
    for inst, started in inst_started.most_common():
        if not inst:
            continue
        scores = inst_scores.get(inst, [])
        avg_score = sum(scores) / len(scores) if scores else 0
        rows.append({
            'inst': inst,
            'started': started,
            'completed': inst_complete.get(inst, 0),
            'avg_score': avg_score,
        })
    return rows


def compute_restart_rate(sessions, devices_seen=None):
    """Sessions that ended at finale and the deck shows another initSt afterward.
    Heuristic: institution + close session_start times don't really help.
    Instead just report restart events seen via session_start frequency per inst.
    Simpler: count session_complete with a subsequent screen_enter back to privacy."""
    restarts = 0
    completed = 0
    for sid, evs in sessions.items():
        complete_idx = None
        for i, e in enumerate(evs):
            if e['event_type'] == 'session_complete':
                complete_idx = i
                completed += 1
                break
        if complete_idx is not None:
            for e in evs[complete_idx + 1:]:
                if e['event_type'] == 'screen_enter' and (e.get('payload') or {}).get('to') == 'privacy':
                    restarts += 1
                    break
    return restarts, completed


# ═══════════════════════════════════════════════════════════════════════
# CHARTS  (return base64-encoded PNG strings)
# ═══════════════════════════════════════════════════════════════════════
def _save_fig(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def _style(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(LINE)
    ax.spines['bottom'].set_color(LINE)
    ax.tick_params(colors=INK, labelsize=10)
    ax.title.set_color(TEAL)
    ax.yaxis.label.set_color(INK)
    ax.xaxis.label.set_color(INK)


def chart_funnel(funnel):
    """Horizontal bar chart with absolute counts + %."""
    labels = [s for s, _ in funnel]
    values = [v for _, v in funnel]
    base = values[0] if values and values[0] else 1
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.barh(labels, values, color=TEAL, edgecolor='white')
    bars[0].set_color(AMBER)  # privacy = starting point
    bars[-1].set_color(GREEN)  # finale = completion
    for i, (label, v) in enumerate(zip(labels, values)):
        pct = 100.0 * v / base if base else 0
        ax.text(v, i, f"  {v}  ({pct:.0f}%)", va='center', color=INK, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel('Sessions')
    ax.set_title('Engagement funnel — sessions reaching each screen')
    _style(ax)
    ax.set_xlim(0, max(values) * 1.25 if values else 1)
    return _save_fig(fig)


def chart_first_try(accuracy):
    labels = [CHALLENGE_LABEL[ch] for ch in ('c1', 'c2', 'c3')]
    pcts = [accuracy[ch][0] * 100 for ch in ('c1', 'c2', 'c3')]
    ns = [accuracy[ch][1] for ch in ('c1', 'c2', 'c3')]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, pcts, color=[TEAL, TEAL, TEAL], edgecolor='white', width=0.55)
    for b, pct, n in zip(bars, pcts, ns):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 2,
                f"{pct:.0f}%\nn={n}", ha='center', color=INK, fontsize=10)
    ax.set_ylim(0, 110)
    ax.set_ylabel('% correct on first try')
    ax.set_title('First-try accuracy per challenge')
    _style(ax)
    return _save_fig(fig)


def chart_c1_wrong_slots(slot_counts):
    """For each of the 3 slots, show distribution of card placements (first try)."""
    slots = [0, 1, 2]
    cards = list(C1_CARDS.keys())
    matrix = [[slot_counts[s].get(c, 0) for c in cards] for s in slots]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    bottom = [0] * len(slots)
    palette = [AMBER, TEAL, GREEN, MUTED, CORAL]
    for ci, card_id in enumerate(cards):
        vals = [m[ci] for m in matrix]
        ax.bar(slots, vals, bottom=bottom, color=palette[ci],
               edgecolor='white', label=C1_CARDS[card_id])
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_xticks(slots)
    ax.set_xticklabels(['Slot 1 (correto: Paracetamol/AINEs)',
                        'Slot 2 (correto: Opióides fracos + AINEs)',
                        'Slot 3 (correto: Opióides fortes + AINEs)'])
    ax.set_ylabel('First-try placements')
    ax.set_title('C1 — Which card did HCPs place in each slot? (first attempt)')
    ax.legend(loc='upper right', fontsize=8, frameon=False)
    _style(ax)
    return _save_fig(fig)


def chart_c2_guesses(guesses):
    fig, ax = plt.subplots(figsize=(9, 3.8))
    if not guesses:
        ax.text(0.5, 0.5, 'No data yet', ha='center', va='center', color=MUTED)
        return _save_fig(fig)
    lo, hi = min(min(guesses), 0), max(max(guesses), 60)
    bins = list(range(lo, hi + 2, 2))
    ax.hist(guesses, bins=bins, color=TEAL, edgecolor='white')
    ax.axvline(C2_TARGET, color=AMBER, linewidth=2, label=f'Correct: {C2_TARGET}')
    ax.set_xlabel('Guessed value')
    ax.set_ylabel('First-try guesses')
    ax.set_title('C2 — Distribution of first-try guesses (correct = 28)')
    ax.legend(frameon=False)
    _style(ax)
    return _save_fig(fig)


def chart_c3_zones(counts):
    labels = ['Via Metabólica\nPreferencial (correto)', 'Outra Via (incorreto)']
    values = [counts.get('p2', 0), counts.get('p1', 0)]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    if not sum(values):
        ax.text(0.5, 0.5, 'No data yet', ha='center', va='center', color=MUTED)
        return _save_fig(fig)
    bars = ax.bar(labels, values, color=[GREEN, CORAL], edgecolor='white', width=0.55)
    total = sum(values)
    for b, v in zip(bars, values):
        pct = 100.0 * v / total if total else 0
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + total * 0.02,
                f"{v}  ({pct:.0f}%)", ha='center', color=INK, fontsize=10)
    ax.set_ylabel('First-try drops')
    ax.set_title('C3 — Pathway chosen on first attempt')
    _style(ax)
    return _save_fig(fig)


def chart_screen_times(times):
    """Average seconds per screen."""
    order = ['register', 'intro', 'c1', 'd1', 'c2', 'd2', 'c3', 'd3', 'finale', 'iec']
    data = [(s, times.get(s, (0, 0))) for s in order if s in times]
    if not data:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.text(0.5, 0.5, 'No data yet', ha='center', va='center', color=MUTED)
        return _save_fig(fig)
    labels = [d[0] for d in data]
    secs = [d[1][0] for d in data]
    ns = [d[1][1] for d in data]
    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.barh(labels, secs, color=TEAL, edgecolor='white')
    for b, s, n in zip(bars, secs, ns):
        ax.text(b.get_width() + max(secs) * 0.01, b.get_y() + b.get_height() / 2,
                f"  {s:.1f}s  (n={n})", va='center', color=INK, fontsize=9)
    ax.set_xlabel('Average seconds')
    ax.set_title('Average time per screen')
    ax.set_xlim(0, max(secs) * 1.25 if secs else 1)
    ax.invert_yaxis()
    _style(ax)
    return _save_fig(fig)


def chart_device(counts):
    if not counts:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, 'No data yet', ha='center', va='center', color=MUTED)
        return _save_fig(fig)
    items = counts.most_common()
    labels = [k for k, _ in items]
    values = [v for _, v in items]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    bars = ax.barh(labels, values, color=MUTED, edgecolor='white')
    total = sum(values)
    for b, v in zip(bars, values):
        pct = 100.0 * v / total if total else 0
        ax.text(b.get_width() + max(values) * 0.01, b.get_y() + b.get_height() / 2,
                f"  {v}  ({pct:.0f}%)", va='center', color=INK, fontsize=10)
    ax.set_xlabel('Sessions')
    ax.set_title('Device breakdown (OS / form factor)')
    ax.set_xlim(0, max(values) * 1.25)
    ax.invert_yaxis()
    _style(ax)
    return _save_fig(fig)


# ═══════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════
def kpi_card(label, value, sub=''):
    return f'''
    <div class="kpi">
      <div class="kpi-value">{value}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-sub">{sub}</div>
    </div>'''


def fmt_seconds(s):
    if s is None:
        return '—'
    if s < 60:
        return f'{s:.0f}s'
    m, s = divmod(int(s), 60)
    return f'{m}m {s:02d}s'


def render_html(stats, charts, date_range):
    rows_html = ''
    for r in stats['institutions'][:15]:
        rows_html += f'''<tr>
          <td>{r['inst'] or '<em>(unknown)</em>'}</td>
          <td class="num">{r['started']}</td>
          <td class="num">{r['completed']}</td>
          <td class="num">{r['avg_score']:.0f}</td>
        </tr>'''

    friction = stats['friction']
    friction_html = ''
    if friction:
        friction_html = f'''
        <div class="grid-2">
          <div>
            <h3>Register completion</h3>
            <p>Average total time: <strong>{friction['t_total']:.1f}s</strong> (n={friction['n']})</p>
            <p>Time per field (focus duration):</p>
            <ul>
              <li>Tipo de profissional: <strong>{friction['type']:.1f}s</strong></li>
              <li>ULS / Grupo: <strong>{friction['uls']:.1f}s</strong></li>
              <li>Pesquisa de instituição: <strong>{friction['inst']:.1f}s</strong></li>
            </ul>
            <p>Avg keystrokes in institution search: <strong>{friction['inputs']:.1f}</strong></p>
          </div>
        </div>'''
    else:
        friction_html = '<p class="muted">No register_complete events yet.</p>'

    return f'''<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="utf-8">
<title>RANTUGUESSER — Analytics Report</title>
<style>
  body {{ font: 14px/1.5 -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          color: {INK}; background: {CREAM}; margin: 0; padding: 40px; }}
  .wrap {{ max-width: 980px; margin: 0 auto; }}
  header {{ border-bottom: 2px solid {AMBER}; padding-bottom: 20px; margin-bottom: 32px; }}
  header h1 {{ color: {TEAL}; font-size: 28px; margin: 0 0 6px; letter-spacing: -0.01em; }}
  header .sub {{ color: {MUTED}; font-size: 13px; }}
  section {{ background: white; border-radius: 12px; padding: 28px; margin-bottom: 24px;
             box-shadow: 0 2px 12px rgba(29, 92, 98, 0.06); }}
  section h2 {{ color: {TEAL}; font-size: 18px; margin: 0 0 4px; }}
  section .lede {{ color: {MUTED}; font-size: 13px; margin-bottom: 18px; }}
  img.chart {{ max-width: 100%; height: auto; display: block; margin: 8px 0; }}
  .kpi-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
  .kpi {{ background: white; border-radius: 10px; padding: 18px;
          box-shadow: 0 2px 8px rgba(29, 92, 98, 0.05); text-align: center; }}
  .kpi-value {{ color: {AMBER}; font-size: 32px; font-weight: 800; line-height: 1; }}
  .kpi-label {{ color: {TEAL}; font-size: 13px; font-weight: 600; margin-top: 6px; }}
  .kpi-sub {{ color: {MUTED}; font-size: 11px; margin-top: 4px; min-height: 14px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }}
  th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid {LINE}; }}
  th {{ color: {TEAL}; font-weight: 600; background: {CREAM}; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .muted {{ color: {MUTED}; }}
  footer {{ color: {MUTED}; font-size: 11px; padding: 24px 0; text-align: center; }}
  @media print {{ body {{ padding: 12px; background: white; }}
                  section {{ box-shadow: none; border: 1px solid {LINE}; }}
                  .kpi {{ box-shadow: none; border: 1px solid {LINE}; }} }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>RANTUGUESSER — Relatório Analítico</h1>
  <div class="sub">{date_range} &nbsp;·&nbsp; gerado em {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</header>

<section>
  <h2>Sumário Executivo</h2>
  <div class="lede">Métricas-chave de engagement e participação.</div>
  <div class="kpi-row">
    {kpi_card('Sessões iniciadas', f"{stats['sessions_started']}")}
    {kpi_card('Sessões completas', f"{stats['sessions_completed']}",
              sub=f"{stats['completion_rate']:.0f}% completion rate")}
    {kpi_card('Duração média', fmt_seconds(stats['avg_duration']),
              sub=f"sessão completa")}
    {kpi_card('Instituições alcançadas', f"{len(stats['institutions'])}",
              sub=f"distintas")}
  </div>
</section>

<section>
  <h2>Funil de engagement</h2>
  <div class="lede">Onde os utilizadores abandonam a experiência.</div>
  <img class="chart" src="data:image/png;base64,{charts['funnel']}">
</section>

<section>
  <h2>Conhecimento prévio dos HCPs</h2>
  <div class="lede">Percentagem de respostas corretas à primeira tentativa por desafio. Reflete o que os profissionais de saúde já sabem.</div>
  <img class="chart" src="data:image/png;base64,{charts['first_try']}">
</section>

<section>
  <h2>C1 — Distribuição de respostas erradas</h2>
  <div class="lede">Qual carta os HCPs colocaram em cada slot (primeira tentativa). Revela os equívocos mais comuns sobre a Escada Analgésica.</div>
  <img class="chart" src="data:image/png;base64,{charts['c1_wrong']}">
</section>

<section>
  <h2>C2 — Distribuição dos palpites</h2>
  <div class="lede">Quantos reports de farmacovigilância os HCPs estimam que a Acemetacina teve em Portugal. Resposta correta: 28.</div>
  <img class="chart" src="data:image/png;base64,{charts['c2_guesses']}">
</section>

<section>
  <h2>C3 — Via metabólica escolhida</h2>
  <div class="lede">Primeira escolha de via metabólica preferencial. Resposta correta: Fase II (Glucoronoconjugação).</div>
  <img class="chart" src="data:image/png;base64,{charts['c3_zones']}">
</section>

<section>
  <h2>Tempo por ecrã</h2>
  <div class="lede">Tempo médio que os utilizadores passam em cada ecrã do jogo. Alta no debrief = boa retenção da informação científica.</div>
  <img class="chart" src="data:image/png;base64,{charts['screen_times']}">
</section>

<section>
  <h2>Fricção no registo</h2>
  <div class="lede">Tempo gasto em cada campo do ecrã de registo.</div>
  {friction_html}
</section>

<section>
  <h2>Dispositivos utilizados</h2>
  <div class="lede">Sistema operativo e tipo de dispositivo.</div>
  <img class="chart" src="data:image/png;base64,{charts['device']}">
</section>

<section>
  <h2>Top instituições</h2>
  <div class="lede">As 15 instituições com mais sessões iniciadas.</div>
  <table>
    <thead>
      <tr>
        <th>Instituição</th>
        <th class="num">Sessões iniciadas</th>
        <th class="num">Sessões completas</th>
        <th class="num">Score médio</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</section>

<section>
  <h2>Métricas de UX</h2>
  <div class="grid-2">
    <div>
      <p><strong>Taxa de restart</strong>: {stats['restart_rate']:.0f}%</p>
      <p class="muted">({stats['restart_count']} restarts em {stats['sessions_completed']} sessões completas)</p>
    </div>
    <div>
      <p><strong>Duração média de sessão completa</strong>: {fmt_seconds(stats['avg_duration'])}</p>
      <p class="muted">Excluindo sessões abandonadas.</p>
    </div>
  </div>
</section>

<footer>
  Dados anonimizados &nbsp;·&nbsp; Não é recolhida informação diretamente identificativa<br>
  Total de eventos analisados: {stats['total_events']:,}
</footer>

</div>
</body>
</html>'''


def write_csv(events, path):
    if not events:
        return
    keys = ['session_id', 'institution', 'event_type', 'payload', 'client_ts', 'server_ts']
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(keys)
        for e in events:
            row = []
            for k in keys:
                v = e.get(k, '')
                if isinstance(v, (dict, list)):
                    v = json.dumps(v, ensure_ascii=False)
                row.append(v)
            w.writerow(row)


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    events = fetch_all_events()
    if not events:
        print("No events found. Has the game been played yet?")
        return

    # Write CSV for ad-hoc analysis
    csv_path = os.path.join(OUTPUT_DIR, 'events.csv')
    write_csv(events, csv_path)
    print(f"Wrote {csv_path}")

    sessions = organize_by_session(events)

    # Aggregate stats
    funnel = compute_funnel(sessions)
    durations = compute_session_durations(events)
    accuracy = compute_first_try_accuracy(events)
    c1_slots = compute_c1_wrong_slots(events)
    c2_guesses = compute_c2_guesses(events)
    c3_zones = compute_c3_zones(events)
    screen_times = compute_screen_times(events)
    friction = compute_register_friction(events)
    devices = compute_device_breakdown(events)
    institutions = compute_institutions(sessions)
    restarts, completed = compute_restart_rate(sessions)

    sessions_started = funnel[0][1] if funnel else 0
    sessions_completed = funnel[-1][1] if funnel else 0

    stats = {
        'sessions_started': sessions_started,
        'sessions_completed': sessions_completed,
        'completion_rate': 100.0 * sessions_completed / sessions_started if sessions_started else 0,
        'avg_duration': sum(durations) / len(durations) if durations else None,
        'restart_count': restarts,
        'restart_rate': 100.0 * restarts / completed if completed else 0,
        'institutions': institutions,
        'friction': friction,
        'total_events': len(events),
    }

    # Render charts
    print("Rendering charts...")
    charts = {
        'funnel': chart_funnel(funnel),
        'first_try': chart_first_try(accuracy),
        'c1_wrong': chart_c1_wrong_slots(c1_slots),
        'c2_guesses': chart_c2_guesses(c2_guesses),
        'c3_zones': chart_c3_zones(c3_zones),
        'screen_times': chart_screen_times(screen_times),
        'device': chart_device(devices),
    }

    date_range = ''
    if DATE_FROM or DATE_TO:
        date_range = f"Período: {DATE_FROM or '…'} a {DATE_TO or '…'}"
    else:
        first_ts = events[0].get('server_ts', '')[:10]
        last_ts = events[-1].get('server_ts', '')[:10]
        date_range = f"Período: {first_ts} a {last_ts}"

    html = render_html(stats, charts, date_range)
    html_path = os.path.join(OUTPUT_DIR, 'report.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Wrote {html_path}")
    print(f"\nDone. Open with:  open {html_path}")


if __name__ == '__main__':
    main()
