# 将来検討として残したもの・未対応事項

## 第一段階では実装しないもの（人間が明示的に指定）

以下は人間の指示により、意図的に実装していない。

- `cheap → standard → strong` の自動昇格
- Reviewer の最低モデルクラス固定（下限ルール）
- `RETURN` 回数による昇格
- `BLOCKED` による昇格
- test failure による昇格
- stage ごとの feature 難易度再判定
- `fix` 時の feature 難易度再判定
- 5段階以上の難易度
- 0.5 刻みなどの細かい係数
- `--difficulty`
- Worker / Reviewer 別の新しい override
- feature 単位の恒久 model override
- 実モデル名の Gate記録
- トークン数・料金・実行時間の新規観測
- 自動的な base level 調整
- モデル選択専用のAI呼び出し
- role 概念そのものの削除
- 大規模な README / tutorial 再編

実AI検証後に必要性が分かったものだけ、後から追加する。

## 拡張しやすさの確認

第一段階の構造が、上記の将来追加を妨げないことを確認した。

| 将来追加 | 必要な変更 |
|---|---|
| 自動昇格 | `model_selection` に値を追加、`escalated_from` キーを追加、`select_model_classes()` に分岐1つ |
| Reviewer 下限 | 丸め規則に1行 |
| プロンプト追加 | `base_level_*` を1行追加（テストが不足を検出する） |
| 難易度の段階変更 | `DIFFICULTY_OFFSETS` の書き換え |

**いずれも「将来必要かもしれない」という理由での事前実装は行っていない。**
上表は、後から追加できることの確認であって、追加の予定ではない。

## 実AI検証で解消したもの

**実AI検証は 2026-08-30 に完了した**（結果は `05_real_ai_validation_prep.md` の「実施結果」）。

`easy` / `hard` の feature を CP1 から CP3 まで通し、いずれも設計どおりのクラスが選ばれ、
`done` まで到達した。最終回帰試験は 294 件 PASS。

これにより、次は未対応事項ではなくなった。

- CP1 Reviewer が実際に難易度を判定・記録すること
- 難易度が製造 stage へ引き継がれること（再判定されないこと）
- 難易度に応じてクラスが変わること

`normal` の feature は専用に作成していないが、**既存 feature（`feature_difficulty` を持たない
CP1 記録）が `normal` として扱われ、従来と同じクラスになること**は実リポジトリの設定で確認済みである
（`02_implementation.md`）。

## 設計変更で解消したもの

**2026-08-30、人間の判断で role 固定方式を削除した**（README の「決定事項 7-A」）。

「`role_*` を将来どの段階で廃止するか」は未決事項ではなくなった。段階的廃止は行わず、
V2 の設計を固めている段階のうちに一度で削除した。

## 未対応事項

### 1. 24_review_checklist_template.md の用語不整合（実AI検証中に発見）

`docs/templates/24_review_checklist_template.md` に「CP1 の下流進行承認」という表現があるが、
現行ルール（`docs/rules/project/70_feature_loop.md`、`docs/templates/gate_record_template.md`）では
**「CP1 の仕様承認」**である。

- **今回は未修正。** モデル選択とは別件であり、指示範囲外のため触っていない
- 実害の有無（runner の承認欄検出は `approval_heading_cp1 = 仕様承認` を使うため影響しない見込み）は未確認
- 修正するかどうかは人間の判断事項

### 2. README / tutorial のオートモード導線

**今回のモデル選択実装とは別の上位テーマである。** 人間の指示により、今回は着手していない。

調査で確認した事実：

| ファイル | 現状 |
|---|---|
| `README.md` | オートモードに言及していない |
| `docs/tutorials/` の4本 | すべてマニュアルモードのみ |
| `docs/overview.md` | オートモードに言及していない |
| `docs/how_to_use_prompts.md` | オートモードに言及していない |

オートモードに触れているのは次だけである。

- `docs/rules/project/70_feature_loop.md`（正本）
- `docs/rules/project/20_workflow.md`（入口）
- `docs/rules/README.md`（索引の1行）
- `prompts/README.md`（入口）
- `tools/README.md`（使い方）

つまり、**新規利用者向けの表の導線は、いまもマニュアルモードだけを案内している。**
モデル選択の説明は正本と `tools/README.md` を更新したが、
「オートモードそのものを表の導線へ出す」作業は未着手である。

これを行うかどうかは人間の判断事項。

### 3. 未決事項（README にも記載）

実AI検証を1回行った結果を踏まえても、なお人間が判断するもの。

- `easy` feature で Reviewer が `cheap` になることの妥当性
  （1回の検証では問題なく完走した。継続観察が必要かは人間の判断）
- コストを下げたい場合に `base_level_*` を調整するか（下記「運用上の所感」）
- `create_feature_spec` の基礎レベルを 2 のままにするか 3 にするか
- 自動昇格の要否
- Worker 指示文の `使用モデル区分` 行を残すか
- Gate記録へ実モデル名を残すか

### 4. Git 操作

人間の指示により、`git commit` / `git tag` / `git push` を行っていない。
既存の Gate履歴・過去実験資産も削除・整理していない。

検証用に作成した `easy` / `hard` の feature は、**人間がこの記録の更新後に削除する予定**である。

## 運用上の所感（人間の所感。実装変更ではない）

実AI検証を終えた時点での、人間の所感として記録する。
**現時点で実装・設定を変更する決定ではない。**

- `easy` で Reviewer が `cheap` でも、今回の検証は問題なく完走した
- `hard` では **strong Reviewer が実際に境界ケースの抜けを1件検出した**（`\` 自身のエスケープ）。
  難易度に応じてクラスを上げる仕組みが、実際にレビュー品質へ効いた例である
- **実務では `hard` 判定が多くなる可能性がある**
- その場合にコストを安い側へ寄せるなら、**`feature_difficulty` の意味を歪めるより、
  `base_level_create_function_design` や `base_level_create_test_design` などの
  prompt base level 側を調整する方が自然**と思われる

最後の点は、`feature_difficulty` が「この feature がどれくらい難しいか」という
事実の判定であるのに対し、`base_level_*` は「この作業にどれくらいの能力が要るか」という
方針値だからである。コスト方針は後者で調整するのが筋が通る。
