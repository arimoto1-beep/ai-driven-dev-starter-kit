# AI駆動開発スターターキット

AIにいきなりコードを書かせるのではなく、**仕様・設計・テスト設計・実装・レビューを工程として分け、人間が重要な判断を持ったまま**開発を進めるためのスターターキットです。

- AIへ丸投げせず、**人間が仕様を決め、最後に受け入れる**
- 各工程の成果物をファイルとして残し、**後から理解・レビュー・引き継ぎできる**ようにする
- AIのレビューを、実装したAIとは**別プロセスで独立して**行う
- 何をどう判断したかを記録として残す

完成度の高いアプリを作ることよりも、この進め方を体験することを目的としています。考え方の背景は [AI駆動開発コンセプト](docs/concept/ai_driven_development.md) を参照してください。

---

## まず知ってほしい開発の流れ

新しい feature を作るときの基本的な流れです。**★が人間の判断ポイント**です。

```text
人間が 20_spec.md（仕様）を用意する
        ↓
AIが仕様をレビューする（Spec Review。何度でも実行できる）
        ↓
★ 人間が仕様を承認する                      … CP1
        ↓
   ここから先は、承認された仕様が前提になる
        ↓
AIが設計する                                 … G1
        ↓
AIがテスト設計をする                          … G2
        ↓
AIが実装・テストを作り、レビューする            … CP3
        ↓
★ 人間が受け入れを判断する                    … CP3
        ↓
      完成
```

- **最初の入力は `20_spec.md` です。** ここが決まらないとAIは製造工程へ進めません
- **通常フローで必ず人間が承認・受け入れを行う固定ポイントは、仕様承認（CP1）と受け入れ（CP3）の2か所**です。このほかにも、AIが判断できない事項に行き当たった場合は人間へ渡されます
- 設計・テスト設計・実装の各段階で、AIは**作る役（Worker）とレビューする役（Reviewer）に分かれ**、指摘があれば修正と再レビューを行います
- `CP1` / `G1` / `G2` / `CP3` は各段階の呼び名です。**名前を覚えなくても流れは追えます**

この進め方を **オートモード** と呼びます。工程を1つずつ手で進める **マニュアルモード** もあります（後述）。

正確な定義は [オートモードの正本](docs/rules/project/70_feature_loop.md) を参照してください。

---

## 人間がすること / AIがすること

| | やること |
|---|---|
| **人間** | 仕様を決める／**CP1 で仕様を承認する**／**CP3 で受け入れを判断する**／AIが判断できない事項を決める |
| **AI** | 仕様のレビュー／設計／テスト設計／実装とテスト／各段階のレビューと記録 |

**「承認したら、あとは全部AI任せ」ではありません。**

- AIは、承認済みの仕様を超えて仕様を勝手に補完しません。不足を見つけたら**仕様工程へ差し戻します**
- 業務上の判断が必要になった場合、AIは決めずに**停止して人間へ渡します**
- **AIが承認欄にチェックを入れることはありません。** 承認するのは人間だけです

判定と停止の記録は、feature ごとの `gates/` に Gate記録として残ります。

---

## オートモードの最初の一歩

### 準備

オートモードは、runner が AI を起動して工程を進めます。実行前に、[`docs/rules/project/70_feature_loop.md`](docs/rules/project/70_feature_loop.md) の設定ブロックへ次の2種類を記入してください。

- `model_cheap` / `model_standard` / `model_strong`：使うモデル名
- `ai_command`：AI を起動するコマンド

リポジトリへコミットしたくない場合は、同じ形式で `tools/feature_loop.local` へ書けます。詳しくは [tools/README.md](tools/README.md) を参照してください。

### 進め方

```text
1. feature フォルダに 20_spec.md を用意する
   docs/<command_or_app_name>/features/<feature_name>/20_spec.md
   ひな形: docs/templates/20_spec_template.md
   prompts/create_feature_spec.md でAIに作成を補助させることもできる
   （確定させるのは人間）

2. 仕様をAIにレビューさせる
   python tools/feature_runner.py --feature <app>/<feature> --spec-review

3. 指摘を確認して仕様を直し、納得したら CP1 Gate記録の
   「仕様承認」欄にチェックを入れる（人間が行う）

4. runner を実行する
   python tools/feature_runner.py --feature <app>/<feature>
   → 設計・テスト設計・実装まで進み、受け入れ判断の手前で停止する

5. 最新の CP3 Gate記録の「受け入れ判断」欄を確認する（人間が行う）
```

実行前に何が起きるか確認したい場合は `--dry-run`、いまの状態を見たい場合は `--status` を使います。

```bash
python tools/feature_runner.py --feature <app>/<feature> --status
```

**実際に1つの feature を最後まで通して試したい場合は、[オートモードの最初の一歩チュートリアル](docs/tutorials/005_automode_first_feature.md) を参照してください。** 題材つきで、上の5ステップを一周します。

途中で止まった場合の再開、通過済み工程のやり直し、使用モデルの自動選択にも対応しています。オプションの一覧と使い分けは [tools/README.md](tools/README.md)、仕組みの正本は [`70_feature_loop.md`](docs/rules/project/70_feature_loop.md) にあります。

---

## もう一つの進め方：マニュアルモード

**個別の prompt を人間が1つずつ実行する進め方です。** オートモードに置き換えられたものではなく、現役の選択肢です。

- 工程ごとに内容を細かく確認したい場合
- AIに任せる範囲を1手ずつ制御したい場合
- 既存機能の変更、バグ対応など、feature を一から作る流れに乗らない作業

**新しい feature を作る場合でも、マニュアルモードを選べます。** オートモードの Worker は、内部でこれらの個別 prompt へ委譲しているため、成果物の作り方は同じです。

| 試したいこと | 入口 |
|---|---|
| 単一 feature を一通り試す | [`010_simple_calculator.md`](docs/tutorials/010_simple_calculator.md) |
| コマンド／アプリと複数 feature をゼロから作る | [`020_create_new_sample_from_scratch.md`](docs/tutorials/020_create_new_sample_from_scratch.md) |
| 実装済み feature の変更を整理する | [`030_update_existing_feature.md`](docs/tutorials/030_update_existing_feature.md) |
| バグ報告から修正までを試す | [`040_bug_fix_flow.md`](docs/tutorials/040_bug_fix_flow.md) |

prompt の一覧は [prompts/README.md](prompts/README.md)、使い方は [docs/how_to_use_prompts.md](docs/how_to_use_prompts.md) にあります。

---

## 想定する利用環境

- Pythonを実行できる環境（runner は標準ライブラリのみで動作します。テスト実行には [`requirements.txt`](requirements.txt) の `pytest` を使います）

必要なAI環境は、進め方によって異なります。

| 進め方 | 必要なもの |
|---|---|
| **マニュアルモード** | リポジトリ内の文書を参照できるAIコーディングエージェント（GitHub Copilot Agent Mode など） |
| **オートモード** | runner が非対話で起動できるAI CLI |

オートモードで使うAI CLI には、次が必要です。

- 1回の指示を渡して**非対話で実行できる**こと
- 使う**モデルをコマンドライン引数で指定できる**こと
- リポジトリ内のファイルを**読み書きできる**こと

`ai_command` には、この起動コマンドをカンマ区切りの argv テンプレートとして書きます。指示文が入る位置を `{instruction}`、モデル名が入る位置を `{model}` で示します。

```text
ai_command = <AI CLI>,<非対話実行のオプション>,{instruction},<モデル指定のオプション>,{model}
```

**特定のベンダーやツールに限定しません。** 上記を満たすAI CLI であれば利用できます。記入例と設定手順は [tools/README.md](tools/README.md) にあります。

実装言語や依存関係の設定は [実装ルール](docs/rules/project/30_development_rules.md)、テスト環境と検証方法は [テストルール](docs/rules/project/40_testing_rules.md) を参照してください。

---

## リポジトリ構成

```text
ai-driven-dev-starter-kit/
├─ README.md
├─ AGENTS.md                            ← AIが最初に読む入口
├─ CLAUDE.md                            ← Claude Code向け補助入口
├─ docs/
│  ├─ README.md                         ← ドキュメント全体の案内
│  ├─ overview.md                       ← ドキュメント構成の説明
│  ├─ how_to_use_prompts.md             ← promptの利用方法
│  ├─ rules/                            ← ルール内容の正本
│  │  ├─ README.md                      ← ルール体系の索引
│  │  ├─ core/                          ← 共通原則
│  │  └─ project/                       ← このキットの具体的な設定
│  │     └─ 70_feature_loop.md          ← オートモードの正本
│  ├─ concept/                          ← AI駆動開発の考え方
│  ├─ context/                          ← 補助コンテキスト、作業メモ
│  ├─ common/                           ← 共通化提案
│  ├─ templates/                        ← 文書のひな形
│  ├─ tutorials/                        ← 体験用チュートリアル
│  └─ <command_or_app_name>/            ← コマンド／アプリの設計文書
│     ├─ 10_overview.md
│     └─ features/<feature_name>/
│        ├─ 20_spec.md                  ← 人間が用意する仕様
│        ├─ 21_design.md、22_flow.md     ← 設計（G1）
│        ├─ 23_test_plan.md、24_review_checklist.md  ← テスト設計（G2）
│        ├─ 25_review_result.md         ← レビュー結果
│        └─ gates/                      ← Gate記録（判定と承認の履歴）
├─ prompts/                             ← task prompt
├─ src/                                 ← 実装コード
├─ tests/                               ← テストコード
├─ tools/
│  └─ feature_runner.py                 ← オートモードのrunner
├─ quality/                             ← 補助ツールが記録・集約した情報
├─ requirements.txt
└─ LICENSE
```

### docs・src・testsの関係

コマンド／アプリごとに、同じ名前の文書・実装・テストを対応させています。

```text
docs/<command_or_app_name>/
src/<command_or_app_name>/
tests/<command_or_app_name>/
```

`docs/<command_or_app_name>/10_overview.md` が設計文書の入口です。feature 固有の資料は、各コマンド／アプリの `features/` 配下から確認できます。

配置、文書の分類、命名の正式な定義は [文書構造](docs/rules/project/10_document_structure.md)、人向けの構成説明は [docs/overview.md](docs/overview.md) を参照してください。

---

## 詳しく知りたい場合

| 知りたいこと | 入口 |
|---|---|
| **オートモードの仕組み（stage、Gate、判定値、モデル選択）** | [project: feature オートモード](docs/rules/project/70_feature_loop.md) |
| **runner の使い方とオプション** | [tools/README.md](tools/README.md) |
| 工程全体と各taskの位置 | [project: ワークフロー](docs/rules/project/20_workflow.md) |
| 承認とレビューの原則 | [core: 承認とレビュー](docs/rules/core/20_approval_and_review.md) |
| AIの変更範囲と保護対象 | [project: AIの権限と保護対象](docs/rules/project/50_ai_permissions.md) |
| レビュー結果の扱い | [project: レビュー方針](docs/rules/project/25_review_policy.md) |
| 実装上の役割分担 | [project: 実装ルール](docs/rules/project/30_development_rules.md) |
| テストの単位と検証方法 | [project: テストルール](docs/rules/project/40_testing_rules.md) |
| ルール体系の全体像 | [docs/rules/README.md](docs/rules/README.md) |
| promptの選び方 | [prompts/README.md](prompts/README.md) |
| promptの使い方 | [docs/how_to_use_prompts.md](docs/how_to_use_prompts.md) |
| テンプレートの選び方 | [docs/templates/README.md](docs/templates/README.md) |
| チュートリアルの選び方 | [docs/tutorials/README.md](docs/tutorials/README.md) |
| ドキュメント全体 | [docs/README.md](docs/README.md) |
| 補助コンテキスト | [docs/context/README.md](docs/context/README.md) |
| 品質情報 | [quality/README.md](quality/README.md) |

個別taskの手順、参照資料、変更範囲は、使用する [`prompts/*.md`](prompts/README.md) を確認してください。

---

## サンプル

| サンプル | 位置づけ | 設計文書の入口 |
|---|---|---|
| `cli_hello_greeting` | 仕様・設計・実装・テスト・レビューが揃ったサンプル | [overview](docs/cli_hello_greeting/10_overview.md) |
| `cli_simple_calculator` | チュートリアルを途中から始めるための初期状態サンプル | [overview](docs/cli_simple_calculator/10_overview.md) |
| `cli_text_counter` | 作業状態の記録やバグ対応文書も確認できるサンプル | [overview](docs/cli_text_counter/10_overview.md) |

## 実行例

サンプルとは別に、**実際にAIを動かしたときの記録**を残しています。**模範例ではありません。**

| 実行例 | 内容 | 入口 |
|---|---|---|
| `cli_text_masker` | 実AIでオートモードを CP1 から CP3 まで一周した履歴。停止と復旧を含む Gate記録が残っている | [README](docs/cli_text_masker/README.md) |

当時の成果物をそのまま保存しているため、**現在の仕様と異なる箇所があります。** 詳しくは上記 README を参照してください。

## ライセンス

このプロジェクトはMIT Licenseで公開しています。詳細は [LICENSE](LICENSE) を参照してください。
