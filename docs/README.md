# ドキュメント案内

## このディレクトリについて

`docs/` には、このスターターキットの説明、ルール、テンプレート、チュートリアル、補助コンテキスト、各コマンド／アプリの設計文書があります。

この README は案内用です。ルールの正本は [`rules/`](rules/README.md) 配下にあります。

## どこから読むか

| 知りたいこと | 入口 |
|---|---|
| ドキュメント全体の構成 | [`overview.md`](overview.md) |
| AI駆動開発の考え方 | [`concept/ai_driven_development.md`](concept/ai_driven_development.md) |
| prompt の使い方 | [`how_to_use_prompts.md`](how_to_use_prompts.md) |
| prompt を選ぶ | [`../prompts/README.md`](../prompts/README.md) |
| ルールの正本と読み順 | [`rules/README.md`](rules/README.md) |
| テンプレートを選ぶ | [`templates/README.md`](templates/README.md) |
| チュートリアルを選ぶ | [`tutorials/README.md`](tutorials/README.md) |
| 補助コンテキストを確認する | [`context/README.md`](context/README.md) |
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

- リポジトリ全体: [`../README.md`](../README.md)
- 補助ツール: [`../tools/README.md`](../tools/README.md)
- 品質情報: [`../quality/README.md`](../quality/README.md)
