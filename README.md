# visualize-doc-v2

テキスト情報を分析し、内容に最適な図解タイプを自動選択してSVG画像として出力する **Claude Code スキル**です。

## 対応図解タイプ（26種）

| カテゴリ | 図解タイプ |
|---------|-----------|
| 全体像・分類 | 概要図、階層ツリー、マインドマップ、マトリクス、ベン図、オントロジー |
| 因果・メカニズム | 因果ループ図、ロジックツリー、IPO図、フィードバック図 |
| プロセス・手順 | フローチャート、シーケンス図、スイムレーン図、タイムライン、状態遷移図 |
| 関係性・構造 | レイヤー図、コンポーネント図、ネットワーク図、概念地図 |
| 比較・意思決定 | 比較表、ポジショニングマップ、ギャップ図、トレードオフ曲線 |
| 体験・認知 | CJM、サービスブループリント、ペルソナ図 |

## サンプルギャラリー

全26種の図解サンプルを確認できます: https://gallery-xi-green.vercel.app

## インストール

### 方法1: スクリプトで自動インストール

```bash
# Git clone の場合
git clone https://github.com/<org>/visualize-doc-skill.git
cd visualize-doc-skill
./install.sh

# ZIP ダウンロードの場合
# 1. このリポジトリページの「Code」→「Download ZIP」からDL
# 2. 展開して中に入る
cd visualize-doc-skill-main
./install.sh
```

### 方法2: 手動コピー

```bash
cp -r skill/ ~/.claude/skills/visualize-doc-v2/
```

## 使い方

Claude Code で以下のように話しかけるだけです:

```
「LINE CRM施策の全体像を図解して」
「ユーザー登録フローをフローチャートにして」
「React / Vue / Svelte を比較するマトリクスを作って」
```

### トリガーワード

- 「図解して」「図にして」「ビジュアライズして」「ダイアグラムにして」
- 特定の図解タイプ名（フローチャート、ロジックツリー、CJM 等）を指定

## 前提条件

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) がインストール済みであること
- Python 3.8+（SVGエンジンの実行に必要）
- Graphviz（オプション: ネットワーク図・コンポーネント図で使用。未インストールでもSVG直接記述で代替）

## ディレクトリ構成

```
skill/                    # Claude Code スキル本体
├── SKILL.md              # スキル定義
├── references/
│   ├── svg-engine.py     # SVG生成エンジン（8種のビルダー関数）
│   ├── design-system.md  # デザイントークン定義
│   └── diagram-catalog.md # 図解タイプカタログ
└── evals/
    └── evals.json        # 評価テストケース

gallery/                  # サンプルギャラリー（参考資料）
├── index.html            # ギャラリーWebページ
├── generate_samples.py   # サンプルSVG生成スクリプト
└── *.svg                 # 26枚のサンプル図解
```

## ライセンス

MIT
