# simple-calculator チュートリアル

このチュートリアルでは、`cli_simple_calculator` の `calculator` 機能を題材に、AI駆動開発の流れを小さく体験します。

チュートリアル専用プロンプトは使いません。
`prompts/` 直下の汎用プロンプトを参照し、チャットで「参照するプロンプトのパス」と「対象機能情報」を渡して進めます。

標準 `prompts/*.md` には、変更してよい範囲、変更してはいけない範囲、`tasks.md` 更新、レビュー結果の記録先、feature / entrypoint / 結合試験の責務分担などの共通ルールが入っています。
チャットでは、参照するプロンプト、対象情報、今回だけの補足条件を短く渡します。詳しくは `docs/how_to_use_prompts.md` の「短いチャット指示の書き方」を参照してください。

---

## 前提

最初の状態では、以下の仕様書と現在地メモが用意されています。

```text
docs/cli_simple_calculator/10_overview.md
docs/cli_simple_calculator/tasks.md
docs/cli_simple_calculator/features/calculator/20_spec.md
docs/cli_simple_calculator/features/calculator/tasks.md
```

このチュートリアルで作成する主なファイルは以下です。

- `docs/cli_simple_calculator/features/calculator/21_design.md`
- `docs/cli_simple_calculator/features/calculator/22_flow.md`
- `docs/cli_simple_calculator/features/calculator/23_test_plan.md`
- `docs/cli_simple_calculator/features/calculator/24_review_checklist.md`
- `docs/cli_simple_calculator/features/calculator/25_review_result.md`
- `docs/cli_simple_calculator/11_integration_test_plan.md`
- `docs/cli_simple_calculator/12_command_review_result.md`
- `src/cli_simple_calculator/entrypoint.py`
- `src/cli_simple_calculator/features/calculator.py`
- `tests/cli_simple_calculator/test_entrypoint_calculator.py`
- `tests/cli_simple_calculator/test_integration_calculator.py`
- `tests/cli_simple_calculator/features/test_calculator.py`

作業後の `tasks.md` 更新は、工程によって扱いが異なります。**扱いは、使用する task プロンプトと `docs/rules/project/50_ai_permissions.md`（`docs/rules/core/50_records_and_reporting.md` も参照）を確認してください。**

`prompts/*.md` は直接編集しません。
必要な情報は、各ステップのチャット例としてAIに渡します。

---

## tasks.md の使い方

チュートリアル開始時は、`docs/cli_simple_calculator/tasks.md` を確認して、command/app 全体の現在地を把握します。
feature 作業に入る前は、`docs/cli_simple_calculator/features/calculator/tasks.md` を確認して、個別機能の現在地を把握します。

作業後の tasks.md の扱いは工程によって異なります。各 `prompts/*.md` の「作業後の tasks.md 更新」または「tasks.md 更新候補」セクションに従い、更新可否の詳細は `docs/rules/project/50_ai_permissions.md` を確認してください。

以降の「作成または更新されるファイル」に `tasks.md` が含まれるステップはドキュメント作成工程・レビュー結果作成工程です。実装工程のステップには tasks.md は含まれません。

---

## 1. 完成済みサンプルで構成を確認する（任意・初回向け）

まず、完成済みサンプル `cli_hello_greeting` を使って、docs / src / tests の対応関係を確認します。
これはAIにサンプルを学習させて次の実装へ流用させるためではなく、利用者がスターターキットの構成を理解するための任意ステップです。

すでに構成を理解している場合や、2回目以降に進める場合は、このステップをスキップして `2. 関数設計を作成する` から始めても構いません。

チャット例:

```text
AGENTS.md を確認したうえで、完成済みサンプルの docs / src / tests の対応関係を説明してください。

確認対象:
- docs/cli_hello_greeting/10_overview.md
- docs/cli_hello_greeting/tasks.md
- docs/cli_hello_greeting/features/greeting/
- docs/cli_hello_greeting/features/greeting/tasks.md
- src/cli_hello_greeting/
- tests/cli_hello_greeting/

確認してほしいこと:
- 20_spec.md の仕様が実装にどう反映されているか
- 21_design.md の関数設計が実装にどう反映されているか
- 22_flow.md の呼び出し定義が実装にどう反映されているか
- 23_test_plan.md の観点がテストにどう反映されているか
- entrypoint.py と features/greeting.py の責務がどう分かれているか

このステップではファイルを変更しないでください。
```

---

## 2. 関数設計を作成する

`prompts/create_function_design.md` を参照して、関数設計を作成します。
作業前に `docs/cli_simple_calculator/features/calculator/tasks.md` を確認し、feature の現在地を把握します。

チャット例:

```text
prompts/create_function_design.md を参照してください。

対象機能フォルダ: docs/cli_simple_calculator/features/calculator/
コマンド/アプリ名: cli_simple_calculator
対象機能名: calculator
作りたいもの: 2つの整数を足し算するシンプルな計算機
補足条件: entrypoint.py は薄くし、機能ロジックは features/calculator.py に置いてください。
```

作成または更新されるファイル:

```text
docs/cli_simple_calculator/features/calculator/21_design.md
docs/cli_simple_calculator/tasks.md
docs/cli_simple_calculator/features/calculator/tasks.md
```

---

## 3. 関数呼び出し定義を作成する

`prompts/create_function_call_flow.md` を参照して、関数同士の呼び出し順と責務分担を整理します。

チャット例:

```text
prompts/create_function_call_flow.md を参照してください。

対象機能フォルダ: docs/cli_simple_calculator/features/calculator/
コマンド/アプリ名: cli_simple_calculator
対象機能名: calculator
作りたいもの: 2つの整数を足し算するシンプルな計算機
補足条件: entrypoint.py から features/calculator.py を呼び出す流れにしてください。
```

作成または更新されるファイル:

```text
docs/cli_simple_calculator/features/calculator/22_flow.md
docs/cli_simple_calculator/tasks.md
docs/cli_simple_calculator/features/calculator/tasks.md
```

---

## 4. テスト計画を作成する

`prompts/create_test_design.md` を参照して、feature 単体テストの観点を整理します。

チャット例:

```text
prompts/create_test_design.md を参照してください。

対象機能フォルダ: docs/cli_simple_calculator/features/calculator/
コマンド/アプリ名: cli_simple_calculator
対象機能名: calculator
作りたいもの: 2つの整数を足し算するシンプルな計算機
補足条件: feature 単体テストは tests/cli_simple_calculator/features/test_calculator.py に置く前提で整理してください。entrypoint の引数解析、標準出力、終了コードは後続の entrypoint テストで扱ってください。
```

作成または更新されるファイル:

```text
docs/cli_simple_calculator/features/calculator/23_test_plan.md
docs/cli_simple_calculator/tasks.md
docs/cli_simple_calculator/features/calculator/tasks.md
```

---

## 5. レビュー観点を作成する

`prompts/create_review_checklist.md` を参照して、レビューで確認する観点を作成します。

`24_review_checklist.md` はレビュー観点の定義です。
レビュー結果や指摘事項は書き込みません。

チャット例:

```text
prompts/create_review_checklist.md を参照してください。

対象機能フォルダ: docs/cli_simple_calculator/features/calculator/
コマンド/アプリ名: cli_simple_calculator
対象機能名: calculator
作りたいもの: 2つの整数を足し算するシンプルな計算機
補足条件: common は保護対象として扱い、共通化候補は提案にとどめてください。
```

作成または更新されるファイル:

```text
docs/cli_simple_calculator/features/calculator/24_review_checklist.md
docs/cli_simple_calculator/tasks.md
docs/cli_simple_calculator/features/calculator/tasks.md
```

---

## 5a. 実装着手承認欄を確認する（人間が行う）

`docs/cli_simple_calculator/features/calculator/24_review_checklist.md` の末尾にある実装着手承認欄を確認してください。

すべての項目を確認したら、チェックを入れてください。
チェックを入れるのは人間です。AIはこの欄にチェックを入れません。

未チェック項目がある状態で次のステップに進むと、`prompts/implement_feature.md` が STOP します。

---

## 6. feature 実装と feature 単体テストを作成する

`prompts/implement_feature.md` を参照して、feature 本体と feature 単体テストを作成します。

チャット例:

```text
prompts/implement_feature.md を参照してください。

対象機能フォルダ: docs/cli_simple_calculator/features/calculator/
コマンド/アプリ名: cli_simple_calculator
対象機能名: calculator
実装ファイル: src/cli_simple_calculator/features/calculator.py
テストファイル: tests/cli_simple_calculator/features/test_calculator.py
作りたいもの: 2つの整数を足し算するシンプルな計算機
補足条件: なし
```

作成または更新されるファイル:

```text
src/cli_simple_calculator/features/calculator.py
tests/cli_simple_calculator/features/test_calculator.py
```

tasks.md の更新が必要な場合は、作業報告に「tasks.md 更新候補」として提示されます。人間が確認して必要であれば別作業として反映します。

---

## 7. feature ソースレビューを行う

`prompts/review_feature_source.md` を参照して、feature 実装ファイルと feature 単体テストファイルを対象にソースレビューを行います。

このステップでは問題を見つけてもファイルを修正しません。修正候補と確認結果をチャットで報告します。
`25_review_result.md` は作成しません。正式なレビュー結果ファイルはステップ 12 で作成します。

チャット例:

```text
prompts/review_feature_source.md を参照してください。

対象機能フォルダ: docs/cli_simple_calculator/features/calculator/
コマンド/アプリ名: cli_simple_calculator
対象機能名: calculator
実装ファイル: src/cli_simple_calculator/features/calculator.py
テストファイル: tests/cli_simple_calculator/features/test_calculator.py
補足条件: ソースレビューだけ行い、実装ファイル、テストファイル、docs、tasks.md は変更しないでください。
```

作成または更新されるファイル:

```text
なし
```

このステップでは、チャットでレビュー結果を報告するだけです。

---

## 8. entrypoint.py と entrypoint テストを作成する

`prompts/implement_entrypoint.md` を参照して、CLI入口と entrypoint のテストを作成します。

チャット例:

```text
prompts/implement_entrypoint.md を参照してください。

コマンド/アプリ名: cli_simple_calculator
対象 overview: docs/cli_simple_calculator/10_overview.md
対象 entrypoint: src/cli_simple_calculator/entrypoint.py
作成または更新するテストファイル: tests/cli_simple_calculator/test_entrypoint_calculator.py
対象 feature: calculator
short_name: calculator
補足条件: entrypoint.py は薄くし、features/calculator.py の機能を呼び出すだけにしてください。
```

作成または更新されるファイル:

```text
src/cli_simple_calculator/entrypoint.py
tests/cli_simple_calculator/test_entrypoint_calculator.py
```

tasks.md の更新が必要な場合は、作業報告に「tasks.md 更新候補」として提示されます。人間が確認して必要であれば別作業として反映します。

---

## 9. 結合試験計画を作成する

`prompts/create_integration_test_plan.md` を参照して、command/app 単位の結合試験計画を作成します。

feature 単体の詳細ロジックは feature 単体テストに任せ、結合試験計画では entrypoint と feature の接続、入出力、終了コード、エラー時の扱いを整理します。

チャット例:

```text
prompts/create_integration_test_plan.md を参照してください。

コマンド/アプリ名: cli_simple_calculator
対象 overview: docs/cli_simple_calculator/10_overview.md
作成または更新する結合試験計画: docs/cli_simple_calculator/11_integration_test_plan.md
対象 entrypoint: src/cli_simple_calculator/entrypoint.py
対象 feature: calculator
補足条件:
- entrypoint.py から calculator feature を呼び出し、command/app として期待どおり動くことを確認する計画にしてください。
- feature 単体の詳細ロジックは feature 単体テストに任せてください。
- まだテストコードは作成しないでください。
```

作成または更新されるファイル:

```text
docs/cli_simple_calculator/11_integration_test_plan.md
docs/cli_simple_calculator/tasks.md
docs/cli_simple_calculator/features/calculator/tasks.md
```

---

## 10. 結合試験を実装する

`prompts/implement_integration_test.md` を参照して、結合試験を実装します。

結合試験は `11_integration_test_plan.md` に従い、subprocess による `entrypoint.py` の実行確認を中心にします。

チャット例:

```text
prompts/implement_integration_test.md を参照してください。

コマンド/アプリ名: cli_simple_calculator
対象 overview: docs/cli_simple_calculator/10_overview.md
対象 結合試験計画: docs/cli_simple_calculator/11_integration_test_plan.md
対象 entrypoint: src/cli_simple_calculator/entrypoint.py
作成または更新するテストファイル: tests/cli_simple_calculator/test_integration_calculator.py
対象 feature: calculator
short_name: calculator
補足条件:
- 結合試験は 11_integration_test_plan.md に従い、subprocess による entrypoint.py の実行確認を中心にしてください。
```

作成または更新されるファイル:

```text
tests/cli_simple_calculator/test_integration_calculator.py
```

tasks.md の更新が必要な場合は、作業報告に「tasks.md 更新候補」として提示されます。人間が確認して必要であれば別作業として反映します。

---

## 11. テストを実行する

実装後、feature 単体テスト、entrypoint テスト、結合試験をまとめて実行します。

```bash
python -m pytest
```

環境によって `python` が使えない場合は、利用しているPythonの実行コマンドに読み替えてください。

---

## 12. feature 単体レビューを行う

`prompts/review_feature.md` を参照して、feature 単体レビューを行います。

レビュー結果は `24_review_checklist.md` ではなく、`25_review_result.md` に記録します。
既存の `25_review_result.md` がある場合でも、古い判定をそのまま採用せず、現在のファイル群を読み直して上書き再作成します。

`entrypoint.py` や結合試験は、feature との責務分担に関係する範囲でだけ確認します。command/app 全体の最終確認は次の `review_command.md` で扱います。

チャット例:

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

作成または更新されるファイル:

```text
docs/cli_simple_calculator/features/calculator/25_review_result.md
docs/cli_simple_calculator/features/calculator/tasks.md
```

---

## 13. command/app 全体レビューを行う

`prompts/review_command.md` を参照して、command/app 全体レビューを行います。

レビュー結果は `docs/cli_simple_calculator/12_command_review_result.md` に記録します。
既存の `12_command_review_result.md` がある場合でも、古い判定をそのまま採用せず、現在の overview、entrypoint、結合試験計画、結合試験、feature 単体レビュー結果を読み直して上書き再作成します。

チャット例:

```text
prompts/review_command.md を参照してください。

コマンド/アプリ名: cli_simple_calculator
対象 overview: docs/cli_simple_calculator/10_overview.md
対象 entrypoint: src/cli_simple_calculator/entrypoint.py
entrypoint テスト: tests/cli_simple_calculator/test_entrypoint_calculator.py
結合試験計画: docs/cli_simple_calculator/11_integration_test_plan.md
結合試験ファイル: tests/cli_simple_calculator/test_integration_calculator.py
command/app 全体レビュー結果ファイル: docs/cli_simple_calculator/12_command_review_result.md
short_name: calculator
補足条件: レビューだけ行い、レビュー結果ファイル以外は変更しないでください。
```

作成または更新されるファイル:

```text
docs/cli_simple_calculator/12_command_review_result.md
docs/cli_simple_calculator/tasks.md
```

### レビュー判定が OK 以外だった場合

`12_command_review_result.md` の判定が `OK` 以外だった場合は、すぐにAIへ修正を依頼しないでください。

1. `12_command_review_result.md` を人間が確認する
2. 反映する指摘と保留する指摘を人間が判断する
3. 反映する場合は、別のチャットでAIに修正を依頼する
4. 修正後に `python -m pytest` を実行する
5. 必要に応じて `prompts/review_command.md` で再レビューする

`feature 単体レビュー（25_review_result.md）` の判定が OK 以外だった場合も、同じ流れで対応します。
`prompts/review_feature.md` で再レビューするか、`prompts/review_command.md` に委ねるかは、指摘の内容に応じて判断してください。

---

## 進めるときの注意

- `prompts/*.md` は直接編集しません
- チャットでは、参照するプロンプトのパス、対象情報、今回だけの補足条件を渡します
- 共通ルールは標準 `prompts/*.md` 側に寄せているため、毎回長く書き直す必要はありません
- `tasks.md` 更新は、各 `prompts/*.md` の作業後ルールに従います
- 人間判断が必要な仕様は、補足条件として明示します
- 仕様にない便利機能は追加しません
- `entrypoint.py` は薄く保ちます
- feature 実装と entrypoint 実装は別のプロンプトで扱います
- feature ソースレビュー（ステップ 7）では修正しません。修正候補がある場合は人間が判断してから別作業でAIに依頼します
- feature 単体レビューと command/app 全体レビューは別のプロンプトで扱います
- 共通化候補があっても、勝手に `src/common/` へ切り出しません
- 結合試験は計画があり必要な場合だけ扱います
- 外部API、CI/CD、デプロイ資産は追加しません
