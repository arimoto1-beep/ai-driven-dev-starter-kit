# オートモードのモデル自動選択

## 目的

オートモードのモデル選択を、役割ごとの固定設定（`role_design` / `role_build` / `role_review`）から、
**feature 難易度 ＋ プロンプト基礎レベル**による自動選択へ切り替える。

利用者がモデルクラスを考えなくて済むようにすることが目的であり、最適化そのものが目的ではない。

```text
明らかに簡単な feature に strong を使わない
明らかに難しい feature に cheap を使わない
通常は利用者がモデルクラスを考えなくてよい
```

この程度を、分かりやすい最小構造で実現することを成功条件とした（人間が指定）。

## 状態

完了（実装・自動テスト・実AI検証まで完了。ただし人間による差分確認と commit は未実施。
「次に行うこと」を参照）

## 作業期間

2026-08-27（調査・設計検討） 〜 2026-08-30（実装・実AI検証）

## 対象

- `tools/feature_runner.py`
- `docs/rules/project/70_feature_loop.md`
- `docs/templates/gate_record_template.md`
- `prompts/review_stage.md`
- `tools/README.md`
- `tests/tools/test_feature_runner.py`

## 現在地

3回の調査・設計検討を経て方針が確定し、実装・自動テスト・実AI検証まで完了した。

- モデルクラスは `prompt基礎レベル + feature難易度` で決まる
- feature 難易度は **CP1 の Reviewer が仕様レビューの一部として1回だけ判定する**（追加AI呼び出しなし）
- ~~従来の `role_*` 固定設定は後方互換として残る~~ → **2026-08-30 に削除**（下記「決定事項 8」）
- Gate記録の front matter を `gate_record/v2` へ変更した

実装中に、**設計時に想定していなかった既存不具合と設定上の落とし穴を2件発見した**（`03_findings.md`）。

その後、人間が `tools/feature_loop.local` から `role_*` を削除してモデル自動選択を有効化した。
**その際に、ローカル設定に隠れていたテスト不備が1件発覚し、修正した**（`03_findings.md` の 2-2件目）。

### 実AI検証の結果（2026-08-30、人間が実施）

`easy` / `hard` の検証用 feature を CP1 から CP3 まで通し、**いずれも設計どおりのクラスが選ばれ、
Human Gate まで到達して `done` となった。**

| | CP1 Reviewer | G1 W/R | G2 W/R | CP3 W/R |
|---|---|---|---|---|
| `easy`（判定 `easy`） | standard | cheap / cheap | cheap / cheap | cheap / cheap |
| `hard`（判定 `hard`） | standard | strong / strong | strong / strong | standard / strong |

- 仕様を修正して CP1 を再レビューした際も `hard` と判定された（難易度が引き継がれ、再判定されない）
- **`hard` の G2 で、strong Reviewer が境界ケースの抜けを1件検出**し、同一 G2 内の `fix` で2ラウンド PASS
- feature 単体テスト 21 件 PASS

詳細な値は `05_real_ai_validation_prep.md` の「実施結果」にある。
**検証用 feature は削除予定のため、Gate記録が失われても事実が残るよう値を書き写してある。**

最終回帰試験は **294 件すべて成功**（検証用 feature のテストを含む件数）。

## 決定事項

すべて人間が指定した方針である。AIは調査結果と選択肢を提示した。

### 1. モデル選択は「基礎レベル ＋ 難易度」の加算だけとする（人間の決定）

```text
level = prompt基礎レベル + feature難易度（easy=-1 / normal=0 / hard=+1）
level を 1〜3 へ丸める
1 → cheap ／ 2 → standard ／ 3 → strong
```

補正ルールをこれ以上増やさない。

### 2. 基礎レベルは role 単位ではなくプロンプト単位で持つ（人間の決定）

AIは第2回検討で role 単位（`design` / `build` / `review`）を提案したが、人間が
「当初想定どおりプロンプト単位にする」と決定した。

理由（人間の指示に基づく整理）：能力要求を実際に決めているのはプロンプトであり、
`stage_*_prompts` を差し替えればレベルも追随する。role を経由する必要がない。

設定場所は `70_feature_loop.md` の既存設定ブロック。プロンプトファイル側へ front matter は新設しない。

### 3. 難易度判定は CP1 Reviewer が1回だけ行う（人間の決定、AIが提案）

AIが第2回検討で提案し、人間が採用した。

CP1 Reviewer はすでに `20_spec.md` 全体を読んでいるため、**モデル選択のための追加AI呼び出しが発生しない。**
判定結果は CP1 Gate記録の `feature_difficulty` に残り、G1 / G2 / CP3 では再判定しない。

### 4. Reviewer の下限ルールは設けない（人間の決定）

AIは第2回検討で「Reviewer は `cheap` にしない」という下限規則を提案したが、
人間が「第一段階では追加しない。実AI検証で必要性が確認された場合に追加する」と決定した。

結果として、`easy` feature では Reviewer も `cheap` になる。

### 5. 自動昇格は第一段階では実装しない（人間の決定）

`RETURN` / `BLOCKED` / test failure からモデル能力不足を推測しない。

### 6. 用語は「V1 / V2」を使わない（人間の訂正）

第2回報告までAIが「V1 / V2」という呼称を使っていたが、人間から次の訂正があった。

```text
V1 = 個別プロンプトを人間が指定して実行する旧版方式 = マニュアルモード
V2 = feature_runner.py を使う現行方式 = オートモード
```

今回の変更はオートモード内部のモデル選択方式の切り替えであり、世代交代ではない。
リポジトリ本文では「V1 / V2」を使わず、「マニュアルモード」「オートモード」
「従来のモデル固定設定」「モデル自動選択」を使う。

Gate の機械可読値は `role_fixed` とする（`v1_fixed` / `legacy_fixed` は不採用）。

### 7-A. role 固定方式は削除する（人間の決定、2026-08-30）

**当初は後方互換として残す方針だったが、削除に変更した。**

人間の判断：`role_design` / `role_build` / `role_review` 方式は数日前にオートモード内部へ入れた
仕組みであり、**外部の既存利用者がいない。** V2（オートモード）自体の設計を固めている最中なので、
「既存実装だから残す」理由がない。

削除にあたり「role 固定方式を削除すると何が失われるか」を先に確認した（AIが確認、人間が判断）。

- 失われるのは **1回の実行で Worker と Reviewer に別々のクラスを指定する手段**だけ
  （`--role-build cheap --role-review strong` のような指定）
- `auto` は基礎レベルにより Worker / Reviewer に別クラスを与える。`manual` は「今回だけ固定する」
  逃げ道であり、単一クラスで足りる
- 恒久的なコスト調整は `base_level_*` で行う方が細かく、`06_deferred.md` の運用上の所感とも一致する

**モデル選択方式は `auto` / `manual` の2つだけになった。** `model_selection` の値も2値。

なお `stage × role の変更範囲`（role = Worker / Reviewer）は**まったく別の概念**であり、
削除対象ではない。今回削除したのは `design` / `build` / `review` というモデル役割である。

### 7. Gate記録スキーマは `gate_record/v2` へ上げる（人間の決定）

front matter の構成が変わるため。**これは Gate記録スキーマの版数であり、キット世代とは別物である。**
既存の `gate_record/v1` 記録は書き換えず、履歴としてそのまま残す。

## 未決事項

実AI検証を1回行った結果を踏まえても、なお人間が判断するもの。

- `easy` feature で Reviewer が `cheap` になることの妥当性（下限ルールを追加するか）
  - 1回の検証では問題なく完走した。継続観察するかは人間の判断
- **コストを下げたい場合に `base_level_*` を調整するか**（下記「運用上の所感」）
- `create_feature_spec` の基礎レベルを 2 のままにするか 3 にするか
- 自動昇格の要否
- Worker 指示文の `使用モデル区分` 行を残すか（現在は従来のまま残している。`04_rejected_options.md` 参照）
- Gate記録へ実モデル名を残すか（監査・再現性 vs. 文書にベンダー名を書かない方針）
- `docs/templates/24_review_checklist_template.md` の用語不整合を修正するか（`06_deferred.md`）

## 運用上の所感（人間の所感。実装変更の決定ではない）

- `easy` で Reviewer が `cheap` でも、今回の検証は問題なく完走した
- `hard` では strong Reviewer が実際に境界ケースの抜けを検出した
- **実務では `hard` 判定が多くなる可能性がある**
- コストを安い側へ寄せる場合、**`feature_difficulty` の意味を歪めるより
  `base_level_*` 側を調整する方が自然**と思われる

詳細は `06_deferred.md` の「運用上の所感」。

## 次に行うこと

1. **検証用 feature（`easy` / `hard`）の削除**（人間が実施予定）
   - 事実は `05_real_ai_validation_prep.md` へ書き写し済みのため、削除しても記録は残る
2. **人間による差分確認と commit**（commit / tag / push は未実施）
3. 未決事項の判断（上記「未決事項」）

## 関連する正式文書

- `docs/rules/project/70_feature_loop.md`（モデル選択の正本）
- `docs/templates/gate_record_template.md`
- `prompts/review_stage.md`
- `tools/README.md`

## 関連する作業メモ

- `20260823_feature_auto_mode_real_ai_validation`（オートモードの実AI検証）
- `20260826_feature_rework_flow`（完成後の修正フロー。今回の直前の作業）

## 付随ファイル一覧

| ファイル | 内容 |
|---|---|
| `01_design.md` | 確定した設計。決定ルール、基礎レベル、優先順位、記録項目 |
| `02_implementation.md` | 実装した内容と変更箇所 |
| `03_findings.md` | 実装中に見つかった想定外 |
| `04_rejected_options.md` | 検討したが採用しなかった案 |
| `05_real_ai_validation_prep.md` | 実AI検証の準備手順と、**実施結果（2026-08-30）** |
| `06_deferred.md` | 将来検討として残したもの、未対応事項、運用上の所感 |
