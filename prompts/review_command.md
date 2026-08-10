# command/app 全体レビューを行ってください

このプロンプトは、command/app 全体のレビューを行い、結果を `docs/<command_or_app_name>/12_command_review_result.md` に記録するためのものです。

feature 単体レビューは `prompts/review_feature.md` の範囲です。このプロンプトでは、overview、entrypoint、結合試験、全体テスト、feature 単体レビュー結果を踏まえて、command/app としての整合を確認します。

---

## 必須参照ルール

この節は、この task で必ず読むルール文書**一覧**の正本です。各ルールの**内容**は、ここに列挙したルール文書を正本とします。このプロンプトが core や project を再定義するものではありません。

`## 参照するファイル` は今回の作業対象資料であり、このルール文書一覧とは役割が異なります。

### 作業開始時に読む

- `docs/rules/core/10_workflow.md`（**未記載と矛盾を区別する**）
- `docs/rules/core/20_approval_and_review.md`（レビューと修正の分離、次工程移行判定 `GO` / `条件付きGO` / `STOP` の定義）
- `docs/rules/core/40_official_docs_and_context.md`（正式資料と補助コンテキストの扱い、**正式資料が意味を定義していない実装詳細**）
- `docs/rules/project/25_review_policy.md`（レビュー結果の評価値）
- `docs/rules/project/30_development_rules.md`（entrypoint を薄く保つ規約、`src/common/` の扱いの判定基準）
- `docs/rules/project/40_testing_rules.md`

### 作業完了時に読む

- `docs/rules/core/50_records_and_reporting.md`

---

## 利用者が指定する項目

- コマンド/アプリ名: `<command_or_app_name>`
- 対象 overview: `docs/<command_or_app_name>/10_overview.md`
- 対象 entrypoint: `src/<command_or_app_name>/entrypoint.py`
- entrypoint テスト: `tests/<command_or_app_name>/test_entrypoint_<short_name>.py`
- 結合試験計画: `docs/<command_or_app_name>/11_integration_test_plan.md`
- 結合試験ファイル: `tests/<command_or_app_name>/test_integration_<short_name>.py`
- command/app 全体レビュー結果ファイル: `docs/<command_or_app_name>/12_command_review_result.md`
- short_name: `単一 feature の command/app では feature 名。複数 feature を束ねる command/app では command/app を短く表す名前`
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

必ず現在の以下を読み直してください。

- `docs/<command_or_app_name>/10_overview.md`
- `docs/<command_or_app_name>/11_integration_test_plan.md`
- `src/<command_or_app_name>/entrypoint.py`
- `tests/<command_or_app_name>/test_entrypoint_<short_name>.py`
- `tests/<command_or_app_name>/test_integration_<short_name>.py`
- `docs/<command_or_app_name>/features/*/25_review_result.md`

必要に応じて、以下も参照してください。

- `docs/<command_or_app_name>/features/*/20_spec.md`
- `docs/<command_or_app_name>/features/*/21_design.md`
- `docs/<command_or_app_name>/features/*/22_flow.md`
- `docs/<command_or_app_name>/features/*/23_test_plan.md`
- `docs/<command_or_app_name>/features/*/24_review_checklist.md`
- `src/<command_or_app_name>/features/*.py`
- `tests/<command_or_app_name>/features/test_*.py`

`docs/context/` が存在する場合は、補助資料として軽く参照して構いません。
ただし、このプロンプトの主責務は、正式資料（`10_overview.md`、`11_integration_test_plan.md`、feature 側の仕様・設計など）・実装・テストの整合確認です。`docs/context/` の横断探索を主責務にしないでください。context 量が増えても command/app 全体レビューを完遂できるようにするためです。
`docs/context/` は確定仕様ではありません。レビュー中に偶然気づいたズレ・矛盾・反映漏れ・未決事項・却下案の混入があれば、軽い確認トリガーとして `12_command_review_result.md` に人間確認事項として記録する程度にとどめてください。そのまま確定仕様として採用しないでください。
`docs/context/` の横断的な深掘りが必要な場合は、このプロンプトでは行わず、`prompts/review_context.md` に委譲してください。
正式資料と矛盾する場合や、AIが判断できない場合は、勝手に解決せず人間確認事項として `12_command_review_result.md` に記録してください。

## 作成または更新するファイル

- `docs/<command_or_app_name>/12_command_review_result.md`

## 変更してよいファイル

- `docs/<command_or_app_name>/12_command_review_result.md`
- `docs/<command_or_app_name>/tasks.md`
- `docs/<command_or_app_name>/features/<feature_name>/tasks.md`
  - 対象 feature が明確な場合のみ、現在地と次に確認することを短く更新する場合に限る

## 変更してはいけないファイル

この節は、**今回の task で変更を許可されていないファイル**です。project が定める**保護対象**（`docs/rules/project/50_ai_permissions.md`）とは別のレイヤであり、両方を満たす必要があります。

レビュー結果ファイル以外を変更しないでください。
ただし、変更してよいファイルに記載した `tasks.md` の必要最小限の更新は例外です。

- `src/`
- `tests/`
- `docs/<command_or_app_name>/10_overview.md`
- `docs/<command_or_app_name>/11_integration_test_plan.md`
- `docs/<command_or_app_name>/features/`
- `prompts/`
- `AGENTS.md`
- `README.md`
- `docs/templates/`
- `docs/context/`（補助資料として参照するだけにとどめ、変更しない）

レビュー中に問題を見つけても、勝手に修正しないでください。修正候補として `12_command_review_result.md` に記録してください。

---

## 再レビュー時のルール

既存の `12_command_review_result.md` が存在する場合でも、古い判定をそのまま採用しないでください。

必ず現在の overview、entrypoint、entrypoint テスト、結合試験計画、結合試験、feature 単体レビュー結果を読み直してください。

既存の `12_command_review_result.md` は参考情報として扱っても構いませんが、最終判定は現在のファイル群に基づいて判断し、新しいレビュー結果として上書き更新してください。

## 作業手順

1. `docs/<command_or_app_name>/10_overview.md` を確認してください
2. feature 分割と feature 単体レビュー結果を確認してください
3. `src/<command_or_app_name>/entrypoint.py` を確認してください
4. `tests/<command_or_app_name>/test_entrypoint_<short_name>.py` を確認してください
5. `docs/<command_or_app_name>/11_integration_test_plan.md` を確認してください
6. `tests/<command_or_app_name>/test_integration_<short_name>.py` を確認してください
7. 必要に応じて feature の 20_spec.md から 24_review_checklist.md まで、実装、単体テストを確認してください
8. `python -m pytest` または利用者が指定したテストコマンドを実行し、全体テスト結果を確認してください
9. レビュー結果を `docs/<command_or_app_name>/12_command_review_result.md` に作成または上書き更新してください

## 共通設計書との整合確認

`docs/<command_or_app_name>/common_design/` が存在する場合は、以下を確認してください。

- 各 feature の実装が、DB設計書（`33_db_design.md`）と整合しているか
- 各 feature の実装が、ファイル設計書（`31_file_design.md`）と整合しているか
- 各 feature の実装が、共通データ設計書（`32_data_design.md`）と整合しているか
- feature 個別設計に、共通設計書に未定義のDBテーブル・ファイル形式・共通データ項目が定義されていないか

整合しない箇所がある場合は、実装を勝手に修正せず、`12_command_review_result.md` に指摘として記録してください。

## 未記載と矛盾を区別する

レビューの前に、次の区別を必ず押さえてください。

| | 内容 | 扱い |
|---|---|---|
| **未記載** | 正式資料がその実装詳細を規定していない。実装側に具体的な処理が存在するが、正式資料が定義する意味には反していない | **それだけでは指摘しません** |
| **矛盾** | 正式資料が定義している意味と、実装の意味が食い違っている | **指摘します** |

**「設計書に書いてない」ことは、「設計書と矛盾している」ことではありません。**

生成されたコードには、同じ仕様・設計でも実装上の揺らぎ（関数の切り方、局所的な書き方、変数名、冗長さ、同じ意味を持つ複数の実装方法など）があります。**揺らぎが存在すること自体を指摘にしないでください。** 複数 feature 間で実装方式が異なること自体も、それだけでは指摘になりません。

指摘する場合は、**どの正式資料の、どの記述が定義している意味と食い違うか**を `12_command_review_result.md` に示してください。

ただし、次は「未記載だから問題なし」としてはいけません。正式資料が意味を定義している領域だからです。

- 仕様にない便利機能の追加
- 外部から見える動作の変更
- `10_overview.md` が定めた責務・Boundary・feature 分割としての意味の変更
- entrypoint と features の責務分担の逸脱
- 共通設計で定義された内容との食い違い

原則の正本は `docs/rules/core/10_workflow.md` の「未記載と矛盾を区別する」です。このプロンプトでは再定義しません。

逆に、実装の中へ**今後も守るべき仕様・設計・共通方針**として維持すべき内容が含まれていると気づいた場合は、指摘事項ではなく、`12_command_review_result.md` の「仕様変更が必要そうな点」へ**逆反映候補である旨を明記**して記録してください。新しい見出しは追加しません。**今後も守るべき意味だと判断した理由を必ず示してください。** 採否は人間が判断し、このプロンプトでは正式資料を更新しません。**逆反映候補があることだけを理由に、最終判定を `要仕様確認` にしないでください。**

## 主に確認すること

- `10_overview.md` が定義する目的・Boundary・責務・feature 分割と、実装全体が食い違っていないこと
- feature 分割が妥当であること
- `entrypoint.py` が薄く保たれていること
- feature 固有ロジックが `entrypoint.py` に入っていないこと
- `src/common/` に勝手に共通化していないこと
- `11_integration_test_plan.md` と `test_integration_<short_name>.py` が整合していること
- `test_entrypoint_<short_name>.py` と `test_integration_<short_name>.py` の役割が重複しすぎていないこと
- `python -m pytest` の結果が確認されていること
- feature 単体レビュー結果に未解決の重大指摘がないこと
- 指定外ファイル名への変更や AI 判断によるアドリブがないこと
- 指定された出力先を AI 判断で変更していないこと
- entrypoint テストと結合試験が標準命名ルールに従っていること
- `pytest` の import mismatch やテストファイル名衝突がある場合、標準命名ルールと現状の差分を確認せずに別名ファイルを作成していないこと
- fallback import などが必要な場合、その理由と影響が説明できること
- 古いレビュー結果の判定をそのまま再利用していないこと

## レビュー結果に記録する内容

`12_command_review_result.md` には、`docs/templates/12_command_review_result_template.md` の見出し構成に沿って以下を記録してください。

- レビュー対象
- 参照したファイル
- 実行した確認内容
- テスト実行結果
- 10_overview.md との整合
- feature 分割の妥当性
- entrypoint の責務確認
- feature 実装との責務分担
- 結合試験計画との整合
- 結合試験実装との整合
- feature 単体レビュー結果の確認
- 指定外変更・AIアドリブの有無
- 指摘事項
- 改善候補
- 仕様変更が必要そうな点
- 最終判定
- 次工程移行判定（GO / 条件付きGO / STOP）
- 作業後報告

## 最終判定

レビュー結果の最後に、以下のいずれかを記録してください。

ここに記載する値は出力形式上の列挙であり、**定義の正本は `docs/rules/project/25_review_policy.md` です。**

- `OK`: 大きな問題なし
- `軽微な指摘あり`: 軽微な修正または確認事項がある
- `要修正`: 実装、テスト、ドキュメントの修正が必要
- `要仕様確認`: 仕様に戻って確認が必要

`軽微な指摘あり` は成果物の状態を表すものであり、これを理由に次工程移行判定を `GO` にしてはいけません。

### 次工程移行判定

上記の判定に加えて、次工程へ進めるかどうかを以下のいずれかで記録してください。

**判定値そのものの定義と、STOP / 条件付きGO の使い分けの正本は `docs/rules/core/20_approval_and_review.md` です。**

- `GO`：次工程へ進んでよい
- `条件付きGO`：未解決項目・後続工程への影響・見直し条件を明記したうえで進んでよい
- `STOP`：次工程へ進んではならない。何を解決すれば進めるかを明記して停止する

人間判断待ち、承認の前提となる未決事項、安全に次工程へ進めない未決事項、または整理されていない未解決事項が残っている場合は `STOP` です。
「要検討として記録した」ことは、「解決した」ことではありません。

条件付きGOとする場合は、以下の6項目を必ず明記してください。

- 未解決項目
- 仮置きする内容と理由
- 条件付きでも進める理由
- 後続工程への影響
- 見直しが必要になる条件
- 人間判断が必要かどうか

STOPとする場合は、次工程の成果物を作成せず、停止して報告してください。

## 禁止事項

- `12_command_review_result.md` 以外を変更しないでください。ただし、対象 `tasks.md` の現在地メモ更新は例外です
- `src/` を変更しないでください
- `tests/` を変更しないでください
- overview、結合試験計画、feature ドキュメントを変更しないでください
- `prompts/`、`AGENTS.md`、`README.md`、`docs/templates/` を変更しないでください
- 指定された出力先を AI 判断で変更しないでください
- `pytest` の import mismatch やテストファイル名衝突を理由に、標準命名ルールと現状の差分を確認せずに別名のテストファイルを作成しないでください
- fallback import を勝手に追加しないでください
- feature 単体レビュー結果を読み直さず、古い判定をそのまま採用しないでください
- レビュー結果の詳細を `tasks.md` に書かないでください
- **正式資料に未記載であることだけを理由に、指摘しないでください**
- **実装方式の揺らぎや、feature 間の実装方式の差異そのものを指摘にしないでください**
- **根拠となる正式資料の記述を示さずに、矛盾として記録しないでください**
- 逆に、**仕様にない便利機能、外部動作の変更、責務・feature 分割としての意味の変更、entrypoint と features の責務分担の逸脱を「未記載だから問題なし」として見逃さないでください**
- **逆反映候補を、AIの判断で正式資料へ反映しないでください**
- **逆反映候補があることだけを理由に、最終判定を `要仕様確認` にしないでください**

## 作業後の報告

作業後に、以下を簡潔に報告してください。

- 作成または更新したファイル
- 参照したファイル
- テスト実行コマンドと結果
- 最終判定
- feature 単体レビュー結果に未解決の重大指摘があったか
- command/app 全体として気になる点

## 作業後の tasks.md 更新

作業後は、対象 command/app または feature の `tasks.md` を必ず確認してください。

必要に応じて、現在の状態、作業メモ、次に確認すること、引き継ぎに必要な短い注意点だけを更新してください。

`tasks.md` には、仕様・設計・テスト計画・レビュー結果の詳細や長いテストログを書かないでください。
詳細は `10_overview.md`、`11_integration_test_plan.md`、`12_command_review_result.md`、feature 側の専用ファイルなど、それぞれの専用ファイルに記録してください。

`tasks.md` を更新しない場合は、更新しない理由を作業報告に書いてください。
