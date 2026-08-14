# AI駆動開発スターターキット

このリポジトリは、AIコーディングエージェントを使い、人間が仕様・設計・実装・テスト・レビューを確認しながら小さく開発する流れを体験するためのスターターキットです。

完成度の高いアプリを作ることよりも、人間が内容を理解し、レビューし、引き継ぎ、最終的な責任を持てる進め方を体験することを目的としています。考え方の背景は [AI駆動開発コンセプト](docs/concept/ai_driven_development.md) を参照してください。

## このリポジトリで体験できること

- コマンド／アプリ単位で `docs`・`src`・`tests` を対応させる構成
- feature 単位で仕様、設計、テスト観点、実装を整理する流れ
- AIに渡す task prompt と、ルール正本を分けて管理する方法
- 文書作成、実装、テスト、レビューを段階的に確認する進め方
- 新規作成、既存機能の変更、バグ対応を題材にしたチュートリアル
- 検証記録とレビュー結果を集約する補助ツール

## 想定する利用環境

- Pythonを実行できる環境
- GitHub Copilot Agent Modeなど、リポジトリ内の文書を参照できるAIコーディングエージェント

実装言語や依存関係の設定は [実装ルール](docs/rules/project/30_development_rules.md)、テスト環境と検証方法は [テストルール](docs/rules/project/40_testing_rules.md) を参照してください。依存関係は [`requirements.txt`](requirements.txt) にあります。

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
│  ├─ concept/                          ← AI駆動開発の考え方
│  ├─ context/                          ← 補助コンテキスト
│  ├─ common/                           ← 共通化提案
│  ├─ templates/                        ← 文書のひな形
│  ├─ tutorials/                        ← 体験用チュートリアル
│  └─ <command_or_app_name>/            ← コマンド／アプリの設計文書
├─ prompts/                             ← task prompt
├─ src/                                 ← 実装コード
├─ tests/                               ← テストコード
├─ tools/                               ← 品質確認の補助ツール
├─ quality/                             ← 補助ツールが記録・集約した情報
├─ requirements.txt
└─ LICENSE
```

## 主要な入口

| 知りたいこと | 入口 |
|---|---|
| ドキュメント全体 | [docs/README.md](docs/README.md) |
| ルール体系 | [docs/rules/README.md](docs/rules/README.md) |
| promptの選び方 | [prompts/README.md](prompts/README.md) |
| promptの使い方 | [docs/how_to_use_prompts.md](docs/how_to_use_prompts.md) |
| テンプレートの選び方 | [docs/templates/README.md](docs/templates/README.md) |
| チュートリアルの選び方 | [docs/tutorials/README.md](docs/tutorials/README.md) |
| 補助コンテキスト | [docs/context/README.md](docs/context/README.md) |
| 補助ツール | [tools/README.md](tools/README.md) |
| 品質情報 | [quality/README.md](quality/README.md) |

## docs・src・testsの関係

コマンド／アプリごとに、同じ名前の文書・実装・テストを対応させています。

```text
docs/<command_or_app_name>/
src/<command_or_app_name>/
tests/<command_or_app_name>/
```

`docs/<command_or_app_name>/10_overview.md` が設計文書の入口です。feature固有の資料は、各コマンド／アプリの `features/` 配下から確認できます。

配置、文書の分類、命名の正式な定義は [文書構造](docs/rules/project/10_document_structure.md)、人向けの構成説明は [docs/overview.md](docs/overview.md) を参照してください。

## 作業の全体像

このキットでは、文書作成、実装、テスト、レビューを分け、人間が段階ごとに確認できるようにしています。変更やバグ対応も、内容を整理してから対応するtaskへ進む構成です。

| 確認したいこと | 参照先 |
|---|---|
| 工程全体と各taskの位置 | [project: ワークフロー](docs/rules/project/20_workflow.md) |
| 承認とレビュー | [core: 承認とレビュー](docs/rules/core/20_approval_and_review.md) |
| 変更内容の整理 | [core: 進め方の原則](docs/rules/core/10_workflow.md) |
| 実装上の役割分担 | [project: 実装ルール](docs/rules/project/30_development_rules.md) |
| テストの単位と検証方法 | [project: テストルール](docs/rules/project/40_testing_rules.md) |
| AIの変更範囲と保護対象 | [project: AIの権限と保護対象](docs/rules/project/50_ai_permissions.md) |
| レビュー結果の扱い | [project: レビュー方針](docs/rules/project/25_review_policy.md) |
| バグ対応を試す | [バグ修正フローのチュートリアル](docs/tutorials/040_bug_fix_flow.md) |
| 実装済みfeatureの変更を試す | [既存feature変更のチュートリアル](docs/tutorials/030_update_existing_feature.md) |

個別taskの手順、参照資料、変更範囲は、使用する [`prompts/*.md`](prompts/README.md) を確認してください。

## はじめて使う場合

1. このREADMEでリポジトリの目的と構成を確認する
2. [docs/README.md](docs/README.md) から、知りたい文書の入口を選ぶ
3. [AI駆動開発コンセプト](docs/concept/ai_driven_development.md) で考え方を確認する
4. [汎用promptの使い方](docs/how_to_use_prompts.md) を確認する
5. [チュートリアル案内](docs/tutorials/README.md) から、試したい題材を選ぶ

一連の流れを初めて試す場合は、既存の初期状態サンプルから始める [simple-calculatorチュートリアル](docs/tutorials/010_simple_calculator.md) が入口です。

## サンプル

| サンプル | 位置づけ | 設計文書の入口 |
|---|---|---|
| `cli_hello_greeting` | 仕様・設計・実装・テスト・レビューが揃ったサンプル | [overview](docs/cli_hello_greeting/10_overview.md) |
| `cli_simple_calculator` | チュートリアルを途中から始めるための初期状態サンプル | [overview](docs/cli_simple_calculator/10_overview.md) |
| `cli_text_counter` | 作業状態の記録やバグ対応文書も確認できるサンプル | [overview](docs/cli_text_counter/10_overview.md) |

## ライセンス

このプロジェクトはMIT Licenseで公開しています。詳細は [LICENSE](LICENSE) を参照してください。
