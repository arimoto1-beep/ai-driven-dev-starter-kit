# 実装した内容と、確認結果

## 変更したファイル

| ファイル | 変更内容 |
|---|---|
| `tools/feature_runner.py` | stale 検出、`artifacts_hash` の受け渡し、`--rework`、`--dry-run` の副作用修正 |
| `docs/rules/project/70_feature_loop.md` | 「完成後の修正」節、`stage_*_artifacts` 設定、`REWORK`、3操作の使い分け |
| `docs/templates/gate_record_template.md` | `artifacts_hash` フィールドと説明、`REWORK` |
| `prompts/review_stage.md` | `artifacts_hash` を転記する指示（`spec_hash` と同じ扱い） |
| `tools/README.md` | 完成後の修正フローの説明、3操作の使い分け表 |
| `tests/tools/test_feature_runner.py` | テスト 40 件追加 |

**`tools/` `docs/rules/` `prompts/` `docs/templates/` はいずれも
`50_ai_permissions.md` の保護対象である。** 今回は利用者から
「検証で見つかった不足を最小限修正してよい」という明示指示があったため変更した。

## 1. stage 成果物のフィンガープリント

設定へ `stage_<stage>_artifacts` を追加した。

```text
stage_g1_artifacts  = {feature_dir}/21_design.md, {feature_dir}/22_flow.md
stage_g2_artifacts  = {feature_dir}/23_test_plan.md, {feature_dir}/24_review_checklist.md
stage_cp3_artifacts = src/{app}/features/{feature}.py, tests/{app}/features/test_{feature}.py
```

runner がこれらの内容ハッシュ（SHA-256）を計算し、`spec_hash` と同じ経路で
Reviewer へ渡す。Reviewer は front matter へ転記するだけで、計算しない。

```text
runner がハッシュ計算 → Reviewer へ渡す → Gate記録へ転記 → 次回 runner が再計算して照合
```

ハッシュにはパス名も混ぜているため、内容の変更だけでなく追加・削除も検出できる。
ディレクトリ指定の場合は git が見ているファイルだけを対象にするため、
`__pycache__` のような無視対象は数えない。

**CP1 は `artifacts_hash` を使わない。** `20_spec.md` の baseline を成立させるのは
Gate の `PASS` ではなく人間の承認であるため、既存の `spec_hash` と仕様承認で判定する。

## 2. stale 検出と停止

`stale_stages()` が、通過後に変更された stage を stages 順で返す。
確認する場所は2箇所ある。

| 場所 | 見る範囲 | 理由 |
|---|---|---|
| `done` / `await_human` の直前 | 全 stage | Worker を起動しないため Manufacturing Preflight が働かない。最後の関門になる |
| stage を通常進行で実行する直前 | その stage より上流だけ | 古い G2 のまま CP3 を作らせない。自分自身は作り直す対象なので見ない |

明示的な人間の操作（`--rework` / `--retry-blocked` / `--review-current`）では止めない。
変更を承知のうえでの指示だからである。

仕様 stage は Manufacturing Preflight が担当し、stale 側では二重に止めない。

停止時の出力はこうなる。

```text
通過済み stage の成果物が、その stage の判定後に変更されています。
  変更が検出された stage: G2
  再確認が必要な下流 stage: CP3

古い判定を完成扱いにしないため、ここで停止します。
どちらで再開するかは人間が決めてください。
  成果物を人間が直した場合   : --review-current G2
  AIに作り直させる場合       : --rework G2
```

**stale の検出そのものは判断ではないため、Gate記録を作らない。**
`await_human` で停止するときに記録を作らないのと同じ扱いにした。
記録が残るのは、人間がどちらかの操作を選んだあとである。

## 3. `--rework <STAGE>`

通過済み stage を Worker からやり直す操作を追加した。

- `triggered_by: REWORK`、`supersedes` にその stage の直近の確定記録が入る
- 過去の Gate記録は削除も上書きもしない
- 製造 stage へ使っても Manufacturing Preflight は働く
- `--rework CP1` でも人間の承認は消えない（承認待ちで停止する）
- `--review-current` / `--retry-blocked` / `--spec-review` とは排他

実行後は通常のオートモードへ戻るため、下流が順に再実行される。

## 4. `--dry-run` の副作用修正（ついでに見つかった既存不具合）

`--rework` の動作確認中に判明した。

`--dry-run` を指定しても、Manufacturing Preflight や収束上限に達した場合は
**`BLOCKED` Gate記録が作成されていた。** `--dry-run` は「実行せず表示する」ための
入口なので、確認しただけで Gate履歴が増えるのは正しくない。

これは `--rework` 追加以前からある挙動で、今回の変更で作り込んだものではない。
`halt()` へ `dry_run` を渡し、記録を作らずに理由だけ表示するようにした。

---

## 実装中に、自分の実装の穴が実AIで見つかった

**最初の実装では、stale 検出を `done` / `await_human` の直前にしか置いていなかった。**

自動テストはすべて通っていた。しかし実AIで確認したところ、次の状況で素通りした。

```text
G2 を --rework で通し直す → 最新記録が G2 PASS → 次の動作は run(CP3)
        ↓
ここで人間が 23_test_plan.md を追記
        ↓
通常実行 → action は done でも await_human でもなく run(CP3)
        ↓
stale チェックが働かず、古い G2 のまま CP3 Worker が起動した
```

実際に CP3 Worker が起動してしまい、途中で停止させた。

`done` / `await_human` は「全部に依存する状態」だが、
**stage を実行することも「上流に依存する行為」である。**
この2つを別々に扱う必要があった。

修正後は、stage 実行前にもその stage の上流だけを確認するようにした。

```text
$ python tools/feature_runner.py --feature cli_mask_rework/ascii_digit_masker
CP3 を実行できません。
通過済み stage の成果物が、その stage の判定後に変更されています。
  変更が検出された stage: G2
  再確認が必要な下流 stage: CP3
```

**自動テストが全部通っていても、実際に動かさないと見えない穴があった。**
前回の実AI検証で得た教訓（`20260823_.../04_findings_and_remaining.md` の1番）が、
そのまま今回も再現した。

---

## 既存テストが設計判断を1つ差し戻した

`test_status_reports_preflight_stop_when_approved_spec_changed` が失敗した。

最初の実装では、`--status` の「次の動作」で stale の表示を優先していた。
そのため、仕様変更時に従来出ていた
`次の動作: Manufacturing Preflight で停止 (stage=G1)` が出なくなっていた。

**同じ状況に2つの説明が競合していた。**
Manufacturing Preflight は既に確立した説明を持つため、そちらを優先し、
stale の表示は Preflight が働かない場合だけ出すようにした。

同様に `test_preflight_blocks_when_spec_changed_after_approval` も失敗し、
stale チェックを Manufacturing Preflight の**後**へ移した。
仕様未承認時に `BLOCKED(spec_not_approved)` 記録が作られる既存の挙動を保つためである。

**既存テストが、責務の重複を2回検出した。**

---

## テスト結果

```text
python -m pytest -q --basetemp=.pytest_tmp
224 passed
```

内訳は、既存 184 件（うち `tests/tools/` は 151 件）＋今回追加 40 件。

追加したテストの範囲。

| 範囲 | 主な確認内容 |
|---|---|
| ハッシュ計算 | 内容変更の検出、ディレクトリへのファイル追加、gitignore 対象の除外 |
| stale 判定 | G1 / G2 / CP3 / CP1 の各変更、上流優先の順序、未承認 feature の誤検出防止 |
| 完成後の停止 | 実装変更・試験観点変更・設計変更・仕様変更、Gate記録を増やさないこと、既存記録を書き換えないこと |
| 上流 stale での stage 実行 | 古い G2 のまま CP3 を起動しないこと、自分自身の stage では止めないこと、通常進行を妨げないこと |
| 後方互換 | `artifacts_hash` の無い記録では従来どおり `done` を返すこと |
| `--rework` | Worker 起動、因果情報、既存記録の保持、下流カスケード、Preflight、CP1 の人間承認、排他、dry-run |
| 既存操作との住み分け | `--retry-blocked` が完成済み feature を拒否すること、`--review-current` が Worker を起動しないこと |
| 設定の整合 | artifacts が Worker の変更範囲に収まること、`tasks.md` / `25_review_result.md` を含まないこと |

新規 feature の正常系、BLOCKED、`--retry-blocked`、`--review-current`、
CP1 approved spec hash、Gate履歴保持は、既存テストが引き続きすべて通っている。

## 実AIでの確認

自動テストの AI は擬似である。**Reviewer が実際に `artifacts_hash` を
転記するかどうかは、実AIでしか確認できない。**

`--rework G2 --once` を実AIで実行した結果、Gate記録 0008 の front matter は次のとおりだった。

```text
gate: G2
run_seq: 8
artifacts_hash: c9d334d47e5d0a3c6113d6e637d5a3e6c057758b076f57a930ca3bbb4d2bbefe
verdict: PASS
triggered_by: REWORK
supersedes: docs/cli_mask_rework/features/ascii_digit_masker/gates/0003_20260823T162053_g2.md
```

値は runner が `--dry-run` で表示した値と一致した。`triggered_by` と `supersedes` も正しい。

その後 `23_test_plan.md` を人間が1行追記したところ、

```text
stage 成果物の baseline:
  G2   **通過後に変更あり**

次の動作: 通過済み成果物の変更を検出したため停止 (G2)
```

となり、通常実行は終了コード 1 で停止した。**ハッシュの往復が実AIで成立した。**

## 実AIで確認していないこと

- `--rework G1` / `--rework CP1` の実AI実行（dry-run と自動テストのみ）
- `artifacts_hash` を持つ CP3 記録を使った完成後の CP3 変更検出
  （検証1の時点では実装前だったため、実AIでは旧挙動のみ確認）

いずれも自動テストでは確認済みだが、実AIでの通し確認は行っていない。
