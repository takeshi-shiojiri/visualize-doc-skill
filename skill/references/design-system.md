# Design System

図解スキルのデザイントークン定義。
svg-engine.py がこのファイルを読み込み、COLORS / FONT / S を自動構築する。

値を変更すると、すべての図解の見た目が一括で変わる。

---

## カラーパレット

| キー | 値 | 用途 |
|------|-----|------|
| bg | #F5F7FA | 図全体の背景 |
| white | #FFFFFF | カード背景 |
| text_primary | #2D3436 | 本文テキスト |
| text_secondary | #636E72 | 補足テキスト |
| text_caption | #95A5A6 | 注釈・ラベル |
| border_light | #D5D8DC | 罫線・区切り線 |
| shadow | #D5D8DC | 影の色 |

## アクセントカラー

| キー | 値 | 意味 | 淡色背景 |
|------|-----|------|---------|
| link_blue | #74B9FF | 入力・接続 | #EBF5FB |
| success_teal | #00B894 | 解決・成功 | #E8F8F5 |
| highlight_yellow | #FDCB6E | 判断・注意 | #FEF9E7 |
| alert_red | #FF7675 | 課題・警告 | #FDEDEC |
| purple | #A29BFE | 比較 | #F0EDFF |
| pink | #FD79A8 | 体験 | #FDEEF4 |

アクセント順序（図解内で色を自動割り当てする際の巡回順）:
link_blue, success_teal, highlight_yellow, alert_red, purple, pink

## タイポグラフィ

フォント: Noto Sans CJK JP, Hiragino Sans, Yu Gothic, sans-serif

| レベル | サイズ | 太さ | 色キー |
|--------|--------|------|--------|
| title | 28 | bold | text_primary |
| subtitle | 18 | normal | text_secondary |
| heading | 20 | bold | white |
| subheading | 16 | bold | text_primary |
| body | 14 | normal | text_primary |
| caption | 12 | normal | text_caption |

## スペーシング

| キー | 値 | 用途 |
|------|-----|------|
| canvas_pad | 60 | 図の外周パディング |
| section_gap_lg | 60 | 大ブロック間（タイトル→本体） |
| section_gap_md | 40 | セクション間 |
| section_gap_sm | 24 | 同一セクション内カード行間 |
| capsule_to_cards | 30 | カプセル見出し→カード |
| subtitle_gap | 12 | タイトル→サブタイトル |
| card_pad_x | 20 | カード内部 左右 |
| card_pad_y | 16 | カード内部 上下 |
| card_title_gap | 10 | カード内タイトル→本文 |
| card_line_h | 22 | カード内本文行間 |
| card_gap_h | 20 | カード間（横方向） |
| card_gap_v | 20 | カード間（縦方向） |
| arrow_gap | 8 | 矢印と要素の隙間 |

## 形状

| キー | 値 | 用途 |
|------|-----|------|
| card_radius | 8 | カード角丸 |
| capsule_h | 40 | カプセル見出し高さ |
| capsule_radius | 20 | カプセル角丸（h/2で完全丸端） |
| footer_h | 50 | フッター高さ |
