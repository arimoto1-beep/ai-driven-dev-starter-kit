# V2ドキュメントのメンテナンス

## 目的

**現在あるV2の実装を変更することではなく、現在仕様の説明を実装へ追いつかせることが目的です。**

スターターキットの実装は、feature 新規開発についてオートモード中心のV2へ進化しています。
しかし README、`docs/overview.md`、tutorials などには、マニュアルモード中心だった時期の説明が残っています。

人間だけでなく**AIがリポジトリを参照して作業する**ため、現在仕様を説明する場所に古い情報が散在している状態は避けたいです。

## 状態

完了（Phase 1〜5 すべて完了。**ドキュメント刷新は完了**）

**ただし commit / push はまだ行っていません。** 人間の差分確認が残っています。

## 作業期間

2026-08-30 〜

## 背景

このキットは当初、人間が個別プロンプトを1つずつ実行する方式（マニュアルモード）を中心に作られていました。

その後、feature 新規開発について次が実装されています。

- オートモード（`tools/feature_runner.py`）
- Worker / Reviewer の分離起動
- Spec Review（`--spec-review`）
- CP1 での人間による仕様承認
- Manufacturing Preflight
- G1 設計 / G2 テスト設計 / CP3 実装・レビュー
- Gate記録
- RETURN / BLOCKED / `--rework` / `--retry-blocked`
- モデル自動選択（`auto` / `manual`）

**実装とルール正本（`docs/rules/project/70_feature_loop.md`）は現行仕様に追いついています。**
追いついていないのは、その外側にある入口文書・チュートリアル・一部テンプレートです。

調査の結果、`README.md` / `AGENTS.md` / `docs/README.md` / `docs/overview.md` /
`docs/how_to_use_prompts.md` / `docs/concept/` / `docs/tutorials/README.md` の**すべてで、
オートモード・`feature_runner`・Gate記録の言及が0件**でした。

## 基本方針

- **feature 新規開発の表玄関はオートモードとする**
- **マニュアルモードは削除しない**
- 現在仕様を説明する文書に残る古い説明は修正する
- `work_notes`、Gate記録、過去レビュー、AI作業ログなどの**履歴は書き換えない**
- まず既存V2を正しく説明することを優先する
- features の上位構造、新しい自動化、新機能追加は**今回の対象外**
- README では詳細機能を全部並べず、「最初の一歩」が理解できる構成を優先する

決定事項の詳細は `02_decisions.md` を参照してください。

## 現在の標準フロー

`docs/rules/project/70_feature_loop.md`（正本）、`tools/feature_runner.py`、
`tests/tools/test_feature_runner.py` を突き合わせて確認した、現在の feature 新規開発フローです。

```text
20_spec.md を人間が用意する（AIが作成を補助してもよいが、確定させるのは人間）
    ↓
Spec Review（--spec-review）
    Worker を起動せず、Reviewer が現在の 20_spec.md を読む。何度でも実行できる
    PJ上位者・顧客レビューなど、runner の外の工程を挟める
    ↓
CP1：人間による仕様承認                      ← Human Gate
    CP1 Gate記録の承認欄に人間がチェックを入れる。ここで baseline が確定する
━━━━━━━━━ 人間側の仕様 / AI製造 の境界 ━━━━━━━━━
Manufacturing Preflight
    runner が製造開始前に自動確認する（人間の手作業ではない）
      1. 仕様レビューが PASS していること
      2. 人間による仕様承認が存在すること
      3. 承認対象の 20_spec.md と現在の 20_spec.md が同一 baseline であること（内容ハッシュ）
    ↓
G1：21_design.md / 22_flow.md               ← AI Gate
    ↓
G2：23_test_plan.md / 24_review_checklist.md ← AI Gate
    ↓
CP3：実装・テスト・25_review_result.md       ← Human Gate
    ↓
人間による受け入れ判断
    ↓
done
```

### stage 内部の進み方

**「Worker → Reviewer の1往復」で必ず終わるとは限りません。**

```text
Worker（prompts/run_stage.md。stage ごとの個別プロンプトへ委譲）
    ↓ 別プロセスとして起動
Reviewer（prompts/review_stage.md）→ Gate記録を作成
    ↓
verdict を判定
  ├ IN_PROGRESS → Worker(mode=fix) → Reviewer を繰り返して収束させる
  │                （上限 max_rounds = 3。超えると BLOCKED(non_convergence)）
  ├ PASS        → 次 stage へ。Human Gate なら承認待ちで停止
  ├ RETURN      → return_to の stage から再実行
  │                （同一 Gate への差し戻し上限 max_returns_per_gate = 3）
  └ BLOCKED     → 停止。自動では再開しない（--retry-blocked の明示が必要）
```

**Worker → Reviewer が基本単位で、`IN_PROGRESS` の間は Worker(mode=fix) → Reviewer を
繰り返して収束させます。** Worker を起動せず Reviewer だけを動かす実行もあります
（`--spec-review` / `--review-current` / 人間コメントによる再判定）。

### 補助操作

| 操作 | 用途 |
|---|---|
| `--spec-review` | 仕様レビューの単独実行。製造は開始しない |
| `--review-current <stage>` | Worker を起動せず、現在の成果物を Reviewer が見直す（人間の修正からの復帰） |
| `--rework <stage>` | 通過済み stage を Worker から作り直す |
| `--retry-blocked` | BLOCKED からの明示的な再試行 |

通過後に成果物が変更された場合は `artifacts_hash` で検出し、古い判定を完成扱いにせず停止します。

### モデル選択

方式は2つだけです。

```text
--model-class の指定なし → auto
    プロンプト基礎レベル（base_level_*） + feature難易度（easy=-1 / normal=0 / hard=+1）
    → 1〜3 へ丸め → 1=cheap / 2=standard / 3=strong
--model-class の指定あり → manual（Worker / Reviewer とも同じクラスへ固定）
```

feature 難易度は **CP1 の Reviewer が仕様レビューの一部として1回だけ判定**し、
CP1 Gate記録の `feature_difficulty` に残ります。G1 以降では再判定しません。

## 現在地

調査（`01_audit.md`）と方針決定（`02_decisions.md`）が完了し、次まで実施済みです。

**Phase 1「明確な矛盾の除去」**（実施結果は `04_phase1_result.md`）

- `docs/overview.md` / `docs/templates/24_review_checklist_template.md` /
  `docs/rules/project/10_document_structure.md` / `prompts/analyze_code_change_impact.md` /
  `docs/tutorials/030_update_existing_feature.md` の5件と、再発防止のためのテスト対象追加1件

**Phase 2A「ルート `README.md` の模様替え」**（実施結果は `05_phase2a_readme_result.md`）

- `README.md` をオートモード中心の入口へ全面的に書き換えた
- マニュアルモードは削除せず、**新規 feature でも選べる現役の選択肢**として位置づけた

**Phase 2B「入口文書への横展開」**（実施結果は `06_phase2b_entry_docs_result.md`）

- README の微修正2点（人間の判断点は固定2か所＋随時、収束は「指摘があれば修正と再レビュー」）
- `docs/README.md`（案内図）／`docs/overview.md`（構造説明）／`docs/how_to_use_prompts.md`（promptの渡し方）／
  `AGENTS.md`（AIの正本への導線）の4文書を、役割を分けて更新
- 5文書すべてから `70_feature_loop.md` へ到達できる状態にした

**Phase 3「workflow の位置づけとチュートリアル」**（実施結果は `07_phase3_workflow_and_tutorial_result.md`）

- Phase 2B の微修正2点（Worker の委譲先の範囲、runner 実行時の人間の指定）
- `20_workflow.md` を「feature 新規開発の2つの進め方」＋「工程一覧（マニュアルモード）」へ再構成
  （**工程内容・承認位置・実装開始条件は変更なし**）
- **オートモードの最初の一歩チュートリアル `docs/tutorials/005_automode_first_feature.md` を新設**
- `docs/tutorials/README.md` の入口を 005 へ変更。既存 tutorial 4本へ位置づけの注記を追加（内容は無変更）
- **005 の実AI一周検証は未実施**（サンプルの扱いが未決のため。詳細は `07_...` の「4. 実行検証」）

**Phase 4「concept / quality / 用語と、サンプル調査」**（実施結果は `08_phase4_concept_quality_samples.md`）

- Phase 3 レビューの4点を修正（`10_overview.md` と `20_spec.md` の関係、未実測の所要時間削除、
  人間判断の固定点、CP1 baseline の説明）
- 「Worker と Reviewer を交互に起動」を、主要な入口5か所で「分離して起動」へ
- `docs/concept/ai_driven_development.md` を現在の思想へ追従（仕様書化はしていない）
- `quality/README.md` へ Gate記録との役割差を追加（**Gate は quality へ自動集約されない**ことを明記）
- `00_project_policy.md` の旧「標準工程」表現を修正。あわせて**索引に無かった `70_feature_loop.md` を追加**
- **サンプル3件を調査し、推奨案（masker=A / rework=C / uppercase=C）と必要作業を整理**
  （**変更は一切していません。最終判断は人間です**）

**Phase 5「サンプル整理と最終整合レビュー」**（実施結果は `09_phase5_final_cleanup_and_review.md`）

- 人間の判断を反映：**`cli_text_masker` は実AI実行履歴例として残し**（`README.md` を新規追加）、
  **`cli_mask_rework` と `cli_uppercase_text` は削除**
- 削除前に必要な事実を work_notes へ記録（rework は `20260826_...` へ追記、uppercase は `09_...` へ）
- 「交互に起動」を**現行資料から全廃**（5か所を「分離して起動」へ）
- 横断検索を A〜E で分類。**D（要修正）は全対応、E（削除対象への参照）は0件**
- `review_prompt_integrity.md` の観点で**静的**整合レビューを実施（**実AIレビューは未実施。理由を記録**）
- テスト **251 passed**（`cli_mask_rework` 削除に伴う −6 のみ）

**ドキュメント刷新（Phase 1〜5）は完了です。commit / push は未実施です。**

## 決定事項

`02_decisions.md` を参照してください。要点は次の3つです。

- feature 新規開発の表玄関はオートモードにする
- マニュアルモードは残す。**「既存変更・バグ対応専用」とは限定しない**
- 現在仕様を説明する場所の古い情報は修正するが、履歴資料は書き換えない

## 未決事項

- ~~`cli_text_masker` / `cli_mask_rework` / `cli_uppercase_text` を正式サンプル化するか整理するか（人間判断）~~
  → **Phase 5 で決着。** 人間の判断により、**masker は「実AI実行履歴例」として残し**（正式サンプルとは別枠）、
  **rework と uppercase は削除**。詳細は `09_phase5_final_cleanup_and_review.md` の第1部
- ~~`docs/rules/project/20_workflow.md` の「標準工程」という呼称をどう変えるか~~
  → **Phase 3 で「工程一覧（マニュアルモード）」へ改題し、決着**
- ~~オートモードのチュートリアルの題材（既存サンプルを使うか、新規に用意するか）~~
  → **Phase 3 で「読者が新しい小さな command/app を作る」形に決着**（既存サンプルを壊さないため）
- **005 チュートリアルを実AIで一周検証するか、いつ行うか**
  → Phase 5 の完了条件からは外した（`cli_text_masker` が実AI実行例として残るため）。**任意の後続作業**
- **`review_prompt_integrity.md` の実AIレビューを行うか**
  → Phase 5 では静的確認のみ。行う場合は**ファイルを変更しない実行設定**で

**決着済み：** README と `docs/overview.md` のディレクトリツリーの役割分担は、Phase 2B で
「README＝リポジトリ全体の俯瞰／overview＝docs 配下の成果物構造の詳細」と決め、併存させました
（`06_phase2b_entry_docs_result.md`）。

## 次に行うこと

1. **人間が Phase 5（および全体）の差分を確認する**
2. **commit する**（まだ実施していません）
3. 任意：**ファイルを変更しない実行設定**で `review_prompt_integrity.md` の実AIレビューを行う
   （Phase 5 では静的確認のみ。理由は `09_...` の第2部3）
4. 任意：**005 チュートリアルの実AI一周検証**を、独立した作業として行う

## 関連する正式文書

- `docs/rules/project/70_feature_loop.md`（オートモードの正本）
- `docs/rules/project/20_workflow.md`（工程と承認位置）
- `docs/rules/project/10_document_structure.md`（成果物の配置）
- `docs/rules/project/50_ai_permissions.md`（承認欄の場所、Gate記録の更新権限）

## 関連する作業メモ

- `20260823_feature_auto_mode_real_ai_validation`（オートモードの実AI検証）
- `20260826_feature_rework_flow`（完成後の修正フロー）
- `20260829_model_auto_selection`（モデル自動選択の設計・実装・検証）
- `20260814_readme_structure`（過去のREADME構成検討。当時の判断として参照する）

## 付随ファイル一覧

| ファイル | 内容 |
|---|---|
| `01_audit.md` | 調査結果。古い・矛盾する記述の一覧と、履歴として残すものの区別 |
| `02_decisions.md` | 人間が決定した方針と、「古い情報 ≠ すべて削除対象」の区別 |
| `03_execution_plan.md` | Phase 1〜5 の作業順と、各 Phase の対象・目的・完了条件 |
| `04_phase1_result.md` | Phase 1 の実施結果。変更内容、直さなかったもの、判断に迷ったもの、完了判定 |
| `05_phase2a_readme_result.md` | Phase 2A の実施結果。README の新構成、残したもの、載せなかった詳細、Phase 2B の課題 |
| `06_phase2b_entry_docs_result.md` | Phase 2B の実施結果。README 微修正、入口4文書の変更、文書間の役割分担、完了判定 |
| `07_phase3_workflow_and_tutorial_result.md` | Phase 3 の実施結果。`20_workflow.md` の再構成、新チュートリアルの題材選定と検証範囲、既存 tutorial の位置づけ、完了判定 |
| `08_phase4_concept_quality_samples.md` | Phase 4 の実施結果。concept / quality / 用語の修正と、**サンプル3件の調査結果・推奨案（人間の判断材料）** |
| `09_phase5_final_cleanup_and_review.md` | Phase 5 の実施結果。**サンプル判断の反映（masker 保存・rework / uppercase 削除）**、最終横断レビュー、整合レビュー、完了判定 |
