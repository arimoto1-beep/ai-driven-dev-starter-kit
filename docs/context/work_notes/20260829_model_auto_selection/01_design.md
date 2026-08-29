# 確定した設計

正本は `docs/rules/project/70_feature_loop.md` の「モデル選択」である。
ここには、そこに書ききらない**なぜそうしたか**を残す。

## 全体像

```text
プロンプトの基礎レベル  +  feature 難易度  =  最終レベル
        ↓
1 → cheap ／ 2 → standard ／ 3 → strong（1〜3 へ丸める）
```

計算はこれだけである。第一段階では補正ルールを追加しない。

## feature 難易度

| 値 | 補正 |
|---|---|
| `easy` | `-1` |
| `normal` | `0` |
| `hard` | `+1` |

### 誰が、いつ判定するか

**CP1 の Reviewer が、仕様レビューの一部として1回だけ判定する。**

CP1 Reviewer はすでに `20_spec.md` 全体を読み、要求・矛盾・曖昧さ・異常系・境界条件を確認している。
そのレビュー結果から難易度を1語で答えさせる。

**モデル選択のための追加AI呼び出しは発生しない。** これが、この方式を採用した最大の理由である。

### どこに保持するか

CP1 Gate記録の front matter（`feature_difficulty`）。**新しいファイル形式も保持機構も作らない。**

読み出しには既存の `find_spec_approval(..., required_spec_hash=...)` をそのまま再利用する。
Manufacturing Preflight のために既に実装・テストされていた関数である。

```python
_, front = find_spec_approval(root, config, feature_dir,
                              required_spec_hash=file_hash(spec))
value = front.get("feature_difficulty", "")
```

### 再判定の条件

`20_spec.md` を変更すると人間の仕様承認が無効になり、再レビューで新しい CP1 記録＝新しい難易度になる。
**この挙動は既存の spec baseline の仕組みがそのまま与えるものであり、再判定のための追加コードは書いていない。**

| 出来事 | 再判定 |
|---|---|
| 通常進行 / `fix` / `RETURN` / `--rework` / `--retry-blocked` | しない |
| `20_spec.md` の変更 → 再レビュー | される |

### CP1 自身の扱い

CP1 を実行する時点では難易度が確定していないため、**選択には `normal` を使う。**

`select_model_classes()` に明示的な分岐を1つ置いている。

```python
at_spec_stage = stage == spec_stage(config)
difficulty = DEFAULT_DIFFICULTY if at_spec_stage else feature_difficulty(...)
```

分岐を置かず単純に読み出す案もあったが、その場合
「承認済み CP1 記録が `hard` を持つ状態で CP1 を再実行すると、CP1 Reviewer が strong になる」
という挙動になる。**新しい判定が過去の判定に引きずられるのは説明しにくい**ため、明示的に `normal` とした。

Reviewer へ渡す値は、仕様 stage では**空**にする。空＝「あなたが判定する」という約束である。

## プロンプト基礎レベル

| プロンプト | 基礎 | 根拠 |
|---|---|---|
| `create_feature_spec` | 2 | Worker 系で唯一「情報不足なら成果物を作らない」という充足性の判断を要求する |
| `create_function_design` | 2 | 承認済み仕様から設計を新規に構成する。責務の切り方・共通化候補の判断を含む |
| `create_function_call_flow` | 1 | 確定済みの `21_design.md` を呼び出しフローへ写し取る変換作業。独自判断は1制約のみ |
| `create_test_design` | 2 | 正常系・異常系・境界値の列挙は分析作業。取りこぼしが `viewpoint_total` に残る |
| `create_review_checklist` | 2 | 上流4成果物からレビュー観点を導出する。追加記述は手続き的だが観点導出は分析作業 |
| `implement_feature` | 1 | 仕様・設計・テスト設計がすべて確定済み。成果物も2ファイルに固定。最も自由度が低い |
| `review_stage` | 2 | 判定・戻り先決定・根拠つき FINDING・保証範囲の単調性など要求が最も多い |

`implement_feature.md` は 203 行と長いが、**長さは禁止事項と確認手順の多さによるもので、判断の自由度ではない。**
むしろ「決められたとおりに作る」ことを繰り返し要求している。

### 複数プロンプトを使う stage

```text
base = max(その stage の stage_*_prompts の基礎レベル)
```

Worker は1回の起動で列挙されたプロンプトすべてを実行するため、**最も要求の高いものを満たせる必要がある。**
合計すると同じ難易度を二重計上し、平均すると難しいほうが薄まる。

現在の設定では G1 = `max(2, 1) = 2`、G2 = `max(2, 2) = 2` となる。

### 未定義時

実行時は `2` で継続する（止めない）。設定漏れは
`test_every_stage_prompt_has_a_base_level` が検出する。**実行時は寛容、テストでは厳密。**

これは既存の `test_config_headings_exist_in_gate_record_template`（設定とテンプレートの整合を
テストで守る）と同じ考え方に合わせた。

## 選択結果

| 実行対象 | 基礎 | `easy` | `normal` | `hard` |
|---|:---:|---|---|---|
| CP1 Worker | 2 | standard | standard | standard |
| CP1 Reviewer | 2 | standard | standard | standard |
| G1 Worker | 2 | cheap | standard | strong |
| G2 Worker | 2 | cheap | standard | strong |
| CP3 Worker | 1 | cheap | cheap | standard |
| G1 / G2 / CP3 Reviewer | 2 | cheap | standard | strong |

### 検証：目的を満たしているか

- **`easy` 列に `strong` は1つもない**
- **`hard` 列に `cheap` は1つもない**（CP3 が standard へ上がる）

### 検証：`normal` は従来の既定と一致する

| | `normal` | 従来の既定 |
|---|---|---|
| CP1 / G1 / G2 Worker | standard | `role_design = standard` |
| CP3 Worker | cheap | `role_build = cheap` |
| Reviewer | standard | `role_review = standard` |

**完全一致する。** 判定基準に「迷った場合は `normal`」と明記したため、
判定が曖昧なときほど従来挙動へ倒れる。移行時の回帰リスクが構造的に小さい。

実リポジトリの設定でも確認済み（`02_implementation.md` の確認結果）。

## 優先順位

```text
1. --model-class <class>                    → model_selection: manual
2. role_* が設定に存在する                   → model_selection: role_fixed
3. prompt基礎レベル + feature難易度           → model_selection: auto（標準）
```

`--model-class` 指定時は難易度も基礎レベルも使わない。Worker / Reviewer とも指定クラスになる。

`role_fixed` の判定は「マージ後の設定に `role_` で始まるキーがあるか」の1点。
**追加フラグを作らない。** 標準の設定ブロックから `role_*` を外したため、
新規利用者は自動選択になり、既存利用者の `feature_loop.local` に残っている場合だけ従来方式になる。

`stage_*_worker_role` / `reviewer_role` は `role_` で始まらないため、判定材料にならない。
これは意図した挙動であり、テストで固定している（`test_uses_role_fixed_ignores_stage_role_assignment`）。

## Gate記録

```yaml
schema: gate_record/v2
feature_difficulty: hard
worker_model_class: standard
reviewer_model_class: strong
model_selection: auto
```

- `feature_difficulty` は **CP1 でのみ Reviewer が判定**し、他 stage では runner が渡した値を転記する
- 他の3キーは全 stage で runner が決め、Reviewer は転記するだけ
- これは `spec_hash` / `artifacts_hash` と同じパターンである（既存の約束事を増やしていない）
- Worker を起動しない実行（`--review-current` など）では `worker_model_class` は空になる

`prompt_base_level` は記録しない。`feature_difficulty` と `worker_model_class` の対で
「なぜこのモデルか」に答えられ、基礎レベルは設定から導出できるため。
