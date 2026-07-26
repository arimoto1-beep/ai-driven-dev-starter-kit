# AI作業ログ

## 基本情報

- 日付: 2026-07-26
- 対象タスク: T-031（コード変更案の影響範囲を整理する汎用プロンプトの追加）
- 対象 command/app: 該当なし（特定の command/app に紐づかない、スターターキット本体の追加のため）
- 対象 feature: 該当なし
- 依頼者: 人間（ユーザー）
- 作業者AI: Claude Code
- 参照プロンプト: 該当なし（`prompts/*.md` を参照した作業ではなく、チャットでの直接依頼に基づくキット本体のメンテナンス作業）

## 依頼内容

コードレベルで思いついた変更案から、仕様・設計・テスト・類似機能への影響を整理する汎用プロンプトを追加する依頼。

- `prompts/analyze_code_change_impact.md` を新規追加する
- このプロンプトはコード変更案を実装するためのものではなく、正式な変更作業へ進む前に影響範囲を整理するためのもの
- 分析ではいかなるファイルも変更せず、結果はチャットで報告する
- コード変更案を、バグ候補・仕様変更・軽微な機能追加・内部設計変更・リファクタリング・類似機能間の整合性改善・標準化・共通化候補・ドキュメント不整合・好み／局所改善・判断材料不足に分類する
- 類似機能との比較、共通化の扱い、影響範囲、リスク、人間判断事項、推奨する次の作業を出力する
- 総合判定は既存の `GO` / `条件付きGO` / `STOP` に合わせる
- プロンプト追加だけで終わらせず、`AGENTS.md`、`README.md`、`docs/overview.md`、`docs/how_to_use_prompts.md`、`docs/tutorials/030_update_existing_feature.md`、`prompts/review_prompt_integrity.md` の既存導線へ組み込む
- バグ修正は従来どおり `docs/tutorials/040_bug_fix_flow.md` へ接続する
- 新しいテンプレート・新しいチュートリアルは追加しない
- 本AI作業ログを作成する（人間からの明示指示あり）
- コミット、push、ブランチ作成は行わない

### 追加依頼（T-031 のコミット前修正）

上記作業の完了報告で、今回の変更とは別に既存ドキュメントの一覧漏れ（`ai_work_logs/` と `ai_work_log_template.md` の記載漏れ）を報告したところ、T-031 のコミット前修正として対応する追加依頼を受けた。

- 新しい機能追加や方針変更は行わず、実際のディレクトリ構成・テンプレート構成・AI作業ログの運用説明が一致するように必要最小限で修正する
- `README.md` のリポジトリ構成ツリーへ `docs/context/ai_work_logs/`、`docs/context/ai_work_logs/README.md`、`docs/templates/ai_work_log_template.md` を反映する（個別ログは列挙せず、一般表記を使う）
- `README.md` のテンプレート一覧へ `ai_work_log_template.md` を追加する
- `AGENTS.md` の「ドキュメントひな形」表へ AI作業ログの行を追加する（`docs/context/` 配下のメモとは役割が異なるため別行にする）
- `docs/overview.md` の「各ファイルの役割」と「テンプレート」へ AI作業ログを追加する
- 新しいログファイルは作成せず、本ログへ統合する
- 変更してよいファイルは `README.md`、`AGENTS.md`、`docs/overview.md`、本ログの4つのみ

### 追加依頼2（T-031 のコミット前追加修正・上流優先の分析）

コード起点の変更案を分析するときに、影響するファイルを列挙するだけでなく、「変更内容を定義すべき正式資料はどれか」「その中で最も上流かつ適切な資料はどれか」「どの資料を正本とするか」「上流から下流へどの順番で反映するか」を明示的に整理できるようにする追加依頼を受けた。

追加した理由:

- 影響する資料が複数ある場合に、どの資料を正本とし、どこから修正を始めるかの判断が明確でなかった
- そのままでは、各 feature の設計書や実装へ同じルールを個別に書き足し、より上流で一度だけ定義すべき内容が下流へ分散するおそれがあった

依頼の要点:

- `prompts/analyze_code_change_impact.md` へ「変更の正本と上流からの更新」節を追加し、作業手順・影響範囲の確認・出力形式・禁止事項も補強する
- 「上流優先」と「すべての上流資料を変更する」を混同させない
- 適切な正本が存在しない場合は、新しい文書やディレクトリを勝手に作らず人間判断に戻す
- 役割の合わない内容を `common_design/` へ押し込まない
- `AGENTS.md`、`README.md`、`docs/overview.md`、`docs/how_to_use_prompts.md`、`docs/tutorials/030_update_existing_feature.md`、`prompts/review_prompt_integrity.md` を必要最小限で補強する
- 新しいログファイルは作成せず、本ログへ統合する

## AIが確認したファイル

- `AGENTS.md`（既存ルール。特に「修正作業の基本ルール」「仕様変更時の作業ルール」「バグ修正の基本ルール」「common の扱い」「docs/context/ の扱い」「保護対象」「次工程移行判定」）
- `README.md`（体験できること、リポジトリ構成、バグ修正フロー、レビューの位置づけ、チュートリアル一覧）
- `docs/overview.md`（ドキュメント構成、prompts の説明）
- `docs/how_to_use_prompts.md`（汎用プロンプト一覧、依頼例、役割分担）
- `docs/tutorials/030_update_existing_feature.md`（変更パターン表、影響範囲整理のプロンプト例）
- `docs/tutorials/040_bug_fix_flow.md`（変更しないが、接続先として位置づけを確認）
- `prompts/review_context.md`（分析専用プロンプトの構成・文体の参考）
- `prompts/review_feature_source.md`（同上。「変更してよいファイル: なし」型プロンプトの書式）
- `prompts/review_prompt_integrity.md`（完全性レビュー観点の構成）
- `docs/context/README.md`
- `docs/context/ai_work_logs/README.md`
- `docs/templates/ai_work_log_template.md`
- `docs/context/ai_work_logs/20260704_T-030_add_ai_work_logs.md`（既存AI作業ログの記載例）
- `git status`（作業開始前に未コミット変更がないことを確認）

追加依頼（コミット前修正）で確認したもの:

- `git status --short`（T-031 の未コミット変更8件が残っていることを確認し、それらを取り消さないことを確認）
- `docs/templates/` の実際のファイル一覧（`ai_work_log_template.md` が実在することを確認）
- `docs/context/` の実際のディレクトリ構成（`ai_work_logs/README.md` と既存ログ2件が実在することを確認）
- `README.md` のリポジトリ構成ツリーとテンプレート一覧の現在の粒度・並び
- `AGENTS.md` の「ドキュメントひな形」表の現在の並び
- `docs/overview.md` の「各ファイルの役割」表と「テンプレート」表の現在の並び

追加依頼2（上流優先の分析）で確認したもの:

- `git status --short`（T-031 の未コミット変更8件が残っていることを確認）
- `prompts/analyze_code_change_impact.md` の現在の節構成と出力形式の番号（1〜12）
- `AGENTS.md` の「コード起点の変更検討」節と「仕様変更時の作業ルール」の作業順
- `AGENTS.md` の「共通設計書の扱い」（`common_design/` の既存用途がファイル設計・データ設計・DB設計であることを確認）
- `README.md` の「コード起点の変更検討」節
- `docs/overview.md` の `analyze_code_change_impact.md` の説明
- `docs/how_to_use_prompts.md` の汎用プロンプト一覧と利用例
- `docs/tutorials/030_update_existing_feature.md` の変更作業の基本方針・変更パターン表・影響範囲整理・進める順番の例
- `prompts/review_prompt_integrity.md` の「11. コード変更影響分析フロー」

## AIが更新したファイル

- `prompts/analyze_code_change_impact.md`（新規作成: コード変更案の分類・類似機能比較・影響範囲・リスク・次の作業を整理する汎用プロンプト。ファイルは変更しない分析専用）
- `AGENTS.md`（更新: 「修正作業の基本ルール」と「仕様変更時の作業ルール」の間に「コード起点の変更検討」節を追加。既存の仕様変更ルール・バグ修正ルール・common の扱いへ参照で接続し、内容は重複させていない）
- `README.md`（更新: 「このリポジトリで体験できること」に1行追加、`prompts/` 一覧に新プロンプトを追加、「コード起点の変更検討」節を追加、チュートリアル表の 030 の説明を更新）
- `docs/overview.md`（更新: 「prompts」節に新プロンプトの位置づけを1段落追加）
- `docs/how_to_use_prompts.md`（更新: 汎用プロンプト一覧に1行追加、依頼例に利用例を1件追加）
- `docs/tutorials/030_update_existing_feature.md`（更新: 変更パターン表に「内部設計の改善」「動作を変えないリファクタリング」「類似機能間の実装方式の統一」「複数 feature にまたがる標準化」「共通化候補」の5行を追加。既存の「変更要求の影響範囲を整理するプロンプト例」を、新プロンプトを参照する「変更案の影響範囲を整理する」へ置き換え、機能追加の例と正常動作コードの改善例の2例を記載。進める順番の例の1行目に参照プロンプトを明記）
- `prompts/review_prompt_integrity.md`（更新: 確認対象・レビュー目的・実行時の注意に1項目ずつ追加し、レビュー観点に「11. コード変更影響分析フロー」を追加）
- `docs/context/ai_work_logs/20260726_T-031_add_code_change_impact_prompt.md`（新規作成: 本ログ）

追加依頼（コミット前修正）で更新したもの:

- `README.md`（更新: リポジトリ構成ツリーの `docs/context/` 配下に `ai_work_logs/`、その `README.md`、個別ログの一般表記 `<date>_<task_id>_<summary>.md` を追加。`docs/templates/` 一覧に `ai_work_log_template.md` を追加し、関連する `context_note_template.md` の直後に配置）
- `AGENTS.md`（更新: 「ドキュメントひな形」表に AI作業ログの行を1行追加。`docs/context/` 配下のメモの行とは分け、正式仕様ではないこと・AIは明示指示なしに作成・更新しないことを併記）
- `docs/overview.md`（更新: 「各ファイルの役割」表に `docs/context/ai_work_logs/` の行を追加し、「テンプレート」表に AI作業ログとひな形の対応を追加。パス表記は `AGENTS.md` と一致させた）
- `docs/context/ai_work_logs/20260726_T-031_add_code_change_impact_prompt.md`（更新: 本ログへ追加依頼の内容と確認結果を統合。新しいログファイルは作成していない）

追加依頼2（上流優先の分析）で更新したもの:

- `prompts/analyze_code_change_impact.md`（更新: 「変更の正本と上流からの更新」節を新設し、正本の定義・上流資料の候補表・上流資料を無理に変更しない条件・適切な正本が存在しない場合の扱い・上流から下流への反映順を記載。作業手順に正本特定と更新順整理の工程を追加（10→14工程）。「影響範囲の確認」に更新順表を追加（既存の影響範囲表は維持）。出力形式に「9. 変更の正本と更新順」を追加し、以降を10〜13へ繰り下げ。「推奨する次の作業」を正本別の進め方へ再構成。禁止事項に5項目追加）
- `AGENTS.md`（更新: 「コード起点の変更検討」節に正本特定・上流から下流への反映・変更不要な上流資料の理由明示・正本がない場合は人間判断の4点を追加。「仕様変更時の作業ルール」の作業順の後に、上流から下流への更新順を4行追記し、正本判断の詳細は新プロンプトを参照する形にした）
- `README.md`（更新: 「コード起点の変更検討」節に正本と更新順の考え方を1段落追加。詳細は新プロンプトと `AGENTS.md` を参照する構成にした）
- `docs/overview.md`（更新: `analyze_code_change_impact.md` の説明に、正本と更新順の整理、正本が存在しない場合の人間判断報告を2文で追加）
- `docs/how_to_use_prompts.md`（更新: 汎用プロンプト一覧の用途説明に正本と更新順を追加。既存の利用例は維持し、直後に「分析結果で正本と更新順を確認してから、個別の文書更新や実装を別作業として依頼する」を追記）
- `docs/tutorials/030_update_existing_feature.md`（更新: 変更作業の基本方針に「正本を決めてから、上流から下流へ進む」を追加。変更パターン表の5行の注意点を調整（全面書き換えはしていない）。表の下に正本が見つからない場合の扱いを追記。分析結果に含まれる4項目を追記。進める順番の例を、正本確認から始まる流れに調整し、この例では `20_spec.md` が正本候補で `10_overview.md` は更新しないことを明記）
- `prompts/review_prompt_integrity.md`（更新: 「11. コード変更影響分析フロー」に正本の扱いに関する8観点を追加）

## AIが更新しなかったファイル

- `CLAUDE.md`
- `docs/templates/` 配下すべて（新しいテンプレートは追加しない指示のため）
- `docs/tutorials/040_bug_fix_flow.md`
- `docs/tutorials/010_simple_calculator.md`、`docs/tutorials/020_create_new_sample_from_scratch.md`
- 既存の他の `prompts/*.md`（`review_prompt_integrity.md` を除く）
- `docs/context/README.md`
- `docs/context/ai_work_logs/README.md`
- サンプル command/app（`cli_hello_greeting`、`cli_simple_calculator`、`cli_text_counter`）の正式資料と `tasks.md`
- `src/`、`tests/`、`requirements.txt`、`tools/`、`quality/`、`.gitignore`、`.claude/`
- `docs/concept/ai_driven_development.md`、`docs/prompt_design_notes.md`、`docs/common/README.md`

## 更新不要と判断した理由

- `docs/templates/`: 新プロンプトはチャット報告のみで、ファイル出力がない。出力先テンプレートが不要なため。新テンプレートを追加しない指示にも従った
- `docs/tutorials/040_bug_fix_flow.md`: バグ修正フロー自体は変更していない。新プロンプトからの接続は、新プロンプト側と 030 側からのリンクで足りるため
- `docs/context/README.md` / `ai_work_logs/README.md`: `docs/context/` の位置づけと運用ルールは変わらない。新プロンプトも既存方針どおり `docs/context/` を軽い確認トリガーとしてのみ扱うため。追加依頼（コミット前修正）でも、AI作業ログの運用ルール自体は両 README に既に記載済みで、今回は上位ドキュメント側の一覧漏れを埋めるだけだったため更新不要と判断した
- `docs/templates/ai_work_log_template.md`: 既に実在し、内容の変更は不要。追加依頼で行ったのは `README.md` / `AGENTS.md` / `docs/overview.md` からの参照追加のみのため
- 追加依頼2で `docs/templates/` を更新しなかった理由: 正本の考え方は分析プロンプト側のルールであり、新しい文書種別・テンプレート・ディレクトリを追加しない方針のため。既存テンプレートの見出し構成にも影響しない
- 追加依頼2で `docs/tutorials/040_bug_fix_flow.md` と他の `prompts/*.md`（`review_prompt_integrity.md` を除く）を更新しなかった理由: 正本の特定は分析段階の責務であり、バグ修正フローや各作成系プロンプトの作業範囲・出力先を変えないため。分析結果からの接続は新プロンプト側の「推奨する次の作業」で示している
- 追加依頼2で `common_design/` 関連のルール本体（`AGENTS.md` の「共通設計書の扱い」）を更新しなかった理由: 既存の用途定義（ファイル設計・データ設計・DB設計）をそのまま前提として参照しており、用途を変更・拡張していないため
- 既存の他の `prompts/*.md`: 新プロンプトは既存プロンプトの前段に置く入口であり、既存プロンプトの責務・作業範囲・出力先を変えないため
- サンプル command/app の正式資料: 今回はキット本体の追加であり、サンプルの仕様・設計・実装・テストに影響しないため
- `src/` / `tests/` / `requirements.txt`: ドキュメントとプロンプトのみの変更で、実装・テスト・依存関係に影響しないため
- `docs/concept/ai_driven_development.md`: コンセプト自体は変更しておらず、新プロンプトは既存コンセプト（人間が理解・レビュー・判断できる形にする）の範囲内のため

## 実行した確認

- 作業開始前に `git status` を実行し、未コミット変更がないことを確認（今回の変更以外を巻き込んでいない）
- `git diff --check` を実行し、空白エラー・コンフリクトマーカーがないことを確認
- 追加・変更した Markdown 内のファイルパスとリンク先が実在することを確認
- `README.md` のリポジトリ構成の `prompts/` 一覧と、実際の `prompts/` 配下のファイル構成が一致することを確認
- `docs/how_to_use_prompts.md` の汎用プロンプト一覧に新プロンプトが記載されていることを確認
- `docs/tutorials/030_update_existing_feature.md` から新プロンプトへの導線があることを確認
- `AGENTS.md` の「仕様変更時の作業ルール」「バグ修正の基本ルール」「common の扱い」と、新設した「コード起点の変更検討」節が矛盾しないことを確認（新節は分類前の入口のみを扱い、各フローへ参照で接続する構成にした）
- 総合判定値が既存の `GO` / `条件付きGO` / `STOP` と統一されていることを確認
- `tasks.md` のハイブリッド更新方針と矛盾しないことを確認（新プロンプトは `tasks.md` を直接更新せず、更新候補として報告する）
- `python -m pytest` を実行
- 更新後の内容に対して `prompts/review_prompt_integrity.md` の観点で完全性レビューを実施

追加依頼（コミット前修正）で実行した確認:

- `git diff --check` を実行し、指摘がないことを確認
- `README.md` のリポジトリ構成ツリーに `docs/context/ai_work_logs/`、`docs/context/ai_work_logs/README.md`、`docs/templates/ai_work_log_template.md` が反映されていることを確認
- `AGENTS.md` と `docs/overview.md` のテンプレート対応が、作成するファイルのパス表記（`docs/context/ai_work_logs/<date>_<task_id>_<summary>.md`）とひな形パス（`docs/templates/ai_work_log_template.md`）の両方で一致していることを確認
- `docs/templates/ai_work_log_template.md` と `docs/context/ai_work_logs/README.md` が実在することを確認
- AI作業ログの説明が `docs/context/README.md` および `docs/context/ai_work_logs/README.md` の既存方針（正式仕様ではない／AIは明示指示なしに作成・更新しない／`docs/context/ai_work_logs/` に配置する）と矛盾しないことを確認
- `README.md` のツリーとテンプレート一覧を全面的に書き換えず、追記のみであることを `git diff` で確認
- 今回変更してよい4ファイル（`README.md`、`AGENTS.md`、`docs/overview.md`、本ログ）以外に新しい差分が発生していないことを `git status --short` で確認
- 追加した Markdown 内のパスがすべて実在することを確認
- `python -m pytest` を再実行

追加依頼2（上流優先の分析）で実行した確認:

- `git diff --check` を実行し、指摘がないことを確認
- `prompts/analyze_code_change_impact.md` に「変更の正本」「最上流かつ適切な正式資料」「変更不要な上流資料の理由」「上流から下流への更新順」「適切な正本が存在しない場合の人間判断」が含まれることを確認
- 出力形式に独立項目「9. 変更の正本と更新順」があることを確認
- 出力形式の番号が 1〜13 の連番で重複・欠番がないこと、本文中の相互参照が番号ではなく節名（「変更の正本と上流からの更新」「影響範囲の確認」「類似機能・横断的な変更の確認」）で行われており、番号ずれが起きない構成であることを確認
- `AGENTS.md`、`README.md`、`docs/overview.md`、`docs/how_to_use_prompts.md`、`docs/tutorials/030_update_existing_feature.md` の説明が、新プロンプト本体と矛盾しないことを確認
- 「上流優先」が「すべての上流資料を機械的に変更する」意味になっていないことを、5ファイルすべてで確認（各所に「形式的にすべて変更しない」「変更不要な上流資料は理由を明示する」を明記）
- `common_design/` の既存用途（`AGENTS.md`「共通設計書の扱い」のファイル設計・データ設計・DB設計）と矛盾していないことを確認
- 適切な正本が存在しない場合に、AIが新しい文書種別・配置場所・ディレクトリを勝手に作らない構成であることを確認（禁止事項にも追加）
- 総合判定が既存の `GO` / `条件付きGO` / `STOP` と矛盾しないことを確認（人間判断待ちで更新順を確定できない場合は STOP、限定的に進められる場合は条件付きGO）
- 追加・変更した Markdown 内のパスがすべて実在することを確認
- `python -m pytest` を実行
- 更新後の内容に対して `prompts/review_prompt_integrity.md` の観点で完全性レビューを実施
- 変更してよい8ファイル以外に新しい差分が発生していないことを `git status --short` で確認

## テスト実行結果

- 実行コマンド: `python -m pytest`
- 結果: 21 passed（実装コード・テストコードは変更していないため、既存テストの回帰確認のみ）

## 残課題・未確認事項

- 新プロンプトを実案件で使ったときに、類似機能比較表の列構成（対象／現在の仕様／現在の実装方式／差異／差異の理由／統一要否／推奨対応）が過不足ないかは、運用後の見直し待ち
- 複数 command/app にまたがる標準化を扱う場合、どの単位で作業を分割するか（feature 単位で順番に進める運用でよいか）は人間判断待ち
- `docs/tutorials/030_update_existing_feature.md` の変更パターン表が9行に増えたため、将来さらに増える場合は分割の要否を検討する必要がある
- `AGENTS.md` への追記量が「必要最小限」の範囲に収まっているかは人間確認待ち
- 完了報告時に人間確認事項として挙げた「`README.md` / `docs/overview.md` に `ai_work_logs/` と `ai_work_log_template.md` の記載がない」件は、追加依頼（コミット前修正）で解消済み
- AI作業ログが増えた場合に、`README.md` のツリーで個別ログを列挙しない方針（一般表記 `<date>_<task_id>_<summary>.md` のみ）を継続してよいかは、運用後の見直し待ち
- 追加依頼2の残課題: 「上流資料の基本的な候補」表は判断材料であり機械的な決定ルールではないと明記したが、実運用でAIが表を決定ルールとして扱わないかは、運用後の確認待ち
- 追加依頼2の人間確認事項: 例外処理の書き方・命名・責務分担・実装パターンなど、複数 feature に共通する実装方針の正本をどこに置くかは、現在のスターターキットの構成では未定義。今回は「正本候補なし → 人間判断」と扱う構成にしたが、恒久的な配置場所（新しい共通資料を設けるか、各 feature の設計書に閉じるか）は人間判断待ち
- 追加依頼2の人間確認事項: `docs/tutorials/030_update_existing_feature.md` の変更パターン表で、注意点セルに正本の考え方を追記した範囲（5行）が「全面的な書き換えではない」範囲に収まっているか

## 正式資料への反映要否

- 仕様書: 該当なし（feature 仕様に関する変更ではないため）
- 設計書: 該当なし
- テスト計画: 該当なし
- レビュー結果: 該当なし
- tasks.md: 該当なし（対象 command/app・feature がないため）
- その他: 今回の変更自体が `AGENTS.md`（正式ルール）、新プロンプト、`README.md`、`docs/overview.md`、`docs/how_to_use_prompts.md`、`docs/tutorials/030_update_existing_feature.md` への反映を兼ねている。重要なルールを本AI作業ログだけに残していないことを確認済み

## レビュー補助メモ

- 判断が分かれそうだった点: 新プロンプトを既存のどのフローの前段に置くか（バグ修正フローの前に置くか、変更作業全般の入口に置くか）
- 採用した判断と理由: 変更作業全般の入口とし、分析結果に応じてバグ修正フロー／仕様変更ルール／設計変更プロンプト／共通化検討へ分岐する構成にした。コードを見た時点では分類が未確定という依頼の前提に合わせるため
- 採用しなかった案: 変更パターン表に「コード起点の変更案」という行を1行追加するだけの統合。分類自体が未確定な状態を扱うため、表の1パターンに収めると「先に分類を決めてから表を引く」順序になり、目的と逆になると判断した
- 仮置きした前提: `AGENTS.md` の新節は「コード起点の変更検討」という名称とし、既存の「修正作業の基本ルール」と「仕様変更時の作業ルール」の間に配置した。分類前の入口 → 分類後の各フロー、という読み順を想定している
- 人間に確認してほしい点: `AGENTS.md` の新節の配置と分量、`docs/tutorials/030_update_existing_feature.md` で既存のプロンプト例を全面的に置き換えた範囲、および追加依頼で `README.md` のテンプレート一覧の末尾（`context_note_template.md` の直後）に `ai_work_log_template.md` を置いた並びが妥当か
- 追加依頼2で判断が分かれそうだった点: 出力形式のどこに「変更の正本と更新順」を置くか（「影響する資産」の前か後か）
- 追加依頼2で採用した判断と理由: 「8. 影響する資産」の直後（9番）に置いた。更新順表は変更が必要な資産の並べ替えであり、影響範囲表を先に示したほうが「変更不要な資産は更新順表に入れず、影響範囲表で理由を示す」という関係を読み取りやすいため。分析の作業手順では、指示どおり正本特定（工程8〜10）を影響資産の洗い出し（工程11）より前に置いている
- 追加依頼2で採用しなかった案: `AGENTS.md` の「仕様変更時の作業ルール」へ正本判断のルール本文を再掲する案。同じルールを二つの節へ長文で重複させないため、上流から下流への更新順だけを追記し、正本判断の詳細は新プロンプトへの参照で整理した

## 備考

該当なし
