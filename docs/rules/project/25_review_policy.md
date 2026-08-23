# project: レビュー方針

## このファイルの目的

このプロジェクトで使う**レビュー結果の評価値**と、その記録・集計の運用を定めます。

## このファイルを読む作業

- feature 単体レビュー
- command/app 全体レビュー
- レビュー結果を記録するとき
- 品質サマリを集計するとき

## このファイルに含めないもの

- `GO` / `条件付きGO` / `STOP` の定義と使い分け → `docs/rules/core/20_approval_and_review.md`
- 条件付きGO の6項目 → 同上
- 未決事項の分類と STOP の条件 → 同上
- 実装着手承認、AIが承認欄を自らチェックしないという原則 → 同上
- 承認欄の場所 → `50_ai_permissions.md`
- レビューをどの工程で行うか → `20_workflow.md`
- 各レビューの確認観点と出力手順 → 対応する `prompts/review_*.md`

---

## 現行スターターキットの初期値

### レビュー結果の評価値

レビュー結果には、次の4値のいずれかを使います。

| 値 | 意味 |
|---|---|
| `OK` | 大きな問題なし |
| `軽微な指摘あり` | 軽微な修正または確認事項がある |
| `要修正` | 実装、テスト、ドキュメントの修正が必要 |
| `要仕様確認` | 仕様に戻って確認が必要 |

この4値は**成果物の状態**を表します。次工程へ進んでよいかは表しません。
2種類の判定の関係は `docs/rules/core/20_approval_and_review.md` を参照してください。

### 「軽微な指摘あり」の扱い

`軽微な指摘あり` は、**プロジェクトが定義した、成果物全体のレビュー結果**です。

- 重大な問題はない
- 修正または確認すべき軽微な指摘がある
- 成果物の品質状態を表す
- **次工程へ進めるかは、この値だけでは決まらない**

**このラベルを付けたことだけを理由に、次のことをしてはなりません。**

- 未解決事項を解決済みとして扱う
- 人間判断を省略する
- 条件付きGO の根拠にする
- 次工程移行判定を自動的に `GO` にする

次工程移行判定は、`docs/rules/core/20_approval_and_review.md` に従って別に行います。

なお、**個別の未決事項をAIが単独で「軽微」と確定することは禁止されています**（同上）。成果物全体の評価に `軽微な指摘あり` を付けることと、個別の未決事項を軽微と断定することは別のことです。

### レビュー結果を記録する成果物

| レビュー | 記録先 | 対応するプロンプト | 対応するテンプレート |
|---|---|---|---|
| feature 単体レビュー | `<対象機能フォルダ>/25_review_result.md` | `prompts/review_feature.md` | `docs/templates/25_review_result_template.md` |
| command/app 全体レビュー | `docs/<command_or_app_name>/12_command_review_result.md` | `prompts/review_command.md` | `docs/templates/12_command_review_result_template.md` |

次のプロンプトは、チャット報告のみでファイルを作りません。したがってこの4値は使いません。

- ソースレビュー（`prompts/review_feature_source.md`）
- 補助コンテキストの横断確認（`prompts/review_context.md`）
- 正式資料とコードの意味上の整合確認（`prompts/review_design_code_consistency.md`）
- 変更の意味と変更ルート・実施状態の整理（`prompts/analyze_code_change_impact.md`）

このうち `prompts/review_design_code_consistency.md` と `prompts/analyze_code_change_impact.md` は、総合判定として次工程移行判定（`GO` / `条件付きGO` / `STOP`）を出力します。判定値の定義は `docs/rules/core/20_approval_and_review.md` を正本とします。他の2本の出力区分は、それぞれのプロンプトを参照してください。

### オートモードの Gate判定との関係

オートモード（`70_feature_loop.md`）では、Gate記録に `verdict`（`PASS` / `RETURN` / `BLOCKED` / `IN_PROGRESS`）を記録します。
**`verdict` の定義の正本は `70_feature_loop.md` です。** この4値は、上記のレビュー結果4値とも、`GO` / `条件付きGO` / `STOP` とも別の軸です。

- `verdict` は、次工程移行判定を置き換えません。Gate記録には両方を記録します
- CP3 の Reviewer は、Gate記録に加えて `25_review_result.md` を作成・更新します。**レビュー結果4値と次工程移行判定は、従来どおり `25_review_result.md` に記録します**
- したがって `tools/quality_report.py` の集計は、オートモードでも変わりません

### 両方の判定を記録する

レビュー結果を記録する成果物には、**レビュー結果と次工程移行判定の両方**を記録します。

- 「最終判定」…… レビュー結果の4値
- 「次工程移行判定」…… `GO` / `条件付きGO` / `STOP`

成果物の状態が `OK` でも、人間判断待ちが残っていれば次工程移行判定は `STOP` になり得ます。片方だけを記録しないでください。

### 集計ツールへの依存

`tools/quality_report.py` は、`docs/` 配下の `25_review_result.md` と `12_command_review_result.md` を走査し、「最終判定」「次工程移行判定」の各見出し配下から**単独行の値**を読み取って `quality/report.md` に集計します。

- レビュー結果4値は `tools/quality_report.py` の `FINAL_REVIEW_RESULTS` に定義されています。
- 次工程移行判定3値は同ファイルの `NEXT_STEP_RESULTS` に定義されています。
- 集計できるようにするため、判定値は**判定候補のいずれかを単独行で**記載してください。

### ラベルを変更する場合

**レビュー結果ラベルは、キット本体との同期変更が必要な設定です。このファイルを書き換えるだけでは完了しません。**

変更する場合、**次をすべて同時に変更する必要があります。**

1. このファイル（正本）
2. `prompts/review_feature.md` の「最終判定」
3. `prompts/review_command.md` の「最終判定」
4. `docs/templates/25_review_result_template.md` の判定候補
5. `docs/templates/12_command_review_result_template.md` の判定候補
6. `tools/quality_report.py` の `FINAL_REVIEW_RESULTS`

いずれかが漏れると、集計が欠落するか、レビュー結果が記録できなくなります。

**AIが勝手に 2〜6 を変更しません。** 変更対象と影響範囲を整理し、人間の承認後に別作業として実施してください。
実施後は `prompts/review_prompt_integrity.md` で整合を確認してください。

---

## 変更する場合の注意

- レビュー結果の評価値はプロジェクトが定めます。値を増減してかまいません。ただし上記のとおり、**このファイルの変更だけでは完了しません。**
- ただし、**`GO` / `条件付きGO` / `STOP` は共通で固定されており、プロジェクトで変更できません**（`docs/rules/core/20_approval_and_review.md`）。
- レビュー結果の値を、次工程移行判定の代わりに使わないでください。成果物の状態と、次へ進めるかの判断は別のことです。

---

## 関連するルール

- 2種類の判定の区別、次工程移行判定の定義 → `docs/rules/core/20_approval_and_review.md`
- レビューと修正の分離、承認された指摘だけを修正すること → 同上
- レビューを行う工程 → `20_workflow.md`
- レビュー結果の保存先 → `10_document_structure.md`
- レビュー結果テンプレートの見出し運用 → `15_document_templates.md`
- オートモードの Gate判定値（`verdict`） → `70_feature_loop.md`
