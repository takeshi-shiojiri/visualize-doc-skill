"""
カタログギャラリー用サンプルSVG一括生成スクリプト
===================================================
26種の図解タイプ全てのサンプルSVGを生成する。
"""
import os
import sys

# svg-engine.py を読み込み
engine_path = os.path.join(os.path.dirname(__file__), '..', 'references', 'svg-engine.py')
exec(open(engine_path).read())

OUTPUT_DIR = os.path.dirname(__file__)

def save(name, svg):
    path = os.path.join(OUTPUT_DIR, f'{name}.svg')
    save_svg(svg, path)
    print(f'  ✓ {name}.svg')


# ============================================================
# 1. build_vertical — LINE CRM施策の全体像
# ============================================================
def gen_vertical():
    config = {
        'title': 'LINE CRM施策の全体像',
        'subtitle': '友だち追加から売上貢献までの施策体系',
        'sections': [
            {'type': 'capsule', 'label': '目的', 'color': COLORS['link_blue']},
            {'type': 'box', 'content': {
                'heading': 'LINEを活用した顧客LTV最大化',
                'body': ['友だち追加→セグメント配信→購買促進→リピート化の一気通貫CRM']
            }, 'color': COLORS['link_blue']},
            {'type': 'capsule', 'label': 'ターゲット', 'color': COLORS['success_teal']},
            {'type': 'cards', 'columns': 3, 'items': [
                {'title': '新規顧客', 'body': ['ECサイト初回訪問者', '広告経由の流入層'], 'color': COLORS['link_blue']},
                {'title': '既存顧客', 'body': ['購入経験あり', '休眠期間3ヶ月以内'], 'color': COLORS['success_teal']},
                {'title': 'VIP顧客', 'body': ['年間購入額10万円以上', 'リピート率80%以上'], 'color': COLORS['purple']},
            ]},
            {'type': 'capsule', 'label': '施策内容', 'color': COLORS['highlight_yellow']},
            {'type': 'cards', 'columns': 3, 'items': [
                {'title': '友だち追加', 'body': ['QRコード配布', 'LP埋め込み', 'インセンティブ設計'], 'color': COLORS['link_blue']},
                {'title': 'セグメント配信', 'body': ['購買履歴ベース', 'タグ分類', 'ステップ配信'], 'color': COLORS['success_teal']},
                {'title': 'リッチメニュー', 'body': ['パーソナライズ表示', 'セグメント別切替', '導線最適化'], 'color': COLORS['highlight_yellow']},
            ]},
            {'type': 'capsule', 'label': 'KPI', 'color': COLORS['alert_red']},
            {'type': 'cards', 'columns': 3, 'items': [
                {'title': '友だち追加数', 'body': ['月間+500人', '追加率15%'], 'color': COLORS['link_blue']},
                {'title': '配信開封率', 'body': ['目標60%以上', '業界平均の1.5倍'], 'color': COLORS['success_teal']},
                {'title': 'LINE経由売上', 'body': ['月商の20%', 'ROAS 400%以上'], 'color': COLORS['alert_red']},
            ]},
        ],
        'connections': [(1, 2), (3, 4), (5, 6)],
        'footer': '✦ 友だち数×開封率×CVR×客単価 = LINE経由売上',
    }
    svg = build_vertical(config)
    save('01_vertical', svg)


# ============================================================
# 2. build_timeline — プロジェクトロードマップ
# ============================================================
def gen_timeline():
    config = {
        'title': 'プロジェクトロードマップ',
        'subtitle': 'EC基盤リニューアル 2026年度計画',
        'phases': [
            {'label': '要件定義', 'period': 'Q1 (1-3月)',
             'body': ['現状分析・課題整理', 'ステークホルダーヒアリング', '要件ドキュメント作成'],
             'color': COLORS['link_blue']},
            {'label': '設計・開発', 'period': 'Q2 (4-6月)',
             'body': ['アーキテクチャ設計', 'API開発・フロント実装', 'データ移行設計'],
             'color': COLORS['success_teal']},
            {'label': 'テスト・QA', 'period': 'Q3 (7-9月)',
             'body': ['単体・結合テスト', '負荷テスト', 'UAT・受入テスト'],
             'color': COLORS['highlight_yellow']},
            {'label': 'リリース・運用', 'period': 'Q4 (10-12月)',
             'body': ['段階的リリース', '監視体制構築', '運用ドキュメント整備'],
             'color': COLORS['alert_red']},
        ],
        'footer': '✦ 各フェーズ終了時にステアリングコミッティでGo/No-Go判定',
    }
    svg = build_timeline(config)
    save('02_timeline', svg)


# ============================================================
# 3. build_matrix — フレームワーク比較表
# ============================================================
def gen_matrix():
    config = {
        'title': 'フロントエンドフレームワーク比較',
        'subtitle': '2026年時点の主要3フレームワーク評価',
        'col_headers': ['React', 'Vue', 'Svelte'],
        'row_headers': ['学習コスト', 'パフォーマンス', 'エコシステム', 'TypeScript対応', '採用実績'],
        'cells': [
            ['中程度 - JSX習得が必要', '低い - テンプレート構文が直感的', '低い - 標準的なHTML拡張'],
            ['仮想DOM、十分高速', '仮想DOM、Reactと同等', 'コンパイル時最適化で最速クラス'],
            ['最大規模、豊富なライブラリ', '公式ツール充実、中規模', '成長中、基本機能は揃う'],
            ['完全対応、型定義豊富', '完全対応、Composition API', '完全対応、ネイティブサポート'],
            ['最多、大企業での採用多数', '中国・アジア圏で強い', '増加中、中小規模に人気'],
        ],
        'col_colors': [COLORS['link_blue'], COLORS['success_teal'], COLORS['alert_red']],
        'footer': '✦ プロジェクト規模・チーム経験・要件に応じて選定すること',
    }
    svg = build_matrix(config)
    save('03_matrix', svg)


# ============================================================
# 4. build_journey_map — ECサイトCJM
# ============================================================
def gen_journey_map():
    config = {
        'title': 'ECサイト カスタマージャーニーマップ',
        'subtitle': '新規顧客の認知から推奨までの体験設計',
        'phases': ['認知', '検討', '購入', '利用', '推奨'],
        'lanes': [
            {'label': 'ユーザー行動', 'color': COLORS['link_blue'],
             'items': ['SNS広告を見る', '商品ページを比較', 'カートに入れて決済', '商品を使用', 'レビューを投稿']},
            {'label': '感情', 'color': COLORS['highlight_yellow'],
             'items': ['興味・期待', '迷い・不安', '期待・緊張', '満足 or 不満', '共有欲・貢献感']},
            {'label': 'タッチポイント', 'color': COLORS['success_teal'],
             'items': ['Instagram広告', 'LP・商品ページ', 'ECカート・決済', 'メール・LINE', 'レビューサイト']},
            {'label': '課題', 'color': COLORS['alert_red'],
             'items': ['認知度が低い', '競合との差別化', 'カート離脱率', 'サポート品質', 'レビュー促進']},
        ],
        'footer': '✦ 各フェーズの課題に対応した施策を設計し、体験全体を最適化する',
    }
    svg = build_journey_map(config)
    save('04_journey_map', svg)


# ============================================================
# 5. build_layer — Webアプリアーキテクチャ
# ============================================================
def gen_layer():
    config = {
        'title': 'Webアプリケーション アーキテクチャ',
        'subtitle': '4層構成のモダンWebスタック',
        'layers': [
            {'label': 'インフラ層', 'body': ['AWS (ECS, RDS, S3, CloudFront)', 'Terraform IaC, GitHub Actions CI/CD'],
             'color': COLORS['alert_red']},
            {'label': 'データ層', 'body': ['PostgreSQL (メインDB)', 'Redis (キャッシュ/セッション)', 'S3 (オブジェクトストレージ)'],
             'color': COLORS['highlight_yellow']},
            {'label': 'API層', 'body': ['FastAPI (REST API)', '認証: Auth0 + JWT', 'OpenAPI仕様で型安全'],
             'color': COLORS['success_teal']},
            {'label': 'フロントエンド層', 'body': ['Next.js (App Router)', 'TailwindCSS + Radix UI', 'React Query (データフェッチ)'],
             'color': COLORS['link_blue']},
        ],
        'arrows': True,
        'footer': '✦ 各層は独立してスケール・デプロイ可能な設計',
    }
    svg = build_layer(config)
    save('05_layer', svg)


# ============================================================
# 6. build_two_columns — As-Is / To-Be ギャップ図
# ============================================================
def gen_two_columns():
    config = {
        'title': '業務改善 ギャップ分析',
        'left_label': 'As-Is（現状）',
        'right_label': 'To-Be（理想）',
        'left_color': COLORS['alert_red'],
        'right_color': COLORS['success_teal'],
        'rows': [
            {'left': {'title': '受注処理', 'body': ['FAXとメールで受注', '手動でExcelに転記', '処理時間: 平均30分/件']},
             'right': {'title': '受注処理', 'body': ['EC+APIで自動受注', 'システム自動連携', '処理時間: 即時〜1分']}},
            {'left': {'title': '在庫管理', 'body': ['目視で棚卸し', '月1回の在庫確認', '欠品率: 5%']},
             'right': {'title': '在庫管理', 'body': ['バーコード読取+IoT', 'リアルタイム在庫把握', '欠品率: 0.5%以下']}},
            {'left': {'title': '顧客対応', 'body': ['電話+メールのみ', '対応履歴が属人的', '平均応答: 24時間']},
             'right': {'title': '顧客対応', 'body': ['チャットbot+有人チャット', 'CRMで一元管理', '平均応答: 5分以内']}},
        ],
        'footer': '✦ 3領域の改善で年間コスト30%削減、顧客満足度20pt向上を目指す',
    }
    svg = build_two_columns(config)
    save('06_two_columns', svg)


# ============================================================
# 7. build_tree (TB) — 組織図
# ============================================================
def gen_tree_tb():
    config = {
        'title': '会社組織図',
        'subtitle': '株式会社サンプルテクノロジーズ',
        'direction': 'TB',
        'root': {
            'label': 'CEO',
            'body': ['代表取締役社長'],
            'children': [
                {'label': 'CTO', 'body': ['技術統括'],
                 'children': [
                     {'label': 'エンジニアリング部', 'body': ['開発チーム×3']},
                     {'label': 'プロダクト部', 'body': ['PdM・デザイン']},
                 ]},
                {'label': 'CFO', 'body': ['財務統括'],
                 'children': [
                     {'label': '経理部', 'body': ['決算・税務']},
                     {'label': '財務部', 'body': ['資金調達・IR']},
                 ]},
                {'label': 'COO', 'body': ['事業統括'],
                 'children': [
                     {'label': '営業部', 'body': ['法人営業×2']},
                     {'label': 'CS部', 'body': ['カスタマーサクセス']},
                     {'label': 'マーケ部', 'body': ['デジタルマーケ']},
                 ]},
            ],
        },
        'footer': '✦ 2026年4月時点の組織体制（従業員数: 120名）',
    }
    svg = build_tree(config)
    save('07_tree_tb', svg)


# ============================================================
# 8. build_tree (LR) — マインドマップ
# ============================================================
def gen_tree_lr():
    config = {
        'title': 'マーケティング戦略 マインドマップ',
        'subtitle': '2026年度ブランド戦略の全体像',
        'direction': 'LR',
        'root': {
            'label': 'ブランド戦略',
            'children': [
                {'label': 'デジタル',
                 'children': [
                     {'label': 'SEO', 'body': ['コンテンツSEO', 'テクニカルSEO']},
                     {'label': 'SNS', 'body': ['Instagram', 'X(Twitter)']},
                     {'label': '広告', 'body': ['リスティング', 'ディスプレイ']},
                 ]},
                {'label': 'オフライン',
                 'children': [
                     {'label': '展示会', 'body': ['年2回出展']},
                     {'label': 'DM', 'body': ['VIP顧客向け']},
                 ]},
                {'label': 'PR',
                 'children': [
                     {'label': 'プレスリリース', 'body': ['月1回配信']},
                     {'label': 'メディア露出', 'body': ['業界誌・Web媒体']},
                 ]},
            ],
        },
    }
    svg = build_tree(config)
    save('08_tree_lr', svg)


# ============================================================
# 9. build_flow — ユーザー登録フロー
# ============================================================
def gen_flow():
    config = {
        'title': 'ユーザー登録フロー',
        'subtitle': 'メール認証付き新規登録プロセス',
        'direction': 'TB',
        'nodes': [
            {'id': 'start', 'label': '開始', 'type': 'start'},
            {'id': 'email', 'label': 'メールアドレス入力', 'body': ['形式チェック実行']},
            {'id': 'validate', 'label': 'バリデーション', 'type': 'decision'},
            {'id': 'error', 'label': 'エラー表示', 'body': ['入力値を修正依頼']},
            {'id': 'password', 'label': 'パスワード設定', 'body': ['8文字以上', '英数字記号混合']},
            {'id': 'confirm', 'label': '確認メール送信', 'body': ['24時間有効なトークン']},
            {'id': 'verify', 'label': 'メール認証完了?', 'type': 'decision'},
            {'id': 'complete', 'label': '登録完了', 'type': 'end'},
            {'id': 'expire', 'label': 'トークン期限切れ', 'type': 'end'},
        ],
        'edges': [
            {'from': 'start', 'to': 'email'},
            {'from': 'email', 'to': 'validate'},
            {'from': 'validate', 'to': 'password', 'label': 'OK'},
            {'from': 'validate', 'to': 'error', 'label': 'NG'},
            {'from': 'error', 'to': 'email'},
            {'from': 'password', 'to': 'confirm'},
            {'from': 'confirm', 'to': 'verify'},
            {'from': 'verify', 'to': 'complete', 'label': '認証済'},
            {'from': 'verify', 'to': 'expire', 'label': '期限切れ'},
        ],
        'footer': '✦ 認証メールは最大3回まで再送可能',
    }
    svg = build_flow(config)
    save('09_flow', svg)


# ============================================================
# 10. build_flow (cycle) — アジャイル開発サイクル
# ============================================================
def gen_flow_cycle():
    config = {
        'title': 'アジャイル開発サイクル',
        'subtitle': 'スクラムベースの反復型開発プロセス',
        'direction': 'TB',
        'nodes': [
            {'id': 'plan', 'label': 'スプリント計画', 'body': ['バックログ選定', '見積もり・担当決定']},
            {'id': 'design', 'label': '設計', 'body': ['技術設計', 'タスク分解']},
            {'id': 'implement', 'label': '実装', 'body': ['コーディング', 'ペアプログラミング']},
            {'id': 'test', 'label': 'テスト', 'body': ['自動テスト', 'コードレビュー']},
            {'id': 'review', 'label': 'スプリントレビュー', 'body': ['デモ・フィードバック', '受入確認']},
            {'id': 'retro', 'label': 'レトロスペクティブ', 'body': ['振り返り', '改善アクション決定']},
        ],
        'edges': [
            {'from': 'plan', 'to': 'design'},
            {'from': 'design', 'to': 'implement'},
            {'from': 'implement', 'to': 'test'},
            {'from': 'test', 'to': 'review'},
            {'from': 'review', 'to': 'retro'},
            {'from': 'retro', 'to': 'plan', 'label': '次スプリント'},
        ],
        'footer': '✦ 1スプリント = 2週間、継続的に改善を回す',
    }
    svg = build_flow(config)
    save('10_flow_cycle', svg)


# ============================================================
# 11. build_tree — ロジックツリー（Why型原因分解）
# ============================================================
def gen_logic_tree():
    config = {
        'title': '売上低下の原因分析（ロジックツリー）',
        'subtitle': 'Why型で根本原因を構造的に分解',
        'direction': 'LR',
        'root': {
            'label': '売上が低下している',
            'children': [
                {'label': '新規獲得の減少',
                 'children': [
                     {'label': '広告効率の悪化', 'body': ['CPA上昇', 'CTR低下']},
                     {'label': '認知チャネルの減少', 'body': ['SNS流入-30%']},
                 ]},
                {'label': '既存顧客の離脱',
                 'children': [
                     {'label': '競合への流出', 'body': ['価格競争力低下']},
                     {'label': 'サービス品質低下', 'body': ['NPS -15pt']},
                 ]},
                {'label': '客単価の低下',
                 'children': [
                     {'label': 'アップセル不足', 'body': ['提案率20%→8%']},
                     {'label': '値引き依存', 'body': ['クーポン使用率70%']},
                 ]},
            ],
        },
        'footer': '✦ 各末端原因に対して打ち手を設計する',
    }
    svg = build_tree(config)
    save('11_logic_tree', svg)


# ============================================================
# 12. build_flow (LR) — IPO図
# ============================================================
def gen_ipo():
    config = {
        'title': 'データパイプライン（IPO図）',
        'subtitle': '入力→処理→出力の構造',
        'direction': 'LR',
        'nodes': [
            {'id': 'in1', 'label': 'CSVファイル', 'type': 'start'},
            {'id': 'in2', 'label': 'APIデータ', 'type': 'start'},
            {'id': 'validate', 'label': 'バリデーション', 'body': ['スキーマ検証', 'NULL除去']},
            {'id': 'transform', 'label': '変換・正規化', 'body': ['日付統一', 'コード変換']},
            {'id': 'aggregate', 'label': '集計処理', 'body': ['日次集計', 'KPI算出']},
            {'id': 'out1', 'label': 'レポート出力', 'type': 'end'},
            {'id': 'out2', 'label': 'DWH格納', 'type': 'end'},
        ],
        'edges': [
            {'from': 'in1', 'to': 'validate'},
            {'from': 'in2', 'to': 'validate'},
            {'from': 'validate', 'to': 'transform'},
            {'from': 'transform', 'to': 'aggregate'},
            {'from': 'aggregate', 'to': 'out1'},
            {'from': 'aggregate', 'to': 'out2'},
        ],
        'footer': '✦ 毎日AM3:00にバッチ実行（所要時間: 約15分）',
    }
    svg = build_flow(config)
    save('12_ipo', svg)


# ============================================================
# 13. build_flow — 因果ループ図
# ============================================================
def gen_causal_loop():
    config = {
        'title': '顧客満足の因果ループ図',
        'subtitle': '強化ループと抑制ループの構造',
        'direction': 'TB',
        'nodes': [
            {'id': 'quality', 'label': 'サービス品質', 'body': ['UX・サポート品質']},
            {'id': 'satisfy', 'label': '顧客満足度', 'body': ['NPS・CSAT']},
            {'id': 'retention', 'label': 'リテンション率', 'body': ['継続率・LTV']},
            {'id': 'revenue', 'label': '売上・利益', 'body': ['月次売上']},
            {'id': 'invest', 'label': '開発投資', 'body': ['R&D予算']},
            {'id': 'cost', 'label': 'コスト圧力', 'body': ['コスト削減要求']},
        ],
        'edges': [
            {'from': 'quality', 'to': 'satisfy', 'label': '+'},
            {'from': 'satisfy', 'to': 'retention', 'label': '+'},
            {'from': 'retention', 'to': 'revenue', 'label': '+'},
            {'from': 'revenue', 'to': 'invest', 'label': '+'},
            {'from': 'invest', 'to': 'quality', 'label': '+'},
            {'from': 'revenue', 'to': 'cost', 'label': '+'},
            {'from': 'cost', 'to': 'invest', 'label': '-'},
        ],
        'footer': '✦ 強化ループ(+)を回し、抑制ループ(-)を管理する',
    }
    svg = build_flow(config)
    save('13_causal_loop', svg)


# ============================================================
# 14. build_flow — 状態遷移図
# ============================================================
def gen_state_transition():
    config = {
        'title': '注文ステータス 状態遷移図',
        'subtitle': 'ECサイトの注文ライフサイクル',
        'direction': 'LR',
        'nodes': [
            {'id': 'cart', 'label': 'カート', 'type': 'start'},
            {'id': 'pending', 'label': '注文確定', 'body': ['決済待ち']},
            {'id': 'paid', 'label': '決済完了', 'body': ['入金確認済']},
            {'id': 'ship', 'label': '発送済', 'body': ['追跡番号発行']},
            {'id': 'deliver', 'label': '配達完了', 'type': 'end'},
            {'id': 'cancel', 'label': 'キャンセル', 'type': 'end'},
            {'id': 'ret', 'label': '返品', 'type': 'end'},
        ],
        'edges': [
            {'from': 'cart', 'to': 'pending', 'label': '注文確定'},
            {'from': 'pending', 'to': 'paid', 'label': '決済成功'},
            {'from': 'pending', 'to': 'cancel', 'label': '取消'},
            {'from': 'paid', 'to': 'ship', 'label': '出荷'},
            {'from': 'paid', 'to': 'cancel', 'label': '返金'},
            {'from': 'ship', 'to': 'deliver', 'label': '受取'},
            {'from': 'deliver', 'to': 'ret', 'label': '返品申請'},
        ],
        'footer': '✦ キャンセルは発送前まで可能、返品は配達後7日以内',
    }
    svg = build_flow(config)
    save('14_state_transition', svg)


# ============================================================
# 15. build_journey_map — スイムレーン図
# ============================================================
def gen_swimlane():
    config = {
        'title': '問い合わせ対応 スイムレーン図',
        'subtitle': '部門横断の業務フロー',
        'phases': ['受付', '一次対応', '調査', 'エスカレーション', '解決・回答'],
        'lanes': [
            {'label': '顧客', 'color': COLORS['link_blue'],
             'items': ['問い合わせ送信', '自動返信受信', '追加情報提供', '—', '回答を確認']},
            {'label': 'CS部門', 'color': COLORS['success_teal'],
             'items': ['チケット発行', 'FAQ確認・初期回答', '担当者にヒアリング', '技術部門に依頼', '最終回答を送付']},
            {'label': '技術部門', 'color': COLORS['highlight_yellow'],
             'items': ['—', '—', 'ログ調査', '原因特定・修正', '修正結果を報告']},
            {'label': 'マネージャー', 'color': COLORS['alert_red'],
             'items': ['—', '—', '—', '優先度判断', '品質レビュー']},
        ],
        'footer': '✦ SLA: 一次回答24h以内、解決72h以内',
    }
    svg = build_journey_map(config)
    save('15_swimlane', svg)


# ============================================================
# 16. build_journey_map — サービスブループリント
# ============================================================
def gen_service_blueprint():
    config = {
        'title': 'オンライン注文 サービスブループリント',
        'subtitle': 'フロント/バック/サポートの対応関係',
        'phases': ['検索', '商品選択', '決済', '配送', 'サポート'],
        'lanes': [
            {'label': '顧客行動', 'color': COLORS['link_blue'],
             'items': ['キーワード検索', '商品詳細を閲覧', 'カート決済', '配送状況確認', '問い合わせ']},
            {'label': 'フロントステージ', 'color': COLORS['success_teal'],
             'items': ['検索UI表示', '商品ページ表示', '決済フォーム', '追跡ページ', 'チャットbot']},
            {'label': 'バックステージ', 'color': COLORS['highlight_yellow'],
             'items': ['Elasticsearch', 'CDN画像配信', '決済API処理', 'WMS出荷指示', 'チケット管理']},
            {'label': 'サポートプロセス', 'color': COLORS['alert_red'],
             'items': ['商品DB更新', '在庫同期', '不正検知', '配送業者連携', 'FAQ更新']},
        ],
        'footer': '✦ 可視線（顧客→フロント）と内部相互作用線（フロント→バック）で責務を分離',
    }
    svg = build_journey_map(config)
    save('16_service_blueprint', svg)


# ============================================================
# 17. build_tree — オントロジー/タクソノミー
# ============================================================
def gen_ontology():
    config = {
        'title': 'デジタルマーケティング タクソノミー',
        'subtitle': '概念と包含関係の定義',
        'direction': 'TB',
        'root': {
            'label': 'デジタルマーケティング',
            'children': [
                {'label': 'オウンドメディア',
                 'children': [
                     {'label': 'Webサイト', 'body': ['コーポレート', 'LP']},
                     {'label': 'ブログ/記事', 'body': ['SEO記事', 'ホワイトペーパー']},
                     {'label': 'メール', 'body': ['メルマガ', 'MA配信']},
                 ]},
                {'label': 'ペイドメディア',
                 'children': [
                     {'label': '検索広告', 'body': ['Google Ads', 'Yahoo!広告']},
                     {'label': 'SNS広告', 'body': ['Meta Ads', 'X Ads']},
                     {'label': 'ディスプレイ', 'body': ['GDN', 'DSP']},
                 ]},
                {'label': 'アーンドメディア',
                 'children': [
                     {'label': 'SNS', 'body': ['UGC', 'シェア']},
                     {'label': 'PR', 'body': ['プレスリリース', 'メディア掲載']},
                     {'label': '口コミ', 'body': ['レビュー', '紹介']},
                 ]},
            ],
        },
        'footer': '✦ トリプルメディアの分類に基づくチャネル体系',
    }
    svg = build_tree(config)
    save('17_ontology', svg)


# ============================================================
# 18. build_tree + build_flow — ペルソナ→課題→価値 対応図
# ============================================================
def gen_persona_value():
    config = {
        'title': 'ペルソナ → 課題 → 提供価値',
        'subtitle': '誰の何をどう解くかの対応関係',
        'direction': 'LR',
        'root': {
            'label': 'ターゲット設計',
            'children': [
                {'label': 'EC店舗オーナー（30代）',
                 'children': [
                     {'label': '課題: リピート率が低い',
                      'children': [
                          {'label': '価値: LINE CRM自動配信'},
                      ]},
                     {'label': '課題: 広告費が高い',
                      'children': [
                          {'label': '価値: SEO+コンテンツ集客'},
                      ]},
                 ]},
                {'label': 'マーケ担当（20代）',
                 'children': [
                     {'label': '課題: 施策の効果が不明',
                      'children': [
                          {'label': '価値: ダッシュボード可視化'},
                      ]},
                     {'label': '課題: 作業が属人的',
                      'children': [
                          {'label': '価値: ワークフロー自動化'},
                      ]},
                 ]},
            ],
        },
        'footer': '✦ ペルソナごとの課題に1:1で価値提案を対応させる',
    }
    svg = build_tree(config)
    save('18_persona_value', svg)


# ============================================================
# 19. SVG直接記述 — ベン図
# ============================================================
def gen_venn():
    W, H = 800, 600
    svg = _svg_header(W, H, 'スキルセットのベン図', '3つの専門領域の重なり')
    svg += _svg_text(W/2, 50, 'プロダクト人材に必要なスキルセット', 'title')
    svg += _svg_text(W/2, 78, '3つの専門領域の交差点', 'subtitle')

    # 3つの円
    circles = [
        (320, 280, COLORS['link_blue'], 'ビジネス'),
        (480, 280, COLORS['success_teal'], 'テクノロジー'),
        (400, 400, COLORS['alert_red'], 'デザイン'),
    ]
    r = 140
    for cx, cy, color, label in circles:
        svg += f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="0.18" stroke="{color}" stroke-width="2.5"/>\n'

    # ラベル（外側）
    svg += _svg_text(250, 210, 'ビジネス', 'subheading')
    svg += _svg_text(550, 210, 'テクノロジー', 'subheading')
    svg += _svg_text(400, 500, 'デザイン', 'subheading')

    # 交差ラベル
    svg += _svg_text(400, 260, 'データ分析', 'body')
    svg += _svg_text(340, 370, 'UXリサーチ', 'body')
    svg += _svg_text(460, 370, '技術設計', 'body')

    # 中心
    svg += f'  <circle cx="400" cy="330" r="30" fill="{COLORS["purple"]}" opacity="0.3"/>\n'
    svg += f'  <text x="400" y="330" text-anchor="middle" dominant-baseline="central" font-size="11px" font-weight="bold" fill="{COLORS["text_primary"]}">PdM</text>\n'

    # フッター
    ft, _ = _svg_footer_box(S['canvas_pad'], H - S['footer_h'] - 20, W - 2*S['canvas_pad'], '✦ 3領域の交差点にプロダクトマネージャーの役割がある')
    svg += ft
    svg += _svg_footer()
    save('19_venn', svg)


# ============================================================
# 20. SVG直接記述 — シーケンス図
# ============================================================
def gen_sequence():
    actors = ['ユーザー', 'フロントエンド', 'APIサーバー', 'データベース']
    messages = [
        (0, 1, 'ログインボタン押下', False),
        (1, 2, 'POST /auth/login', False),
        (2, 3, 'SELECT user WHERE email=?', False),
        (3, 2, 'ユーザーデータ返却', True),
        (2, 2, 'JWT生成', False),
        (2, 1, '200 OK + token', True),
        (1, 0, 'ダッシュボード表示', True),
    ]

    W = 900
    pad = S['canvas_pad']
    actor_gap = (W - 2 * pad) / (len(actors) - 1)
    actor_xs = [pad + i * actor_gap for i in range(len(actors))]
    header_y = 120
    msg_start_y = 170
    msg_gap = 55
    H = msg_start_y + len(messages) * msg_gap + 100

    svg = _svg_header(W, H, 'ログイン認証シーケンス図', 'ユーザー認証フローの時系列')
    svg += _svg_text(W/2, 40, 'ログイン認証 シーケンス図', 'title')
    svg += _svg_text(W/2, 66, 'JWT認証フローの時系列表現', 'subtitle')

    # アクターボックス + ライフライン
    for i, (name, ax) in enumerate(zip(actors, actor_xs)):
        color = ACCENT_CYCLE[i % len(ACCENT_CYCLE)]
        bw = max(_text_width_est(name, 14) + 30, 100)
        bx = ax - bw / 2
        svg += _svg_rect(bx, header_y - 20, bw, 36, fill=color, stroke=None, rx=6, shadow=True)
        svg += f'  <text x="{ax}" y="{header_y}" text-anchor="middle" dominant-baseline="central" font-size="13px" font-weight="bold" fill="{COLORS["white"]}">{_esc(name)}</text>\n'
        # ライフライン
        svg += f'  <line x1="{ax}" y1="{header_y + 18}" x2="{ax}" y2="{H - 60}" stroke="{COLORS["border_light"]}" stroke-width="1.5" stroke-dasharray="6,4"/>\n'

    # メッセージ
    for idx, (fr, to, label, is_response) in enumerate(messages):
        y = msg_start_y + idx * msg_gap
        x1, x2 = actor_xs[fr], actor_xs[to]
        if fr == to:
            # Self-message
            loop_w = 60
            svg += f'  <path d="M{x1},{y} L{x1+loop_w},{y} L{x1+loop_w},{y+20} L{x1},{y+20}" fill="none" stroke="{COLORS["text_secondary"]}" stroke-width="1.5" marker-end="url(#arrowhead)"/>\n'
            svg += f'  <text x="{x1+loop_w+6}" y="{y+10}" text-anchor="start" font-size="12px" fill="{COLORS["text_primary"]}">{_esc(label)}</text>\n'
        else:
            dash = ' stroke-dasharray="6,3"' if is_response else ''
            svg += f'  <line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{COLORS["text_secondary"]}" stroke-width="1.5" marker-end="url(#arrowhead)"{dash}/>\n'
            lx = (x1 + x2) / 2
            svg += f'  <text x="{lx}" y="{y - 8}" text-anchor="middle" font-size="12px" fill="{COLORS["text_primary"]}">{_esc(label)}</text>\n'

    ft, _ = _svg_footer_box(pad, H - S['footer_h'] - 20, W - 2*pad, '✦ 実線=リクエスト、破線=レスポンス')
    svg += ft
    svg += _svg_footer()
    save('20_sequence', svg)


# ============================================================
# 21. SVG直接記述 — ポジショニングマップ
# ============================================================
def gen_positioning_map():
    W, H = 800, 700
    pad = S['canvas_pad']
    svg = _svg_header(W, H, 'ポジショニングマップ', '2軸上の相対位置')
    svg += _svg_text(W/2, 45, 'CRMツール ポジショニングマップ', 'title')
    svg += _svg_text(W/2, 72, '価格帯 × 機能の豊富さで比較', 'subtitle')

    # 軸
    ox, oy = 120, 580  # 原点
    ax_w, ax_h = 580, 440  # 軸の長さ
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="{COLORS["text_secondary"]}" stroke-width="2" marker-end="url(#arrowhead)"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ax_h}" stroke="{COLORS["text_secondary"]}" stroke-width="2" marker-end="url(#arrowhead)"/>\n'

    # 軸ラベル
    svg += f'  <text x="{ox+ax_w/2}" y="{oy+35}" text-anchor="middle" font-size="14px" font-weight="bold" fill="{COLORS["text_primary"]}">価格帯 →</text>\n'
    svg += f'  <text x="{ox-35}" y="{oy-ax_h/2}" text-anchor="middle" font-size="14px" font-weight="bold" fill="{COLORS["text_primary"]}" transform="rotate(-90,{ox-35},{oy-ax_h/2})">機能の豊富さ →</text>\n'

    # プロット
    items = [
        (0.2, 0.3, 'ツールA', COLORS['link_blue'], '無料/シンプル'),
        (0.4, 0.6, 'ツールB', COLORS['success_teal'], '中価格/バランス型'),
        (0.75, 0.85, 'ツールC', COLORS['purple'], '高価格/多機能'),
        (0.6, 0.4, 'ツールD', COLORS['highlight_yellow'], '中高/特化型'),
        (0.85, 0.55, 'ツールE', COLORS['alert_red'], '高価格/レガシー'),
        (0.3, 0.75, 'ツールF', COLORS['pink'], '低価格/高機能'),
    ]
    for rx, ry, name, color, desc in items:
        px = ox + rx * ax_w
        py = oy - ry * ax_h
        svg += f'  <circle cx="{px}" cy="{py}" r="22" fill="{color}" opacity="0.2" stroke="{color}" stroke-width="2"/>\n'
        svg += f'  <circle cx="{px}" cy="{py}" r="5" fill="{color}"/>\n'
        svg += f'  <text x="{px}" y="{py - 28}" text-anchor="middle" font-size="13px" font-weight="bold" fill="{COLORS["text_primary"]}">{_esc(name)}</text>\n'
        svg += f'  <text x="{px}" y="{py + 35}" text-anchor="middle" font-size="10px" fill="{COLORS["text_caption"]}">{_esc(desc)}</text>\n'

    ft, _ = _svg_footer_box(pad, H - S['footer_h'] - 15, W - 2*pad, '✦ 右上が高価格×多機能。自社ポジションの空白地帯を探す')
    svg += ft
    svg += _svg_footer()
    save('21_positioning_map', svg)


# ============================================================
# 22. SVG直接記述 — トレードオフ曲線
# ============================================================
def gen_tradeoff():
    W, H = 800, 600
    pad = S['canvas_pad']
    svg = _svg_header(W, H, 'トレードオフ曲線', '速度と品質の二律背反')
    svg += _svg_text(W/2, 45, '開発速度 vs 品質 トレードオフ', 'title')
    svg += _svg_text(W/2, 72, '最適バランスの可視化', 'subtitle')

    # 軸
    ox, oy = 120, 480
    ax_w, ax_h = 560, 350
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox+ax_w}" y2="{oy}" stroke="{COLORS["text_secondary"]}" stroke-width="2" marker-end="url(#arrowhead)"/>\n'
    svg += f'  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-ax_h}" stroke="{COLORS["text_secondary"]}" stroke-width="2" marker-end="url(#arrowhead)"/>\n'
    svg += f'  <text x="{ox+ax_w/2}" y="{oy+35}" text-anchor="middle" font-size="14px" font-weight="bold" fill="{COLORS["text_primary"]}">開発速度 →</text>\n'
    svg += f'  <text x="{ox-35}" y="{oy-ax_h/2}" text-anchor="middle" font-size="14px" font-weight="bold" fill="{COLORS["text_primary"]}" transform="rotate(-90,{ox-35},{oy-ax_h/2})">品質 →</text>\n'

    # トレードオフ曲線（逆双曲線）
    import math
    points = []
    for i in range(50):
        t = 0.08 + i * 0.018
        px = ox + t * ax_w
        py = oy - (0.08 / t) * ax_h * 0.7
        if oy - ax_h < py < oy:
            points.append(f'{px:.0f},{py:.0f}')
    svg += f'  <polyline points="{" ".join(points)}" fill="none" stroke="{COLORS["link_blue"]}" stroke-width="3"/>\n'

    # ラベルポイント
    spots = [
        (0.15, 0.75, 'MVP', COLORS['success_teal'], '速度重視'),
        (0.5, 0.35, '最適点', COLORS['purple'], 'バランス'),
        (0.8, 0.18, 'エンタープライズ', COLORS['alert_red'], '品質重視'),
    ]
    for rx, ry, name, color, desc in spots:
        px = ox + rx * ax_w
        py = oy - ry * ax_h
        svg += f'  <circle cx="{px}" cy="{py}" r="8" fill="{color}" stroke="{COLORS["white"]}" stroke-width="2"/>\n'
        svg += f'  <text x="{px}" y="{py-16}" text-anchor="middle" font-size="13px" font-weight="bold" fill="{COLORS["text_primary"]}">{_esc(name)}</text>\n'
        svg += f'  <text x="{px}" y="{py+22}" text-anchor="middle" font-size="11px" fill="{COLORS["text_caption"]}">{_esc(desc)}</text>\n'

    # 効率フロンティア帯
    svg += f'  <text x="{ox+ax_w-20}" y="{oy-ax_h+30}" text-anchor="end" font-size="12px" font-style="italic" fill="{COLORS["link_blue"]}">効率フロンティア</text>\n'

    ft, _ = _svg_footer_box(pad, H - S['footer_h'] - 15, W - 2*pad, '✦ 曲線上が最適解。曲線の内側（左下）は改善余地あり')
    svg += ft
    svg += _svg_footer()
    save('22_tradeoff', svg)


# ============================================================
# 23. SVG直接記述 — 概念地図（コンセプトマップ）
# ============================================================
def gen_concept_map():
    W, H = 900, 650
    pad = S['canvas_pad']
    svg = _svg_header(W, H, '概念地図', 'DXの構成要素と関係性')
    svg += _svg_text(W/2, 45, 'DX推進 概念地図', 'title')
    svg += _svg_text(W/2, 72, '概念間の距離と関係性で意味を表現', 'subtitle')

    # ノード定義（x, y, label, color, size）
    nodes = [
        (450, 200, 'DX推進', COLORS['text_primary'], 50),
        (200, 180, 'データ活用', COLORS['link_blue'], 38),
        (700, 180, 'プロセス改革', COLORS['success_teal'], 38),
        (300, 350, 'AI/ML', COLORS['purple'], 32),
        (600, 350, '自動化', COLORS['highlight_yellow'], 32),
        (150, 400, 'データ基盤', COLORS['link_blue'], 28),
        (450, 450, 'クラウド', COLORS['alert_red'], 30),
        (750, 400, 'アジャイル', COLORS['success_teal'], 28),
        (350, 520, 'セキュリティ', COLORS['pink'], 26),
        (600, 520, '人材育成', COLORS['highlight_yellow'], 28),
    ]

    # エッジ定義
    edges = [
        (0, 1, '活用'), (0, 2, '推進'), (1, 3, '技術'),
        (2, 4, '手段'), (1, 5, '基盤'), (3, 6, '実行環境'),
        (4, 6, '基盤'), (2, 7, '手法'), (5, 8, '要件'),
        (6, 8, '要件'), (4, 9, '必要'), (7, 9, '必要'),
    ]

    # エッジ描画
    for fi, ti, label in edges:
        fx, fy = nodes[fi][0], nodes[fi][1]
        tx, ty = nodes[ti][0], nodes[ti][1]
        mx, my = (fx+tx)/2, (fy+ty)/2
        svg += f'  <line x1="{fx}" y1="{fy}" x2="{tx}" y2="{ty}" stroke="{COLORS["border_light"]}" stroke-width="1.5"/>\n'
        svg += f'  <text x="{mx}" y="{my-6}" text-anchor="middle" font-size="10px" fill="{COLORS["text_caption"]}">{_esc(label)}</text>\n'

    # ノード描画
    for x, y, label, color, r in nodes:
        svg += f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{color}" opacity="0.15" stroke="{color}" stroke-width="2"/>\n'
        svg += f'  <text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="central" font-size="12px" font-weight="bold" fill="{COLORS["text_primary"]}">{_esc(label)}</text>\n'

    ft, _ = _svg_footer_box(pad, H - S['footer_h'] - 15, W - 2*pad, '✦ 近い概念ほど関連性が強い。中心がコア概念')
    svg += ft
    svg += _svg_footer()
    save('23_concept_map', svg)


# ============================================================
# 24. SVG直接記述 — コンポーネント図
# ============================================================
def gen_component():
    W, H = 900, 650
    pad = S['canvas_pad']
    svg = _svg_header(W, H, 'コンポーネント図', 'マイクロサービス構成')
    svg += _svg_text(W/2, 45, 'ECプラットフォーム コンポーネント図', 'title')
    svg += _svg_text(W/2, 72, 'マイクロサービスの構成と依存関係', 'subtitle')

    # コンポーネントボックス
    components = [
        (80,  130, 200, 80, 'API Gateway', COLORS['link_blue']),
        (60,  280, 160, 70, '認証サービス', COLORS['success_teal']),
        (260, 280, 160, 70, '商品サービス', COLORS['highlight_yellow']),
        (460, 280, 160, 70, '注文サービス', COLORS['alert_red']),
        (660, 280, 160, 70, '決済サービス', COLORS['purple']),
        (160, 430, 160, 70, '商品DB', COLORS['highlight_yellow']),
        (360, 430, 160, 70, '注文DB', COLORS['alert_red']),
        (560, 430, 160, 70, '通知サービス', COLORS['pink']),
        (360, 550, 160, 60, 'メッセージキュー', COLORS['text_secondary']),
    ]

    for x, y, w, h, label, color in components:
        bg = COLORS['white']
        svg += _svg_rect(x, y, w, h, fill=bg, stroke=color, stroke_width=2, rx=8, shadow=True)
        # コンポーネントアイコン（小さい二重箱）
        ix, iy = x + w - 25, y + 5
        svg += f'  <rect x="{ix}" y="{iy}" width="18" height="12" rx="2" fill="none" stroke="{color}" stroke-width="1.5"/>\n'
        svg += f'  <rect x="{ix-4}" y="{iy+2}" width="8" height="3" rx="1" fill="{color}"/>\n'
        svg += f'  <rect x="{ix-4}" y="{iy+7}" width="8" height="3" rx="1" fill="{color}"/>\n'
        svg += f'  <text x="{x+w/2}" y="{y+h/2+4}" text-anchor="middle" font-size="13px" font-weight="bold" fill="{COLORS["text_primary"]}">{_esc(label)}</text>\n'

    # 依存関係（矢印）
    deps = [
        (180, 210, 140, 280),   # Gateway → 認証
        (180, 210, 340, 280),   # Gateway → 商品
        (180, 210, 540, 280),   # Gateway → 注文
        (540, 350, 740, 280),   # 注文 → 決済
        (340, 350, 240, 430),   # 商品 → 商品DB
        (540, 350, 440, 430),   # 注文 → 注文DB
        (540, 350, 640, 430),   # 注文 → 通知
        (640, 500, 440, 550),   # 通知 → MQ
    ]
    for x1, y1, x2, y2 in deps:
        svg += f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{COLORS["text_secondary"]}" stroke-width="1.5" marker-end="url(#arrowhead)"/>\n'

    ft, _ = _svg_footer_box(pad, H - S['footer_h'] - 8, W - 2*pad, '✦ 矢印は依存方向。各サービスは独立してデプロイ可能')
    svg += ft
    svg += _svg_footer()
    save('24_component', svg)


# ============================================================
# 25. SVG直接記述 — ネットワーク図
# ============================================================
def gen_network():
    W, H = 900, 650
    pad = S['canvas_pad']
    svg = _svg_header(W, H, 'ネットワーク図', 'システム間の接続関係')
    svg += _svg_text(W/2, 45, '社内システム ネットワーク図', 'title')
    svg += _svg_text(W/2, 72, '多対多のシステム間接続を可視化', 'subtitle')

    # ノード
    net_nodes = [
        (450, 180, 'ERP', COLORS['link_blue'], 42),
        (200, 250, 'CRM', COLORS['success_teal'], 38),
        (700, 250, 'EC基盤', COLORS['alert_red'], 38),
        (150, 420, 'MA', COLORS['purple'], 34),
        (350, 420, 'DWH', COLORS['highlight_yellow'], 36),
        (550, 420, 'WMS', COLORS['pink'], 34),
        (750, 420, '決済GW', COLORS['alert_red'], 34),
        (300, 550, 'BI', COLORS['link_blue'], 30),
        (600, 550, '配送API', COLORS['success_teal'], 30),
    ]

    # エッジ（双方向接続）
    net_edges = [
        (0, 1), (0, 2), (0, 4), (1, 3), (1, 4),
        (2, 5), (2, 6), (4, 7), (5, 8), (3, 4),
        (2, 4), (6, 2),
    ]

    for fi, ti in net_edges:
        fx, fy = net_nodes[fi][0], net_nodes[fi][1]
        tx, ty = net_nodes[ti][0], net_nodes[ti][1]
        svg += f'  <line x1="{fx}" y1="{fy}" x2="{tx}" y2="{ty}" stroke="{COLORS["border_light"]}" stroke-width="2"/>\n'

    for x, y, label, color, r in net_nodes:
        svg += f'  <circle cx="{x}" cy="{y}" r="{r}" fill="{COLORS["white"]}" stroke="{color}" stroke-width="3" filter="url(#shadow)"/>\n'
        svg += f'  <text x="{x}" y="{y}" text-anchor="middle" dominant-baseline="central" font-size="13px" font-weight="bold" fill="{COLORS["text_primary"]}">{_esc(label)}</text>\n'

    ft, _ = _svg_footer_box(pad, H - S['footer_h'] - 8, W - 2*pad, '✦ ERP/DWHがハブ。接続数が多いノードほど障害影響が大きい')
    svg += ft
    svg += _svg_footer()
    save('25_network', svg)


# ============================================================
# 26. build_matrix — 比較表（スコアカード）
# ============================================================
def gen_scorecard():
    config = {
        'title': 'CRMツール選定 スコアカード',
        'subtitle': '重み付き評価による選定',
        'col_headers': ['Salesforce', 'HubSpot', 'Zoho CRM'],
        'row_headers': ['機能充実度', 'カスタマイズ性', '料金', '導入容易性', 'サポート体制'],
        'cells': [
            ['5/5 - 業界最多の機能', '4/5 - マーケ統合が強み', '3/5 - 基本機能は十分'],
            ['5/5 - Apex開発可能', '3/5 - テンプレートベース', '4/5 - APIが充実'],
            ['2/5 - 高コスト', '4/5 - 無料プランあり', '5/5 - 最安クラス'],
            ['2/5 - 専門人材が必要', '5/5 - 直感的なUI', '4/5 - ガイド充実'],
            ['4/5 - 24h対応（有償）', '4/5 - 日本語対応', '3/5 - 英語中心'],
        ],
        'col_colors': [COLORS['link_blue'], COLORS['alert_red'], COLORS['success_teal']],
        'footer': '✦ 総合: HubSpot 20pt > Zoho 19pt > Salesforce 18pt',
    }
    svg = build_matrix(config)
    save('26_scorecard', svg)


# ============================================================
# メイン実行
# ============================================================
if __name__ == '__main__':
    print('カタログギャラリー用SVG生成中...\n')
    generators = [
        # 既存10種
        ('01 概要図 (vertical)', gen_vertical),
        ('02 タイムライン', gen_timeline),
        ('03 マトリクス', gen_matrix),
        ('04 CJM', gen_journey_map),
        ('05 レイヤー図', gen_layer),
        ('06 ギャップ図', gen_two_columns),
        ('07 階層ツリー (TB)', gen_tree_tb),
        ('08 マインドマップ (LR)', gen_tree_lr),
        ('09 フローチャート', gen_flow),
        ('10 フィードバック図', gen_flow_cycle),
        # 追加16種
        ('11 ロジックツリー', gen_logic_tree),
        ('12 IPO図', gen_ipo),
        ('13 因果ループ図', gen_causal_loop),
        ('14 状態遷移図', gen_state_transition),
        ('15 スイムレーン図', gen_swimlane),
        ('16 サービスブループリント', gen_service_blueprint),
        ('17 オントロジー', gen_ontology),
        ('18 ペルソナ→課題→価値', gen_persona_value),
        ('19 ベン図', gen_venn),
        ('20 シーケンス図', gen_sequence),
        ('21 ポジショニングマップ', gen_positioning_map),
        ('22 トレードオフ曲線', gen_tradeoff),
        ('23 概念地図', gen_concept_map),
        ('24 コンポーネント図', gen_component),
        ('25 ネットワーク図', gen_network),
        ('26 比較表(スコアカード)', gen_scorecard),
    ]

    success = 0
    failed = []
    for name, gen_func in generators:
        try:
            gen_func()
            success += 1
        except Exception as e:
            print(f'  ✗ {name}: {e}')
            failed.append((name, str(e)))

    print(f'\n完了: {success}/{len(generators)} 成功')
    if failed:
        print('失敗:')
        for name, err in failed:
            print(f'  - {name}: {err}')
        sys.exit(1)
