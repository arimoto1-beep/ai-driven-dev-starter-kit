# 実AI検証の準備

**AIはローカル設定を変更していない。実AI呼び出しも行っていない。**
以下は、人間が実AI検証を始める前に行う操作である。

## 現在の状態

このリポジトリは、いま**従来のモデル固定設定（`role_fixed`）で動作する。**

```text
$ python tools/feature_runner.py --feature <app>/<feature> --dry-run
従来のモデル固定設定（role_*）で動作しています。
role_* を削除すると、モデル自動選択になります。
```

理由は `tools/feature_loop.local` に次の3行が残っているためである。

```text
role_design    = standard
role_build     = cheap
role_review    = standard
```

`docs/rules/project/70_feature_loop.md` の設定ブロックからは `role_*` を削除済みだが、
`read_config()` はローカル設定をマージするため、こちらが残っていると従来方式になる。

## 変更する箇所

`tools/feature_loop.local` から **`role_*` の3行だけ**を削除する。

削除後の内容は次のようになる（`model_*` と `ai_command` はそのまま）。

```text
model_cheap    = claude-haiku-4-5
model_standard = claude-sonnet-5
model_strong   = claude-opus-5

ai_command     = claude,-p,{instruction},--model,{model},--permission-mode,acceptEdits,--allowedTools,Bash(python -m pytest *)
```

- このファイルは `.gitignore` 対象なので、削除してもリポジトリの差分には出ない
- `base_level_*` をここへ書く必要はない。ルール文書の設定ブロックにある
- 元へ戻したい場合は3行を書き戻せばよい

## 変更後の確認

```bash
python tools/feature_runner.py --feature <app>/<feature> --status
```

冒頭の従来方式の通知が消え、次の行が出れば自動選択になっている。

```text
モデル選択: auto（feature_difficulty=normal）
```

実行前の選択結果は `--dry-run` で確認できる。

```bash
python tools/feature_runner.py --feature <app>/<feature> --dry-run
```

```text
モデル選択: auto（feature_difficulty=normal）
Worker   base=2  class=standard  model=claude-sonnet-5
  使用prompt: prompts/create_function_design.md, prompts/create_function_call_flow.md
Reviewer base=2  class=standard  model=claude-sonnet-5
  使用prompt: prompts/review_stage.md
```

## 検証したい点

### 1. CP1 Reviewer が難易度を判定・記録するか（最重要）

**ここだけが実AIでしか確認できない。** 他はすべて自動テストで固定済みである。

```bash
python tools/feature_runner.py --feature <app>/<feature> --spec-review
```

生成された CP1 Gate記録の front matter を確認する。

```yaml
schema: gate_record/v2
feature_difficulty: normal        # easy / normal / hard のいずれかが入っているか
reviewer_model_class: standard
model_selection: auto
```

確認したいこと：

- 3値以外の値（`medium` など）を書いていないか
- 判定基準を勝手に細分化していないか
- 難易度が `verdict` の判定に影響していないか（`hard` でも `PASS` になり得る）

### 2. 難易度が製造 stage へ引き継がれるか

CP1 を承認したあと G1 を実行し、G1 Gate記録の `feature_difficulty` が
**CP1 と同じ値**であることを確認する。再判定されていたら設計どおりでない。

### 3. 難易度に応じてクラスが変わるか

難易度の違う feature を複数用意し、`--dry-run` で選択結果を比べる。

| feature | G1 Worker | CP3 Worker | Reviewer |
|---|---|---|---|
| `easy` | cheap | cheap | cheap |
| `normal` | standard | cheap | standard |
| `hard` | strong | standard | strong |

### 4. `easy` feature でレビューが機能しているか

下限ルールを設けていないため、`easy` では Reviewer も `cheap` になる。
`findings_total` が常に 0 件、`review_rounds` が常に 1 のような状態が続く場合、
下限ルールの追加を検討する材料になる（`04_rejected_options.md` の3を参照）。

### 5. 既存 feature が壊れていないこと

`feature_difficulty` を持たない既存の CP1 記録は `normal` として扱われ、
**従来と同じクラスが選ばれる**（ファイルを変更しない形で確認済み。`02_implementation.md`）。

既存の `gate_record/v1` 記録はそのまま読める。書き換えていない。

## 注意

- 既存の Gate記録は書き換えない。新しい記録から `gate_record/v2` になる
- 1つの feature の中に `v1` と `v2` の記録が混在するのは正常である
- 検証で作られた Gate記録も履歴として残す（削除・整理しない）

---

# 実施結果（2026-08-30）

**ここから下は、人間が実施した実AI検証の結果である。** 上記は実施前の準備手順であり、変更していない。

検証用に `easy` / `hard` の feature を作成し、CP1 から CP3 まで通した。
**検証用 feature は、この記録の更新後に削除する予定である**（人間の判断）。
そのため Gate記録が失われても事実が残るよう、確認できた値をここへ書き写す。

## easy の feature

| 実行対象 | 選ばれたクラス | 設計上の期待 |
|---|---|---|
| CP1 Reviewer | standard | standard（CP1 は難易度未確定のため `normal` 扱い） |
| G1 Worker / Reviewer | cheap / cheap | cheap / cheap |
| G2 Worker / Reviewer | cheap / cheap | cheap / cheap |
| CP3 Worker / Reviewer | cheap / cheap | cheap / cheap |

- CP1 Reviewer が `feature_difficulty: easy` を判定・記録した
- Human Gate まで到達し、最終的に `done` となった

**すべて設計どおりである。**

## hard の feature

| 実行対象 | 選ばれたクラス | 設計上の期待 |
|---|---|---|
| CP1 Reviewer | standard | standard |
| G1 Worker / Reviewer | strong / strong | strong / strong |
| G2 Worker / Reviewer | strong / strong | strong / strong |
| CP3 Worker / Reviewer | standard / strong | standard / strong |

- CP1 Reviewer が `feature_difficulty: hard` を判定・記録した
- **仕様を修正して CP1 を再レビューした際も `hard` と判定された**
- G2 で、**エスケープ対象が `\` 自身の場合の境界ケース不足を strong Reviewer が1件検出**した
- その指摘は同一 G2 内で `fix` され、2ラウンドで `PASS` した
- feature 単体のテスト 21 件が PASS
- Human Gate まで到達し、最終的に `done` となった

**すべて設計どおりである。** 特に次の2点が実データで確認できた。

- 難易度が製造 stage（G1 / G2 / CP3）へ正しく引き継がれる
- CP3 Worker だけが `standard`（基礎レベル 1 + 1）に下がり、Reviewer は `strong` のまま

## 最終回帰試験

```bash
python -m pytest --basetemp=.pytest_tmp
294 passed
```

（検証用 feature のテストを含む件数。検証用 feature の削除後は件数が減る）

## 検証中に気づいた点

`docs/templates/24_review_checklist_template.md` の「CP1 の下流進行承認」という用語が、
現行ルールの「CP1 の仕様承認」と一致していない。

**今回は未修正。** モデル選択とは別件である。`06_deferred.md` に記載した。
