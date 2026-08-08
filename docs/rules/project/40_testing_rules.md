# project: テストルール（どう検証するか）

## このファイルの目的

このプロジェクトの試験の単位、検証方法、テストコードの配置を定めます。

## このファイルを読む作業

- テスト計画の作成
- feature 実装、entrypoint 実装
- 結合試験計画の作成、結合試験の実装
- バグ修正の実装
- 実装や修正の後に検証を行うとき

## このファイルに含めないもの

- テスト観点の作り方、確認項目の立て方 → 対応する `prompts/*.md`
- 実装言語と実装規約 → `30_development_rules.md`
- テスト計画書の配置とひな形 → `10_document_structure.md`
- 検証を実施し報告するという原則 → `docs/rules/core/10_workflow.md`、`docs/rules/core/50_records_and_reporting.md`

---

## 現行スターターキットの初期値

### 試験の基本単位

- **feature 単位の単体試験を基本**とします。
- 必要に応じて、**command/app 単位の結合試験**も扱います。
- 結合試験は常に必須ではありません。**entrypoint から複数 feature を束ねて確認する必要がある場合**に扱います。

### 単体試験と結合試験の役割分担

| 試験 | 確認するもの | 計画書 |
|---|---|---|
| feature 単体試験 | feature の詳細ロジック、正常系、異常系、境界値 | `23_test_plan.md` |
| 結合試験 | `entrypoint.py` と feature の接続、入出力、終了コード、エラー時の扱い | `11_integration_test_plan.md` |

feature 単体の詳細ロジックは、feature 単体試験で確認します。結合試験で重複して確認しません。

### 検証コマンド

```text
python -m pytest
```

- 実装後、レビュー指摘の反映後、バグ修正後に、このコマンドで検証します。
- 報告時は、実行コマンドと結果を記載します（`docs/rules/core/50_records_and_reporting.md`）。
- 環境の理由でこのコマンドが実行できない場合は、利用可能な Python 実体で代替実行し、その旨を報告します。実行できなかった場合は理由を報告します。

### テストファイルの配置

```text
tests/
  <command_or_app_name>/
    test_entrypoint_<short_name>.py      entrypoint のテスト
    test_integration_<short_name>.py     結合試験
    features/
      test_<feature_name>.py             feature 単体テスト
```

`<short_name>` の規約は `10_document_structure.md` を参照してください。
複数 command/app 間で同名ファイルが衝突しないよう、この命名を使います。

### テスト実装時の制約

- テストを通すために、feature 実装や共通処理を勝手に変更しません。
- 結合試験を実装している途中でテストしにくいと判断しても、勝手に `src/` を変更しません。実装側の変更が必要そうな場合は、作業報告に記載し、人間レビューに回します。

（この制約の根拠は `docs/rules/core/30_change_safety.md` の「作業対象の限定」です）

---

## 変更する場合の注意

- テストフレームワークやコマンドを変更する場合、`30_development_rules.md` の許可依存も併せて確認してください。
- 試験の単位を変更する場合、`docs/rules/core/10_workflow.md` の「検証は粒度ごとに確認対象を分ける」を満たしているか確認してください。粒度を1つに統合すると、この原則を満たせなくなります。

---

## 関連するルール

- 検証を実施する原則 → `docs/rules/core/10_workflow.md`
- 検証結果を再現できる形で報告する → `docs/rules/core/50_records_and_reporting.md`
- 実装規約 → `30_development_rules.md`
- テスト計画書の配置 → `10_document_structure.md`
