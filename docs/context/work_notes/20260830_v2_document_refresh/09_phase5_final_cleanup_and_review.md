# Phase 5 実施結果：サンプル整理と最終整合レビュー（2026-08-30）

このドキュメント刷新作業の最終 Phase です。

**過去の記録（`01_audit.md` 〜 `08_phase4_concept_quality_samples.md`）は書き換えていません。**

---

# 第1部：サンプル判断の反映

Phase 4 の調査を受け、**人間が次を決定しました。**

| サンプル | 決定 |
|---|---|
| `cli_text_masker` | **残す。** ただし「現在仕様の模範サンプル」ではなく**実AI実行履歴例**として扱う |
| `cli_mask_rework` | **削除** |
| `cli_uppercase_text` | **削除** |

## 1. `cli_text_masker`

### 位置づけ

**実AIでオートモードを CP1 から CP3 まで一周させた、2026-08-23 時点の実行結果**として残しました。
正式サンプル（`cli_hello_greeting` / `cli_simple_calculator` / `cli_text_counter`）とは**別枠**です。

### なぜ成果物を現在仕様へ書き換えなかったか

**実行当時の記録だからです。**

後から現在仕様へ書き換えると、「当時どう動いたのか」が分からなくなります。
特に `tasks.md` と Gate履歴の食い違い（`tasks.md` は G2、Gate は CP3 `PASS`）は、
**実行中に現在地メモが更新されないまま終わったという事実そのもの**です。化粧直しはしていません。

**README 追加以外、このディレクトリのファイルは1つも変更していません。**

### 新規作成した README（`docs/cli_text_masker/README.md`）で説明したこと

| 節 | 内容 |
|---|---|
| このディレクトリは何か | 実AI実行履歴例であり**現在仕様の模範サンプルではない**こと、実行日、正式サンプルと 005 チュートリアルへの導線 |
| 見どころ：`gates/` | Gate記録7件の一覧（CP1 → G1 → G2 → CP3 で **BLOCKED 3回 → PASS**）と、そこから確認できること。`--history` の実行例。**Gate を1件ずつ解説する文書にはしていない** |
| 現在仕様と異なる点 | 下記4点を表で明示し、**「誤りとして修正するのではなく、当時の検証結果を保存しているため残している」**と説明 |
| なぜ直さないのか | 書き換えると当時の動作が分からなくなること |
| 中身 | ディレクトリ構成 |
| 関連 | 検証の経緯（work_note）、正本、005、tools/README |

### 意図的に残した旧情報

| 箇所 | 当時 | 現在 |
|---|---|---|
| Gate記録の `schema` | `gate_record/v1`（8ファイル） | `gate_record/v2` |
| Gate記録のモデル関連 field | `model_design` / `model_build` / `model_review`（8ファイル） | `feature_difficulty` / `worker_model_class` / `reviewer_model_class` / `model_selection` |
| `24_review_checklist.md` | 「CP1 の**下流進行承認**」（2ファイル） | 「CP1 の**仕様承認**（現在の `20_spec.md` と同一 baseline）」 |
| `tasks.md` | 現在地が「G2、G2 Gate 未実施」 | Gate履歴は CP3 `PASS` まで進んでいる |

**README で「現在仕様を確認する場合は `70_feature_loop.md` を参照」と明示しています。**

### どこから案内したか

**既存の「サンプル」表とは別の枠**にしました。同列に見えないようにするためです。

| ファイル | 追加内容 |
|---|---|
| `README.md` | サンプル表の下に**新設した「## 実行例」節**。「サンプルとは別に、実際にAIを動かしたときの記録」「**模範例ではありません**」と明記 |
| `docs/README.md` | 「feature を開発する」表へ「**実AIでオートモードを実行した履歴を見る**（模範例ではなく実行記録）」の1行 |
| `docs/tutorials/005_automode_first_feature.md` | 「次に読むもの」へ「実AIでオートモードを実行したときの Gate記録の実物」の1行 |

## 2. `cli_mask_rework`（削除）

### 削除前に残した事実

**`docs/context/work_notes/20260826_feature_rework_flow/README.md` へ「検証用サンドボックスの削除」節を追記しました。**

- 削除したパス3つ
- 削除してよいと判断した根拠（`cli_text_masker` の複製で `src` はバイト単位で同一、検証結果は作業メモに残っている、複製元を残すことになった、正式導線から未参照）
- **この削除で失われたもの**（`--rework` の Gate記録 0008 のファイル本体、テスト6件）

**`--rework` の検証内容そのものは、既に `04_implementation.md`「実AIでの確認」に転記されていました。**
Phase 4 の調査では「未転記」と評価しましたが、**再確認したところ転記済みでした**（`triggered_by: REWORK`、
`supersedes` が 0003 を指すこと、`artifacts_hash` の値と往復）。そのため重複させず、削除の事実と
失われたものだけを追記しています。

**Gate記録を別の場所へ丸ごとコピーはしていません。**

### 削除したもの

```text
docs/cli_mask_rework/    （10_overview.md、features 一式、gates 8件）
src/cli_mask_rework/     （features/ascii_digit_masker.py、__init__.py）
tests/cli_mask_rework/   （テスト6件）
```

### テスト件数への影響

**257 件 → 251 件（−6 件）。** 減少分は `tests/cli_mask_rework/` の6件のみです。

## 3. `cli_uppercase_text`（削除）

### 実体の確認

Phase 4 の想定どおり、**`src/cli_uppercase_text/` と `tests/cli_uppercase_text/` は存在しませんでした。**
削除したのは `docs/cli_uppercase_text/` のみです。

### 削除前に残した事実

**専用の作業メモが存在しなかったため、ここへ記録します。** 削除前に採取した事実のみで、
経緯の推測は加えていません。

```text
docs/cli_uppercase_text/
├─ 10_overview.md
└─ features/uppercase/
   ├─ 20_spec.md、21_design.md、22_flow.md   （23_test_plan.md 以降は未作成）
   ├─ tasks.md                               （現在地: CP1、最終更新 2026-08-23）
   └─ gates/                                 （3件）
```

Gate記録3件の内容（front matter から確認できた事実）。

| ファイル | `gate` | `verdict` | 備考 |
|---|---|---|---|
| `0001_20260823T111952_g0.md` | **`G0`** | `BLOCKED` | `blocked_reason: state_error`、`recorded_by: runner` |
| `0002_20260823T114154_g0.md` | **`G0`** | `PASS` | `triggered_by: RETRY_BLOCKED`、`recorded_by: reviewer` |
| `0003_20260823T114604_cp1.md` | `CP1` | `PASS` | `triggered_by: INITIAL`、`recorded_by: reviewer` |

事実として言えること。

- **オートモードの stage 構成に `G0` が存在した時期の試行**である
- **現在の stage 構成は `CP1` / `G1` / `G2` / `CP3` で、`G0` は存在しない**
- `src` / `tests` が作られておらず、**未完成のまま役割を終えた**
- `20260826_feature_rework_flow/01_verification_method.md` では、
  「既存の実AI検証履歴」として `cli_text_masker`（7件）と並べて Gate記録3件が挙げられ、
  **修正フロー検証では変更しない対象**として扱われていた

**なぜ `G0` が廃止されたのかは、リポジトリ内の記録からは確認できませんでした。推測は書きません。**

### 削除したもの

```text
docs/cli_uppercase_text/    （docs のみ。src / tests は元から存在しない）
```

テスト件数への影響はありません。

---

# 第2部：最終整合レビュー

## 1. 「交互に起動」の最終判断

Phase 4 で対象外として残していた5か所を、指示された判断基準で再確認しました。

**結論：5か所すべて修正しました。** 現行資料から「交互に起動」は**0件**になりました。

| ファイル | 判断 | 修正後 |
|---|---|---|
| `docs/rules/project/70_feature_loop.md:35` | **修正。** 正本のモード比較表であり、**オートモード全体の説明として「常に交互」と読める** | 「runner が各 stage で Worker と Reviewer を**分離して起動**し」 |
| `prompts/README.md:11` | **修正。** 「単独で手動実行できる」補足はあるが、**runner 自身が Reviewer だけを動かす実行には触れていなかった** | 「別プロセスとして**分離して起動**します。**Reviewer だけを動かす実行もあります**（`--spec-review` / `--review-current`）」 |
| `tools/README.md:13` | **修正。** runner 自身の説明であり精度が要る | 「別プロセスとして**分離して起動**し」 |
| `docs/tutorials/010_simple_calculator.md:6` | **修正。** 括弧内だが**オートモード全体の説明**であり、基準に照らすと修正対象 | 「Worker と Reviewer を**分離して起動**する進め方」 |
| `docs/tutorials/020_..._from_scratch.md:6` | **修正。** 同上 | 同上 |

**機械的な全置換ではありません。** 各箇所が「stage 通常実行の局所的な説明」か
「runner 全体の説明」かを確認したうえで判断しました。

**なお、Worker → Reviewer を往復するという事実自体は失われていません。** 収束ループ
（`IN_PROGRESS` → `Worker(mode=fix)` → Reviewer）は `70_feature_loop.md` の「Gate 判定値」節に、
005 チュートリアルには「指摘があれば修正と再レビューを行います」として残っています。

## 2. 横断検索結果（A〜E 分類）

### D（現在仕様として古く、修正が必要）→ **今回すべて修正**

| 対象 | 内容 |
|---|---|
| 「交互に起動」5か所 | 上記1のとおり修正 |

**それ以外の D は検出されませんでした。**

### E（削除した対象への参照で、除去が必要）→ **0件**

`cli_mask_rework` / `cli_uppercase_text` を検索した結果、**現行資料・`prompts/`・`tools/`・
Python コード・tests・設定ファイルからの参照は0件**でした。残っているのは `work_notes` のみで、
これは B（履歴）です。

### A（現在仕様として正しい）

| 語 | 状態 |
|---|---|
| `下流進行承認` | **現行資料に0件** |
| `G0` / `g0` | **現行資料に0件**（`cli_uppercase_text` の削除により消滅） |
| `role_fixed` / `role_design` / `role_build` / `role_review` | **現行資料に0件** |
| `model_design` / `model_build` / `model_review` | **現行資料に0件** |
| `実装着手承認` | 現行資料に 46 件。**すべて方式（`manual`）の文脈が明示されている**か、事実の記述 |
| `CP1` / `CP3` | 「CP1＝仕様承認」「CP3＝受け入れ判断」で全文書一致 |
| 実装開始条件（`auto`） | **`CP1 の仕様承認（現在の 20_spec.md と同一 baseline）AND 最新 G2 Gate記録の verdict: PASS`** の1文が、`overview` / `20_workflow` / `50_ai_permissions` / `70_feature_loop` / `24_review_checklist_template` / `030 tutorial` の**6か所で完全一致** |
| `オートモード` / `マニュアルモード` | 入口・rules・templates・prompts・tutorials で一貫 |
| `Worker` / `Reviewer` / `run_stage` / `review_stage` | 役割と入口の説明が一貫 |
| `Gate` / `quality` | 役割差が `quality/README.md` に明示済み |

`標準工程` は現行資料に8件残っていますが、**すべて「通常の工程」という一般名詞としての用法**で、
Phase 3 で改題した見出し（`## 工程一覧（マニュアルモード）`）を指すものはありません。**A 分類です。**

### B（履歴として正しい）→ 修正しない

- `docs/context/work_notes/` 配下すべて（`cli_mask_rework` / `cli_uppercase_text` への言及、
  `role_fixed`、`G0`、`gate_record/v1` などを含む）
- `docs/context/ai_work_logs/`、`docs/context/rejected_verbose_option.md`
- 既存の正式サンプルの `25_review_result.md` / `12_command_review_result.md`
- `tests/tools/test_feature_runner.py` の `G0` 検出テスト（**旧 stage を残さないことを検査する側**）

### C（実AI実行履歴例として意図的に残す）→ 修正しない

`docs/cli_text_masker/` 配下の旧情報。

| 内容 | 件数 |
|---|---|
| `gate_record/v1` | 8ファイル |
| `model_design` 等の旧 field | 8ファイル |
| 「下流進行承認」 | 2ファイル |
| `tasks.md` の現在地と Gate履歴の食い違い | 1ファイル |

**すべて `docs/cli_text_masker/README.md` で「当時の記録として残している」と明示済みです。**

## 3. `review_prompt_integrity.md` による整合レビュー

### 実施方法：静的レビュー（**実AI未実施**）

**実AIによるレビューは実施していません。** 理由は2つです。

1. **費用が発生する。** このプロンプトは全ルール文書を読む構成のため、1回でも入力が大きい
2. **`ai_command` に `--permission-mode acceptEdits` が含まれている。** プロンプト自体は
   ファイルを変更しない設計だが、**commit 直前の最終確認で、AI が意図せずファイルを変更する
   リスクを取るべきではない**と判断した

代わりに、**プロンプトの13観点のうち、今回の刷新が触れた範囲を静的に確認**しました。

### 確認した観点と結果

| 観点 | 確認方法 | 結果 |
|---|---|---|
| **1. 全体方針の一貫性** | 「すべての変更を仕様書から始める」と読める記述の検索 | **問題なし。** 検出された4件はいずれも**「そうではない」と否定している**文（`concept:38`、`core/10_workflow:34`、`030 tutorial:22`、`review_prompt_integrity:30`） |
| **4. テンプレートとの整合** | 既存テスト（`-k "template or config or heading or doc"`）20件 | **全 PASS** |
| **5. 次工程移行判定** | レビュー結果4値と `GO`/`条件付きGO`/`STOP` の分離 | **問題なし。** `25_review_policy.md` の規定を変更しておらず、`quality/README.md` の追記もこれと整合 |
| **12. core / project / task の責務分離** | `docs/rules/core/` へのプロジェクト固有値（`feature_runner`、`cli_*`、`python -m pytest`、`feature_loop.local`）の混入検索 | **0件。混入なし** |
| **12. 正本の一本化** | 今回追記した文書での「正本」宣言の確認 | **問題なし。** `README` / `overview` / `concept` / `quality/README` / `cli_text_masker/README` はいずれも**自身が正本だと主張せず、`docs/rules/` 配下へ委譲**している |
| **13. 作業メモの整合** | 今回の work_note が第二の正本になっていないか | **問題なし。** `20260830_v2_document_refresh/README.md` は正本を `70_feature_loop.md` と明示し、自身は経緯の記録に留まっている |

### 指摘・修正したもの

**静的レビューの範囲では、新たな不整合は検出されませんでした。**
上記1（「交互に起動」）は Phase 4 からの持ち越しとして、このレビューとは別に修正しています。

### 未解決事項

- **実AIによる整合レビューは未実施です。** 特に観点2（AIの権限範囲）、観点3（成果物の接続）、
  観点9（重複・責務衝突）、観点10（商用開発への適用性）、観点11（変更ルートのフロー）は、
  **文書全体を読み通す必要があり、静的検索では確認しきれていません**
- 実施する場合は、`--permission-mode` を編集不可にするなど、**ファイルを変更しない実行設定**で
  行うことを推奨します

---

# 第3部：結果

## 現在の文書構造（最終状態）

```text
README.md                         初見の人へ、何をするキットかと feature 開発の流れ・最初の一歩
docs/README.md                    docs 配下の案内図
docs/overview.md                  リポジトリと成果物の構造説明（どこに何があるか）
docs/how_to_use_prompts.md        prompt の選び方と渡し方（auto / manual の違いを含む）
docs/concept/                     なぜこの構造にしているか（思想。仕様の正本ではない）
AGENTS.md                         AIが作業開始時に正しい正本へ到達するための入口
docs/rules/project/00_project_policy.md  プロジェクト設定の索引（70_feature_loop を含む）
docs/rules/project/20_workflow.md        工程、承認を置く位置、2つの進め方の位置づけ
docs/rules/project/70_feature_loop.md    オートモードの仕様正本
docs/tutorials/005_..._first_feature.md  オートモードを一周する体験
docs/tutorials/010〜040                   マニュアルモードで工程を1つずつ進める体験
docs/cli_text_masker/README.md           実AI実行履歴例の位置づけと注意
quality/README.md                        検証記録とレビュー結果の集約（Gate記録との役割差を明示）
tools/README.md                          runner の使い方の正本
```

## 残している歴史的旧情報

| 何が | どこに | なぜ |
|---|---|---|
| `gate_record/v1`、旧モデル field、「下流進行承認」、`tasks.md` と Gate の食い違い | `docs/cli_text_masker/` | **実AI実行履歴例。** 当時の記録として保存。README で明示 |
| `role_fixed` / `role_design` 等の削除済み概念、`G0`、`cli_mask_rework` / `cli_uppercase_text` への言及 | `docs/context/work_notes/` | **当時の判断・検証の記録**。書き換えない |
| 旧AI作業ログ | `docs/context/ai_work_logs/` | **旧方式として凍結済み**と明記されている |
| 却下案 | `docs/context/rejected_verbose_option.md` | 却下の記録 |
| 過去のテスト件数など | 各 `25_review_result.md` / `12_command_review_result.md` | 当時のレビュー結果という管理記録 |
| `G0` という文字列 | `tests/tools/test_feature_runner.py` | **旧 stage を残さないことを検査するテスト**。含むのが正常 |

## テスト結果

```text
削除前: 257 passed
削除後: 251 passed
差:     −6（tests/cli_mask_rework/ の6件のみ）
```

**FAIL 0件。** 削除対象以外のテストは1件も減っていません（`cli_text_masker` の6件は残存）。

## リンク・参照確認

- 変更した Markdown のローカルリンク：**全件実在**（機械検証）
- 削除したサンプルへの参照：**現行資料・コード・tests・設定から0件**
- Python import・tests 参照：**壊れなし**（251 passed）

## 自己レビュー

| # | 観点 | 結果 |
|---|---|---|
| 1 | 初見の人はオートモードを最初の経路として理解できるか | **OK。** README の流れの図が最初、`docs/README` / `tutorials/README` も先頭がオートモード |
| 2 | マニュアルモードも現役と理解できるか | **OK。** README / docs/README / overview / how_to_use_prompts / 20_workflow / tutorials/README / 010・020 で明記 |
| 3 | 新規 feature でも manual を選べると分かるか | **OK。** 5文書で「新規 feature でも利用できる」と明記 |
| 4 | `20_spec.md` が feature 開発の最初の入力だと分かるか | **OK。** README の図、005 の「初期状態」節 |
| 5 | 新規 command/app の場合だけ `10_overview.md` も先に必要と分かるか | **OK。** 005 の状況別の表（Phase 4 で追加） |
| 6 | CP1 が仕様承認だと一貫しているか | **OK。** 全文書一致 |
| 7 | 「下流進行承認」が現在仕様として残っていないか | **OK。** 現行資料0件。残るのは `cli_text_masker`（履歴例、README で明示） |
| 8 | auto の実装開始条件が manual と混ざっていないか | **OK。** 6文書で同一文言 |
| 9 | Worker / Reviewer の役割が正しいか | **OK。** 入口は `run_stage` / `review_stage`、委譲先は stage 設定に限る、と統一 |
| 10 | Reviewer 単独実行と矛盾する説明がないか | **OK。** 「交互に起動」を全廃し、`70_feature_loop` / `prompts/README` / `20_workflow` に単独実行を明記 |
| 11 | Gate と quality を混同していないか | **OK。**「Gate記録は `quality/` へ自動で集約されません」と明記 |
| 12 | `cli_text_masker` を現在仕様の模範例と誤認しないか | **OK。** README 冒頭で否定、README.md では「サンプル」表と別枠の「実行例」節 |
| 13 | masker の旧情報が、履歴として残していると分かるか | **OK。** README に4項目の表と「なぜ直さないのか」 |
| 14 | rework / uppercase の削除で参照切れがないか | **OK。** 現行資料0件、251 passed |
| 15 | 履歴を現在仕様へ書き換えていないか | **OK。** work_notes / gates / ai_work_logs / cli_text_masker の成果物は未変更 |
| 16 | AIに README 等を読ませても旧マニュアル工程だけへ引っ張られないか | **OK。** 入口5文書すべてでオートモードが先。旧承認方式を標準とする記述なし |
| 17 | 刷新後に、AIが現在の正本へ到達できるか | **OK。** `AGENTS.md` → `00_project_policy.md`（**Phase 4 で `70_feature_loop.md` を索引へ追加**）→ 正本 |
| 18 | Phase 1〜5 の目的がすべて満たされたか | **OK。** 下記 |

### Phase 1〜5 の目的達成状況

| Phase | 目的 | 結果 |
|---|---|---|
| 1 | 明確な矛盾の除去 | 完了。AIが古い規則で誤判断する経路を除去 |
| 2A | README のV2化 | 完了。オートモードを表玄関に |
| 2B | 入口文書への横展開 | 完了。5文書から正本へ到達可能 |
| 3 | workflow の位置づけとチュートリアル | 完了。005 新設、既存4本の位置づけ明示 |
| 4 | concept / quality / 用語、サンプル調査 | 完了。判断材料を提示 |
| 5 | サンプル整理と最終整合 | 完了。本ファイル |

## Phase 5 完了判定

**完了。**

- サンプル3件の人間判断を反映（masker=履歴例として残す＋README追加、rework / uppercase=削除）
- 削除前に必要な事実を work_notes へ記録
- 「交互に起動」を現行資料から全廃
- 横断検索を A〜E で分類し、**D は全修正、E は0件**
- `review_prompt_integrity.md` の観点で静的整合レビューを実施（**実AI未実施を明示**）
- テスト 251 passed（削除分 −6 のみ）、リンク・参照切れなし

## commit 前の状態

**まだ commit / push していません。** 人間の差分確認が残っています。

## 次に行うこと

1. **人間が Phase 5 の差分を確認する**
2. commit する
3. 必要なら、ファイルを変更しない実行設定で `review_prompt_integrity.md` の実AIレビューを行う
4. 必要なら、005 チュートリアルの実AI一周検証を独立した作業として行う
