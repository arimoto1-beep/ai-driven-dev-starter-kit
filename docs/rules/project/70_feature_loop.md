# project: feature オートモード（収束ループ）

## このファイルの目的

feature 単位の新規開発を、AIレビューと修正の収束ループで進める**オートモード**の設定を定めます。
stage、Gate、判定値、baseline、役割ごとの変更範囲、モデル役割、レビュー独立性、記録の場所を、このファイルが正本とします。

`tools/feature_runner.py` は、このファイルの「runner 設定ブロック」を読んで動作します。
**ルール文書と設定を同じファイルに置くことで、正本を1つに保ちます。**

## このファイルを読む作業

- `prompts/run_stage.md`（Worker）
- `prompts/review_stage.md`（Reviewer）
- オートモードで実装を行う作業
- Gate記録を読む作業
- モデル割り当てを変更するとき

## このファイルに含めないもの

- 収束ループを許す上位原則、baseline の概念 → `docs/rules/core/20_approval_and_review.md`
- `GO` / `条件付きGO` / `STOP` の定義 → 同上
- レビュー結果の評価値（`OK` など4値） → `25_review_policy.md`
- マニュアルモードの標準工程 → `20_workflow.md`
- 成果物の配置と分類 → `10_document_structure.md`
- 各 stage で使う個別プロンプトの手順 → 対応する `prompts/*.md`

---

## オートモードとマニュアルモード

| モード | 進め方 | 使うもの |
|---|---|---|
| **マニュアルモード** | 人間が個別プロンプトを1つずつ実行する（従来どおり） | `prompts/create_*.md`、`prompts/implement_*.md`、`prompts/review_*.md` |
| **オートモード** | runner が Worker と Reviewer を交互に起動し、Gate で判定する | `tools/feature_runner.py`、`prompts/run_stage.md`、`prompts/review_stage.md` |

- **既存の個別プロンプトは、マニュアルモードとしてそのまま維持します。** オートモードの導入で廃止しません。
- オートモードの Worker は、**手順を自分で定義せず、既存の個別プロンプトへ委譲します。** 成果物の作り方の正本は、引き続き個別プロンプトです。
- 途中でマニュアルモードへ降り、その後オートモードへ復帰できます。Reviewer は常に現在のファイルを読み直すため、人間が手を入れた状態でも判定できます。

---

## stage と Gate

```text
G0（要求確定）      → AI Gate
CP1（上流設計）     → Human Gate ... 下流進行承認
G2（詳細設計・テスト設計） → AI Gate
CP3（実装・テスト） → Human Gate ... 受け入れ判断
```

| stage | 主な成果物 | Gate種別 | Gate の問い |
|---|---|---|---|
| `G0` | `20_spec.md` | AI | 業務意図を発明せずに、要求を導出できるか |
| `CP1` | `21_design.md`、`22_flow.md` | **人間** | この上流設計を前提として、下流工程へ自動で進めてよいか |
| `G2` | `23_test_plan.md`、`24_review_checklist.md` | AI | 実装AIが独自の仕様判断を追加せずに、コードとテストを書けるか |
| `CP3` | 実装、テスト、`25_review_result.md` | **人間** | この feature を完成成果物として受け入れてよいか |

AI Gate は `PASS` のとき人間を止めません。`BLOCKED` または `RETURN` のときだけ人間へ渡します。

### CP1 は実装着手承認ではありません

**CP1 の人間承認は「下流進行承認」です。** CP1 の時点では、詳細設計・テスト設計・テストパターンがまだ存在しません。
人間が承認しているのは、上流設計の方向・責務分割・トレードオフであり、「詳細設計とテスト設計を確認したうえで実装を承認した」ではありません。

**実装開始条件は、次の2つがともに成立することです。**

1. 最新の CP1 Gate記録に、人間による**下流進行承認**のチェックがある
2. 最新の G2 Gate記録の `verdict` が `PASS` である

どちらか一方だけでは実装へ進みません。詳細は「実装開始条件」の節を参照してください。

---

## Gate 判定値

`verdict` は次の4値です。**この値は、次工程移行判定（`GO` / `条件付きGO` / `STOP`）を置き換えるものではありません。** 両方を Gate記録へ記録します。

| `verdict` | 意味 | `next_step` | 次の処理 |
|---|---|---|---|
| `PASS` | 収束済み。人間判断を要する項目がない | `GO` または `条件付きGO` | 次 stage へ。Human Gate なら承認待ちで停止 |
| `RETURN` | 問題が、通過済み Gate で baseline 化した成果物にある | `STOP` | `return_to` の stage から再実行 |
| `BLOCKED` | AIだけでは決められない | `STOP` | 理由を提示して停止 |
| `IN_PROGRESS` | 収束ループの途中（Gate判定はまだ出ていない） | 記載しない | Worker を `mode: fix` で起動し、再レビューする |

`条件付きGO` とする場合は、`docs/rules/core/20_approval_and_review.md` の6項目をすべて Gate記録へ明記します。

### `blocked_reason`

| 値 | 意味 |
|---|---|
| `business_decision` | 業務意図の決めが必要 |
| `tradeoff` | 複数案があり、選好は人間の領域 |
| `risk_acceptance` | リスクを受容するかの判断 |
| `non_convergence` | 収束ループまたは差し戻しが上限に達した |
| `guard_violation` | 変更範囲または保証範囲のガードに触れた |
| `missing_info` | 外部情報が不足している |
| `state_error` | 状態遷移を解決できない、または AI の実行が異常終了した |

### runner が作成する Gate記録

**runner 自身が処理の継続を禁止した場合も、正式な Gate記録を新規作成します。**
画面出力ではなくファイルが正式記録であるため、停止の事実を画面だけに残しません。

| 停止の原因 | `blocked_reason` |
|---|---|
| Reviewer が変更範囲に違反した | `guard_violation` |
| 収束ループが `max_rounds` に達した | `non_convergence` |
| 差し戻しが `max_returns_per_gate` に達した | `non_convergence` |
| 状態遷移を解決できない（`verdict` / `return_to` / `gate` が不正、承認見出しの欠落） | `state_error` |
| Worker または Reviewer が異常終了した | `state_error` |

- runner が作成した記録は `recorded_by: runner` を持ちます。Reviewer が作成した記録は `recorded_by: reviewer` です
- **既存の確定記録は書き換えません。** 新しい記録として追加します
- 原因を解消して再実行すると、さらに新しい記録が作成されます

なお、Worker の変更範囲違反は runner が Reviewer へ渡し、**Reviewer が** `BLOCKED(guard_violation)` として記録します。Worker の違反は成果物の状態に関する判断を伴うためです。

### `return_to`

`RETURN` のとき、戻り先の stage 名（`G0` / `CP1` / `G2`）を記録します。
戻り先の判定基準は1つです。**その修正が、通過済み Gate で baseline 化した成果物に触る必要があるか。**

| 触る必要があるもの | 判定 |
|---|---|
| 現在 stage の生成・更新対象だけ | stage 内で修正（Gate判定に出さない） |
| `23_test_plan.md`、`24_review_checklist.md` | `RETURN(G2)` |
| `21_design.md`、`22_flow.md` | `RETURN(CP1)` |
| `20_spec.md` の要求そのもの | `RETURN(G0)` |
| 業務上どちらが正しいか決められない | `BLOCKED(business_decision)` |

同じ Gate へ `max_returns_per_gate` 回を超えて差し戻された場合は、`BLOCKED(non_convergence)` として人間へ渡します。

---

## stage × role の変更範囲

**変更してよい範囲は、stage だけでは決まりません。役割（Worker / Reviewer）ごとに定義します。**

`<F>` は対象機能フォルダ（`docs/<command_or_app_name>/features/<feature_name>/`）を表します。

| stage | role | 生成・更新してよい（未baseline） | baseline 化済み（変更不可） |
|---|---|---|---|
| `G0` | Worker | `<F>/20_spec.md`、`<F>/tasks.md` | — |
| `G0` | Reviewer | `<F>/gates/` のみ | 上記以外すべて |
| `CP1` | Worker | `<F>/21_design.md`、`<F>/22_flow.md`、`<F>/tasks.md` | `<F>/20_spec.md` |
| `CP1` | Reviewer | `<F>/gates/` のみ | 上記以外すべて |
| `G2` | Worker | `<F>/23_test_plan.md`、`<F>/24_review_checklist.md`、`<F>/tasks.md` | `20_spec.md`、`21_design.md`、`22_flow.md` |
| `G2` | Reviewer | `<F>/gates/` のみ | 上記以外すべて |
| `CP3` | Worker | `src/<app>/features/`、`tests/<app>/` | `20_spec.md`〜`24_review_checklist.md` |
| `CP3` | Reviewer | `<F>/gates/`、**`<F>/25_review_result.md`** | 上記以外すべて |

### Reviewer が `25_review_result.md` を書くこと

CP3 の Reviewer だけは、Gate記録に加えて `25_review_result.md` を作成・更新します。
これは既存の feature 単体レビュー結果であり、`tools/quality_report.py` の集計対象です。

**これは「レビューAIは成果物を修正しない」という原則と矛盾しません。**

- `25_review_result.md` は**レビュー結果を記録するファイル**であり、レビュー対象の成果物ではありません
- core の「レビュー中・調査中は、**レビュー結果を記録するファイル以外を**変更しません」に沿っています
- Reviewer は、いかなる stage でも設計書・フロー・テスト計画・実装・テストコードを変更しません

### 2つの記録の役割分担

| ファイル | 役割 | 上書き |
|---|---|---|
| `25_review_result.md` | feature 単体レビューの**最終結果**（従来どおり） | する |
| `<F>/gates/<記録>.md` | その Gate 実行の**経過**（FINDING、修正、収束、判定） | **しない** |

役割が違うため、重複ではありません。

---

## Gate記録

### 配置と命名

```text
docs/<command_or_app_name>/features/<feature_name>/gates/
  0001_20260822T161400_g0.md
  0002_20260822T163000_cp1.md
  0003_20260822T171000_g2.md
  0004_20260822T180000_cp3.md
  0005_20260822T183000_g2.md
```

- 形式は `<連番4桁>_<タイムスタンプ>_<stage小文字>.md`
- 連番は feature 内で単調増加します。**名前順が実行順と一致することを保証します**
- タイムスタンプは Gate 実行の開始時刻（`%Y%m%dT%H%M%S`）
- stage ごとのサブディレクトリは作りません
- 同名が存在する場合は末尾に `_2`、`_3` を付けます。**既存ファイルを上書きしません**

### immutable の境界

- `verdict: IN_PROGRESS` の間だけ、同じファイルへラウンドを追記します
- **`PASS` / `RETURN` / `BLOCKED` のいずれかを書いた時点で immutable です。** 以後は書き換えず、新しい記録を作ります
- 例外は人間確認欄です。**人間だけ**が、確定後の記録へチェックと回答を記入します

### front matter

**フラットな `key: value` のみを使います。入れ子とリスト構文を使いません。** リストはカンマ区切り、空値は未設定を表します。
この制約により、runner は外部ライブラリなしで front matter を読めます。

**runner は Markdown 本文を解析しません。** 状態遷移に使うのは front matter だけです。本文は人間向けです。

記録する項目は `docs/templates/gate_record_template.md` を参照してください。

### 因果の追跡

| 目的 | 使う情報 | 使う主体 |
|---|---|---|
| 次に何をするか | `verdict`、`return_to`（**全stage横断で最新の1件**） | runner |
| なぜ再実行されたか | `triggered_by`、`triggered_by_record` | 人間、`--history` |
| どの記録を置き換えたか | `supersedes` | 人間、`--history` |

**runner は stage 別の最新ではなく、全stage横断で最新の1件を読みます。** stage 別に読むと、`RETURN` の直後に差し戻し前の古い `PASS` を採用してしまいます。

`RETURN` の後は、通常の stage 順で再開します。`RETURN(CP1)` なら CP1 → G2 → CP3 と進みます。上流が変わった以上、下流も再検証が必要だからです。**特別な復帰経路を設けません。**

### 人間コメントからの再判定

Human Gate の記録に**未処理の人間コメント**（「気になる点」の自然文）がある場合、runner は**承認待ちより先に Reviewer を再起動します。**

```text
CP3 が PASS → 人間が「気になる点」へ自然文を記入 → runner を再実行
  ↓
Worker は起動しない。Reviewer だけが、現在の成果物とコメントを読む
  ↓
根拠つきで分類する
  ├─ 現 stage 内で修正できる → FINDING として記録し、収束ループへ
  ├─ RETURN(G2) / RETURN(CP1) / RETURN(G0)
  └─ BLOCKED(business_decision)
  ↓
新しい Gate記録として残す（既存記録は書き換えない）
```

**処理済みかどうかは、後続記録の `triggered_by_record` が自分を指しているかで判定します。**
確定済み記録へ処理済みマークを書き込まないため、immutable を保ったまま二重処理を防げます。

人間が新しいコメントを書きたい場合は、**最新の Gate記録**の「気になる点」へ記入します。

### マニュアル介入からの復帰

途中でマニュアルモードへ降りて成果物を直した場合、**Worker を再実行すると人間の修正が上書きされる可能性があります。**
そのため、Worker を起動せず現在の成果物をそのまま Reviewer へ渡す入口を用意します。

```bash
python tools/feature_runner.py --feature <app>/<feature> --review-current G2
```

- **Worker を起動しません。** 現在の成果物をそのまま Reviewer が読み直します
- Gate記録に `mode: manual`、`triggered_by: MANUAL` が残り、マニュアル介入からの復帰であることを追跡できます
- その stage の直近の確定記録が `supersedes` に入ります
- 以降は通常のオートモードへ戻ります

---

## 実装開始条件

`24_review_checklist.md` に「実装開始条件」の節を置き、どちらの方式で条件を満たすかを記録します。
**この記載により、後から読む人が、どちらの方式で実装が開始されたかを判別できます。**

| 方式 | 実装開始条件 | 承認の記録先 |
|---|---|---|
| `manual` | `24_review_checklist.md` の「実装着手承認欄」が全項目チェック済み | `24_review_checklist.md` |
| `auto` | **CP1 の下流進行承認 AND 最新 G2 Gate記録の `verdict: PASS`** | `<F>/gates/` の CP1 / G2 Gate記録 |

- 既定は `manual` です。**方式を記載していない既存の `24_review_checklist.md` は `manual` として扱います**（後方互換）
- `auto` の場合、「実装着手承認欄」は使用しません。未チェックのまま残ることが正常です
- 方式そのものを記載するのはAIです。これは事実の記録であり、承認ではありません
- **AIは、どちらの方式でも承認欄にチェックを入れません**

---

## モデル役割

| 役割 | 使う場面 | 既定のクラス |
|---|---|---|
| `design` | G0 / CP1 / G2 の Worker | `standard` |
| `build` | CP3 の Worker | `cheap` |
| `review` | すべての stage の Reviewer | `standard` |

モデルクラスは `cheap` / `standard` / `strong` の3つです。
**ルール文書とプロンプトには、実際のモデル名を書きません。** 実モデルは下記の設定ブロックだけに書きます。

解決の流れは `stage → role → model class → 実モデル` です。runner がこれを解決し、Worker / Reviewer を起動します。
**プロンプト自身がモデルを変更しません。モデルの選択は起動側の責務です。**

### 使い分けの例

プリセットという仕組みは設けません。設定ブロックの `role_*` を3行書き換えるだけです。

| 使い分け | `role_design` | `role_build` | `role_review` |
|---|---|---|---|
| コスト優先（低リスク、試作） | `cheap` | `cheap` | `standard` |
| **標準（既定）** | `standard` | `cheap` | `standard` |
| 品質優先（難易度・影響が大きい） | `strong` | `standard` | `strong` |

1回だけ変える場合は、runner の `--role-design strong` などで上書きします。
**実際に使ったクラスは Gate記録へ必ず記録します。**

---

## レビュー独立性

| レベル | 構成 | `review_independence` |
|---|---|---|
| L0 | 同一セッションでレビューする | `same_context` |
| L1 | 同一モデル・別プロセス（**既定**） | `separate_context` |
| L2 | 別ベンダーのAI | `separate_vendor` |

- runner は Worker と Reviewer を**毎回別プロセスとして起動します。** 会話履歴や思考過程を引き継ぐ経路が存在しないため、既定で L1 が成立します
- **Reviewer へ渡してよいもの**：正式資料、現在の成果物、Gate記録、レビュー観点、必要な設定
- **渡さないもの**：Worker の会話履歴、思考過程、設計意図の口頭説明、「問題ありません」という申し送り
- **判定はレベルに依存しません。** L1 でも `PASS` を出せます。複数AIサービスの契約を必須にしません
- L2 を使う場合も `prompts/review_stage.md` をそのまま渡します。判定基準はプロンプト内で自己完結させます

---

## 保証範囲の維持

**テストケース件数の単調性では判定しません。** parameterized test への統合や重複テストの整理で、件数は正当に減ります。

守るのは次の対応です。

| 指標 | 意味 |
|---|---|
| `req_total` | `20_spec.md` の必須要件（REQ-ID）の総数 |
| `req_covered` | いずれかの設計要素・テスト観点へ対応づいている要求の数 |
| `viewpoint_total` | `23_test_plan.md` のテスト観点（観点ID）の総数 |
| `viewpoint_covered` | 対応するテストを持つ観点の数 |

**これら4つの値が、直前の Gate記録より減っている場合、AI単独で進めません。** `BLOCKED(guard_violation)` として人間へ渡します。

| 操作 | テスト件数 | 観点カバレッジ | 判定 |
|---|---|---|---|
| 3件を parameterized test へ統合 | 3 → 1 | 3 → 3 | 通る |
| 重複テストを整理して削除 | 5 → 4 | 4 → 4 | 通る |
| 落ちるテストを削除 | 5 → 4 | 5 → 4 | `BLOCKED` |
| アサーションを消して緑にする | 5 → 5 | 5 → 4 | `BLOCKED` |
| 要求を1つ削除 | — | 14 → 13 | `BLOCKED` |

---

## 変更範囲のガード

runner は、Worker と Reviewer の**実行直前と実行直後**のリポジトリ状態を比較し、**その実行によって発生した変更だけ**を判定対象にします。

- 実行前から存在する未コミット変更を、その実行の変更と誤認しません
- **実行前から変更されていたファイルへの追加変更も検出します**（パス集合ではなく内容ハッシュで比較するため）
- 既存の未コミット変更を壊しません（stash も reset も行いません）

範囲外の変更を検出した場合、runner はその一覧を Reviewer へ渡します。Reviewer は `guard_violations` を記録し、`BLOCKED(guard_violation)` とします。
**runner は自動で変更を巻き戻しません。** 巻き戻すかどうかは人間が判断します。

このガードは粗い網です。個々のプロンプトの `## 変更してはいけないファイル` を置き換えるものではありません。**両方を満たす必要があります。**

---

## runner 設定ブロック

`tools/feature_runner.py` は、下のフェンス付きブロック（言語指定 `feature_loop`）だけを読みます。

- 1行1件の `key = value` です。入れ子とリスト構文を使いません
- `#` で始まる行はコメントです
- リストはカンマ区切りです
- `{app}` はコマンド/アプリ名、`{feature}` は feature 名、`{feature_dir}` は対象機能フォルダに置換されます
- `tools/feature_loop.local` が存在する場合、同じ形式で上書きします（`.gitignore` 対象）

```feature_loop
# --- 役割へのモデルクラス割り当て（コスト調整はここを変える） ---
role_design    = standard
role_build     = cheap
role_review    = standard

# --- モデルクラスへの実モデル割り当て（利用者が記入する。ここ以外にモデル名を書かない） ---
model_cheap    = <記入してください>
model_standard = <記入してください>
model_strong   = <記入してください>

# --- AI CLI の起動コマンド（カンマ区切りの argv テンプレート。shell を経由しない） ---
# {instruction} に指示文、{model} に実モデル名が入る。
# 例: claude,-p,{instruction},--model,{model}
ai_command     = <記入してください>

# --- ループ制御 ---
stages               = G0, CP1, G2, CP3
human_gates          = CP1, CP3
max_rounds           = 3
max_returns_per_gate = 3

# --- レビュー独立性（Gate記録へ記録する値） ---
review_independence  = separate_context

# --- 人間確認欄の見出し（runner が承認状態と自然文を読む位置） ---
# human_gates に含めた stage には、対応する approval_heading_* が必要。
approval_heading_cp1 = 下流進行承認（CP1 のみ）
approval_heading_g2  = 実装工程進行承認（G2 を Human Gate にした場合のみ）
approval_heading_cp3 = 受け入れ判断（CP3 のみ）
human_note_heading   = 気になる点（任意）

# --- stage ごとの Worker の役割 ---
stage_g0_worker_role  = design
stage_cp1_worker_role = design
stage_g2_worker_role  = design
stage_cp3_worker_role = build
reviewer_role         = review

# --- stage × role の生成・更新対象 ---
stage_g0_worker    = {feature_dir}/20_spec.md, {feature_dir}/tasks.md
stage_g0_reviewer  = {feature_dir}/gates/
stage_cp1_worker   = {feature_dir}/21_design.md, {feature_dir}/22_flow.md, {feature_dir}/tasks.md
stage_cp1_reviewer = {feature_dir}/gates/
stage_g2_worker    = {feature_dir}/23_test_plan.md, {feature_dir}/24_review_checklist.md, {feature_dir}/tasks.md
stage_g2_reviewer  = {feature_dir}/gates/
stage_cp3_worker   = src/{app}/features/, tests/{app}/
stage_cp3_reviewer = {feature_dir}/gates/, {feature_dir}/25_review_result.md

# --- stage ごとに Worker が委譲する既存プロンプト（マニュアルモードの正本） ---
stage_g0_prompts   = prompts/create_feature_spec.md
stage_cp1_prompts  = prompts/create_function_design.md, prompts/create_function_call_flow.md
stage_g2_prompts   = prompts/create_test_design.md, prompts/create_review_checklist.md
stage_cp3_prompts  = prompts/implement_feature.md
```

### 設定を変更する場合の注意

- `stages` と `human_gates` を変更する場合、`docs/rules/core/20_approval_and_review.md` の承認境界を満たせるか確認してください。**core の承認原則を緩和できません**
- `human_gates = CP1, G2, CP3` と書くと、G2 でも人間が停止します。慎重に運用したい場合の設定です。**この設定を使う場合、`approval_heading_g2` が必要です**（既定で記入済み）。Gate記録テンプレートにも対応する承認欄があります
- **`human_gates` に stage を追加する場合は、対応する `approval_heading_<stage小文字>` と、Gate記録テンプレートの承認欄を同時に用意してください。** 欠けている場合、runner は `BLOCKED(state_error)` として停止します
- `stage_*_worker` / `stage_*_reviewer` を広げる場合、上記「stage × role の変更範囲」の表と、対応する `prompts/*.md` の `## 変更してよいファイル` も同時に更新してください
- `model_*` と `ai_command` は利用者の環境に依存します。**リポジトリへコミットしたくない場合は `tools/feature_loop.local` へ書いてください**

---

## 変更する場合の注意

- **オートモードの導入を理由に、マニュアルモードの個別プロンプトを削除しないでください。**
- Gate記録を上書き方式へ変更しないでください。工程を後から追えることが、この方式の目的です。
- `verdict` の4値を増減する場合、`tools/feature_runner.py` の分岐と `docs/templates/gate_record_template.md` も同時に変更してください。
- `GO` / `条件付きGO` / `STOP` は core 固定です。`verdict` で置き換えられません。

---

## 関連するルール

- 収束ループを許す上位原則、baseline の概念 → `docs/rules/core/20_approval_and_review.md`
- Gate記録の配置と分類 → `10_document_structure.md`
- 承認欄の場所と更新権限 → `50_ai_permissions.md`
- レビュー結果の評価値 → `25_review_policy.md`
- マニュアルモードの標準工程 → `20_workflow.md`
- Gate記録のひな形 → `docs/templates/gate_record_template.md`
- runner の使い方 → `tools/README.md`
