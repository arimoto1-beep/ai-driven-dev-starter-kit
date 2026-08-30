# Phase 2B 実施結果：入口文書への横展開（2026-08-30）

Phase 2A で確定した README の説明方針を、他の入口文書へ横展開した記録です。

**`01_audit.md` / `02_decisions.md` / `03_execution_plan.md` / `04_phase1_result.md` /
`05_phase2a_readme_result.md` は書き換えていません。**

---

## 1. README の微修正（2点）

Phase 2A の構成は維持し、人間の指摘2点だけを直しました。

### 修正1：人間の判断点が2か所しかないように読める

```diff
- **人間が必ず止まって判断するのは、仕様承認（CP1）と受け入れ（CP3）の2か所**です
+ **通常フローで必ず人間が承認・受け入れを行う固定ポイントは、仕様承認（CP1）と受け入れ（CP3）の2か所**です。
+ このほかにも、AIが判断できない事項に行き当たった場合は人間へ渡されます
```

「固定ポイントは2か所」と「そのほかにも人間へ戻る場合がある」を分けました。
`RETURN` / `BLOCKED` という用語は出していません（Phase 2A の方針を維持）。

### 修正2：無制限に収束するように読める

```diff
- 指摘が解消するまで修正を繰り返します
+ 指摘があれば修正と再レビューを行います
```

`max_rounds` などの詳細は追加していません。

---

## 2. 変更した入口文書

### `docs/README.md`（監査 M-6）

**役割：docs 配下の案内図。**

| 変更 | 内容 |
|---|---|
| 冒頭に1文追加 | 「リポジトリ全体の目的と、feature 開発の流れそのものは `../README.md` にあります」と明記し、**この文書が案内図であることを宣言** |
| 「どこから読むか」を3グループへ再編 | 平坦な10行の表を `feature を開発する` / `構造・ルール・ひな形を知る` / `そのほか` に分割 |
| **オートモードの入口を追加** | `rules/project/70_feature_loop.md`（仕組みの正本）と `../tools/README.md`（runner の使い方）の2行を、feature 開発グループの**先頭**に配置 |
| マニュアルモードの位置づけ | 同グループ内に「工程を1つずつ進める（**新規 feature でも利用できる**）」として併記 |
| `overview.md` の役割を明示 | 「**どこに何があるか**（docs / src / tests の対応、feature 内の各文書、`gates/`、prompts の種類）」と説明を具体化 |
| 「関連する入口」 | prompt 一覧を追加。tools を「オートモードの runner を含む」と補足 |

**サンプル一覧（`コマンド／アプリの設計文書` の表）は変更していません。** 案内されていない3件
（`cli_text_masker` / `cli_mask_rework` / `cli_uppercase_text`）は追加も削除もしていません（Phase 4 の人間判断事項）。

### `docs/overview.md`（監査 H-5 の残り）

**役割：リポジトリの構造と各成果物の役割を理解する文書。**

| 変更 | 内容 |
|---|---|
| 冒頭で役割を宣言 | 「**リポジトリの構造と各成果物の役割**を人間が理解するための概要」と定義し、**流れは README、詳細仕様は `70_feature_loop.md`** へ2行のリンクで振り分けた |
| 基本構成ツリー | `features/<feature_name>/` 配下へ `gates/<連番4桁>_<タイムスタンプ>_<stage小文字>.md` を追加。ツリー直後に「オートモードで進めた場合に作成される。マニュアルモードだけで進めた feature には存在しない」と補足 |
| 各ファイルの役割 | `gates/` 配下の行を追加。**判定・承認欄・停止理由を1件1ファイルで残すこと、確定した記録は書き換えないこと**まで。ひな形と正本へリンク |
| prompts 節 | 「runner から使われる」（`run_stage.md` / `review_stage.md`）と「人間が選んで渡す」（個別 prompt）の2種類を表で整理。**`run_stage.md` が個別 prompt へ委譲すること**を明記 |
| 今回の対象範囲 | オートモード／マニュアルモードの2行の表を先頭に置き、**どちらも現役の選択肢**と明記。既存の対象一覧は「どちらの進め方でも共通」と位置づけた |

**開発フローの図は再掲していません。** README へのリンク1行で済ませています。

### `docs/how_to_use_prompts.md`（監査 M-5）

**役割：prompt をどう選び、どうAIへ渡すか。この役割は変えていません。**

| 変更 | 内容 |
|---|---|
| 「どこから始めるか」を2小節へ分割 | `オートモードの場合：人間が1本ずつ選ぶ必要はありません` と `マニュアルモードの場合：目的に合う prompt を人間が選びます` |
| オートモードの委譲図 | `feature_runner.py` → Worker(`run_stage.md`) → 各作業用 prompt / Reviewer(`review_stage.md`) の3行の図。人間が渡すのは `--feature` だけであること、委譲先は `70_feature_loop.md` の設定が決めることを記載 |
| マニュアルモードの位置づけ | 「**このドキュメントで説明するのはこちらの渡し方**」と明示し、**新規 feature でも利用できる**ことを追記。既存の「まず 010 を開く」はこの小節の中へ収まった |
| 汎用プロンプト一覧 | 「runner が渡す」／「人間が選んで渡す」の2行の表を追加。`run_stage.md` / `review_stage.md` は**人間が普段直接渡す必要がない**が単独手動実行もできる、と明記 |

**この文書を「オートモードの使い方」に作り変えていません。** 基本方針・2つの参照・保護対象との違い・
短いチャット指示の書き方・依頼例など、本来の内容はすべて維持しています。

### `AGENTS.md`（監査 M-8）

**役割：AIが作業開始時に正しいルールへ到達するための入口。**

| 変更 | 内容 |
|---|---|
| 作業分類表 | 「実装・変更」行に `project/70_feature_loop.md`（**feature オートモードで進める場合は**）、「レビュー・承認」行に同（**Gate記録を読む・作る場合は**）を条件付きで追加 |
| 表の直後に1段落追加 | オートモードで進める場合**またはその可能性がある場合**に読むこと、何の正本か（stage / Gate / 判定値 / 承認位置 / 変更範囲 / Gate記録）、**バグ対応や文書修正など使わない作業では不要**であることを明記 |

**過剰な規則にしていません。** 「すべての作業で必ず読む」とは書かず、条件を付けています。
既存の読む順番（AGENTS → `00_project_policy.md` → task プロンプト → `## 必須参照ルール`）、
core / project / task の分離、「task プロンプトの `## 必須参照ルール` が正本」という原則は変更していません。

---

## 3. 文書間の役割分担（最終状態）

```text
README.md
    初見の人へ、何をするキットかと feature 開発の流れ・最初の一歩を説明する入口

docs/README.md
    docs 配下の案内図。「この目的ならこの文書へ」を示す

docs/overview.md
    リポジトリと成果物の構造説明。どこに何があり、各ファイルが何を書くものか

docs/how_to_use_prompts.md
    prompt の選び方と渡し方。オートモード（runner が渡す）と
    マニュアルモード（人間が渡す）の違いを含む

AGENTS.md
    AIが作業開始時に正しい正本へ到達するための入口

docs/rules/project/70_feature_loop.md
    オートモードの仕様正本（stage / Gate / 判定 / 停止・再開 / モデル選択）

tools/README.md
    runner の使い方の正本（コマンド、オプション、設定）
```

---

## 4. 重複を減らした箇所

| 箇所 | 対応 |
|---|---|
| `docs/overview.md` 冒頭 | 開発フローを再掲せず、**README（流れ）と `70_feature_loop.md`（詳細仕様）への2行のリンク**に置き換えた |
| `docs/README.md` 冒頭 | 目的と流れは README にあると明記し、案内図へ徹させた |
| `docs/overview.md` prompts 節 | `run_stage` / `review_stage` の説明を「runner から起動される入口」「個別 prompt へ委譲する」の2点に絞り、**使い方は `how_to_use_prompts.md`、仕組みは `70_feature_loop.md`** へリンク |
| `docs/how_to_use_prompts.md` | 委譲の仕組みを図3行にとどめ、stage ごとの委譲先は `70_feature_loop.md` の設定が決めるとしてリンク |
| `AGENTS.md` | stage / Gate の説明を一切書かず、**正本の名前と適用条件だけ**にした |

**オートモードの詳細仕様（`RETURN` / `BLOCKED` / `artifacts_hash` / `max_rounds` / モデル選択の計算式など）は、
今回変更したどの入口文書にも書いていません。**

---

## 5. 検索結果

### オートモードへの入口（対象文書での到達性）

| 文書 | `feature_runner` | `70_feature_loop` | `run_stage` | `review_stage` |
|---|---|---|---|---|
| `README.md` | 4 | 5 | 0 | 0 |
| `AGENTS.md` | 1 | 3 | 0 | 0 |
| `docs/README.md` | 0※ | 1 | 0 | 0 |
| `docs/overview.md` | 3 | 5 | 1 | 1 |
| `docs/how_to_use_prompts.md` | 2 | 1 | 2 | 2 |

※ `docs/README.md` は案内図のため、スクリプト名は書かず「オートモードの runner の使い方」として
`../tools/README.md` へリンクしています。

**5文書すべてから `70_feature_loop.md` へ到達できます。**

### 「実装着手承認」の残存（対象文書内）

| 箇所 | 扱い |
|---|---|
| `docs/overview.md:81`「末尾に実装着手承認欄を含む」 | **事実として正しい。** `auto` でも欄自体は存在し、使用しないだけ（Phase 1 で判定済み） |
| `docs/overview.md:130`（実装前承認ゲートの表） | **Phase 1 の修正結果。** `manual` / `auto` の方式差を明示済みで、そのまま維持 |

**`README.md` / `AGENTS.md` / `docs/README.md` / `docs/how_to_use_prompts.md` には0件です。**

### 旧マニュアル経路だけを標準として案内する箇所（対象文書内）

| 箇所 | 扱い |
|---|---|
| `docs/how_to_use_prompts.md:33`「まず `010_simple_calculator.md` を開いてください」 | **今回の変更で「マニュアルモードの場合」小節の中へ収まった。** マニュアルモードの入口としては正しい案内なので、そのまま維持 |
| `docs/how_to_use_prompts.md:180`「標準工程に固定されない随時利用のレビュー」 | `20_workflow.md` の「標準工程」という呼称を参照した表現。**呼称の見直しは Phase 3（M-2）** のため今回は変更せず |

---

## 6. Phase 3 以降への持ち越し

**今回は変更していません。**

| 対象 | 内容 | Phase |
|---|---|---|
| `docs/rules/project/20_workflow.md` | 「標準工程」＝マニュアルモードという呼称と節順。内容は正確（M-2）。`how_to_use_prompts.md:180` がこの呼称を参照している | 3 |
| `docs/tutorials/README.md` | 入口が 010（マニュアル）のまま。README / `how_to_use_prompts.md` からはマニュアルモードの文脈でリンクしているため現時点で矛盾はない（M-3） | 3 |
| 既存 tutorial 4本 | マニュアルモードの例としての位置づけ明示（M-3） | 3 |
| オートモードのチュートリアル新設 | 未着手（M-3） | 3 |
| サンプル3件 | `cli_text_masker` / `cli_mask_rework` / `cli_uppercase_text` の扱い。`docs/README.md` のサンプル表へ追加も削除もしていない（M-7）。Phase 1 から持ち越した「下流進行承認」の残存2件もここに含む | 4 |
| `docs/concept/ai_driven_development.md` | Worker/Reviewer 分離、Gate、仕様承認境界が未反映（M-9） | 4 |
| `quality/README.md` | Gate記録との関係に触れていない（L-1） | 4 |

### 新たに解消したもの

`05_phase2a_readme_result.md` で Phase 2B の課題として挙げた
**「README ↔ `docs/overview.md` のツリー役割分担」は、今回決めて反映しました。**

- README のツリー：**リポジトリ全体の俯瞰**。`tools/feature_runner.py` と `gates/` を含み、どこに何があるかを1画面で示す
- `docs/overview.md` のツリー：**docs 配下の成果物構造の詳細**。`common_design/` や `bugs/` を含み、各ファイルの役割表と対で読む

両者は粒度が異なるため、統合せず併存させます。

---

## 7. 判断に迷った点

### 1. `docs/README.md` のサンプル表を触るか

**触らないと判断しました。**

`docs/` には案内されていない3件がありますが、扱いは Phase 4 の人間判断事項です。
「存在するから追加する」も「案内がないから削除する」も、今回の指示で明確に禁止されています。
表は旧状態のまま維持しました。

### 2. `AGENTS.md` の「レビュー・承認」行にも追加するか

**追加しました。**

M-8 は「実装・変更」を挙げていましたが、Gate記録を読む・作る作業は「レビュー・承認」に分類されます。
task プロンプト（`review_stage.md`）が指定されていれば `## 必須参照ルール` から到達できますが、
**プロンプト指定なしで Gate記録を扱う作業では到達経路がありません。**

ただし無条件では書かず、「Gate記録を読む・作る場合は」と条件を付けました。

### 3. `docs/how_to_use_prompts.md` の「まず 010 を開く」を残すか

**残しました。**

この文はマニュアルモードの入口案内として現在も正しく、今回の変更で
「マニュアルモードの場合」小節の中に位置づけられました。
オートモードのチュートリアルが新設される Phase 3 まで、代替の入口が存在しないためです。

### 4. `docs/overview.md` に Gate記録の front matter を書くか

**書かないと判断しました。**

指示どおり Gate schema や内部フィールドは詳述せず、「判定・承認欄・停止理由を1件1ファイルで残す」
「確定した記録は書き換えない」という**役割の説明にとどめ**、ひな形（`gate_record_template.md`）と
正本（`70_feature_loop.md`）へリンクしました。

---

## 8. テスト結果

```bash
python -m pytest --basetemp=.pytest_tmp
257 passed
```

FAIL 0件。件数は Phase 2A 実施後と同じです。

`git diff --check` は空（空白エラーなし）。

**変更した5文書のリンク70件が、すべて実在することをスクリプトで確認**しました。

---

## 9. 自己レビュー（README → docs/README → docs/overview → how_to_use_prompts の順で通読）

| # | 観点 | 結果 |
|---|---|---|
| 1 | 初見でオートモードが feature 新規開発の最初の経路として見えるか | **OK。** README の流れの図が最初。`docs/README.md` は「feature を開発する」グループの先頭にオートモードを配置 |
| 2 | マニュアルモードも現役の選択肢として残っているか | **OK。** README・`docs/README.md`・`docs/overview.md`・`how_to_use_prompts.md` の4文書すべてで併記 |
| 3 | 新規 feature でマニュアルモードを使えないという誤解がないか | **OK。** `docs/README.md`「新規 feature でも利用できる」、`docs/overview.md`「新規 feature でも利用できる」、`how_to_use_prompts.md`「新しい feature を作る場合でも利用できます」 |
| 4 | README と overview が同じ説明を重複していないか | **OK。** overview は流れを再掲せずリンクへ。ツリーは粒度を分けた（上記6） |
| 5 | overview を読めば `gates/` の存在と役割が分かるか | **OK。** 基本構成ツリー・ツリー直後の補足・各ファイルの役割表の3か所 |
| 6 | prompt 利用者が auto/manual の違いを理解できるか | **OK。** `how_to_use_prompts.md` 冒頭の2小節と、プロンプト一覧の2行の表 |
| 7 | AIが `AGENTS.md` から `70_feature_loop.md` へ到達できるか | **OK。** 分類表2行＋直後の段落 |
| 8 | 詳細仕様が入口文書へコピーされすぎていないか | **OK。** `RETURN` / `BLOCKED` / `artifacts_hash` / `max_rounds` / モデル選択の計算式は、変更したどの文書にも無い |
| 9 | 古い実装着手承認方式をオートモードの標準として説明していないか | **OK。** 対象4文書に該当記述なし。`docs/overview.md` の2件は方式差を明示済み（Phase 1 の結果）か事実の記述 |

---

## 10. Phase 2B 完了判定

**完了。**

- README の微修正2点を反映した
- `docs/README.md` / `docs/overview.md` / `docs/how_to_use_prompts.md` / `AGENTS.md` の4文書を、
  それぞれの役割に沿って更新した
- 5文書すべてから `70_feature_loop.md` へ到達できる
- 同じ説明のコピーではなく、役割分担と正本へのリンクに寄せた
- 禁止された変更（`20_workflow.md` の節順、tutorial、サンプル3件、`concept/`、`quality/`、runner 実装、
  モデル選択仕様）は行っていない
- Phase 1 で変更した5ファイルの差分は維持している（再編集していない）

---

## 次に行うこと

1. 人間が Phase 2B の差分を確認する
2. Phase 3（`20_workflow.md` の位置づけ、オートモードのチュートリアル新設、既存 tutorial の位置づけ明示）へ進む
3. Phase 4 の前に、サンプル3件の扱いを人間が判断する
