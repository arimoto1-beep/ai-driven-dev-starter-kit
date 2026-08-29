# 実装した内容

## 実装順序

人間が指定した順序どおりに進めた。

1. Gate記録の4キー化 ＋ `gate_record/v2` ＋ Worker モデルクラス記録欠落の修正
2. プロンプト基礎レベルによるモデル決定
3. `--model-class`（manual override）
4. CP1 Reviewer による難易度判定と反映
5. dry-run 表示
6. ドキュメント更新
7. 自動テスト

途中で設計変更が必要になる問題は発生しなかった。

## tools/feature_runner.py

### 削除した関数

- `resolve_model(config, role, overrides)`
  役割から実モデルまでを一度に解決していた。責務を分割したため不要になった。

### 追加した関数

すべて「モデル選択」節に集約した。

| 関数 | 役割 |
|---|---|
| `feature_difficulty(root, config, ctx)` | 承認済み CP1 Gate記録から難易度を読む。無効値・欠落は `normal` |
| `base_level(config, prompt)` | プロンプト1本の基礎レベル。未定義・数値でない場合は `2` |
| `prompts_base_level(config, prompts)` | カンマ区切りのプロンプト群の最大値 |
| `level_class(level)` | 1〜3 へ丸めて `cheap` / `standard` / `strong` |
| `uses_role_fixed(config)` | `role_` で始まるキーの有無 |
| `role_class(config, role, overrides)` | 従来方式の role → クラス（旧 `resolve_model` の前半） |
| `actual_model(config, model_class)` | クラス → 実モデル（旧 `resolve_model` の後半） |
| `select_model_classes(...)` | 優先順位3段の分岐。setup の元になる dict を返す |
| `describe_selection(setup)` | dry-run の要約1行 |
| `describe_side(setup, side)` | dry-run の Worker / Reviewer 1行 |

### 変更した関数

| 関数 | 変更 |
|---|---|
| `stage_setup()` | 第1引数に `root`、末尾に `model_class` を追加。role 解決をやめ `select_model_classes()` を使う |
| `build_reviewer_instruction()` | `model_class` / `human_gate` の2引数を `setup` に集約。`使用モデル区分` を4キーへ置換 |
| `execute()` | `model_class` を受け取る。Worker を起動しない場合、`worker_class` / `worker_model` を空にする |
| `write_runner_record()` | `schema` を `gate_record/v2` へ。`model_*` 3キーを新4キーへ。`setup` を任意引数で受ける |
| `show_dry_run()` | 選択の要約と使用プロンプトを表示 |
| `cmd_status()` | モデル選択の状態を1行表示 |
| `cmd_run()` | `model_class` を受け取る。値の検証、`--role-*` との排他、従来方式の通知 |
| `main()` | `--model-class` を追加。`--role-*` の help を後方互換と明記 |

### 設計上の判断

**排他チェックは `main()` ではなく `cmd_run()` へ置いた。**
`--review-current` / `--retry-blocked` / `--spec-review` / `--rework` の排他チェックが
すでに `cmd_run()` にあるため、同じ場所へ揃えた。副次的に、自動テストから直接検証できるようになった。

**Worker のモデルクラスを空にする処理は `execute()` に置いた。**
`setup` を作る側（`stage_setup`）は「この stage の Worker はどのクラスか」を答えるだけで、
「今回 Worker を起動するか」は `action.kind` を持つ `execute()` にしかわからない。

## docs/rules/project/70_feature_loop.md

- 「モデル役割」節を「モデル選択」節へ全面的に書き換え
  - 決定ルール、難易度、基礎レベル、選択結果の表、`--model-class`、優先順位
  - 末尾に「従来のモデル固定設定（後方互換）」小節を追加し、`role_*` の説明を移した
- 設定ブロックから `role_design` / `role_build` / `role_review` を削除
- 設定ブロックへ `base_level_*` 7行を追加
- `stage_*_worker_role` に「従来のモデル固定設定でのみ使用する」と注記

## docs/templates/gate_record_template.md

- `schema: gate_record/v2`
- `model_design` / `model_build` / `model_review` → `feature_difficulty` / `worker_model_class` /
  `reviewer_model_class` / `model_selection`
- コメントへ、各キーの責務（CP1 のみ判定・他は転記）と `gate_record/v1` の扱いを追記
- 判定サマリ表へ「モデル選択」行を追加

## prompts/review_stage.md

- 「利用者が指定する項目」の `使用モデル区分` を4キーへ置換
- CP1 節へ「feature 難易度の判定」小節を追加（判定基準3値、迷ったら `normal`、追加調査をしない）
- 「モデル選択結果の記録」小節を追加（転記するだけ）
- front matter 例を `gate_record/v2` と新4キーへ

## tools/README.md

- `--role-design strong` の例を `--model-class strong` へ置換
- 「モデル選択」節を追加（決定ルール、dry-run の表示例）
- 「従来のモデル固定設定（後方互換）」節を追加

## prompts/run_stage.md

**変更していない。** Worker 指示文の `使用モデル区分` はそのまま残した（`04_rejected_options.md` 参照）。

## tests/tools/test_feature_runner.py

- sandbox 設定から `role_*` を削除し、`base_level_*` 7行を追加
  → **既存テストの大半が、そのままモデル自動選択の経路を通るようになった**
- `stage_g1_prompts` を2本にして `max` 合成を実際に通るようにした
- `FakeAI` が実モデル（argv の `{model}`）も記録するようにした
- `approve_spec()` に `difficulty` 引数を追加（省略時は難易度を持たない従来の記録）
- 旧 `resolve_model` 系4テストを削除し、部品ごとのユニットテストへ置換
- モデル選択のループ全体テスト、優先順位テスト、記録・表示テストを追加

## 確認結果

### 自動テスト

```text
python -m pytest --basetemp=<scratchpad>/pt2
264 passed
```

（うち `tests/tools/test_feature_runner.py` は 231 件）

**注意：** この環境では `pytest` の既定の一時ディレクトリが使えず、`--basetemp` の指定が必要だった。
テストコード側の問題ではない（`03_findings.md`）。

### 実リポジトリ設定での確認

`tools/feature_loop.local` に `role_*` があるため、現在は従来方式で動作する。

```text
$ python tools/feature_runner.py --feature cli_uppercase_text/uppercase --spec-review --dry-run
従来のモデル固定設定（role_*）で動作しています。
role_* を削除すると、モデル自動選択になります。
...
モデル選択: role_fixed（従来のモデル固定設定。role_* を削除するとモデル自動選択になります）
Reviewer role=review  class=standard  model=claude-sonnet-5
```

`--model-class` は従来方式より優先される。

```text
$ python tools/feature_runner.py --feature cli_uppercase_text/uppercase --spec-review --model-class strong --dry-run
モデル選択: manual（--model-class による指定）
Reviewer class=strong  model=claude-opus-5
```

排他チェック。

```text
$ python tools/feature_runner.py ... --model-class strong --role-design cheap --dry-run
--model-class と --role-* は同時に指定できません。
```

**`role_*` を削除した場合の挙動も、ファイルを変更せずに確認した**
（実リポジトリの設定から `role_*` だけを除いた dict で `select_model_classes()` を実行）。

```text
role_fixed 判定: True -> False
feature_difficulty: normal

CP1  selection=auto  worker base=2 class=standard  reviewer base=2 class=standard
G1   selection=auto  worker base=2 class=standard  reviewer base=2 class=standard
G2   selection=auto  worker base=2 class=standard  reviewer base=2 class=standard
CP3  selection=auto  worker base=1 class=cheap     reviewer base=2 class=standard
```

既存 feature の CP1 記録は `feature_difficulty` を持たないため `normal` となり、
**従来の既定と同じクラスが選ばれる。** 設計時の想定どおりである。
