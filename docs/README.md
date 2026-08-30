# ドキュメント案内

## このディレクトリについて

`docs/` には、このスターターキットの説明、ルール、テンプレート、チュートリアル、補助コンテキスト、各コマンド／アプリの設計文書があります。

この README は案内用です。ルールの正本は [`rules/`](rules/README.md) 配下にあります。

## どこから読むか

**リポジトリ全体の目的と、feature 開発の流れそのものは [`../README.md`](../README.md) にあります。** この案内図は、そこから docs 配下へ入ってきた人が目的の文書へ移動するためのものです。

### feature を開発する

feature 新規開発の進め方は2つあります。**どちらも現役の選択肢です。**

| 知りたいこと | 入口 |
|---|---|
| **オートモードを実際に一周してみる（最初の一歩）** | [`tutorials/005_automode_first_feature.md`](tutorials/005_automode_first_feature.md) |
| **実AIでオートモードを実行した履歴を見る**（模範例ではなく実行記録） | [`cli_text_masker/README.md`](cli_text_masker/README.md) |
| **オートモードの仕組み**（stage、Gate、判定値、承認位置、モデル選択） | [`rules/project/70_feature_loop.md`](rules/project/70_feature_loop.md)（正本） |
| **オートモードの runner の使い方**（コマンド、オプション、設定） | [`../tools/README.md`](../tools/README.md) |
| **マニュアルモードで工程を1つずつ進める**（新規 feature でも利用できる） | [`../prompts/README.md`](../prompts/README.md)、[`how_to_use_prompts.md`](how_to_use_prompts.md) |
| 工程全体と承認を置く位置 | [`rules/project/20_workflow.md`](rules/project/20_workflow.md) |

### 構造・ルール・ひな形を知る

| 知りたいこと | 入口 |
|---|---|
| **どこに何があるか**（docs / src / tests の対応、feature 内の各文書、`gates/`、prompts の種類） | [`overview.md`](overview.md) |
| ルールの正本と読み順 | [`rules/README.md`](rules/README.md) |
| テンプレートを選ぶ | [`templates/README.md`](templates/README.md) |
| AI駆動開発の考え方 | [`concept/ai_driven_development.md`](concept/ai_driven_development.md) |

### そのほか

| 知りたいこと | 入口 |
|---|---|
| チュートリアルを選ぶ | [`tutorials/README.md`](tutorials/README.md) |
| 補助コンテキスト・作業メモを確認する | [`context/README.md`](context/README.md) |
| 共通化提案を確認する | [`common/README.md`](common/README.md) |
| prompt 設計の背景を確認する | [`prompt_design_notes.md`](prompt_design_notes.md) |

## コマンド／アプリの設計文書

各 `10_overview.md` を入口に、必要に応じて同じディレクトリ内の feature、結合試験、レビュー、バグ対応の文書へ進んでください。

| コマンド／アプリ | 設計文書の入口 |
|---|---|
| 名前からあいさつ文を作る CLI | [`cli_hello_greeting/10_overview.md`](cli_hello_greeting/10_overview.md) |
| 2つの整数を足す体験用 CLI | [`cli_simple_calculator/10_overview.md`](cli_simple_calculator/10_overview.md) |
| 入力文字列の文字数を返す CLI | [`cli_text_counter/10_overview.md`](cli_text_counter/10_overview.md) |

## 関連する入口

- リポジトリ全体と feature 開発の流れ: [`../README.md`](../README.md)
- prompt 一覧: [`../prompts/README.md`](../prompts/README.md)
- 補助ツール（オートモードの runner を含む）: [`../tools/README.md`](../tools/README.md)
- 品質情報: [`../quality/README.md`](../quality/README.md)
