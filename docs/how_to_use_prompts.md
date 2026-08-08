# 汎用プロンプトの使い方

このドキュメントでは、`prompts/` 直下にある汎用プロンプトの使い方を説明します。

汎用プロンプトは、直接書き換えて使う作業メモではありません。固定の作業ルールとして置き、チャットで「参照するプロンプトのパス」と「対象機能情報」を渡して使います。

---

## どこから始めるか

チュートリアルを進めたい場合は、まず `docs/tutorials/010_simple_calculator.md` を開いてください。
汎用プロンプトの使い方だけを確認したい場合は、このドキュメントを上から読んでください。

---

## 基本方針

- `prompts/*.md` は固定の作業ルールとして参照します
- 利用時に `prompts/*.md` を直接編集しません
- チュートリアルでも `prompts/` 直下の汎用プロンプトを使います
- チュートリアル専用プロンプト置き場は作成しません
- AIは、指定されたプロンプト、`AGENTS.md`（薄い入口）、そのプロンプトの `## 必須参照ルール` に列挙されたルール文書に従って作業します
- ルール内容の正本は `docs/rules/` 配下です（索引: [rules/README.md](rules/README.md)）
- AIは、プロンプトに書かれた作業範囲を超えて実装、テスト作成、レビューへ勝手に進みません

---

## 使い方

チャットでは、次のように依頼します。

```text
prompts/create_function_design.md を参照してください。

対象機能フォルダ: docs/cli_simple_calculator/features/calculator/
コマンド/アプリ名: cli_simple_calculator
対象機能名: calculator
作りたいもの: 2つの整数を足し算するシンプルな計算機
補足条件: なし
```

ポイントは、`prompts/create_function_design.md` の中身を書き換えないことです。必要な情報は、チャット側で渡します。

---

## プロンプトの中にある2つの「参照」

各プロンプトには、名前の似た2つの節があります。役割が違うので混同しないでください。

| 節 | 何を指すか | 誰のためのものか |
|---|---|---|
| `## 必須参照ルール` | **その作業でAIが守るルール文書の一覧**（`docs/rules/` 配下） | AI。作業開始前に読む |
| `## 参照するファイル` | **今回の作業対象として読む資料**（仕様書、設計書、実装、テストなど） | AI。作業対象そのもの |

`## 必須参照ルール` は、そのプロンプトで読むルール文書**一覧**の正本です。
ただし、**各ルールの内容の正本は列挙先の `docs/rules/*.md`** であり、プロンプトがルールを定義しているわけではありません。

通常のプロンプトでは、core 2〜3ファイルと project 2〜3ファイル程度を列挙しています。
`prompts/review_prompt_integrity.md` だけは、キット自体の整合性をレビューするため全ルールを読む例外です。

## 「変更してはいけないファイル」と「保護対象」の違い

こちらも似ていますが、別のレイヤです。両方を満たす必要があります。

| 用語 | 意味 | 正本 |
|---|---|---|
| **保護対象** | プロジェクトが定める、AIが人間の明示指示なしに変更できないファイル群 | `docs/rules/project/50_ai_permissions.md` |
| **変更してはいけないファイル** | **今回のtaskで**変更を許可されていないファイル | 各プロンプトの `## 変更してはいけないファイル` |

保護対象でなくても、今回のtaskでは変更できないファイルがあります。逆に、taskの一覧に書かれていなくても保護対象は変更できません。

---

## 短いチャット指示の書き方

標準プロンプトには、作業範囲、変更してよいファイル、変更してはいけないファイル、`tasks.md` の扱い、`src/common/` を勝手に触らないこと、レビュー結果の記録先、feature / entrypoint / 結合試験の責務分担などの共通ルールが含まれています。

そのため、チャットでは毎回すべてのルールを書き直すのではなく、今回固有の情報を中心に渡します。

チャットで渡す主な情報:

- command/app 名
- feature 名
- 対象フォルダ
- 実装ファイル
- テストファイル
- 作りたいもの
- 実行イメージ
- 今回やらないこと
- 補足条件

標準プロンプトに任せてよい内容の例:

- 指定外ファイルを変更しない
- `tasks.md`（現在地メモ）の扱い
- `src/common/` を勝手に作成・更新しない
- レビュー結果を専用の記録先へ書く
- feature / entrypoint / 結合試験の責務を分ける

`tasks.md` は作業状態を引き継ぐための現在地メモです。**AIが直接更新できる範囲は task によって異なります。** 実際の更新可否は、使用する task プロンプトと、`docs/rules/core/50_records_and_reporting.md`／`docs/rules/project/50_ai_permissions.md` を確認してください。

一方で、仕様判断に関わることは人間がチャットで明示します。たとえば、空文字列をどう扱うか、文字数をどう数えるか、fallback import を方針化するか、skip されたテストを成功扱いしてよいか、などです。

短いチャット指示の例:

```text
prompts/implement_feature.md を参照してください。

対象機能フォルダ: docs/<command_or_app_name>/features/<feature_name>/
コマンド/アプリ名: <command_or_app_name>
対象機能名: <feature_name>
実装ファイル: src/<command_or_app_name>/features/<feature_name>.py
テストファイル: tests/<command_or_app_name>/features/test_<feature_name>.py
作りたいもの: <今回作りたい機能>
補足条件: なし
```

仕様として迷いやすい点がある場合は、`補足条件` に短く追加します。

```text
補足条件:
- 空文字列は有効な入力として扱ってください。
- 文字数は Python の len() 相当で数えてください。
- レビューだけ行い、実装ファイルとテストファイルは変更しないでください。
```

---

## 汎用プロンプト一覧

バグ修正フロー全体の進め方は `docs/tutorials/040_bug_fix_flow.md` を参照してください。個別プロンプトを単体で使う前に、報告 → 調査 → 修正計画 → 人間承認 → 実装の順番を確認します。

| プロンプト | 用途 | 主な出力先 |
|---|---|---|
| `prompts/create_overview.md` | コマンド/アプリ全体の overview を作成する | `docs/<command_or_app_name>/10_overview.md` |
| `prompts/create_feature_spec.md` | feature 仕様を作成する | `<対象機能フォルダ>/20_spec.md` |
| `prompts/create_function_design.md` | 関数設計を作成する | `<対象機能フォルダ>/21_design.md` |
| `prompts/create_function_call_flow.md` | 関数呼び出し定義を作成する | `<対象機能フォルダ>/22_flow.md` |
| `prompts/create_test_design.md` | feature 単体のテスト計画を作成する | `<対象機能フォルダ>/23_test_plan.md` |
| `prompts/create_review_checklist.md` | feature 単体レビュー観点と実装着手承認欄を作成する（承認欄は未チェックで作成） | `<対象機能フォルダ>/24_review_checklist.md` |
| `prompts/create_integration_test_plan.md` | command/app 単位の結合試験計画を作成する | `docs/<command_or_app_name>/11_integration_test_plan.md` |
| `prompts/create_common_design_index.md` | 共通設計書の目次・feature 対応表を作成する | `docs/<command_or_app_name>/common_design/30_common_design_index.md` |
| `prompts/create_file_design.md` | 入出力・中間ファイル・ディレクトリ構成の共通設計書を作成する | `docs/<command_or_app_name>/common_design/31_file_design.md` |
| `prompts/create_data_design.md` | 共通データ項目・ID体系・ステータス定義の設計書を作成する | `docs/<command_or_app_name>/common_design/32_data_design.md` |
| `prompts/create_db_design.md` | DB種別・テーブル・カラム・制約・トランザクション方針の設計書を作成する | `docs/<command_or_app_name>/common_design/33_db_design.md` |
| `prompts/implement_feature.md` | feature 本体と feature 単体テストを作成する（事前に `24_review_checklist.md` の実装着手承認欄がすべてチェック済みであることを確認。未チェックがあれば STOP） | 指定された feature 実装ファイル、feature 単体テストファイル |
| `prompts/review_feature_source.md` | feature 実装直後のソースレビューを行う（中間チェック。修正はしない） | チャットで報告（ファイル出力なし） |
| `prompts/implement_entrypoint.md` | `entrypoint.py` と entrypoint のテストを作成する | `src/<command_or_app_name>/entrypoint.py`、`tests/<command_or_app_name>/test_entrypoint_<short_name>.py` |
| `prompts/implement_integration_test.md` | 結合試験を実装する | `tests/<command_or_app_name>/test_integration_<short_name>.py` |
| `prompts/review_feature.md` | feature 単体レビューを行う | `<対象機能フォルダ>/25_review_result.md` |
| `prompts/review_command.md` | command/app 全体レビューを行う | `docs/<command_or_app_name>/12_command_review_result.md` |
| `prompts/review_context.md` | `docs/context/` を横断探索し、正式資料への反映候補・矛盾候補・未決事項・却下案の混入候補・人間確認事項を候補として整理する（候補のみ。正式資料・docs/context/ は変更しない） | チャットで報告（ファイル出力なし） |
| `prompts/analyze_code_change_impact.md` | コード起点の変更案を、バグ・仕様変更・内部設計変更・リファクタリング・類似機能間の整合性改善・標準化・共通化候補などに整理し、影響範囲、変更内容の正本となる最上流の正式資料、上流から下流への更新順、次の作業を報告する（ファイルは変更しない） | チャットで報告（ファイル出力なし） |
| `prompts/create_bug_report.md` | バグ報告書を作成する（原因調査・修正はしない） | `docs/<command_or_app_name>/bugs/<bug_id>/10_bug_report.md` |
| `prompts/investigate_bug.md` | バグ原因を調査し調査書を作成する（修正はしない） | `docs/<command_or_app_name>/bugs/<bug_id>/20_bug_investigation.md` |
| `prompts/create_bug_fix_plan.md` | バグ修正計画書を作成する（承認待ち。修正はしない） | `docs/<command_or_app_name>/bugs/<bug_id>/30_bug_fix_plan.md` |
| `prompts/implement_bug_fix.md` | 承認済み修正計画に従ってバグを修正する | 修正計画書に記載された実装ファイル、テストファイル |
| `prompts/prepare_work_note.md` | 作業の経緯・判断・手戻り・現在地を、人間とAIが後から追える作業メモへ構成する。リポジトリを参照できるAIでも参照できないAIでも利用でき、人間確認後、保存できるAIはそのまま保存し、保存できないAIは自己完結した反映指示を生成する（開発工程には含まれない） | `docs/context/work_notes/<work_folder>/README.md` ほか |
| `prompts/review_prompt_integrity.md` | スターターキット自体のプロンプト・テンプレート・導線の完全性をレビューする（開発対象機能のレビューではない。キットのメンテナンス用） | チャットで報告（ファイル出力なし） |

---

## review_feature と review_command の役割分担

`prompts/review_feature_source.md` は feature 実装直後の中間チェック用です。`implement_feature.md` 直後に、実装ファイルと単体テストファイルを仕様・設計・テスト計画と照合します。修正候補はチャットで報告するだけで、ファイルは変更しません。`25_review_result.md` も作成しません。

`prompts/review_feature.md` は feature 単体レビュー用です。主に feature 配下の `20_spec.md` から `24_review_checklist.md`、feature 実装、feature 単体テストを確認し、結果を `<対象機能フォルダ>/25_review_result.md` に記録します。

`prompts/review_command.md` は command/app 全体レビュー用です。`10_overview.md`、`entrypoint.py`、`test_entrypoint_<short_name>.py`、`11_integration_test_plan.md`、`test_integration_<short_name>.py`、feature 単体レビュー結果を確認し、結果を `docs/<command_or_app_name>/12_command_review_result.md` に記録します。

entrypoint と結合試験まで含めた最終確認は、`review_command.md` で扱います。`review_feature.md` で entrypoint や結合試験に触れる場合は、feature との責務分担に関係する範囲にとどめます。

`prompts/review_context.md` は `docs/context/` の横断探索を専任で行うプロンプトです。通常レビュー（`review_feature.md` / `review_command.md`）やバグ調査（`investigate_bug.md` / `create_bug_fix_plan.md`）は、`docs/context/` を軽い確認トリガーとしてのみ扱い、横断探索を主責務にしません。context 量が増えても通常レビューやバグ調査を完遂できるようにするためです。`docs/context/` の深掘りが必要になったら、`review_context.md` に委譲します。

`review_context.md` は候補出し専用です。正式資料・`docs/context/`・`bugs/` 配下のいずれも変更せず、結果はチャットで報告します。採用・却下・保留は人間が判断し、採用されたものだけを別作業として正式資料へ反映します。

---

## テスト計画と結合試験計画の役割分担

`23_test_plan.md` は feature 単体のテスト計画です。feature の詳細ロジック、正常系、異常系、境界値などを確認します。

`11_integration_test_plan.md` は command/app 単位の結合試験計画です。`entrypoint.py` と feature の接続、入出力、終了コード、エラー時の扱いを確認します。

---

## レビュー結果の役割分担

| ファイル | 役割 |
|---|---|
| `24_review_checklist.md` | feature 単体レビューで確認する観点を定義する |
| `25_review_result.md` | feature 単体レビューの結果、指摘事項、判定を記録する |
| `12_command_review_result.md` | command/app 全体レビューの結果、指摘事項、判定を記録する |

既存の `25_review_result.md` や `12_command_review_result.md` がある場合でも、古い判定をそのまま採用しません。現在のファイル群を読み直して再レビューし、レビュー結果ファイルを上書き更新します。

---

## レビュー補助メモ

ドキュメント作成系・実装系のプロンプトでは、作業完了報告にレビュー補助メモを添えます。
これは、AIが作った成果物を人間がレビューする前に、重点的に見る箇所を素早く把握するための短い申し送りです。

レビュー補助メモの記載項目とルールは `docs/rules/core/50_records_and_reporting.md` の「レビュー補助メモ」を参照してください。
AIの思考過程の記録ではなく、`tasks.md` にも書きません。専用ファイルも作りません。

---

## 対象情報として渡すもの

- 参照するプロンプトのパス
- 対象 overview
- 対象 entrypoint
- entrypoint テストファイル
- 対象機能フォルダ
- コマンド/アプリ名
- 対象機能名
- 作りたいもの
- 実行イメージまたは利用イメージ
- 今回やらないこと
- 実装ファイル
- テストファイル
- レビュー結果ファイル
- 結合試験計画ファイル
- 補足条件

実装ファイルとテストファイルは、原則として以下の形にします。

```text
src/<command_or_app_name>/features/<feature_name>.py
tests/<command_or_app_name>/features/test_<feature_name>.py
```

entrypoint テストと結合試験は、複数 command/app 間で同名ファイルが衝突しないように以下の標準命名にします。

```text
tests/<command_or_app_name>/test_entrypoint_<short_name>.py
tests/<command_or_app_name>/test_integration_<short_name>.py
```

`<short_name>` は、単一 feature の command/app では feature 名を使います。
複数 feature を束ねる command/app では、command/app を短く表す名前を使います。

---

## 変更してはいけないもの

汎用プロンプトを使う作業では、原則として次を変更しません（代表例）。

- `prompts/*.md`
- `AGENTS.md`、`docs/rules/`
- `docs/templates/`
- 指定された出力先以外の feature ドキュメント
- 指定された実装ファイル以外の実装コード
- 指定されたテストファイル以外のテストコード
- `src/common/`
- CI/CD、デプロイ関連のファイル

必要だと感じた場合も、勝手に変更せず、今後の改善候補として記録します。

**保護対象の一覧（AIが人間の明示指示なしに変更できないファイル）の正本は `docs/rules/project/50_ai_permissions.md` です。**
**今回のtaskで変更できる範囲は、使用するプロンプトの `## 変更してよいファイル` / `## 変更してはいけないファイル` を見てください。**

---

## 依頼例

```text
prompts/review_feature.md を参照してください。

対象機能フォルダ: docs/cli_simple_calculator/features/calculator/
コマンド/アプリ名: cli_simple_calculator
対象機能名: calculator
実装ファイル: src/cli_simple_calculator/features/calculator.py
テストファイル: tests/cli_simple_calculator/features/test_calculator.py
レビュー結果ファイル: docs/cli_simple_calculator/features/calculator/25_review_result.md
補足条件: レビューだけ行い、実装ファイルとテストファイルは変更しないでください。
```

```text
prompts/analyze_code_change_impact.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
変更したい内容: 入力チェックの書き方を、他の feature と同じ方式にそろえたい
変更したい理由または違和感: 正常に動いているが、この feature だけ例外の投げ方が違う気がする
関連する実装ファイル: src/cli_text_counter/features/text_counter.py
類似機能または比較対象: src/cli_hello_greeting/features/greeting.py
外部から見える動作を変えたいか: 変えたくない
補足条件: 分析だけ行い、ファイルは変更しないでください。
```

分析結果で正本と更新順を確認してから、個別の文書更新や実装を別作業として依頼します。

```text
prompts/review_command.md を参照してください。

コマンド/アプリ名: cli_simple_calculator
対象 overview: docs/cli_simple_calculator/10_overview.md
対象 entrypoint: src/cli_simple_calculator/entrypoint.py
entrypoint テスト: tests/cli_simple_calculator/test_entrypoint_calculator.py
結合試験計画: docs/cli_simple_calculator/11_integration_test_plan.md
結合試験ファイル: tests/cli_simple_calculator/test_integration_calculator.py
command/app 全体レビュー結果ファイル: docs/cli_simple_calculator/12_command_review_result.md
補足条件: レビューだけ行い、レビュー結果ファイル以外は変更しないでください。
```
