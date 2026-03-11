"""
visualize-doc SVG エンジン
===========================
テキスト→SVG図解生成のためのスタイル定義とレイアウト関数。

出力: SVGファイル（ブラウザ表示可能、Figmaで編集可能）
依存: Python標準ライブラリのみ（matplotlib不要）

使い方:
  exec(open('.../svg-engine.py').read())
  svg = build_vertical(config)
  save_svg(svg, '/mnt/user-data/outputs/diagram.svg')
"""

import html as _html
import json as _json
import re as _re
import shutil as _shutil
import subprocess as _subprocess
import os as _os

# Graphviz（dotコマンド）の可用性フラグ
HAS_GRAPHVIZ = _shutil.which('dot') is not None

# ============================================================
# 1. design-system.md パーサー
# ============================================================

def _parse_design_system(md_path):
    """design-system.md を読み込み、デザイントークンを抽出する。"""
    with open(md_path, encoding='utf-8') as f:
        lines = f.readlines()

    section = ''
    tables = {}  # section_name -> list of row dicts
    extra = {}   # section_name -> list of non-table lines
    _header_skipped = {}  # section_name -> bool

    for line in lines:
        line = line.rstrip('\n')
        if line.startswith('## '):
            section = line[3:].strip()
            tables[section] = []
            extra[section] = []
            _header_skipped[section] = False
            continue
        if not section:
            continue
        # テーブル行（| で始まる）
        if line.startswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            # 区切り行をスキップ（--- のみ）
            if not cells or all(set(c) <= set('-: ') for c in cells):
                continue
            # 最初のデータ行はヘッダーなのでスキップ
            if not _header_skipped[section]:
                _header_skipped[section] = True
                continue
            tables[section].append(cells)
        elif line.strip():
            extra[section].append(line.strip())

    return tables, extra


def _load_design_tokens():
    """design-system.md からCOLORS, FONT_FAMILY, FONT, S, ACCENT_CYCLEを構築。"""
    # パス解決: svg-engine.py と同じディレクトリの design-system.md
    _candidates = [
        _os.path.join(_os.path.dirname(__file__), 'design-system.md')
            if '__file__' in dir() else '',
        _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'design-system.md')
            if '__file__' in dir() else '',
    ]
    # exec() 環境用: 既知のスキルパスを試行
    _skill_paths = [
        '/mnt/skills/user/visualize-doc/references/design-system.md',
        _os.path.expanduser('~/.claude/skills/visualize-doc-v2/references/design-system.md'),
    ]
    _candidates.extend(_skill_paths)

    md_path = None
    for p in _candidates:
        if p and _os.path.exists(p):
            md_path = p
            break

    if md_path is None:
        return None  # フォールバック用

    tables, extra = _parse_design_system(md_path)

    # --- COLORS ---
    colors = {}
    # カラーパレット: [キー, 値, 用途]
    for row in tables.get('カラーパレット', []):
        if len(row) >= 2:
            colors[row[0]] = row[1]

    # アクセントカラー: [キー, 値, 意味, 淡色背景]
    accent_keys = []
    for row in tables.get('アクセントカラー', []):
        if len(row) >= 4:
            key, val, _meaning, bg_val = row[0], row[1], row[2], row[3]
            colors[key] = val
            # 淡色背景を bg_xxx キーで登録（link_blue → bg_blue）
            short = key.replace('link_', '').replace('success_', '').replace('highlight_', '').replace('alert_', '')
            colors[f'bg_{short}'] = bg_val
            accent_keys.append(key)

    # アクセント順序
    accent_cycle_keys = accent_keys  # デフォルト: テーブル順
    for line in extra.get('アクセントカラー', []):
        if line.startswith('アクセント順序'):
            continue
        if ',' in line and not line.startswith('#'):
            accent_cycle_keys = [k.strip() for k in line.split(',')]
            break
    accent_cycle = [colors[k] for k in accent_cycle_keys if k in colors]

    # --- FONT ---
    font_family = "'Noto Sans CJK JP', 'Hiragino Sans', 'Yu Gothic', sans-serif"
    for line in extra.get('タイポグラフィ', []):
        if line.startswith('フォント:') or line.startswith('フォント：'):
            font_family = line.split(':', 1)[-1].split('：', 1)[-1].strip()
            break

    font = {}
    for row in tables.get('タイポグラフィ', []):
        if len(row) >= 4:
            level, size, weight, color_key = row[0], row[1], row[2], row[3]
            font[level] = {
                'size': int(size),
                'weight': weight,
                'color': colors.get(color_key, color_key),
            }

    # --- S (spacing + shape) ---
    spacing = {}
    for section_name in ('スペーシング', '形状'):
        for row in tables.get(section_name, []):
            if len(row) >= 2:
                spacing[row[0]] = int(row[1])

    return colors, font_family, font, spacing, accent_cycle


# デザイントークンをロード（失敗時はフォールバック）
_tokens = _load_design_tokens()
if _tokens is not None:
    COLORS, FONT_FAMILY, FONT, S, ACCENT_CYCLE = _tokens
    # FONT_FAMILY をSVG用にクォート付きに整形
    if "'" not in FONT_FAMILY:
        FONT_FAMILY = "'" + "', '".join(f.strip() for f in FONT_FAMILY.split(',')) + "'"
else:
    # design-system.md が見つからない場合のハードコードフォールバック
    COLORS = {
        'bg': '#F5F7FA', 'text_primary': '#2D3436', 'text_secondary': '#636E72',
        'text_caption': '#95A5A6', 'white': '#FFFFFF',
        'alert_red': '#FF7675', 'success_teal': '#00B894',
        'highlight_yellow': '#FDCB6E', 'link_blue': '#74B9FF',
        'purple': '#A29BFE', 'pink': '#FD79A8',
        'bg_blue': '#EBF5FB', 'bg_yellow': '#FEF9E7', 'bg_teal': '#E8F8F5',
        'bg_red': '#FDEDEC', 'bg_purple': '#F0EDFF', 'bg_pink': '#FDEEF4',
        'border_light': '#D5D8DC', 'shadow': '#D5D8DC',
    }
    ACCENT_CYCLE = [
        COLORS['link_blue'], COLORS['success_teal'],
        COLORS['highlight_yellow'], COLORS['alert_red'],
        COLORS['purple'], COLORS['pink'],
    ]
    FONT_FAMILY = "'Noto Sans CJK JP', 'Hiragino Sans', 'Yu Gothic', sans-serif"
    FONT = {
        'title': {'size': 28, 'weight': 'bold', 'color': COLORS['text_primary']},
        'subtitle': {'size': 18, 'weight': 'normal', 'color': COLORS['text_secondary']},
        'heading': {'size': 20, 'weight': 'bold', 'color': COLORS['white']},
        'subheading': {'size': 16, 'weight': 'bold', 'color': COLORS['text_primary']},
        'body': {'size': 14, 'weight': 'normal', 'color': COLORS['text_primary']},
        'caption': {'size': 12, 'weight': 'normal', 'color': COLORS['text_caption']},
    }
    S = {
        'canvas_pad': 60, 'section_gap_lg': 60, 'section_gap_md': 40,
        'section_gap_sm': 24, 'capsule_to_cards': 30, 'subtitle_gap': 12,
        'card_pad_x': 20, 'card_pad_y': 16, 'card_title_gap': 10,
        'card_line_h': 22, 'card_gap_h': 20, 'card_gap_v': 20,
        'arrow_gap': 8, 'card_radius': 8, 'capsule_h': 40,
        'capsule_radius': 20, 'footer_h': 50,
    }

# ============================================================
# 4. ユーティリティ
# ============================================================

def _esc(text):
    """SVG用テキストエスケープ。絵文字も除去。"""
    text = str(text)
    text = _re.sub(r'[\U00010000-\U0010FFFF]', '', text)  # 絵文字除去
    return _html.escape(text)


def _text_width_est(text, font_size):
    """テキスト幅の推定（px）。日本語は全角、英数は半角で計算。"""
    w = 0
    for ch in str(text):
        if ord(ch) > 0x2FFF:
            w += font_size * 0.95  # 日本語全角
        else:
            w += font_size * 0.55  # 英数半角
    return w


def _shadow_filter():
    """SVG影フィルター定義"""
    return '''<filter id="shadow" x="-5%" y="-5%" width="115%" height="115%">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#D5D8DC" flood-opacity="0.4"/>
    </filter>'''


def _arrow_marker():
    """矢印マーカー定義"""
    c = COLORS['text_secondary']
    return f'''<marker id="arrowhead" markerWidth="10" markerHeight="10"
            refX="8" refY="5" orient="auto-start-reverse">
      <polygon points="0 0, 10 5, 0 10" fill="{c}"/>
    </marker>'''


def _svg_header(width, height, title='', desc=''):
    """SVGヘッダー生成"""
    t = _esc(title)
    d = _esc(desc)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {width} {height}"
     width="{width}" height="{height}"
     role="img" aria-labelledby="diagram-title diagram-desc"
     style="font-family: {FONT_FAMILY};">
  <title id="diagram-title">{t}</title>
  <desc id="diagram-desc">{d}</desc>
  <defs>
    {_shadow_filter()}
    {_arrow_marker()}
  </defs>
  <rect width="{width}" height="{height}" fill="{COLORS['bg']}" rx="0"/>
'''


def _svg_footer():
    return '</svg>'


# ============================================================
# 5. SVG要素プリミティブ
# ============================================================

def _svg_text(x, y, text, level='body', anchor='middle', max_width=None):
    """テキスト要素。levelはFONTのキー名。"""
    f = FONT[level]
    t = _esc(text)
    fw = f"font-weight=\"{f['weight']}\"" if f['weight'] != 'normal' else ''
    return (f'  <text x="{x}" y="{y}" text-anchor="{anchor}" '
            f'font-size="{f["size"]}px" {fw} '
            f'fill="{f["color"]}" dominant-baseline="central">{t}</text>\n')


def _svg_rect(x, y, w, h, fill='#FFFFFF', stroke=None, stroke_width=2,
              rx=None, shadow=True):
    """矩形。影付きカード用。"""
    rx = rx if rx is not None else S['card_radius']
    parts = []
    filt = ' filter="url(#shadow)"' if shadow else ''
    sc = f' stroke="{stroke}" stroke-width="{stroke_width}"' if stroke else ''
    parts.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" '
                 f'rx="{rx}" fill="{fill}"{sc}{filt}/>\n')
    return ''.join(parts)


def _svg_capsule(cx, cy, text, color, min_w=160):
    """カプセル型見出し（角丸背景 + 白抜き太字）。"""
    h = S['capsule_h']
    text_w = _text_width_est(text, FONT['heading']['size'])
    w = max(min_w, text_w + 40)
    x = cx - w / 2
    y = cy - h / 2
    rx = S['capsule_radius']
    parts = []
    parts.append(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" '
                 f'rx="{rx}" fill="{color}"/>\n')
    parts.append(_svg_text(cx, cy, text, 'heading'))
    return ''.join(parts), w, h


def _normalize_body(body_input, max_chars_per_line=None):
    """body入力を正規化。str/list/1文字リスト全てに対応。
    max_chars_per_lineを指定すると自動折り返し。"""
    if body_input is None:
        return []
    if isinstance(body_input, str):
        # 文字列がそのまま渡された場合 → 改行で分割
        lines = [l.strip() for l in body_input.split('\n') if l.strip()]
    elif isinstance(body_input, list):
        if len(body_input) == 0:
            return []
        # 1文字ずつ分解されたリストの検出:
        # - 要素数が5以上
        # - 80%以上の要素が1文字（改行を除く）
        non_empty = [x for x in body_input if isinstance(x, str) and x.strip()]
        if len(non_empty) >= 5:
            single_char_count = sum(1 for x in non_empty if len(x.strip()) <= 1)
            ratio = single_char_count / len(non_empty) if non_empty else 0
            if ratio >= 0.8:
                # 1文字ずつ分解されている → 結合して改行で分割
                joined = ''.join(str(x) for x in body_input)
                lines = [l.strip() for l in joined.split('\n') if l.strip()]
                return _wrap_lines(lines, max_chars_per_line)
        # 通常のリスト
        lines = []
        for item in body_input:
            s = str(item).strip()
            if s:
                lines.append(s)
    else:
        lines = [str(body_input)]

    return _wrap_lines(lines, max_chars_per_line)


def _wrap_lines(lines, max_chars_per_line):
    """テキスト行を指定文字数で折り返し"""
    if not max_chars_per_line or max_chars_per_line <= 0:
        return lines
    wrapped = []
    for line in lines:
        while len(line) > max_chars_per_line:
            # 折り返し位置を探す（句読点、スペース、記号を優先）
            break_at = max_chars_per_line
            for sep in ['。', '、', '　', ' ', '）', '）', '→']:
                idx = line.rfind(sep, 0, max_chars_per_line)
                if idx > max_chars_per_line * 0.4:
                    break_at = idx + len(sep)
                    break
            wrapped.append(line[:break_at])
            line = line[break_at:]
        if line:
            wrapped.append(line)
    return wrapped


def _svg_card(x, y, w, title, body_lines, border_color, bg=None):
    """カード（影付き角丸ボックス + タイトル + 本文リスト）。
    高さは内容から自動計算。返り値: (svg_str, 実際の高さ)

    body_lines: str, list[str], またはNone。自動正規化・折り返しされる。"""
    bg = bg or COLORS['white']
    pad_x = S['card_pad_x']
    pad_y = S['card_pad_y']

    # テキスト幅からの文字数上限を計算
    text_area_w = w - 2 * pad_x
    char_w_avg = FONT['body']['size'] * 0.75  # 日英混合の平均文字幅
    max_chars = max(int(text_area_w / char_w_avg), 10)

    # body入力の正規化 + 自動折り返し
    lines = _normalize_body(body_lines, max_chars_per_line=max_chars)

    # 高さ計算
    title_h = FONT['subheading']['size'] + S['card_title_gap'] if title else 0
    body_h = len(lines) * S['card_line_h'] if lines else 0
    h = pad_y + title_h + body_h + pad_y
    h = max(h, 60)  # 最低高さ

    parts = []
    parts.append(_svg_rect(x, y, w, h, fill=bg, stroke=border_color))

    cursor_y = y + pad_y
    if title:
        cursor_y += FONT['subheading']['size'] * 0.5
        parts.append(_svg_text(x + w / 2, cursor_y, title, 'subheading'))
        cursor_y += FONT['subheading']['size'] * 0.5 + S['card_title_gap']

    for line in lines:
        cursor_y += S['card_line_h'] * 0.5
        parts.append(_svg_text(x + pad_x, cursor_y, line, 'body', anchor='start'))
        cursor_y += S['card_line_h'] * 0.5

    return ''.join(parts), h


def _svg_arrow_v(x, y1, y2):
    """垂直矢印（上→下）。"""
    gap = S['arrow_gap']
    return (f'  <line x1="{x}" y1="{y1 + gap}" x2="{x}" y2="{y2 - gap}" '
            f'stroke="{COLORS["text_secondary"]}" stroke-width="2" '
            f'marker-end="url(#arrowhead)"/>\n')


def _svg_arrow_h(x1, x2, y):
    """水平矢印（左→右）。"""
    gap = S['arrow_gap']
    return (f'  <line x1="{x1 + gap}" y1="{y}" x2="{x2 - gap}" y2="{y}" '
            f'stroke="{COLORS["text_secondary"]}" stroke-width="2" '
            f'marker-end="url(#arrowhead)"/>\n')


def _svg_vs_circle(cx, cy, r=22):
    """VS円形ラベル"""
    return (f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{COLORS["text_primary"]}"/>\n'
            f'  <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
            f'font-size="14px" font-weight="bold" fill="{COLORS["white"]}">VS</text>\n')


def _svg_footer_box(x, y, w, text):
    """フッターボックス"""
    h = S['footer_h']
    parts = []
    parts.append(_svg_rect(x, y, w, h, fill=COLORS['bg_teal'],
                           stroke=COLORS['success_teal'], rx=8, shadow=False))
    parts.append(_svg_text(x + w / 2, y + h / 2, text, 'body'))
    return ''.join(parts), h


# ============================================================
# 6. build_vertical() — 縦型セクション図解
# ============================================================

def build_vertical(config, base_width=1000):
    """縦型セクション配置のSVGを生成。

    config keys:
        title: str
        subtitle: str (optional)
        sections: list of section dicts
        connections: list of (from_idx, to_idx) (optional)
        footer: str (optional)

    section types:
        {'type': 'box', 'content': {'heading': str, 'body': [str,...]},
         'color': str (optional)}
        {'type': 'capsule', 'label': str, 'color': str (optional)}
        {'type': 'cards', 'columns': int, 'items': [
            {'title': str, 'body': [str,...], 'color': str}, ...
        ]}

    Returns: SVG string
    """
    pad = S['canvas_pad']
    content_w = base_width - 2 * pad
    cx = base_width / 2

    # --- Pass 1: 高さ計算 + 要素位置の記録 ---
    elements = []  # (type, y_top, y_bottom, cx, data)
    cursor_y = pad

    # タイトル
    cursor_y += FONT['title']['size'] * 0.6
    title_y = cursor_y
    cursor_y += FONT['title']['size'] * 0.6
    if config.get('subtitle'):
        cursor_y += S['subtitle_gap']
        cursor_y += FONT['subtitle']['size'] * 0.6
        subtitle_y = cursor_y
        cursor_y += FONT['subtitle']['size'] * 0.6
    else:
        subtitle_y = None

    cursor_y += S['section_gap_lg']

    sections = config.get('sections', [])
    section_positions = []  # (y_top, y_bottom, cx) for connections

    for i, sec in enumerate(sections):
        sec_top = cursor_y

        if sec['type'] == 'capsule':
            cursor_y += S['capsule_h']
            section_positions.append((sec_top, cursor_y, cx))
            if i < len(sections) - 1:
                next_type = sections[i + 1]['type']
                cursor_y += S['capsule_to_cards'] if next_type == 'cards' else S['section_gap_md']

        elif sec['type'] == 'box':
            content = sec.get('content', {})
            box_w = min(content_w * 0.7, 700)
            text_area_w_box = box_w - 2 * S['card_pad_x']
            char_w_avg_box = FONT['body']['size'] * 0.75
            max_chars_box = max(int(text_area_w_box / char_w_avg_box), 10)
            body = _normalize_body(content.get('body'), max_chars_box)
            title_h = FONT['subheading']['size'] + S['card_title_gap'] if content.get('heading') else 0
            body_h = len(body) * S['card_line_h']
            box_h = S['card_pad_y'] + title_h + body_h + S['card_pad_y']
            box_h = max(box_h, 60)
            cursor_y += box_h
            section_positions.append((sec_top, cursor_y, cx))
            if i < len(sections) - 1:
                cursor_y += S['section_gap_md']

        elif sec['type'] == 'cards':
            columns = sec.get('columns', 3)
            items = sec.get('items', [])
            n_rows = -(-len(items) // columns)
            card_w = (content_w - (columns - 1) * S['card_gap_h']) / columns
            text_area_w = card_w - 2 * S['card_pad_x']
            char_w_avg = FONT['body']['size'] * 0.75
            max_chars = max(int(text_area_w / char_w_avg), 10)

            row_cursor = cursor_y
            for row_i in range(n_rows):
                start = row_i * columns
                row_items = items[start:start + columns]
                max_lines = max(
                    (len(_normalize_body(it.get('body'), max_chars))
                     for it in row_items), default=2)
                title_h = FONT['subheading']['size'] + S['card_title_gap']
                row_h = S['card_pad_y'] + title_h + max_lines * S['card_line_h'] + S['card_pad_y']
                row_h = max(row_h, 60)
                row_cursor += row_h
                if row_i < n_rows - 1:
                    row_cursor += S['card_gap_v']

            section_positions.append((sec_top, row_cursor, cx))
            cursor_y = row_cursor
            if i < len(sections) - 1:
                cursor_y += S['section_gap_md']

    # フッター
    footer_y = None
    if config.get('footer'):
        cursor_y += S['section_gap_lg']
        footer_y = cursor_y
        cursor_y += S['footer_h']

    total_height = cursor_y + pad

    # --- Pass 2: SVG生成 ---
    svg = _svg_header(base_width, total_height,
                      config.get('title', ''), config.get('subtitle', ''))

    # タイトル
    svg += _svg_text(cx, title_y, config.get('title', ''), 'title')
    if subtitle_y:
        svg += _svg_text(cx, subtitle_y, config['subtitle'], 'subtitle')

    # セクション
    cursor_y = title_y + FONT['title']['size'] * 0.6
    if subtitle_y:
        cursor_y = subtitle_y + FONT['subtitle']['size'] * 0.6
    cursor_y += S['section_gap_lg']

    for i, sec in enumerate(sections):
        if sec['type'] == 'capsule':
            color = sec.get('color', COLORS['text_primary'])
            cap_svg, _, _ = _svg_capsule(cx, cursor_y + S['capsule_h'] / 2,
                                         sec.get('label', ''), color)
            svg += cap_svg
            cursor_y += S['capsule_h']
            if i < len(sections) - 1:
                next_type = sections[i + 1]['type']
                cursor_y += S['capsule_to_cards'] if next_type == 'cards' else S['section_gap_md']

        elif sec['type'] == 'box':
            content = sec.get('content', {})
            color = sec.get('color', COLORS['link_blue'])
            box_w = min(content_w * 0.7, 700)
            box_x = pad + (content_w - box_w) / 2
            card_svg, box_h = _svg_card(box_x, cursor_y, box_w,
                                        content.get('heading', ''),
                                        content.get('body', []), color)
            svg += card_svg
            cursor_y += box_h
            if i < len(sections) - 1:
                cursor_y += S['section_gap_md']

        elif sec['type'] == 'cards':
            columns = sec.get('columns', 3)
            items = sec.get('items', [])
            n_rows = -(-len(items) // columns)
            card_w = (content_w - (columns - 1) * S['card_gap_h']) / columns

            for row_i in range(n_rows):
                start = row_i * columns
                row_items = items[start:start + columns]
                # 行の高さを統一
                max_lines = max((len(it.get('body', [])) for it in row_items), default=2)
                title_h = FONT['subheading']['size'] + S['card_title_gap']
                row_h = S['card_pad_y'] + title_h + max_lines * S['card_line_h'] + S['card_pad_y']
                row_h = max(row_h, 60)

                for col_i, item in enumerate(row_items):
                    card_x = pad + col_i * (card_w + S['card_gap_h'])
                    color = item.get('color', ACCENT_CYCLE[
                        (row_i * columns + col_i) % len(ACCENT_CYCLE)])
                    card_svg, _ = _svg_card(card_x, cursor_y, card_w,
                                            item.get('title', ''),
                                            item.get('body', []), color)
                    svg += card_svg

                cursor_y += row_h
                if row_i < n_rows - 1:
                    cursor_y += S['card_gap_v']

            if i < len(sections) - 1:
                cursor_y += S['section_gap_md']

    # 接続矢印
    for conn in config.get('connections', []):
        from_idx, to_idx = conn[0], conn[1]
        if from_idx < len(section_positions) and to_idx < len(section_positions):
            _, y_bot, from_cx = section_positions[from_idx]
            y_top, _, to_cx = section_positions[to_idx]
            svg += _svg_arrow_v((from_cx + to_cx) / 2, y_bot, y_top)

    # フッター
    if config.get('footer') and footer_y is not None:
        ft_svg, _ = _svg_footer_box(pad, footer_y, content_w, config['footer'])
        svg += ft_svg

    svg += _svg_footer()
    return svg


# ============================================================
# 7. build_timeline() — タイムライン / ロードマップ
# ============================================================

def build_timeline(config, base_width=1000):
    """横軸タイムラインのSVGを生成。フェーズを上下交互に配置。

    config keys:
        title: str
        subtitle: str (optional)
        phases: list of phase dicts
            {'label': str, 'period': str (optional), 'body': [str,...],
             'color': str (optional)}
        footer: str (optional)

    Returns: SVG string
    """
    pad = S['canvas_pad']
    cx = base_width / 2
    content_w = base_width - 2 * pad
    phases = config.get('phases', [])
    n = len(phases)
    if n == 0:
        n = 1

    # カード幅・配置
    card_gap = S['card_gap_h']
    card_w = min((content_w - (n - 1) * card_gap) / n, 220)
    total_cards_w = n * card_w + (n - 1) * card_gap
    start_x = pad + (content_w - total_cards_w) / 2

    # テキスト折り返し上限
    text_area_w = card_w - 2 * S['card_pad_x']
    char_w_avg = FONT['body']['size'] * 0.75
    max_chars = max(int(text_area_w / char_w_avg), 10)

    # --- Pass 1: 高さ計算 ---
    cursor_y = pad
    cursor_y += FONT['title']['size'] * 0.6
    title_y = cursor_y
    cursor_y += FONT['title']['size'] * 0.6
    subtitle_y = None
    if config.get('subtitle'):
        cursor_y += S['subtitle_gap']
        cursor_y += FONT['subtitle']['size'] * 0.6
        subtitle_y = cursor_y
        cursor_y += FONT['subtitle']['size'] * 0.6

    cursor_y += S['section_gap_lg']

    # カード高さを事前計算（上下交互配置のため最大高さが必要）
    card_heights = []
    for phase in phases:
        lines = _normalize_body(phase.get('body'), max_chars)
        title_h = FONT['subheading']['size'] + S['card_title_gap'] if phase.get('label') else 0
        body_h = len(lines) * S['card_line_h']
        ch = S['card_pad_y'] + title_h + body_h + S['card_pad_y']
        ch = max(ch, 60)
        card_heights.append(ch)

    max_card_h = max(card_heights) if card_heights else 80
    timeline_line_y_offset = 20  # タイムラインの軸線位置（カード領域の中央付近）

    # レイアウト: 上カード領域 + 軸線 + 下カード領域
    top_card_area = max_card_h + 15  # 上カード + ピリオドラベル分
    axis_area = 40  # 軸線 + ドット
    bottom_card_area = max_card_h + 15

    cards_zone_top = cursor_y
    axis_y = cards_zone_top + top_card_area + axis_area / 2
    cards_zone_bottom = axis_y + axis_area / 2 + bottom_card_area

    cursor_y = cards_zone_bottom

    footer_y = None
    if config.get('footer'):
        cursor_y += S['section_gap_lg']
        footer_y = cursor_y
        cursor_y += S['footer_h']

    total_height = cursor_y + pad

    # --- Pass 2: SVG生成 ---
    svg = _svg_header(base_width, total_height,
                      config.get('title', ''), config.get('subtitle', ''))

    # タイトル
    svg += _svg_text(cx, title_y, config.get('title', ''), 'title')
    if subtitle_y:
        svg += _svg_text(cx, subtitle_y, config['subtitle'], 'subtitle')

    # タイムライン軸線
    line_x1 = start_x + card_w / 2 - 10
    line_x2 = start_x + (n - 1) * (card_w + card_gap) + card_w / 2 + 10
    svg += (f'  <line x1="{line_x1}" y1="{axis_y}" x2="{line_x2}" y2="{axis_y}" '
            f'stroke="{COLORS["border_light"]}" stroke-width="3" '
            f'stroke-linecap="round"/>\n')

    # フェーズごとにカード + ドット + ピリオドラベル
    for i, phase in enumerate(phases):
        card_x = start_x + i * (card_w + card_gap)
        dot_cx = card_x + card_w / 2
        color = phase.get('color', ACCENT_CYCLE[i % len(ACCENT_CYCLE)])
        is_top = (i % 2 == 0)

        # ドット（軸上）
        svg += (f'  <circle cx="{dot_cx}" cy="{axis_y}" r="8" '
                f'fill="{color}" stroke="{COLORS["white"]}" stroke-width="3"/>\n')

        if is_top:
            # カードは軸の上
            card_y = axis_y - axis_area / 2 - card_heights[i]
            # 縦線（カード下端→ドット）
            svg += (f'  <line x1="{dot_cx}" y1="{card_y + card_heights[i]}" '
                    f'x2="{dot_cx}" y2="{axis_y - 10}" '
                    f'stroke="{color}" stroke-width="2" stroke-dasharray="4,3"/>\n')
        else:
            # カードは軸の下
            card_y = axis_y + axis_area / 2
            # 縦線（ドット→カード上端）
            svg += (f'  <line x1="{dot_cx}" y1="{axis_y + 10}" '
                    f'x2="{dot_cx}" y2="{card_y}" '
                    f'stroke="{color}" stroke-width="2" stroke-dasharray="4,3"/>\n')

        # カード
        card_svg, _ = _svg_card(card_x, card_y, card_w,
                                phase.get('label', ''),
                                phase.get('body', []), color)
        svg += card_svg

        # ピリオドラベル（カードの外側）
        if phase.get('period'):
            if is_top:
                period_y = card_y - 8
            else:
                period_y = card_y + card_heights[i] + 16
            svg += _svg_text(dot_cx, period_y, phase['period'], 'caption')

    # フッター
    if config.get('footer') and footer_y is not None:
        ft_svg, _ = _svg_footer_box(pad, footer_y, content_w, config['footer'])
        svg += ft_svg

    svg += _svg_footer()
    return svg


# ============================================================
# 8. build_matrix() — 2軸マトリクス / 比較表
# ============================================================

def build_matrix(config, base_width=1000):
    """2軸マトリクスのSVGを生成。

    config keys:
        title: str
        subtitle: str (optional)
        col_headers: [str, ...]  — 列ヘッダー
        row_headers: [str, ...]  — 行ヘッダー
        cells: [[str or list, ...], ...]  — cells[row][col] の2次元配列
        col_colors: [str, ...] (optional) — 列ごとのアクセント色
        footer: str (optional)

    Returns: SVG string
    """
    pad = S['canvas_pad']
    cx = base_width / 2
    content_w = base_width - 2 * pad

    col_headers = config.get('col_headers', [])
    row_headers = config.get('row_headers', [])
    cells = config.get('cells', [])
    n_cols = len(col_headers)
    n_rows = len(row_headers)
    col_colors = config.get('col_colors',
                            [ACCENT_CYCLE[i % len(ACCENT_CYCLE)] for i in range(n_cols)])

    # 列幅計算（行ヘッダー列 + データ列）
    row_header_w = min(content_w * 0.2, 180)
    data_area_w = content_w - row_header_w
    col_w = data_area_w / max(n_cols, 1)

    # セル内テキスト折り返し
    cell_text_w = col_w - 2 * S['card_pad_x']
    char_w_avg = FONT['body']['size'] * 0.75
    max_chars = max(int(cell_text_w / char_w_avg), 8)

    # 行の高さを事前計算
    header_row_h = S['capsule_h'] + 10
    row_heights = []
    for ri in range(n_rows):
        max_lines = 1
        for ci in range(n_cols):
            cell_val = cells[ri][ci] if ri < len(cells) and ci < len(cells[ri]) else ''
            lines = _normalize_body(cell_val, max_chars)
            max_lines = max(max_lines, len(lines))
        rh = S['card_pad_y'] * 2 + max_lines * S['card_line_h']
        rh = max(rh, 50)
        row_heights.append(rh)

    # --- Pass 1: 高さ計算 ---
    cursor_y = pad
    cursor_y += FONT['title']['size'] * 0.6
    title_y = cursor_y
    cursor_y += FONT['title']['size'] * 0.6
    subtitle_y = None
    if config.get('subtitle'):
        cursor_y += S['subtitle_gap']
        cursor_y += FONT['subtitle']['size'] * 0.6
        subtitle_y = cursor_y
        cursor_y += FONT['subtitle']['size'] * 0.6

    cursor_y += S['section_gap_lg']
    grid_top = cursor_y
    cursor_y += header_row_h  # 列ヘッダー行
    for rh in row_heights:
        cursor_y += rh

    footer_y = None
    if config.get('footer'):
        cursor_y += S['section_gap_lg']
        footer_y = cursor_y
        cursor_y += S['footer_h']

    total_height = cursor_y + pad

    # --- Pass 2: SVG生成 ---
    svg = _svg_header(base_width, total_height,
                      config.get('title', ''), config.get('subtitle', ''))

    svg += _svg_text(cx, title_y, config.get('title', ''), 'title')
    if subtitle_y:
        svg += _svg_text(cx, subtitle_y, config['subtitle'], 'subtitle')

    grid_x = pad + row_header_w

    # 列ヘッダー（カプセル）
    for ci, header in enumerate(col_headers):
        cap_cx = grid_x + ci * col_w + col_w / 2
        cap_cy = grid_top + header_row_h / 2
        color = col_colors[ci] if ci < len(col_colors) else ACCENT_CYCLE[ci % len(ACCENT_CYCLE)]
        cap_svg, _, _ = _svg_capsule(cap_cx, cap_cy, header, color, min_w=col_w * 0.8)
        svg += cap_svg

    # データ行
    row_y = grid_top + header_row_h
    for ri in range(n_rows):
        rh = row_heights[ri]

        # 行の背景（交互色）
        if ri % 2 == 0:
            svg += _svg_rect(pad, row_y, content_w, rh,
                             fill='#FFFFFF', shadow=False, rx=0)
        else:
            svg += _svg_rect(pad, row_y, content_w, rh,
                             fill='#FAFBFC', shadow=False, rx=0)

        # 行ヘッダー
        svg += _svg_text(pad + row_header_w / 2, row_y + rh / 2,
                         row_headers[ri], 'subheading')

        # セル
        for ci in range(n_cols):
            cell_val = cells[ri][ci] if ri < len(cells) and ci < len(cells[ri]) else ''
            lines = _normalize_body(cell_val, max_chars)
            cell_x = grid_x + ci * col_w + S['card_pad_x']
            cell_cy = row_y + S['card_pad_y']
            for li, line in enumerate(lines):
                ly = cell_cy + li * S['card_line_h'] + S['card_line_h'] / 2
                svg += _svg_text(cell_x, ly, line, 'body', anchor='start')

        row_y += rh

    # グリッド線
    # 水平線
    line_y = grid_top + header_row_h
    for ri in range(n_rows + 1):
        svg += (f'  <line x1="{pad}" y1="{line_y}" x2="{pad + content_w}" y2="{line_y}" '
                f'stroke="{COLORS["border_light"]}" stroke-width="1"/>\n')
        if ri < n_rows:
            line_y += row_heights[ri]

    # 垂直線（行ヘッダーとデータ列の境界）
    grid_bottom = grid_top + header_row_h + sum(row_heights)
    svg += (f'  <line x1="{grid_x}" y1="{grid_top + header_row_h}" '
            f'x2="{grid_x}" y2="{grid_bottom}" '
            f'stroke="{COLORS["border_light"]}" stroke-width="1"/>\n')

    # フッター
    if config.get('footer') and footer_y is not None:
        ft_svg, _ = _svg_footer_box(pad, footer_y, content_w, config['footer'])
        svg += ft_svg

    svg += _svg_footer()
    return svg


# ============================================================
# 9. build_journey_map() — CJM / サービスブループリント
# ============================================================

def build_journey_map(config, base_width=1100):
    """横フェーズ×縦レーンのジャーニーマップSVGを生成。

    config keys:
        title: str
        subtitle: str (optional)
        phases: [str, ...]  — フェーズ名（横軸）
        lanes: [
            {'label': str, 'color': str (optional),
             'items': [str_or_list, ...]  — phases と同数。各フェーズのセル内容
            }, ...
        ]
        footer: str (optional)

    Returns: SVG string
    """
    pad = S['canvas_pad']
    cx = base_width / 2
    content_w = base_width - 2 * pad

    phases = config.get('phases', [])
    lanes = config.get('lanes', [])
    n_phases = len(phases)
    n_lanes = len(lanes)

    # レイアウト定数
    lane_label_w = min(content_w * 0.15, 140)
    phase_area_w = content_w - lane_label_w
    phase_w = phase_area_w / max(n_phases, 1)
    phase_header_h = S['capsule_h'] + 16

    # セル内テキスト折り返し
    cell_text_w = phase_w - 2 * S['card_pad_x'] - 8
    char_w_avg = FONT['body']['size'] * 0.75
    max_chars = max(int(cell_text_w / char_w_avg), 8)

    # レーン高さを事前計算（各レーンで最も行数が多いセルに合わせる）
    lane_heights = []
    for lane in lanes:
        items = lane.get('items', [])
        max_lines = 1
        for pi in range(n_phases):
            cell_val = items[pi] if pi < len(items) else ''
            lines = _normalize_body(cell_val, max_chars)
            max_lines = max(max_lines, len(lines))
        lh = S['card_pad_y'] * 2 + max(max_lines, 1) * S['card_line_h']
        lh = max(lh, 55)
        lane_heights.append(lh)

    # --- Pass 1: 高さ計算 ---
    cursor_y = pad
    cursor_y += FONT['title']['size'] * 0.6
    title_y = cursor_y
    cursor_y += FONT['title']['size'] * 0.6
    subtitle_y = None
    if config.get('subtitle'):
        cursor_y += S['subtitle_gap']
        cursor_y += FONT['subtitle']['size'] * 0.6
        subtitle_y = cursor_y
        cursor_y += FONT['subtitle']['size'] * 0.6

    cursor_y += S['section_gap_lg']
    grid_top = cursor_y
    cursor_y += phase_header_h
    for lh in lane_heights:
        cursor_y += lh

    footer_y = None
    if config.get('footer'):
        cursor_y += S['section_gap_lg']
        footer_y = cursor_y
        cursor_y += S['footer_h']

    total_height = cursor_y + pad

    # --- Pass 2: SVG生成 ---
    svg = _svg_header(base_width, total_height,
                      config.get('title', ''), config.get('subtitle', ''))

    svg += _svg_text(cx, title_y, config.get('title', ''), 'title')
    if subtitle_y:
        svg += _svg_text(cx, subtitle_y, config['subtitle'], 'subtitle')

    phase_x0 = pad + lane_label_w  # フェーズ列の開始X

    # フェーズヘッダー（カプセル）
    for pi, phase_name in enumerate(phases):
        cap_cx = phase_x0 + pi * phase_w + phase_w / 2
        cap_cy = grid_top + phase_header_h / 2
        color = ACCENT_CYCLE[pi % len(ACCENT_CYCLE)]
        cap_svg, _, _ = _svg_capsule(cap_cx, cap_cy, phase_name, color,
                                      min_w=phase_w * 0.85)
        svg += cap_svg

    # レーン描画
    lane_y = grid_top + phase_header_h
    for li, lane in enumerate(lanes):
        lh = lane_heights[li]
        lane_color = lane.get('color', ACCENT_CYCLE[li % len(ACCENT_CYCLE)])
        items = lane.get('items', [])

        # レーン背景（交互色）
        bg = '#FFFFFF' if li % 2 == 0 else '#FAFBFC'
        svg += _svg_rect(pad, lane_y, content_w, lh,
                         fill=bg, shadow=False, rx=0)

        # レーン境界線（破線）
        svg += (f'  <line x1="{pad}" y1="{lane_y}" '
                f'x2="{pad + content_w}" y2="{lane_y}" '
                f'stroke="{COLORS["border_light"]}" stroke-width="1" '
                f'stroke-dasharray="6,3"/>\n')

        # レーンラベル（左端、色付きバー + テキスト）
        bar_w = 5
        svg += _svg_rect(pad, lane_y, bar_w, lh,
                         fill=lane_color, shadow=False, rx=0)
        svg += _svg_text(pad + bar_w + lane_label_w / 2, lane_y + lh / 2,
                         lane.get('label', ''), 'subheading')

        # セル内容
        for pi in range(n_phases):
            cell_val = items[pi] if pi < len(items) else ''
            lines = _normalize_body(cell_val, max_chars)
            cell_x = phase_x0 + pi * phase_w + S['card_pad_x']
            cell_top = lane_y + S['card_pad_y']
            for line_i, line in enumerate(lines):
                ly = cell_top + line_i * S['card_line_h'] + S['card_line_h'] / 2
                svg += _svg_text(cell_x, ly, line, 'body', anchor='start')

        lane_y += lh

    # 最下部の境界線
    svg += (f'  <line x1="{pad}" y1="{lane_y}" '
            f'x2="{pad + content_w}" y2="{lane_y}" '
            f'stroke="{COLORS["border_light"]}" stroke-width="1" '
            f'stroke-dasharray="6,3"/>\n')

    # フェーズ間の垂直区切り線
    for pi in range(1, n_phases):
        vx = phase_x0 + pi * phase_w
        svg += (f'  <line x1="{vx}" y1="{grid_top + phase_header_h}" '
                f'x2="{vx}" y2="{lane_y}" '
                f'stroke="{COLORS["border_light"]}" stroke-width="1" '
                f'stroke-dasharray="4,4" opacity="0.5"/>\n')

    # フッター
    if config.get('footer') and footer_y is not None:
        ft_svg, _ = _svg_footer_box(pad, footer_y, content_w, config['footer'])
        svg += ft_svg

    svg += _svg_footer()
    return svg


# ============================================================
# 10. build_layer() — レイヤー図（積み上げ構造）
# ============================================================

def build_layer(config, base_width=1000):
    """下→上に積み上げるレイヤー図のSVGを生成。

    config keys:
        title: str
        subtitle: str (optional)
        layers: [  — 下層から上層の順
            {'label': str, 'body': [str,...] (optional),
             'color': str (optional)}, ...
        ]
        arrows: bool (default True) — レイヤー間の上向き矢印
        footer: str (optional)

    Returns: SVG string
    """
    pad = S['canvas_pad']
    cx = base_width / 2
    content_w = base_width - 2 * pad

    layers = config.get('layers', [])
    show_arrows = config.get('arrows', True)
    n = len(layers)

    # レイヤーの幅（中央寄せ、上層ほど少し狭くするオプション）
    layer_w = min(content_w * 0.85, 800)
    layer_gap = 16 if show_arrows else 8
    arrow_space = 24 if show_arrows else 0

    # テキスト折り返し
    text_area_w = layer_w - 2 * S['card_pad_x']
    char_w_avg = FONT['body']['size'] * 0.75
    max_chars = max(int(text_area_w / char_w_avg), 10)

    # レイヤー高さを事前計算
    layer_heights = []
    for layer in layers:
        lines = _normalize_body(layer.get('body'), max_chars)
        label_h = FONT['subheading']['size'] + (S['card_title_gap'] if lines else 0)
        body_h = len(lines) * S['card_line_h']
        lh = S['card_pad_y'] + label_h + body_h + S['card_pad_y']
        lh = max(lh, 60)
        layer_heights.append(lh)

    # 淡色背景マッピング
    _bg_map = [
        (COLORS['link_blue'], COLORS['bg_blue']),
        (COLORS['success_teal'], COLORS['bg_teal']),
        (COLORS['highlight_yellow'], COLORS['bg_yellow']),
        (COLORS['alert_red'], COLORS['bg_red']),
        (COLORS['purple'], COLORS['bg_purple']),
        (COLORS['pink'], COLORS['bg_pink']),
    ]

    # --- Pass 1: 高さ計算 ---
    cursor_y = pad
    cursor_y += FONT['title']['size'] * 0.6
    title_y = cursor_y
    cursor_y += FONT['title']['size'] * 0.6
    subtitle_y = None
    if config.get('subtitle'):
        cursor_y += S['subtitle_gap']
        cursor_y += FONT['subtitle']['size'] * 0.6
        subtitle_y = cursor_y
        cursor_y += FONT['subtitle']['size'] * 0.6

    cursor_y += S['section_gap_lg']
    layers_zone_top = cursor_y

    # 描画は上→下だが、データは下→上。reversed で上から描画する。
    total_layers_h = sum(layer_heights) + (n - 1) * (layer_gap + arrow_space)
    cursor_y += total_layers_h

    footer_y = None
    if config.get('footer'):
        cursor_y += S['section_gap_lg']
        footer_y = cursor_y
        cursor_y += S['footer_h']

    total_height = cursor_y + pad

    # --- Pass 2: SVG生成 ---
    svg = _svg_header(base_width, total_height,
                      config.get('title', ''), config.get('subtitle', ''))

    svg += _svg_text(cx, title_y, config.get('title', ''), 'title')
    if subtitle_y:
        svg += _svg_text(cx, subtitle_y, config['subtitle'], 'subtitle')

    # レイヤーを上から描画（リストの末尾=最上層から）
    draw_y = layers_zone_top
    drawn_positions = []  # (y_top, y_bottom, layer_idx) 上から順

    for draw_i, orig_i in enumerate(reversed(range(n))):
        layer = layers[orig_i]
        lh = layer_heights[orig_i]
        lx = pad + (content_w - layer_w) / 2

        # 色
        color = layer.get('color', ACCENT_CYCLE[orig_i % len(ACCENT_CYCLE)])
        # 淡色背景を探す
        bg = COLORS['white']
        for accent, light in _bg_map:
            if accent == color:
                bg = light
                break

        # レイヤーボックス
        svg += _svg_rect(lx, draw_y, layer_w, lh,
                         fill=bg, stroke=color, stroke_width=2,
                         rx=S['card_radius'], shadow=True)

        # ラベル
        lines = _normalize_body(layer.get('body'), max_chars)
        inner_y = draw_y + S['card_pad_y'] + FONT['subheading']['size'] * 0.5
        svg += _svg_text(cx, inner_y, layer.get('label', ''), 'subheading')

        if lines:
            inner_y += FONT['subheading']['size'] * 0.5 + S['card_title_gap']
            for line in lines:
                inner_y += S['card_line_h'] * 0.5
                svg += _svg_text(cx, inner_y, line, 'body')
                inner_y += S['card_line_h'] * 0.5

        drawn_positions.append((draw_y, draw_y + lh))
        draw_y += lh

        # 矢印（次のレイヤーとの間）
        if draw_i < n - 1:
            if show_arrows:
                arrow_y1 = draw_y + layer_gap / 2 + arrow_space
                arrow_y2 = draw_y + layer_gap / 2
                svg += _svg_arrow_v(cx, arrow_y1, arrow_y2)
            draw_y += layer_gap + arrow_space

    # フッター
    if config.get('footer') and footer_y is not None:
        ft_svg, _ = _svg_footer_box(pad, footer_y, content_w, config['footer'])
        svg += ft_svg

    svg += _svg_footer()
    return svg


# ============================================================
# 11. build_two_columns() — 左右比較（VS図）
# ============================================================

def build_two_columns(config, base_width=1000):
    """左右比較（VS図）のSVGを生成。

    config keys:
        title, subtitle, left_label, right_label,
        left_color, right_color,
        rows: [{'left': {'title','body'}, 'right': {'title','body'}}, ...],
        vs_label: bool (default True),
        footer: str (optional)

    Returns: SVG string
    """
    pad = S['canvas_pad']
    cx = base_width / 2
    col_gap = 80  # VS用中央ギャップ
    content_w = base_width - 2 * pad
    card_w = (content_w - col_gap) / 2
    left_x = pad
    right_x = pad + card_w + col_gap
    vs_x = pad + card_w + col_gap / 2

    left_color = config.get('left_color', COLORS['link_blue'])
    right_color = config.get('right_color', COLORS['alert_red'])
    rows = config.get('rows', [])

    # --- Pass 1: 高さ計算 ---
    cursor_y = pad
    cursor_y += FONT['title']['size'] * 0.6
    title_y = cursor_y
    cursor_y += FONT['title']['size'] * 0.6
    subtitle_y = None
    if config.get('subtitle'):
        cursor_y += S['subtitle_gap']
        cursor_y += FONT['subtitle']['size'] * 0.6
        subtitle_y = cursor_y
        cursor_y += FONT['subtitle']['size'] * 0.6

    cursor_y += S['section_gap_lg']
    capsule_y = cursor_y + S['capsule_h'] / 2
    cursor_y += S['capsule_h'] + S['capsule_to_cards']

    cards_top_y = cursor_y
    row_heights = []
    text_area_w = card_w - 2 * S['card_pad_x']
    char_w_avg = FONT['body']['size'] * 0.75
    max_chars = max(int(text_area_w / char_w_avg), 10)
    for row in rows:
        left_lines = len(_normalize_body(row.get('left', {}).get('body'), max_chars))
        right_lines = len(_normalize_body(row.get('right', {}).get('body'), max_chars))
        max_lines = max(left_lines, right_lines, 1)
        title_h = FONT['subheading']['size'] + S['card_title_gap']
        rh = S['card_pad_y'] + title_h + max_lines * S['card_line_h'] + S['card_pad_y']
        rh = max(rh, 60)
        row_heights.append(rh)

    cards_total_h = sum(row_heights) + (len(rows) - 1) * S['card_gap_v'] if rows else 0
    cards_bottom_y = cards_top_y + cards_total_h

    cursor_y = cards_bottom_y
    footer_y = None
    if config.get('footer'):
        cursor_y += S['section_gap_lg']
        footer_y = cursor_y
        cursor_y += S['footer_h']

    total_height = cursor_y + pad

    # --- Pass 2: SVG生成 ---
    svg = _svg_header(base_width, total_height,
                      config.get('title', ''), config.get('subtitle', ''))

    svg += _svg_text(cx, title_y, config.get('title', ''), 'title')
    if subtitle_y:
        svg += _svg_text(cx, subtitle_y, config['subtitle'], 'subtitle')

    # カプセル見出し
    left_cap_cx = left_x + card_w / 2
    right_cap_cx = right_x + card_w / 2
    cap_w = card_w * 0.7
    cap_svg, _, _ = _svg_capsule(left_cap_cx, capsule_y,
                                  config.get('left_label', '左'), left_color, min_w=cap_w)
    svg += cap_svg
    cap_svg, _, _ = _svg_capsule(right_cap_cx, capsule_y,
                                  config.get('right_label', '右'), right_color, min_w=cap_w)
    svg += cap_svg

    # カード行
    row_y = cards_top_y
    for ri, row in enumerate(rows):
        rh = row_heights[ri]
        left_data = row.get('left', {})
        right_data = row.get('right', {})
        card_svg, _ = _svg_card(left_x, row_y, card_w,
                                left_data.get('title', ''),
                                left_data.get('body', []), left_color)
        svg += card_svg
        card_svg, _ = _svg_card(right_x, row_y, card_w,
                                right_data.get('title', ''),
                                right_data.get('body', []), right_color)
        svg += card_svg
        row_y += rh + S['card_gap_v']

    # VSラベル（カード群の天地中央）
    if config.get('vs_label', True):
        vs_cy = (cards_top_y + cards_bottom_y) / 2
        svg += _svg_vs_circle(vs_x, vs_cy)

    # フッター
    if config.get('footer') and footer_y is not None:
        ft_svg, _ = _svg_footer_box(pad, footer_y, content_w, config['footer'])
        svg += ft_svg

    svg += _svg_footer()
    return svg


# ============================================================
# 12. build_tree() — ツリー図（階層/ロジック/組織図/マインドマップ）
# ============================================================

def build_tree(config, base_width=1000):
    """ツリー図（階層ツリー/ロジックツリー/組織図/マインドマップ）のSVGを生成。

    config keys:
        title: str
        subtitle: str (optional)
        root: dict — 再帰的ツリー構造
            {'label': str, 'body': str/[str] (optional),
             'children': [child_node, ...] (optional),
             'color': str (optional)}
        direction: 'TB' | 'LR' (default 'TB')
        footer: str (optional)

    Returns: SVG string
    """
    pad = S['canvas_pad']
    direction = config.get('direction', 'TB')
    root_data = config.get('root', {})
    sibling_gap = S['card_gap_h']
    level_gap = 56

    # 淡色背景マッピング
    _bg_map = {
        COLORS['link_blue']: COLORS['bg_blue'],
        COLORS['success_teal']: COLORS['bg_teal'],
        COLORS['highlight_yellow']: COLORS['bg_yellow'],
        COLORS['alert_red']: COLORS['bg_red'],
        COLORS['purple']: COLORS['bg_purple'],
        COLORS['pink']: COLORS['bg_pink'],
    }

    # --- Step 1: ツリーをフラット化 ---
    nodes = []

    def _flatten(data, depth=0, parent_idx=-1):
        idx = len(nodes)
        nodes.append({
            'data': data, 'depth': depth, 'parent_idx': parent_idx,
            'w': 0, 'h': 0, 'subtree_extent': 0,
            'cx': 0, 'cy': 0, 'color': None,
            'children': [], '_body_lines': [],
        })
        for child_data in data.get('children', []):
            child_idx = _flatten(child_data, depth + 1, idx)
            nodes[idx]['children'].append(child_idx)
        return idx

    _flatten(root_data)
    if not nodes:
        return _svg_header(base_width, 200) + _svg_footer()

    max_depth = max(n['depth'] for n in nodes)

    # --- Step 2: ノードサイズ計算 ---
    max_node_w = 240
    min_node_w = 100
    text_area_w = max_node_w - 2 * S['card_pad_x']
    char_w_avg = FONT['body']['size'] * 0.75
    max_chars = max(int(text_area_w / char_w_avg), 10)

    for n in nodes:
        data = n['data']
        label = data.get('label', '')
        body = _normalize_body(data.get('body'), max_chars)
        n['_body_lines'] = body

        label_w = _text_width_est(label, FONT['subheading']['size'])
        body_w = max((_text_width_est(line, FONT['body']['size'])
                      for line in body), default=0)
        text_w = max(label_w, body_w)
        w = text_w + 2 * S['card_pad_x'] + 8
        w = max(w, min_node_w)
        w = min(w, max_node_w)

        label_h = FONT['subheading']['size']
        if body:
            label_h += S['card_title_gap']
        body_h = len(body) * S['card_line_h']
        h = S['card_pad_y'] + label_h + body_h + S['card_pad_y']
        h = max(h, 44)

        n['w'] = w
        n['h'] = h

    # --- Step 3: 色の割り当て ---
    def _assign_colors(idx, branch_color=None):
        nd = nodes[idx]
        data = nd['data']
        if nd['depth'] == 0:
            nd['color'] = data.get('color', COLORS['text_primary'])
            for i, ci in enumerate(nd['children']):
                c = nodes[ci]['data'].get('color',
                    ACCENT_CYCLE[i % len(ACCENT_CYCLE)])
                _assign_colors(ci, c)
        else:
            nd['color'] = data.get('color', branch_color)
            for ci in nd['children']:
                _assign_colors(ci, nd['color'])

    _assign_colors(0)

    # --- Step 4: レイアウト計算 ---
    spread_key = 'w' if direction == 'TB' else 'h'
    depth_key = 'h' if direction == 'TB' else 'w'

    # サブツリー幅をボトムアップ計算
    def _calc_extent(idx):
        nd = nodes[idx]
        children = nd['children']
        if not children:
            nd['subtree_extent'] = nd[spread_key]
        else:
            for ci in children:
                _calc_extent(ci)
            children_total = (sum(nodes[ci]['subtree_extent'] for ci in children)
                            + (len(children) - 1) * sibling_gap)
            nd['subtree_extent'] = max(nd[spread_key], children_total)

    _calc_extent(0)

    # 各深さレベルの最大ノードサイズ
    level_size = {}
    for n in nodes:
        d = n['depth']
        level_size[d] = max(level_size.get(d, 0), n[depth_key])

    # 深さ方向の位置（各レベルの中央）
    level_pos = {}
    pos = 0
    for d in range(max_depth + 1):
        level_pos[d] = pos + level_size[d] / 2
        pos += level_size[d] + level_gap
    total_depth_extent = pos - level_gap

    # 展開方向の位置（トップダウン再帰）
    def _assign_spread(idx, center):
        nd = nodes[idx]
        nd['_spread'] = center
        nd['_depth_pos'] = level_pos[nd['depth']]
        children = nd['children']
        if not children:
            return
        children_total = (sum(nodes[ci]['subtree_extent'] for ci in children)
                        + (len(children) - 1) * sibling_gap)
        start = center - children_total / 2
        for ci in children:
            child_extent = nodes[ci]['subtree_extent']
            _assign_spread(ci, start + child_extent / 2)
            start += child_extent + sibling_gap

    _assign_spread(0, nodes[0]['subtree_extent'] / 2)

    # cx/cy にマッピング
    for n in nodes:
        if direction == 'TB':
            n['cx'] = n['_spread']
            n['cy'] = n['_depth_pos']
        else:
            n['cx'] = n['_depth_pos']
            n['cy'] = n['_spread']

    # --- Step 5: キャンバスサイズ ---
    title_area_h = FONT['title']['size'] * 1.2
    if config.get('subtitle'):
        title_area_h += S['subtitle_gap'] + FONT['subtitle']['size'] * 1.2
    title_area_h += S['section_gap_lg']

    footer_space = 0
    if config.get('footer'):
        footer_space = S['section_gap_lg'] + S['footer_h']

    if direction == 'TB':
        tree_w = nodes[0]['subtree_extent']
        tree_h = total_depth_extent
        canvas_w = max(base_width, tree_w + 2 * pad)
        canvas_h = pad + title_area_h + tree_h + footer_space + pad
        offset_x = (canvas_w - tree_w) / 2
        offset_y = pad + title_area_h
    else:
        tree_w = total_depth_extent
        tree_h = nodes[0]['subtree_extent']
        canvas_w = max(base_width, tree_w + 2 * pad)
        canvas_h = pad + title_area_h + tree_h + footer_space + pad
        offset_x = (canvas_w - tree_w) / 2
        offset_y = pad + title_area_h

    for n in nodes:
        n['cx'] += offset_x
        n['cy'] += offset_y

    # --- Step 6: SVG生成 ---
    cx_canvas = canvas_w / 2
    cursor_y = pad
    cursor_y += FONT['title']['size'] * 0.6
    title_y = cursor_y
    cursor_y += FONT['title']['size'] * 0.6
    subtitle_y = None
    if config.get('subtitle'):
        cursor_y += S['subtitle_gap']
        cursor_y += FONT['subtitle']['size'] * 0.6
        subtitle_y = cursor_y

    svg = _svg_header(canvas_w, canvas_h,
                      config.get('title', ''), config.get('subtitle', ''))

    svg += _svg_text(cx_canvas, title_y, config.get('title', ''), 'title')
    if subtitle_y:
        svg += _svg_text(cx_canvas, subtitle_y, config['subtitle'], 'subtitle')

    # --- エッジ描画（ノードの背面に配置） ---
    for n in nodes:
        if n['parent_idx'] < 0:
            continue
        p = nodes[n['parent_idx']]
        edge_color = n['color']

        if direction == 'TB':
            px, py = p['cx'], p['cy'] + p['h'] / 2
            nx, ny = n['cx'], n['cy'] - n['h'] / 2
            mid_y = (py + ny) / 2
            hdist = abs(nx - px)
            vdist = ny - py
            r = min(8, hdist / 2 if hdist > 1 else 0, vdist / 4)
            r = max(r, 0)

            if hdist < 1:
                svg += (f'  <line x1="{px:.1f}" y1="{py:.1f}" '
                       f'x2="{nx:.1f}" y2="{ny:.1f}" '
                       f'stroke="{edge_color}" stroke-width="2" opacity="0.5"/>\n')
            elif r < 2:
                svg += (f'  <path d="M {px:.1f} {py:.1f} '
                       f'L {px:.1f} {mid_y:.1f} '
                       f'L {nx:.1f} {mid_y:.1f} '
                       f'L {nx:.1f} {ny:.1f}" '
                       f'fill="none" stroke="{edge_color}" '
                       f'stroke-width="2" opacity="0.5"/>\n')
            else:
                dx = 1 if nx > px else -1
                svg += (f'  <path d="M {px:.1f} {py:.1f} '
                       f'L {px:.1f} {mid_y - r:.1f} '
                       f'Q {px:.1f} {mid_y:.1f} {px + dx * r:.1f} {mid_y:.1f} '
                       f'L {nx - dx * r:.1f} {mid_y:.1f} '
                       f'Q {nx:.1f} {mid_y:.1f} {nx:.1f} {mid_y + r:.1f} '
                       f'L {nx:.1f} {ny:.1f}" '
                       f'fill="none" stroke="{edge_color}" '
                       f'stroke-width="2" opacity="0.5"/>\n')
        else:  # LR
            px, py = p['cx'] + p['w'] / 2, p['cy']
            nx, ny = n['cx'] - n['w'] / 2, n['cy']
            mid_x = (px + nx) / 2
            hdist = nx - px
            vdist = abs(ny - py)
            r = min(8, vdist / 2 if vdist > 1 else 0, hdist / 4)
            r = max(r, 0)

            if vdist < 1:
                svg += (f'  <line x1="{px:.1f}" y1="{py:.1f}" '
                       f'x2="{nx:.1f}" y2="{ny:.1f}" '
                       f'stroke="{edge_color}" stroke-width="2" opacity="0.5"/>\n')
            elif r < 2:
                svg += (f'  <path d="M {px:.1f} {py:.1f} '
                       f'L {mid_x:.1f} {py:.1f} '
                       f'L {mid_x:.1f} {ny:.1f} '
                       f'L {nx:.1f} {ny:.1f}" '
                       f'fill="none" stroke="{edge_color}" '
                       f'stroke-width="2" opacity="0.5"/>\n')
            else:
                dy = 1 if ny > py else -1
                svg += (f'  <path d="M {px:.1f} {py:.1f} '
                       f'L {mid_x - r:.1f} {py:.1f} '
                       f'Q {mid_x:.1f} {py:.1f} {mid_x:.1f} {py + dy * r:.1f} '
                       f'L {mid_x:.1f} {ny - dy * r:.1f} '
                       f'Q {mid_x:.1f} {ny:.1f} {mid_x + r:.1f} {ny:.1f} '
                       f'L {nx:.1f} {ny:.1f}" '
                       f'fill="none" stroke="{edge_color}" '
                       f'stroke-width="2" opacity="0.5"/>\n')

    # --- ノード描画 ---
    for n in nodes:
        data = n['data']
        x = n['cx'] - n['w'] / 2
        y = n['cy'] - n['h'] / 2
        w, h = n['w'], n['h']
        color = n['color']
        body_lines = n['_body_lines']
        label = data.get('label', '')

        if n['depth'] == 0:
            # ルートノード: アクセントカラーで塗りつぶし
            svg += _svg_rect(x, y, w, h, fill=color, rx=S['card_radius'])
            if not body_lines:
                svg += (f'  <text x="{n["cx"]:.1f}" y="{n["cy"]:.1f}" '
                       f'text-anchor="middle" '
                       f'font-size="{FONT["subheading"]["size"]}px" '
                       f'font-weight="bold" fill="{COLORS["white"]}" '
                       f'dominant-baseline="central">{_esc(label)}</text>\n')
            else:
                iy = y + S['card_pad_y'] + FONT['subheading']['size'] * 0.5
                svg += (f'  <text x="{n["cx"]:.1f}" y="{iy:.1f}" '
                       f'text-anchor="middle" '
                       f'font-size="{FONT["subheading"]["size"]}px" '
                       f'font-weight="bold" fill="{COLORS["white"]}" '
                       f'dominant-baseline="central">{_esc(label)}</text>\n')
                iy += FONT['subheading']['size'] * 0.5 + S['card_title_gap']
                for line in body_lines:
                    iy += S['card_line_h'] * 0.5
                    svg += (f'  <text x="{n["cx"]:.1f}" y="{iy:.1f}" '
                           f'text-anchor="middle" '
                           f'font-size="{FONT["body"]["size"]}px" '
                           f'fill="{COLORS["white"]}" '
                           f'dominant-baseline="central">'
                           f'{_esc(line)}</text>\n')
                    iy += S['card_line_h'] * 0.5
        else:
            # 非ルート: カードスタイル（淡色背景 + アクセントボーダー）
            bg = _bg_map.get(color, COLORS['white'])
            svg += _svg_rect(x, y, w, h, fill=bg, stroke=color,
                           rx=S['card_radius'])
            if not body_lines:
                svg += _svg_text(n['cx'], n['cy'], label, 'subheading')
            else:
                iy = y + S['card_pad_y'] + FONT['subheading']['size'] * 0.5
                svg += _svg_text(n['cx'], iy, label, 'subheading')
                iy += FONT['subheading']['size'] * 0.5 + S['card_title_gap']
                for line in body_lines:
                    iy += S['card_line_h'] * 0.5
                    svg += _svg_text(n['cx'], iy, line, 'body')
                    iy += S['card_line_h'] * 0.5

    # フッター
    if config.get('footer'):
        footer_y = canvas_h - pad - S['footer_h']
        content_w = canvas_w - 2 * pad
        ft_svg, _ = _svg_footer_box(pad, footer_y, content_w, config['footer'])
        svg += ft_svg

    svg += _svg_footer()
    return svg


# ============================================================
# 13. build_flow() — フローチャート / 状態遷移図
# ============================================================

def build_flow(config, base_width=1000):
    """フローチャート/状態遷移図のSVGを生成。

    config keys:
        title: str
        subtitle: str (optional)
        direction: 'TB' | 'LR' (default 'TB')
        nodes: [
            {'id': str, 'label': str, 'body': str/[str] (optional),
             'type': 'process'|'decision'|'start'|'end' (default 'process'),
             'color': str (optional)},
        ]
        edges: [
            {'from': str, 'to': str, 'label': str (optional)},
        ]
        footer: str (optional)

    Returns: SVG string
    """
    from collections import deque

    pad = S['canvas_pad']
    direction = config.get('direction', 'TB')
    node_list = config.get('nodes', [])
    edge_list = config.get('edges', [])
    sibling_gap = S['card_gap_h'] + 10
    level_gap = 64

    # ノードタイプ別デフォルト色
    _type_colors = {
        'start': COLORS['success_teal'],
        'end': COLORS['alert_red'],
        'decision': COLORS['highlight_yellow'],
    }
    _bg_map = {
        COLORS['link_blue']: COLORS['bg_blue'],
        COLORS['success_teal']: COLORS['bg_teal'],
        COLORS['highlight_yellow']: COLORS['bg_yellow'],
        COLORS['alert_red']: COLORS['bg_red'],
        COLORS['purple']: COLORS['bg_purple'],
        COLORS['pink']: COLORS['bg_pink'],
    }

    # --- Step 1: グラフ構築 ---
    node_map = {}
    node_order = []
    for i, nd in enumerate(node_list):
        nid = nd.get('id', f'n{i}')
        node_map[nid] = {
            'data': nd, 'id': nid, 'layer': 0,
            'in_edges': [], 'out_edges': [],
            'w': 0, 'h': 0, 'cx': 0, 'cy': 0,
            'order_in_layer': i, '_body_lines': [],
            '_type': nd.get('type', 'process'),
        }
        node_order.append(nid)

    for edge in edge_list:
        fid, tid = edge.get('from', ''), edge.get('to', '')
        if fid in node_map and tid in node_map:
            node_map[fid]['out_edges'].append(edge)
            node_map[tid]['in_edges'].append(edge)

    if not node_map:
        return _svg_header(base_width, 200) + _svg_footer()

    # --- Step 2: 後退エッジ検出 + レイヤー割り当て ---
    # DFSで後退エッジ（サイクル形成）を検出
    _dfs_state = {}
    _back_pairs = set()

    def _detect_back(nid):
        _dfs_state[nid] = 'gray'
        for edge in node_map[nid]['out_edges']:
            tid = edge['to']
            if tid not in node_map:
                continue
            if _dfs_state.get(tid) == 'gray':
                _back_pairs.add((edge.get('from', ''), tid))
            elif _dfs_state.get(tid) != 'black':
                _detect_back(tid)
        _dfs_state[nid] = 'black'

    for nid in node_order:
        if _dfs_state.get(nid) != 'black':
            _detect_back(nid)

    # エッジ分類
    forward_edges = []
    back_edges = []
    for edge in edge_list:
        fid, tid = edge.get('from', ''), edge.get('to', '')
        if fid in node_map and tid in node_map:
            if (fid, tid) in _back_pairs:
                back_edges.append(edge)
            else:
                forward_edges.append(edge)

    # DAG上でKahn's algorithm（後退エッジを除外）
    dag_in = {nid: 0 for nid in node_map}
    for edge in forward_edges:
        tid = edge.get('to', '')
        if tid in dag_in:
            dag_in[tid] += 1

    queue = deque([nid for nid, c in dag_in.items() if c == 0])
    if not queue:
        queue.append(node_order[0])

    topo_set = set()
    while queue:
        nid = queue.popleft()
        if nid in topo_set:
            continue
        topo_set.add(nid)
        for edge in node_map[nid]['out_edges']:
            tid = edge['to']
            if (nid, tid) in _back_pairs:
                continue
            if tid in node_map:
                node_map[tid]['layer'] = max(
                    node_map[tid]['layer'],
                    node_map[nid]['layer'] + 1)
                dag_in[tid] -= 1
                if dag_in[tid] <= 0 and tid not in topo_set:
                    queue.append(tid)

    for nid in node_map:
        if nid not in topo_set:
            node_map[nid]['layer'] = 0

    # --- Step 3: レイヤー内順序（重心法） ---
    layers = {}
    for nid, nd in node_map.items():
        layers.setdefault(nd['layer'], []).append(nid)

    max_layer = max(layers.keys()) if layers else 0

    if 0 in layers:
        layers[0].sort(key=lambda nid: node_order.index(nid))
        for i, nid in enumerate(layers[0]):
            node_map[nid]['order_in_layer'] = i

    for l in range(1, max_layer + 1):
        if l not in layers:
            continue
        for nid in layers[l]:
            nd = node_map[nid]
            preds = [e['from'] for e in nd['in_edges']
                     if e['from'] in node_map and node_map[e['from']]['layer'] < l]
            if preds:
                nd['_bary'] = sum(
                    node_map[p]['order_in_layer'] for p in preds) / len(preds)
            else:
                nd['_bary'] = node_order.index(nid)
        layers[l].sort(key=lambda nid: node_map[nid].get('_bary', 0))
        for i, nid in enumerate(layers[l]):
            node_map[nid]['order_in_layer'] = i

    # --- Step 4: ノードサイズ計算 ---
    max_node_w = 220
    min_node_w = 100
    text_area_w = max_node_w - 2 * S['card_pad_x']
    char_w_avg = FONT['body']['size'] * 0.75
    max_chars = max(int(text_area_w / char_w_avg), 10)

    for nid, nd in node_map.items():
        data = nd['data']
        ntype = nd['_type']
        label = data.get('label', '')
        body = _normalize_body(data.get('body'), max_chars)
        nd['_body_lines'] = body

        label_w = _text_width_est(label, FONT['subheading']['size'])
        body_w = max((_text_width_est(line, FONT['body']['size'])
                      for line in body), default=0)
        text_w = max(label_w, body_w)

        if ntype == 'decision':
            inner_w = max(text_w + 30, 80)
            inner_h = max(FONT['subheading']['size'] + 20, 40)
            nd['w'] = inner_w * 1.5
            nd['h'] = inner_h * 1.5
        elif ntype in ('start', 'end'):
            nd['w'] = max(text_w + 40, 120)
            nd['h'] = max(FONT['subheading']['size'] + 24, 44)
        else:
            w = text_w + 2 * S['card_pad_x'] + 8
            w = max(w, min_node_w)
            w = min(w, max_node_w)
            label_h = FONT['subheading']['size']
            if body:
                label_h += S['card_title_gap']
            body_h = len(body) * S['card_line_h']
            h = S['card_pad_y'] + label_h + body_h + S['card_pad_y']
            nd['w'] = w
            nd['h'] = max(h, 44)

    # --- Step 5: 色の割り当て ---
    process_idx = 0
    for nid in node_order:
        if nid not in node_map:
            continue
        nd = node_map[nid]
        data = nd['data']
        ntype = nd['_type']
        if data.get('color'):
            nd['color'] = data['color']
        elif ntype in _type_colors:
            nd['color'] = _type_colors[ntype]
        else:
            nd['color'] = ACCENT_CYCLE[process_idx % len(ACCENT_CYCLE)]
            process_idx += 1

    # --- Step 6: 位置計算 ---
    spread_key = 'w' if direction == 'TB' else 'h'
    depth_key = 'h' if direction == 'TB' else 'w'

    layer_depth = {}
    layer_spread = {}
    for l in range(max_layer + 1):
        nids = layers.get(l, [])
        if not nids:
            continue
        layer_depth[l] = max(node_map[nid][depth_key] for nid in nids)
        layer_spread[l] = (sum(node_map[nid][spread_key] for nid in nids)
                          + (len(nids) - 1) * sibling_gap)

    level_pos = {}
    pos = 0
    for l in range(max_layer + 1):
        if l not in layer_depth:
            continue
        level_pos[l] = pos + layer_depth[l] / 2
        pos += layer_depth[l] + level_gap
    total_depth = pos - level_gap if pos > level_gap else pos

    max_spread = max(layer_spread.values()) if layer_spread else 0

    for l in range(max_layer + 1):
        nids = layers.get(l, [])
        if not nids:
            continue
        total_w = layer_spread[l]
        start = (max_spread - total_w) / 2
        for nid in nids:
            nd = node_map[nid]
            nd['_spread'] = start + nd[spread_key] / 2
            start += nd[spread_key] + sibling_gap
            nd['_depth'] = level_pos[l]

    for nid, nd in node_map.items():
        if direction == 'TB':
            nd['cx'] = nd.get('_spread', 0)
            nd['cy'] = nd.get('_depth', 0)
        else:
            nd['cx'] = nd.get('_depth', 0)
            nd['cy'] = nd.get('_spread', 0)

    # --- Step 7: キャンバスサイズ ---
    title_area_h = FONT['title']['size'] * 1.2
    if config.get('subtitle'):
        title_area_h += S['subtitle_gap'] + FONT['subtitle']['size'] * 1.2
    title_area_h += S['section_gap_lg']

    footer_space = 0
    if config.get('footer'):
        footer_space = S['section_gap_lg'] + S['footer_h']

    back_margin = 40 if back_edges else 0

    if direction == 'TB':
        canvas_w = max(base_width, max_spread + 2 * pad + back_margin)
        canvas_h = pad + title_area_h + total_depth + footer_space + pad
        offset_x = (canvas_w - max_spread) / 2
        offset_y = pad + title_area_h
    else:
        canvas_w = max(base_width, total_depth + 2 * pad)
        canvas_h = pad + title_area_h + max_spread + footer_space + pad + back_margin
        offset_x = (canvas_w - total_depth) / 2
        offset_y = pad + title_area_h

    for nid, nd in node_map.items():
        nd['cx'] += offset_x
        nd['cy'] += offset_y

    # --- Step 8: SVG生成 ---
    cx_canvas = canvas_w / 2
    cursor_y = pad
    cursor_y += FONT['title']['size'] * 0.6
    title_y = cursor_y
    cursor_y += FONT['title']['size'] * 0.6
    subtitle_y = None
    if config.get('subtitle'):
        cursor_y += S['subtitle_gap']
        cursor_y += FONT['subtitle']['size'] * 0.6
        subtitle_y = cursor_y

    svg = _svg_header(canvas_w, canvas_h,
                      config.get('title', ''), config.get('subtitle', ''))
    svg += _svg_text(cx_canvas, title_y, config.get('title', ''), 'title')
    if subtitle_y:
        svg += _svg_text(cx_canvas, subtitle_y, config['subtitle'], 'subtitle')

    edge_color = COLORS['text_secondary']

    # --- 前進エッジ ---
    for edge in forward_edges:
        fid, tid = edge['from'], edge['to']
        fn, tn = node_map[fid], node_map[tid]

        if direction == 'TB':
            # 出発点: ソースの下端（decision は位置で側面出口を判定）
            sx, sy = fn['cx'], fn['cy'] + fn['h'] / 2
            if fn['_type'] == 'decision':
                dx_dist = tn['cx'] - fn['cx']
                if abs(dx_dist) > fn['w'] / 3:
                    side = 1 if dx_dist > 0 else -1
                    sx = fn['cx'] + side * fn['w'] / 2
                    sy = fn['cy']
            ex, ey = tn['cx'], tn['cy'] - tn['h'] / 2
            mid_y = (sy + ey) / 2
            hdist = abs(ex - sx)
            vdist = ey - sy

            if vdist < 1:
                svg += (f'  <line x1="{sx:.1f}" y1="{sy:.1f}" '
                       f'x2="{ex:.1f}" y2="{ey:.1f}" '
                       f'stroke="{edge_color}" stroke-width="2" '
                       f'marker-end="url(#arrowhead)"/>\n')
            elif hdist < 1:
                svg += (f'  <line x1="{sx:.1f}" y1="{sy:.1f}" '
                       f'x2="{ex:.1f}" y2="{ey:.1f}" '
                       f'stroke="{edge_color}" stroke-width="2" '
                       f'marker-end="url(#arrowhead)"/>\n')
            else:
                r = min(8, hdist / 2, vdist / 4)
                r = max(r, 0)
                dx = 1 if ex > sx else -1
                if r < 2:
                    svg += (f'  <path d="M {sx:.1f} {sy:.1f} '
                           f'L {sx:.1f} {mid_y:.1f} '
                           f'L {ex:.1f} {mid_y:.1f} '
                           f'L {ex:.1f} {ey:.1f}" '
                           f'fill="none" stroke="{edge_color}" '
                           f'stroke-width="2" '
                           f'marker-end="url(#arrowhead)"/>\n')
                else:
                    svg += (f'  <path d="M {sx:.1f} {sy:.1f} '
                           f'L {sx:.1f} {mid_y - r:.1f} '
                           f'Q {sx:.1f} {mid_y:.1f} '
                           f'{sx + dx * r:.1f} {mid_y:.1f} '
                           f'L {ex - dx * r:.1f} {mid_y:.1f} '
                           f'Q {ex:.1f} {mid_y:.1f} '
                           f'{ex:.1f} {mid_y + r:.1f} '
                           f'L {ex:.1f} {ey:.1f}" '
                           f'fill="none" stroke="{edge_color}" '
                           f'stroke-width="2" '
                           f'marker-end="url(#arrowhead)"/>\n')

            if edge.get('label'):
                lx = (sx + ex) / 2
                ly = mid_y - 10
                svg += (f'  <rect x="{lx - 20:.1f}" y="{ly - 10:.1f}" '
                       f'width="40" height="16" rx="3" '
                       f'fill="{COLORS["bg"]}" opacity="0.9"/>\n')
                svg += _svg_text(lx, ly, edge['label'], 'caption')

        else:  # LR
            sx, sy = fn['cx'] + fn['w'] / 2, fn['cy']
            if fn['_type'] == 'decision':
                dy_dist = tn['cy'] - fn['cy']
                if abs(dy_dist) > fn['h'] / 3:
                    side = 1 if dy_dist > 0 else -1
                    sx = fn['cx']
                    sy = fn['cy'] + side * fn['h'] / 2
            ex, ey = tn['cx'] - tn['w'] / 2, tn['cy']
            mid_x = (sx + ex) / 2
            hdist = ex - sx
            vdist = abs(ey - sy)

            if hdist < 1:
                svg += (f'  <line x1="{sx:.1f}" y1="{sy:.1f}" '
                       f'x2="{ex:.1f}" y2="{ey:.1f}" '
                       f'stroke="{edge_color}" stroke-width="2" '
                       f'marker-end="url(#arrowhead)"/>\n')
            elif vdist < 1:
                svg += (f'  <line x1="{sx:.1f}" y1="{sy:.1f}" '
                       f'x2="{ex:.1f}" y2="{ey:.1f}" '
                       f'stroke="{edge_color}" stroke-width="2" '
                       f'marker-end="url(#arrowhead)"/>\n')
            else:
                r = min(8, vdist / 2, hdist / 4)
                r = max(r, 0)
                dy = 1 if ey > sy else -1
                if r < 2:
                    svg += (f'  <path d="M {sx:.1f} {sy:.1f} '
                           f'L {mid_x:.1f} {sy:.1f} '
                           f'L {mid_x:.1f} {ey:.1f} '
                           f'L {ex:.1f} {ey:.1f}" '
                           f'fill="none" stroke="{edge_color}" '
                           f'stroke-width="2" '
                           f'marker-end="url(#arrowhead)"/>\n')
                else:
                    svg += (f'  <path d="M {sx:.1f} {sy:.1f} '
                           f'L {mid_x - r:.1f} {sy:.1f} '
                           f'Q {mid_x:.1f} {sy:.1f} '
                           f'{mid_x:.1f} {sy + dy * r:.1f} '
                           f'L {mid_x:.1f} {ey - dy * r:.1f} '
                           f'Q {mid_x:.1f} {ey:.1f} '
                           f'{mid_x + r:.1f} {ey:.1f} '
                           f'L {ex:.1f} {ey:.1f}" '
                           f'fill="none" stroke="{edge_color}" '
                           f'stroke-width="2" '
                           f'marker-end="url(#arrowhead)"/>\n')

            if edge.get('label'):
                lx = mid_x
                ly = (sy + ey) / 2 - 10
                svg += _svg_text(lx, ly, edge['label'], 'caption')

    # --- 後退エッジ（ループ線: 破線 + 曲線） ---
    for edge in back_edges:
        fid, tid = edge['from'], edge['to']
        fn, tn = node_map[fid], node_map[tid]

        if direction == 'TB':
            sx = fn['cx'] + fn['w'] / 2
            sy = fn['cy']
            ex = tn['cx'] + tn['w'] / 2
            ey = tn['cy']
            curve_x = max(sx, ex) + 40
            svg += (f'  <path d="M {sx:.1f} {sy:.1f} '
                   f'C {curve_x:.1f} {sy:.1f} '
                   f'{curve_x:.1f} {ey:.1f} {ex:.1f} {ey:.1f}" '
                   f'fill="none" stroke="{edge_color}" stroke-width="2" '
                   f'stroke-dasharray="6,3" '
                   f'marker-end="url(#arrowhead)"/>\n')
            if edge.get('label'):
                svg += _svg_text(curve_x + 5, (sy + ey) / 2,
                               edge['label'], 'caption', anchor='start')
        else:
            sx = fn['cx']
            sy = fn['cy'] + fn['h'] / 2
            ex = tn['cx']
            ey = tn['cy'] + tn['h'] / 2
            curve_y = max(sy, ey) + 40
            svg += (f'  <path d="M {sx:.1f} {sy:.1f} '
                   f'C {sx:.1f} {curve_y:.1f} '
                   f'{ex:.1f} {curve_y:.1f} {ex:.1f} {ey:.1f}" '
                   f'fill="none" stroke="{edge_color}" stroke-width="2" '
                   f'stroke-dasharray="6,3" '
                   f'marker-end="url(#arrowhead)"/>\n')
            if edge.get('label'):
                svg += _svg_text((sx + ex) / 2, curve_y + 12,
                               edge['label'], 'caption')

    # --- ノード描画 ---
    for nid in node_order:
        if nid not in node_map:
            continue
        nd = node_map[nid]
        data = nd['data']
        x = nd['cx'] - nd['w'] / 2
        y = nd['cy'] - nd['h'] / 2
        w, h = nd['w'], nd['h']
        color = nd['color']
        ntype = nd['_type']
        label = data.get('label', '')
        body_lines = nd['_body_lines']
        bg = _bg_map.get(color, COLORS['white'])

        if ntype == 'decision':
            # ひし形（ダイヤモンド）
            pts = (f'{nd["cx"]:.1f},{y:.1f} '
                   f'{x + w:.1f},{nd["cy"]:.1f} '
                   f'{nd["cx"]:.1f},{y + h:.1f} '
                   f'{x:.1f},{nd["cy"]:.1f}')
            svg += (f'  <polygon points="{pts}" '
                   f'fill="{bg}" stroke="{color}" stroke-width="2" '
                   f'filter="url(#shadow)"/>\n')
            svg += _svg_text(nd['cx'], nd['cy'], label, 'subheading')

        elif ntype in ('start', 'end'):
            # 楕円
            svg += (f'  <ellipse cx="{nd["cx"]:.1f}" '
                   f'cy="{nd["cy"]:.1f}" '
                   f'rx="{w / 2:.1f}" ry="{h / 2:.1f}" '
                   f'fill="{color}" filter="url(#shadow)"/>\n')
            svg += (f'  <text x="{nd["cx"]:.1f}" y="{nd["cy"]:.1f}" '
                   f'text-anchor="middle" '
                   f'font-size="{FONT["subheading"]["size"]}px" '
                   f'font-weight="bold" fill="{COLORS["white"]}" '
                   f'dominant-baseline="central">{_esc(label)}</text>\n')

        else:  # process
            svg += _svg_rect(x, y, w, h, fill=bg, stroke=color,
                           rx=S['card_radius'])
            if not body_lines:
                svg += _svg_text(nd['cx'], nd['cy'], label, 'subheading')
            else:
                iy = y + S['card_pad_y'] + FONT['subheading']['size'] * 0.5
                svg += _svg_text(nd['cx'], iy, label, 'subheading')
                iy += FONT['subheading']['size'] * 0.5 + S['card_title_gap']
                for line in body_lines:
                    iy += S['card_line_h'] * 0.5
                    svg += _svg_text(nd['cx'], iy, line, 'body')
                    iy += S['card_line_h'] * 0.5

    # フッター
    if config.get('footer'):
        footer_y = canvas_h - pad - S['footer_h']
        content_w = canvas_w - 2 * pad
        ft_svg, _ = _svg_footer_box(pad, footer_y, content_w, config['footer'])
        svg += ft_svg

    svg += _svg_footer()
    return svg


# ============================================================
# 8. Graphviz連携（SVG出力に変更）
# ============================================================

def graphviz_to_svg(dot_source, output_path):
    """DOTソースからSVGを生成。Graphviz未インストール時はエラーで案内。"""
    if not HAS_GRAPHVIZ:
        raise RuntimeError(
            "Graphviz (dot) が見つかりません。\n"
            "対処法:\n"
            "  1. SVG直接記述またはSVGエンジン関数で代替する\n"
            "  2. Graphvizをインストールする (brew install graphviz / apt install graphviz)")
    dot_path = '/tmp/_vd_temp.dot'
    with open(dot_path, 'w', encoding='utf-8') as f:
        f.write(dot_source)
    result = _subprocess.run(
        ['dot', '-Tsvg', '-o', output_path, dot_path],
        capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Graphviz error: {result.stderr}")
    return output_path


def graphviz_header(title='', subtitle='', engine='dot', rankdir='TB'):
    """Graphviz DOTヘッダー（既存互換）"""
    label_html = f'<B><FONT POINT-SIZE="20">{_esc(title)}</FONT></B>'
    if subtitle:
        label_html += f'<BR/><FONT POINT-SIZE="13" COLOR="{COLORS["text_secondary"]}">{_esc(subtitle)}</FONT>'
    return (
        f'digraph G {{\n'
        f'  graph [rankdir={rankdir}, bgcolor="{COLORS["bg"]}", '
        f'pad=1.0, nodesep=0.6, ranksep=0.8, '
        f'label=<{label_html}>, labelloc=t, fontname="Noto Sans CJK JP"];\n'
        f'  node [shape=box, style="rounded,filled", fontname="Noto Sans CJK JP", '
        f'fontsize=10, margin="0.25,0.15"];\n'
        f'  edge [color="{COLORS["text_secondary"]}", penwidth=2];\n'
    )


def graphviz_node(node_id, label, role='body', level=0, sublabel=None):
    """Graphvizノード定義（既存互換）"""
    accent, bg = ACCENT_CYCLE[level % len(ACCENT_CYCLE)], COLORS['white']
    if level < len([
        (COLORS['link_blue'], COLORS['bg_blue']),
        (COLORS['success_teal'], COLORS['bg_teal']),
        (COLORS['highlight_yellow'], COLORS['bg_yellow']),
        (COLORS['alert_red'], COLORS['bg_red']),
        (COLORS['purple'], COLORS['bg_purple']),
        (COLORS['pink'], COLORS['bg_pink']),
    ]):
        pair = [
            (COLORS['link_blue'], COLORS['bg_blue']),
            (COLORS['success_teal'], COLORS['bg_teal']),
            (COLORS['highlight_yellow'], COLORS['bg_yellow']),
            (COLORS['alert_red'], COLORS['bg_red']),
            (COLORS['purple'], COLORS['bg_purple']),
            (COLORS['pink'], COLORS['bg_pink']),
        ][level]
        accent, bg = pair

    sizes = {'root': 15, 'heading': 12, 'body': 10}
    fontsize = sizes.get(role, 10)

    if sublabel:
        label_html = (f'<{_esc(label)}<BR/>'
                      f'<FONT POINT-SIZE="9" COLOR="{COLORS["text_caption"]}">'
                      f'{_esc(sublabel)}</FONT>>')
        return (f'  {node_id} [label={label_html}, fontsize={fontsize}, '
                f'fillcolor="{bg}", color="{accent}"];')

    if role == 'root':
        return (f'  {node_id} [label="{_esc(label)}", fontsize={fontsize}, '
                f'fontcolor="{COLORS["white"]}", '
                f'fillcolor="{accent}", color="{accent}"];')
    else:
        return (f'  {node_id} [label="{_esc(label)}", fontsize={fontsize}, '
                f'fillcolor="{bg}", color="{accent}"];')


# ============================================================
# 9. 保存・変換ヘルパー
# ============================================================

def save_svg(svg_str, filepath):
    """SVGを保存"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(svg_str)
    return filepath


def svg_to_png(svg_path, png_path=None, scale=2):
    """SVG→PNG変換（cairosvg使用、任意）"""
    if png_path is None:
        png_path = svg_path.replace('.svg', '.png')
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=scale)
    except ImportError:
        # cairosvg未インストール時はrsvg-convertを試す
        result = _subprocess.run(
            ['rsvg-convert', '-z', str(scale), '-o', png_path, svg_path],
            capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"PNG変換失敗。cairosvgまたはrsvg-convertが必要です。\n{result.stderr}")
    return png_path
