# cli_text_masker — 実AIでオートモードを実行した履歴例

## このディレクトリは何か

**実際のAIを使って、feature オートモードを CP1 から CP3 まで一周させたときの実行結果です。**
2026-08-23 に実行したもので、**当時の成果物をそのまま保存しています。**

**現在仕様の模範サンプルではありません。** 「こう書くのが正しい」という見本として読まないでください。
読む目的は、**オートモードを回すと実際に何が残るのかを、作られた実物として確認すること**です。

| | |
|---|---|
| 位置づけ | 実AI実行履歴例（検証記録） |
| 実行日 | 2026-08-23 |
| 進め方 | オートモード（`tools/feature_runner.py`） |
| 題材 | 文字列中の ASCII 数字をマスクする feature |
| 検証の経緯 | [`../context/work_notes/20260823_feature_auto_mode_real_ai_validation/`](../context/work_notes/20260823_feature_auto_mode_real_ai_validation/README.md) |

正式なサンプルは `cli_hello_greeting` / `cli_simple_calculator` / `cli_text_counter` です。
オートモードの進め方を学ぶ場合は [`../tutorials/005_automode_first_feature.md`](../tutorials/005_automode_first_feature.md) を参照してください。

---

## 見どころ：`gates/`

**このディレクトリの主な価値は [`features/ascii_digit_masker/gates/`](features/ascii_digit_masker/gates/) にあります。**

Gate記録が7件残っており、**正常系だけでなく、途中で止まって復旧した履歴**が読めます。

```text
1  CP1  PASS               仕様レビューと人間の仕様承認
2  G1   PASS               設計
3  G2   PASS               テスト設計
4  CP3  BLOCKED            実行環境の問題で停止
5  CP3  BLOCKED            範囲外のファイル変更を検出して停止
6  CP3  BLOCKED            同上
7  CP3  PASS               復旧後に完成、人間が受け入れ
```

確認できることの例です。

- 人間が承認した記録が、どのファイルのどこに残るのか
- AI が範囲外のファイルを変更したとき、どう記録されて止まるのか
- 止まった記録は消されず、**新しい記録が積み上がる**こと
- 差し戻しや停止の理由が、どの程度の粒度で残るのか

```bash
python tools/feature_runner.py --feature cli_text_masker/ascii_digit_masker --history
```

**この README は Gate記録を1件ずつ解説する文書ではありません。** 実物を読んでください。
判定値や記録項目の意味は [`../rules/project/70_feature_loop.md`](../rules/project/70_feature_loop.md) が正本です。

---

## 現在仕様と異なる点

**当時の実行結果を保存しているため、現在の仕様とは異なる箇所があります。**
これらは誤りではなく、**修正もしていません。**

| 箇所 | 当時の内容 | 現在の仕様 |
|---|---|---|
| Gate記録の `schema` | `gate_record/v1` | `gate_record/v2` |
| Gate記録のモデル関連フィールド | `model_design` / `model_build` / `model_review` | `feature_difficulty` / `worker_model_class` / `reviewer_model_class` / `model_selection` |
| `24_review_checklist.md` の実装開始条件 | 「CP1 の**下流進行承認**」 | 「CP1 の**仕様承認**（現在の `20_spec.md` と同一 baseline）」 |
| `tasks.md` の現在地 | 「G2、G2 Gate 未実施」 | Gate履歴は CP3 `PASS` まで進んでいる（`tasks.md` が実行中のまま更新されていない） |

**現在仕様を確認する場合は、必ず [`../rules/project/70_feature_loop.md`](../rules/project/70_feature_loop.md) を参照してください。**
Gate記録の項目やスキーマについても、このディレクトリの実物ではなく現在の正本が優先です。
ひな形は [`../templates/gate_record_template.md`](../templates/gate_record_template.md) にあります。

### なぜ直さないのか

**実行当時の記録だからです。**

後から現在仕様へ書き換えると、「当時どう動いたのか」が分からなくなります。
`tasks.md` と Gate履歴の食い違いも、**実行中に現在地メモが更新されないまま終わった**という
事実そのものです。化粧直しはしていません。

---

## 中身

```text
docs/cli_text_masker/
├─ README.md                              このファイル
├─ 10_overview.md
└─ features/ascii_digit_masker/
   ├─ 20_spec.md                          人間が用意した仕様
   ├─ 21_design.md、22_flow.md             AI が作成（G1）
   ├─ 23_test_plan.md、24_review_checklist.md  AI が作成（G2）
   ├─ 25_review_result.md                 AI が作成（CP3）
   ├─ tasks.md
   └─ gates/                              Gate記録 7件

src/cli_text_masker/features/ascii_digit_masker.py
tests/cli_text_masker/features/test_ascii_digit_masker.py
```

実装とテストは現在も動作し、`python -m pytest` の対象に含まれています。

---

## 関連

- 検証の経緯と結論: [`../context/work_notes/20260823_feature_auto_mode_real_ai_validation/`](../context/work_notes/20260823_feature_auto_mode_real_ai_validation/README.md)
- オートモードの正本: [`../rules/project/70_feature_loop.md`](../rules/project/70_feature_loop.md)
- オートモードを自分で試す: [`../tutorials/005_automode_first_feature.md`](../tutorials/005_automode_first_feature.md)
- runner の使い方: [`../../tools/README.md`](../../tools/README.md)
