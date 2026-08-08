# バグを調査してください

このプロンプトは、`10_bug_report.md` と関連ファイルを読み、`docs/<command_or_app_name>/bugs/<bug_id>/20_bug_investigation.md` を作成または更新するためのものです。

このプロンプトファイルは直接書き換えず、チャットでこのファイルのパスと下の「利用者が指定する項目」を指定して使います。
それ以外の作業ルールは変更せず、このプロンプトの `## 必須参照ルール` に列挙されたルール文書に従ってください。成果物を作成する場合は、`docs/templates/` の該当テンプレートに従ってください。

---

## 必須参照ルール

この節は、この task で必ず読むルール文書**一覧**の正本です。各ルールの**内容**は、ここに列挙したルール文書を正本とします。このプロンプトが core や project を再定義するものではありません。

`## 参照するファイル` は今回の作業対象資料であり、このルール文書一覧とは役割が異なります。

### 作業開始時に読む

- `docs/rules/core/10_workflow.md`（調査と修正を分ける。分類が未確定なまま着手しない）
- `docs/rules/core/40_official_docs_and_context.md`（補助コンテキストは確定仕様ではない。横断探索を主責務にしない）
- `docs/rules/project/15_document_templates.md`
- `docs/rules/project/30_development_rules.md`

### 作業完了時に読む

- `docs/rules/core/50_records_and_reporting.md`

---

## 利用者が指定する項目

- 対象 command/app: `<command_or_app_name>`
- 対象 feature: `<feature_name>`
- バグID: `<bug_id>`
- バグ報告書: `docs/<command_or_app_name>/bugs/<bug_id>/10_bug_report.md`
- バグ調査書の出力先: `docs/<command_or_app_name>/bugs/<bug_id>/20_bug_investigation.md`
- 対象機能フォルダ: `docs/<command_or_app_name>/features/<feature_name>/`
- 実装ファイル: `src/<command_or_app_name>/features/<feature_name>.py`
- テストファイル: `tests/<command_or_app_name>/features/test_<feature_name>.py`
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

必ず現在の以下を読んでください。

- `docs/templates/20_bug_investigation_template.md`
- `docs/<command_or_app_name>/bugs/<bug_id>/10_bug_report.md`
- `docs/<command_or_app_name>/features/<feature_name>/20_spec.md`
- `docs/<command_or_app_name>/features/<feature_name>/21_design.md`
- `docs/<command_or_app_name>/features/<feature_name>/22_flow.md`
- `docs/<command_or_app_name>/features/<feature_name>/23_test_plan.md`
- `src/<command_or_app_name>/features/<feature_name>.py`
- `tests/<command_or_app_name>/features/test_<feature_name>.py`

必要に応じて以下も参照してください。

- `docs/<command_or_app_name>/10_overview.md`
- `src/<command_or_app_name>/entrypoint.py`
- `tests/<command_or_app_name>/test_entrypoint_<short_name>.py`
- `docs/<command_or_app_name>/11_integration_test_plan.md`
- `tests/<command_or_app_name>/test_integration_<short_name>.py`
- `docs/context/`（補助資料。確定仕様ではない。確認トリガーとしてのみ参照する）

## 変更してよいファイル

- `docs/<command_or_app_name>/bugs/<bug_id>/20_bug_investigation.md`（新規作成または更新）

## 変更してはいけないファイル

- このプロンプトファイル
- `AGENTS.md`
- `README.md`
- `docs/templates/`
- `prompts/`
- `src/`（実装コードは一切変更しない）
- `tests/`（テストコードは一切変更しない）
- `docs/<command_or_app_name>/features/` 配下の既存ドキュメント（仕様・設計・テスト計画は変更しない）
- `docs/<command_or_app_name>/bugs/<bug_id>/10_bug_report.md`
- `docs/<command_or_app_name>/bugs/<bug_id>/30_bug_fix_plan.md`
- `docs/context/`（補助資料として参照するだけにとどめ、変更しない）

---

## 作業範囲

1. `10_bug_report.md` を確認してください
2. 関連する仕様、設計、フロー、テスト計画を確認してください
3. 実装ファイルとテストファイルを確認してください
4. 原因仮説を整理してください（仕様バグ、実装バグ、テストバグ、ドキュメント不整合を分けて考えてください）
5. 影響範囲を整理してください
6. `20_bug_investigation.md` を作成または更新してください
7. 仕様・設計・テスト計画の変更が必要そうな場合は、勝手に変更せず「仕様変更が必要か」「設計変更が必要か」「テスト計画変更が必要か」のセクションに記録してください

## 調査の視点

以下の4分類で原因を分けて考えてください。

- **仕様バグ**: 仕様自体に誤りや不整合がある
- **実装バグ**: 仕様は正しいが、実装が仕様に従っていない
- **テストバグ**: 仕様と実装は正しいが、テストが誤っている
- **ドキュメント不整合**: 仕様・設計・実装の間に記述の矛盾がある

仕様通りに動いているが期待と違う場合は、バグではなく仕様変更候補として扱ってください。

## docs/context/ を使った確認

`docs/context/` が存在する場合は、補助資料として軽く確認してください。
基準は常に正式資料（仕様・設計・テスト計画）であり、`docs/context/` は確定仕様ではありません。`docs/context/` の横断探索を調査の主責務にしないでください。context 量が増えてもバグ調査を完遂できるようにするためです。

- バグ報告が、`docs/context/` にある未決事項・却下案・保留事項・未反映の会議メモに基づいていないかを、軽い確認トリガーとして確認する
- 基づいている疑いがある場合は、実装バグと断定せず、仕様変更候補または人間確認事項として `20_bug_investigation.md` に記録する
- `docs/context/` の内容を、そのまま確定仕様として原因や正解の根拠に使わない
- AIが確定可否を判断できない場合は、人間確認事項として記録する
- `docs/context/` の横断的な深掘りが必要な場合は、この調査では行わず、`prompts/review_context.md` に委譲する

## 禁止事項

- この段階で実装コード（`src/`）を変更しないでください
- この段階でテストコード（`tests/`）を変更しないでください
- この段階で仕様・設計・テスト計画（`docs/<command_or_app_name>/features/`）を変更しないでください
- `30_bug_fix_plan.md` を先取りして作成しないでください
- 原因仮説の段階で「修正済み」として扱わないでください
- 調査結果の範囲を超えて、修正内容まで書かないでください

## レビュー補助メモ

作業後の報告に、レビュー補助メモを含めてください。
記載項目とルールは `docs/rules/core/50_records_and_reporting.md` の「レビュー補助メモ」に従います（このプロンプトには定義を複製しません）。

レビュー補助メモは作業完了報告（チャット）に出力します。`tasks.md` には書きません。

## 作業後の tasks.md 更新候補

このプロンプトでは `tasks.md` を直接更新しません。

`tasks.md` の更新が必要と判断した場合は、作業報告に「tasks.md 更新候補」として記載してください。
`tasks.md` の実際の更新は、人間が確認したうえで別作業として行います。

## 作業後の報告

作業後に、以下を簡潔に報告してください。

- 作成または更新したファイル
- 参照したファイル
- 原因仮説の要約（仮説の種別を含む）
- 仕様・設計・テスト計画への影響の有無
- 追加で確認が必要なことの有無
- 調査段階の判定（調査完了 / 追加調査が必要 / 仕様確認待ち）
- 次にやること（`prompts/create_bug_fix_plan.md` を使った修正計画の作成）
