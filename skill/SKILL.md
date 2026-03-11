---
name: visualize-doc-v2
description: |
  テキスト情報を分析し、内容に最適な図解タイプを自動選択してSVG画像として出力するスキル。
  トリガー条件：
  - 「図解して」「図にして」「ビジュアライズして」「ダイアグラムにして」等の指示
  - NotionページURLと共に視覚化を依頼された場合
  - セッション内容やリサーチ結果を画像として整理したいという依頼
  - 特定の図解タイプ名（フローチャート、ロジックツリー、CJM等）を指定された場合
  ※ グラフ・チャート（棒グラフ、円グラフ等のデータ可視化）は対象外。
---

# visualize-doc — テキスト→SVG図解 生成スキル

テキスト情報（Notion、会話、リサーチ結果等）を構造分析し、
最適な図解タイプを選択して**SVGファイル**を生成する。
SVGはブラウザで直接表示でき、Figma等で後編集も可能。

## 対応する6カテゴリ / 26種の図解タイプ

1. **全体像・分類**: 階層ツリー、マインドマップ、マトリクス、ベン図、オントロジー
2. **因果・メカニズム**: 因果ループ図、ロジックツリー、IPO図、フィードバック図
3. **プロセス・手順**: フローチャート、シーケンス図、スイムレーン図、タイムライン、状態遷移図
4. **関係性・構造**: レイヤー図、コンポーネント図、ネットワーク図、概念地図
5. **比較・意思決定**: 比較表、ポジショニングマップ、ギャップ図、トレードオフ曲線
6. **体験・認知**: カスタマージャーニーマップ、サービスブループリント、ペルソナ→課題→価値図

---

## ワークフロー

### Step 1: 入力取得

| ソース | 取得方法 |
|--------|---------|
| NotionページURL | `notion-fetch` で本文取得 |
| テキスト / コピペ | そのまま使用 |
| 会話コンテキスト | 直近のセッション内容を抽出 |
| ファイル(PDF等) | アップロードされたファイルから読み取り |

### Step 2: 構造分析 → 図解タイプ選択

#### 2-1. カテゴリ自動判定ルール

| シグナル（内容の特徴） | → カテゴリ |
|---------------------|-----------|
| 階層、分類、カテゴリ、種類、包含 | → 1. 全体像・分類 |
| 原因、結果、因果、影響、仕組み | → 2. 因果・メカニズム |
| 手順、ステップ、フロー、分岐、時系列 | → 3. プロセス・手順 |
| 構成、依存、レイヤー、接続、連携 | → 4. 関係性・構造 |
| 比較、選定、評価、差分、ギャップ | → 5. 比較・意思決定 |
| 体験、ジャーニー、ペルソナ、感情 | → 6. 体験・認知 |

#### 2-2. カテゴリ内の図解タイプ選択

`references/diagram-catalog.md` の選択ヒントに基づき具体的な図解タイプを決定。

#### 2-3. レンダリング方式の判定

**★ レンダリング優先順位**: SVGエンジン関数 → Graphviz → SVG直接記述（上から順に検討）

| 方式 | 対象 | 関数 |
|------|------|------|
| **SVGエンジン関数** | 縦型セクション、概要図、IPO図 | `build_vertical()` |
| **SVGエンジン関数** | タイムライン、ロードマップ | `build_timeline()` |
| **SVGエンジン関数** | マトリクス、比較表 | `build_matrix()` |
| **SVGエンジン関数** | ジャーニーマップ、サービスブループリント | `build_journey_map()` |
| **SVGエンジン関数** | レイヤー図、技術スタック、OSI模型 | `build_layer()` |
| **SVGエンジン関数** | 左右比較、VS図、ギャップ図 | `build_two_columns()` |
| **SVGエンジン関数** | 階層ツリー、ロジックツリー、マインドマップ、組織図 | `build_tree()` |
| **SVGエンジン関数** | フローチャート、状態遷移図、因果ループ図 | `build_flow()` |
| **Graphviz → SVG** | ネットワーク図、コンポーネント図等（上記でカバーできないグラフ） | `graphviz_to_svg()` |
| **SVG直接記述** | 上記すべてでカバーできない特殊な図解 | — |

#### 2-4. ユーザー確認

```
📊 図解タイプの提案:
- カテゴリ: [カテゴリ名]
- 図解タイプ: [タイプ名]
- 理由: [選択理由を1文で]

この図解タイプで生成しますか？
```

ユーザーが特定の図解タイプを指定している場合、確認は省略してよい。

### Step 3: 図解生成

#### 3-1. エンジン読み込み（★ 毎回必須）

**図解を生成するたびに、必ず以下を実行すること。**
同一セッション内で2回目以降の図解でも省略してはならない。

```python
exec(open('/mnt/skills/user/visualize-doc/references/svg-engine.py').read())
```

> **注意**: Chat/Coworkの `/mnt/skills/user/` に配置されていない場合はパスを読み替える。

読み込み後に使える関数・変数:
- `HAS_GRAPHVIZ` — Graphviz可用性フラグ（`True`/`False`）。Graphviz系を使う前に必ず確認する
- `build_vertical(config)` — 縦型セクション図解
- `build_timeline(config)` — 水平タイムライン・ロードマップ
- `build_matrix(config)` — 2軸マトリクス・比較表
- `build_journey_map(config)` — カスタマージャーニーマップ・サービスブループリント
- `build_layer(config)` — レイヤー図・アーキテクチャ図
- `build_two_columns(config)` — 左右比較（VS図）
- `build_tree(config)` — 階層ツリー・ロジックツリー・組織図・マインドマップ
- `build_flow(config)` — フローチャート・状態遷移図・因果ループ図
- `graphviz_header()`, `graphviz_node()` — Graphviz DOTヘルパー
- `graphviz_to_svg(dot_source, path)` — DOT→SVG変換（要`HAS_GRAPHVIZ`チェック）
- `save_svg(svg_str, path)` — SVG保存
- `svg_to_png(svg_path)` — SVG→PNG変換（任意）

#### 3-2. SVGエンジン関数で生成する場合

**★ 座標の手計算は禁止。必ずSVGエンジン関数を使用すること。**

```python
# 縦型セクション（概要図、IPO図、レイヤー図等）
config = {
    'title': '...',
    'subtitle': '...',   # optional
    'sections': [...],    # box, capsule, cards
    'connections': [...], # optional: [(from, to), ...]
    'footer': '...',      # optional
}
svg = build_vertical(config)
save_svg(svg, '/mnt/user-data/outputs/diagram.svg')
```

**★ body の書き方（最重要ルール）:**

bodyには**表示したい行ごとの文字列リスト**を渡す。
1行が長い場合はエンジンが自動折り返しするので、**無理に短くする必要はない**。

```python
# ✅ 正しい例: 各要素が「表示したい1行」
'body': ['手順が決まっていて、同じ材料を入れれば同じ料理ができる']
'body': ['line-analyze', '商品URL → LINE施策3パターン']

# ❌ 間違い: 文字列をそのまま渡す（1文字ずつ分解される）
'body': '手順が決まっていて...'

# ❌ 間違い: 1文字ずつリストにする
'body': ['手', '順', 'が', '決', ...]
```

```python
# タイムライン・ロードマップ
config = {
    'title': '...',
    'subtitle': '...',   # optional
    'phases': [
        {'label': 'フェーズ名', 'period': 'Q1',  # optional
         'body': ['説明テキスト'], 'color': COLORS['link_blue']},  # color optional
        ...
    ],
    'footer': '...',      # optional
}
svg = build_timeline(config)
save_svg(svg, '/mnt/user-data/outputs/diagram.svg')
```

```python
# マトリクス・比較表
config = {
    'title': '...',
    'subtitle': '...',   # optional
    'col_headers': ['列A', '列B', '列C'],
    'row_headers': ['行1', '行2'],
    'cells': [
        ['セルA1', 'セルB1', 'セルC1'],  # 行1のデータ
        ['セルA2', 'セルB2', 'セルC2'],  # 行2のデータ
    ],
    'col_colors': [COLORS['link_blue'], ...],  # optional
    'footer': '...',      # optional
}
svg = build_matrix(config)
save_svg(svg, '/mnt/user-data/outputs/diagram.svg')
```

```python
# カスタマージャーニーマップ・サービスブループリント
config = {
    'title': '...',
    'subtitle': '...',   # optional
    'phases': ['認知', '検討', '購入', '利用'],  # 横軸フェーズ
    'lanes': [
        {'label': 'ユーザー行動', 'color': COLORS['link_blue'],  # color optional
         'items': ['検索する', '比較する', '購入する', '使う']},  # phasesと同数
        {'label': 'タッチポイント',
         'items': ['広告', 'LP', 'EC', 'アプリ']},
    ],
    'footer': '...',      # optional
}
svg = build_journey_map(config)
save_svg(svg, '/mnt/user-data/outputs/diagram.svg')
```

```python
# レイヤー図・アーキテクチャ図（下層→上層の順で定義）
config = {
    'title': '...',
    'subtitle': '...',   # optional
    'layers': [
        {'label': 'インフラ層', 'body': ['AWS, Docker'],
         'color': COLORS['link_blue']},  # color optional
        {'label': 'アプリ層', 'body': ['Next.js, FastAPI']},
        {'label': 'UI層', 'body': ['React Components']},
    ],
    'arrows': True,       # レイヤー間の矢印（default: True）
    'footer': '...',      # optional
}
svg = build_layer(config)
save_svg(svg, '/mnt/user-data/outputs/diagram.svg')
```

```python
# 左右比較（VS図、ギャップ図）
config = {
    'title': '...',
    'left_label': '...', 'right_label': '...',
    'left_color': COLORS['link_blue'],
    'right_color': COLORS['alert_red'],
    'rows': [{'left': {...}, 'right': {...}}, ...],
    'footer': '...',  # optional
}
svg = build_two_columns(config)
save_svg(svg, '/mnt/user-data/outputs/diagram.svg')
```

```python
# 階層ツリー・ロジックツリー・組織図・マインドマップ
config = {
    'title': '...',
    'subtitle': '...',   # optional
    'direction': 'TB',   # 'TB'(上→下) or 'LR'(左→右), default 'TB'
    'root': {
        'label': 'ルートノード',
        'body': ['補足テキスト'],  # optional
        'children': [
            {'label': '子ノード1', 'body': ['説明'],
             'children': [
                 {'label': '孫ノード', 'body': ['詳細']},
             ]},
            {'label': '子ノード2'},
        ],
    },
    'footer': '...',      # optional
}
svg = build_tree(config)
save_svg(svg, '/mnt/user-data/outputs/diagram.svg')
```

```python
# フローチャート・状態遷移図・因果ループ図
config = {
    'title': '...',
    'subtitle': '...',   # optional
    'direction': 'TB',   # 'TB'(上→下) or 'LR'(左→右), default 'TB'
    'nodes': [
        {'id': 'start', 'label': '開始', 'type': 'start'},
        {'id': 'step1', 'label': '処理1', 'body': ['詳細説明']},
        {'id': 'check', 'label': '条件分岐?', 'type': 'decision'},
        {'id': 'step2', 'label': '処理2'},
        {'id': 'end', 'label': '終了', 'type': 'end'},
    ],
    'edges': [
        {'from': 'start', 'to': 'step1'},
        {'from': 'step1', 'to': 'check'},
        {'from': 'check', 'to': 'step2', 'label': 'Yes'},
        {'from': 'check', 'to': 'end', 'label': 'No'},
        {'from': 'step2', 'to': 'end'},
    ],
    'footer': '...',      # optional
}
# node type: 'process'(default), 'decision'(菱形), 'start'(楕円/緑), 'end'(楕円/赤)
svg = build_flow(config)
save_svg(svg, '/mnt/user-data/outputs/diagram.svg')
```

#### 3-3. Graphviz系で生成する場合

**★ Graphviz可用性チェック**: エンジン読み込み後、`HAS_GRAPHVIZ` フラグで利用可否を確認する。
`False` の場合はSVG直接記述にフォールバックすること。

```python
if HAS_GRAPHVIZ:
    dot = graphviz_header(title='...', subtitle='...')
    dot += graphviz_node('n1', 'ルートノード', role='root', level=0)
    dot += graphviz_node('n2', '子ノード', role='heading', level=1)
    dot += '  n1 -> n2;\n'
    dot += '}\n'
    graphviz_to_svg(dot, '/mnt/user-data/outputs/diagram.svg')
else:
    # SVG直接記述でフォールバック（3-4参照）
    pass
```

#### 3-4. SVG直接記述の場合（最終手段）

上記でカバーできない図解のみ。以下のルールを必ず守る:

- **viewBox**: `0 0 [width] [height]`（高さはコンテンツに合わせて自動計算）
- **フォント**: `FONT_FAMILY` 変数を使用（`'Noto Sans CJK JP', 'Hiragino Sans', sans-serif`）
- **色**: `COLORS` 辞書の値のみ使用（ハードコード禁止）
- **余白**: `S` 辞書の値を参照（`S['canvas_pad']`=60px, `S['section_gap_lg']`=60px 等）
- **アクセシビリティ**: `<title>` と `<desc>` を必ず含める
- **矢印**: `<marker>` を `<defs>` に定義して使用
- **テキストエスケープ**: `_esc()` を使用

#### 3-5. 品質チェック（生成後）

- [ ] 日本語テキストが正しく表示されているか
- [ ] 要素の重なりがないか
- [ ] カラーがCOLORS辞書の値を使っているか
- [ ] 余白が十分か
- [ ] 矢印が要素間に正しく接続されているか
- [ ] SVGエンジン関数を使用したか？（手計算していないか）

### Step 4: 出力

1. SVGを `/mnt/user-data/outputs/` に保存
2. `present_files` で提示
3. 簡潔な説明を添える

**PNG変換**: ユーザーがPNGを求めた場合は `svg_to_png()` で変換する。

---

## デザイン仕様

`references/design-system.md` に外部化済み。SVGエンジンが起動時に自動読み込みする。
手動でのカラーコードや余白値のハードコードは禁止。必ず `COLORS`, `FONT`, `S` 辞書を参照すること。

---

## 制約とエッジケース

### 要素数の上限

| 図解タイプ | 推奨上限 |
|-----------|---------|
| ツリー系 | 深さ4段、幅8ノード |
| フローチャート | 15ステップ |
| CJM | 6フェーズ×5レーン |

上限を超える場合はユーザーに分割を提案する。

### やらないこと

- データの数値可視化（棒グラフ、円グラフ等）
- アイソメトリック3D表現
- アニメーション/インタラクティブ出力

---

## references/ の参照タイミング

| ファイル | いつ読むか |
|---------|----------|
| `svg-engine.py` | **★ 毎回**: 図解生成のたびに必ずexec()する |
| `diagram-catalog.md` | **必要時**: カテゴリ内の選択に迷った場合 |
| `design-system.md` | **読まない**: svg-engine.pyが自動読み込み。デザイントークン変更時のみ編集 |
