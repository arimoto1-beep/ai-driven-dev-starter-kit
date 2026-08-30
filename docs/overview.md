# ドキュメント構成

この文書は、**リポジトリの構造と各成果物の役割**を人間が理解するための概要です。「どこに何があり、それぞれ何を書くファイルか」を説明します。

- feature 開発が**どう流れるか**（オートモードの体験と最初の一歩） → [`../README.md`](../README.md)
- オートモードの**詳細仕様**（stage、Gate、判定値、モデル選択） → [`rules/project/70_feature_loop.md`](rules/project/70_feature_loop.md)

**AIが守るルールの正本は `docs/rules/` 配下です**（索引: [rules/README.md](rules/README.md)）。この文書はルールの正本ではありません。

このリポジトリでは、コマンド/アプリ単位で docs、src、tests を対応させます。

```text
docs/<command_or_app_name>/
src/<command_or_app_name>/
tests/<command_or_app_name>/
tests/<command_or_app_name>/test_entrypoint_<short_name>.py
tests/<command_or_app_name>/test_integration_<short_name>.py
tests/<command_or_app_name>/features/test_<feature_name>.py
```

`<short_name>` は、単一 feature の command/app では feature 名を使います。
複数 feature を束ねる command/app では、command/app を短く表す名前を使います。

個別 feature は `features/<feature_name>/` 配下で管理します。

---

## 基本構成

```text
docs/
  <command_or_app_name>/
    10_overview.md
    tasks.md
    11_integration_test_plan.md
    12_command_review_result.md
    common_design/
      30_common_design_index.md
      31_file_design.md
      32_data_design.md
      33_db_design.md
    features/
      <feature_name>/
        tasks.md
        20_spec.md
        21_design.md
        22_flow.md
        23_test_plan.md
        24_review_checklist.md
        25_review_result.md
        gates/
          <連番4桁>_<タイムスタンプ>_<stage小文字>.md
    bugs/
      <bug_id>/
        10_bug_report.md
        20_bug_investigation.md
        30_bug_fix_plan.md
```

`tasks.md` は作業状態を引き継ぐための現在地メモです。command/app 単位と feature 単位の両方に配置します。まだ作業状態を記録する必要がない場合は、無理に作成しません。
`common_design/` は、複数 feature にまたがる共通設計が必要になった場合に追加します。すべての command/app で必須ではありません。
`25_review_result.md` は、feature 単体レビューを行った場合に作成します。
`12_command_review_result.md` は、command/app 全体レビューを行った場合に作成します。
まだレビューしていない場合は、無理に作成しません。
`gates/` は、オートモード（`tools/feature_runner.py`）で feature を進めた場合に作成されます。マニュアルモードだけで進めた feature には存在しません。

---

## 各ファイルの役割

| ファイル | 役割 |
|---|---|
| `10_overview.md` | コマンド/アプリ全体の目的、入口、機能一覧、責務分担を書く |
| `tasks.md` | 作業状態を引き継ぐための現在地メモ。現在の状態・次にやること・保留事項を短く書く。仕様・設計・レビュー結果の代わりにしない |
| `11_integration_test_plan.md` | command/app 単位の結合試験計画を書く |
| `12_command_review_result.md` | command/app 全体レビュー結果を書く |
| `20_spec.md` | feature の要件・仕様を書く |
| `21_design.md` | 関数単位の責務、入力、出力、エラー方針を書く |
| `22_flow.md` | 関数同士の呼び出し順、依存関係、全体フローを書く |
| `23_test_plan.md` | feature 単体テストの観点を書く |
| `24_review_checklist.md` | feature 単体レビュー観点を書く。末尾に実装着手承認欄を含む。レビュー結果は書き込まない |
| `25_review_result.md` | feature 単体レビュー結果、指摘事項、最終判定を書く |
| `gates/` 配下 | オートモードの Gate記録。各段階の判定、人間の承認欄、停止の理由を1件1ファイルで残す。**確定した記録は書き換えず、新しい記録を追加する。** ひな形は `docs/templates/gate_record_template.md`、記録項目の正本は `docs/rules/project/70_feature_loop.md` |
| `10_bug_report.md` | バグ報告を整理する。原因断定や修正はしない |
| `20_bug_investigation.md` | 仕様・設計・実装・テストを確認し、原因仮説と影響範囲を整理する。修正はしない |
| `30_bug_fix_plan.md` | 修正対象、テスト方針、確認コマンド、人間承認欄を整理する。承認前に実装しない |
| `docs/context/` | 会議メモ・未決事項・却下案などの補助資料。確定仕様ではなく、レビュー・バグ調査・任意調査の確認トリガーとして参照する |
| `docs/context/ai_work_logs/` | 旧AI作業ログ。**旧方式として凍結しており、新規作成しません。** 既存の記録は当時の経緯を確認するために保持する |
| `docs/context/work_notes/` | 作業メモ。作業の経緯・判断・手戻り・現在地を、作業テーマ単位のフォルダとREADME.mdで残す現行の記録方式。`prompts/prepare_work_note.md` で構成し、人間確認後に保存する |

`25_review_result.md` は feature 単体の仕様、設計、実装、単体テストを確認するためのレビュー結果です。
`12_command_review_result.md` は overview、entrypoint、結合試験、全体テスト、feature 単体レビュー結果を確認するためのレビュー結果です。

---

## テンプレート

ドキュメントを作成する場合は、`docs/templates/` 配下のひな形を使います。代表例は次のとおりです。

| 作成するファイル | 参照するテンプレート |
|---|---|
| `10_overview.md` | `docs/templates/10_overview_template.md` |
| `20_spec.md` | `docs/templates/20_spec_template.md` |
| `21_design.md` | `docs/templates/21_design_template.md` |
| `23_test_plan.md` | `docs/templates/23_test_plan_template.md` |
| `25_review_result.md` | `docs/templates/25_review_result_template.md` |

**全成果物とひな形の対応表、および文書種別ごとの見出しの扱い（維持するか省略してよいか）は `docs/rules/project/15_document_templates.md` が正本です。**

---

## docs/context（補助コンテキスト）

`docs/context/` は、会議メモ・チャット補足・過去判断・未決事項・却下案・注意事項を集める補助資料の置き場です。

**位置づけ（正式資料との関係、矛盾時の扱い）の正本は `docs/rules/core/40_official_docs_and_context.md`、AIの更新権限の正本は `docs/rules/project/50_ai_permissions.md` です。**
置き場としての使い方は `docs/context/README.md` を参照してください。

`docs/context/` の横断探索は、通常レビューやバグ調査の主責務にしません。通常レビュー（`prompts/review_feature.md` / `prompts/review_command.md`）やバグ調査（`prompts/investigate_bug.md` / `prompts/create_bug_fix_plan.md`）は `docs/context/` を軽い確認トリガーとしてのみ扱い、深掘りが必要な場合は `prompts/review_context.md` に委譲します。これは、context 量が増えても通常レビューやバグ調査を完遂できるようにするためです。
`prompts/review_context.md` は候補出し専用で、正式資料・`docs/context/`・`bugs/` 配下のいずれも変更しません。採用・却下・保留は人間が判断します。

---

## 実装前承認ゲート

feature 実装（`prompts/implement_feature.md`）に進む前に満たすべき条件は、`24_review_checklist.md` の「実装開始条件」に記載された方式によって異なる。

| 方式 | 実装開始条件 |
|---|---|
| `manual`（既定。記載がない場合を含む） | `24_review_checklist.md` 末尾の「実装着手承認欄」が全項目チェック済み |
| `auto` | **CP1 の仕様承認（現在の `20_spec.md` と同一 baseline）AND 最新 G2 Gate記録の `verdict: PASS`** |

`manual` では、承認欄に未チェック項目がある場合、AIは実装を開始せず STOP する。
`auto` では、この承認欄を使用しない。**未チェックのまま残ることが正常であり、STOP の理由にはならない。**

**どちらの方式でも、AIが承認欄にチェックを入れて進んではならない。**

実装開始条件の正本 → `docs/rules/project/70_feature_loop.md`／承認境界と停止判断の正本 → `docs/rules/core/20_approval_and_review.md`／承認欄の場所 → `docs/rules/project/50_ai_permissions.md`

---

## バグ修正フロー

バグ修正は、報告 → 調査 → 修正計画 → 人間承認 → 実装の順に進める。
仕様・設計・テスト計画の更新が必要な場合は、修正実装とは別作業として扱う。

`bug_id` は `bug_001` のような形式を基本とする。同一 command/app 内で重複しない名前にする。
チュートリアルでは `bug_001` を使用してよい。

工程の全体像 → `docs/rules/project/20_workflow.md`

---

## entrypoint と features

`src/<command_or_app_name>/entrypoint.py` はCLI入口です。

- CLI引数を受け取る
- `features/` 配下の機能を呼び出す
- 結果を標準出力に出す
- 終了コードを返す

feature 固有のロジックは `src/<command_or_app_name>/features/<feature_name>.py` に置きます。
`entrypoint.py` に業務ロジック本体や複雑な変換処理を置かないでください。

entrypoint のテストは `tests/<command_or_app_name>/test_entrypoint_<short_name>.py` に置きます。
結合試験は `tests/<command_or_app_name>/test_integration_<short_name>.py` に置きます。
feature の単体テストは `tests/<command_or_app_name>/features/test_<feature_name>.py` に置きます。

実装規約の正本 → `docs/rules/project/30_development_rules.md`／テスト規約の正本 → `docs/rules/project/40_testing_rules.md`

---

## feature フォルダ名の番号プレフィックス

単純なアプリでは、feature フォルダ名は `text_counter` のように機能名だけで構いません。

処理順・呼び出し順・パイプライン順が重要な場合は、`010_`、`020_` のような番号プレフィックスを付けてもよいです。

```text
docs/<command_or_app_name>/features/
├─ 010_load_inputs/
├─ 020_normalize_data/
├─ 030_compare_items/
└─ 040_output_result/
```

番号プレフィックスは、人間とAIが処理順を共有しやすくするためのものです。以下の点に注意してください。

- Python の実装ファイル名やモジュール名まで番号付きにする必要はない
- 番号付き feature フォルダを使う場合も、フォルダ内のドキュメント番号体系（`20_spec.md` など）は変わらない
- `tasks.md` は番号なしのまま現在地メモとして扱う

---

## テスト計画と結合試験計画

`23_test_plan.md` は feature 単体テストの計画です。
feature の詳細ロジック、正常系、異常系、境界値などを確認します。

`11_integration_test_plan.md` は command/app 単位の結合試験計画です。
`entrypoint.py` から feature を呼び出したときの接続、入出力、終了コード、エラー時の扱いを確認します。

結合試験は常に必須ではありません。entrypoint から feature を束ねて確認する必要がある場合に扱います。

---

## common の扱い

`src/common/` は共通処理置き場です。

ただし、AIは人間の明示指示なしに `src/common/` を作成・更新しません。
共通化候補がある場合は、設計書、レビュー結果、または作業報告に提案として記録します。
提案をまとめる場合は、`docs/templates/30_common_proposal_template.md` を使います。

保護対象とAIの更新権限の正本 → `docs/rules/project/50_ai_permissions.md`

---

## prompts

`prompts/` 直下には、実プロジェクトでも使う汎用プロンプトだけを配置します。チュートリアル専用プロンプトは置きません。

プロンプトは、使われ方で2種類に分かれます。

| 種類 | prompt | 位置づけ |
|---|---|---|
| runner から使われる | `run_stage.md`（Worker）、`review_stage.md`（Reviewer） | オートモードで `tools/feature_runner.py` が別プロセスとして起動する入口。`run_stage.md` は成果物の作り方を自分で定義せず、**その stage に設定された作業用プロンプトへ委譲する** |
| 人間が選んで渡す | 下記の個別プロンプト（`create_*` / `implement_*` / `review_*` など） | マニュアルモードで人間が1つずつ実行する。**このうち stage に設定されたものは、Worker の委譲先にもなる** |

どの stage がどのプロンプトへ委譲するかは、`docs/rules/project/70_feature_loop.md` の設定が正本です。ここには一覧を複製しません。
選び方と渡し方は `docs/how_to_use_prompts.md` を参照してください。

汎用プロンプトは直接書き換えず、チャットで参照するプロンプトのパスと対象情報を渡して使います。
各プロンプトの冒頭には `## 必須参照ルール` があり、**その作業でAIが読むルール文書の一覧**が列挙されています。
詳しくは `docs/how_to_use_prompts.md` を参照してください。

`review_feature_source.md` は `implement_feature.md` 直後の中間チェック用プロンプトです。実装ファイルとテストファイルを仕様・設計・テスト計画と照合し、修正候補をチャットで報告します。ファイルは変更しません。`25_review_result.md` も作成しません。正式なレビュー結果は `review_feature.md` で行います。

`analyze_code_change_impact.md` は、コードに関する**変更**を扱うプロンプトです。中心の問いは「この変更は、正式資料で意味を定義・維持する必要があるか」です。**コードを変更する前でも、変更した後でも使えます。** 実施済みの変更（Git差分）も入力にでき、人間が直接行った変更でもAIが行った変更でも同じように扱います。

分析は**2つの異なる軸**で整理されます。混同しないでください。

- **変更ルート**：この変更を、正式資料でどう扱うべきか
- **実施状態**：この変更が、実際にどこまで進んでいるか

変更点ごとに、次の変更ルートと根拠を報告します。

- A. 正式資料への反映不要（実装詳細で完結する）
- B. 正式資料を正本として下流へ反映
- C. コード起点の知見を正式資料へ逆反映
- 判断不能

あわせて、実施状態（未着手／一部実施／実施済み）と、コード先行の有無を報告します。**コード先行は変更ルートではなく実施状態であり、ルートB・Cのいずれでも起こりえます。**

ルートBの場合は、変更内容を定義すべき最上流かつ役割の合う正式資料（正本）と、正本から下流への更新順を整理します。**「正本候補なし」を一律に停止の理由にはしません。** 正式資料が意味を定義していない実装詳細であればルートAとして扱い、本来正式資料へ残すべき意味なのに置き場がない場合は、新しい資料を作らず人間判断事項として報告します。ファイルは変更しません（Git参照も読み取り専用です）。採用可否と進むフローは人間が判断し、バグ候補はバグ修正フローへ接続します。

`review_design_code_consistency.md` は、**現在の状態**を見るプロンプトです。中心の問いは「現在の正式資料と現在のコードに、意味上の矛盾がないか」です。指定した scope（feature / command/app / 共通処理など）に対して実行します。scope の指定は必須で、リポジトリ全体を無制限に読むことはしません。

出力では、「意味上の矛盾」と「正式資料には未記載だが問題ではない実装詳細」を明示的に分けます。**正式資料に書かれていない実装詳細は、それだけでは指摘しません。** 正式資料へ昇格させるべき知見が見つかった場合は、逆反映候補として別枠で報告します。ファイルは変更せず、採否は人間が判断します。

**2つのプロンプトの役割を混同しないでください。** `analyze_code_change_impact.md` は変更を見ます。`review_design_code_consistency.md` は現在の状態を見ます。

`review_context.md` は `docs/context/` の横断探索専任プロンプトです。通常レビューから探索責務を分離し、正式資料への反映候補・矛盾候補・未決事項・却下案の混入候補・人間確認事項を候補として整理してチャットで報告します。正式資料・`docs/context/`・`bugs/` 配下のいずれも変更しません。採用・却下・保留は人間が判断し、採用分だけを別作業として正式資料へ反映します。

---

## 今回の対象範囲

このスターターキットでは、feature 単体の単体試験を基本にします。
必要に応じて、command/app 単位の結合試験計画と結合試験も扱います。

進め方は2つあります。**どちらも現役の選択肢です。**

| 進め方 | 内容 | 詳しく |
|---|---|---|
| **オートモード** | `tools/feature_runner.py` が各AI工程で Worker と Reviewer を分離して起動し、段階ごとに Gate で判定する。人間は仕様承認と受け入れを判断する | `rules/project/70_feature_loop.md`、`../tools/README.md` |
| **マニュアルモード** | 人間が個別プロンプトを1つずつ実行する。新規 feature でも利用できる | `rules/project/20_workflow.md`、`../prompts/README.md` |

下記は、どちらの進め方でも共通の対象範囲です。

対象にするもの:

- overview による command/app 全体の整理
- feature 分割
- feature 仕様の整理
- 関数設計
- 関数呼び出し定義
- feature 単体テスト計画
- feature 実装
- feature 単体テスト
- 必要に応じた結合試験計画
- 必要に応じた結合試験
- feature ソースレビュー（実装直後の中間チェック）
- feature 単体レビュー
- command/app 全体レビュー

対象外:

- 外部システム連携
- CI/CD
- デプロイ
- 本番運用設定
