# AGENTS.md

このキットでは、**人間が理解・レビュー・引き継ぎ・責任を持てる形で、AI駆動開発を進めます。**
AIへコードを丸投げする仕組みではありません。最終的な責任主体は人間です。

このファイルはルール集ではなく、必要なルールへ到達するための**入口**です。詳細は各正本を読んでください。

---

## 常に守る原則

- 作業を段階的に進め、必要な工程・レビュー・承認を飛ばさない
- 仕様にない機能を勝手に追加しない
- 不明点や未決事項を黙って補完しない
- 仮定を置く場合は、仮定であることと理由を明示する
- AIだけで判断できない内容は、人間判断事項として報告する
- 対象外のファイルや保護対象を勝手に変更しない
- レビュー結果（成果物の状態）と次工程移行判定（次へ進んでよいか）を混同しない
- 次工程移行判定は `GO` / `条件付きGO` / `STOP` の3値で整理し、**最終判断は人間が行う**

各原則の条件と例外は、下記の正本に定義されています。ここでは再定義しません。

---

## 読む順番

作業開始時は、まず次の2つを必ず読みます。

1. このファイル
2. `docs/rules/project/00_project_policy.md`（このプロジェクトの設定と索引）

**task プロンプトが指定されている場合**は、続けて次の順で読んでください。

3. 指定された `prompts/*.md`
4. その task プロンプトの `## 必須参照ルール` に列挙された文書
5. その task プロンプトの `## 参照するファイル` に示された作業対象資料

**そのtaskで読むルール文書の一覧は、task プロンプトの `## 必須参照ルール` が正本です。** このファイルには task 別の対応表を置きません。

---

## task プロンプトが指定されていない場合

作業を粗く分類し、該当する起点を読んでください。複数にまたがる場合は組み合わせます。

| 作業の性質 | 起点 |
|---|---|
| **実装・変更**（仕様変更を含む） | `core/10_workflow.md`、`core/30_change_safety.md`、`project/20_workflow.md`、`project/30_development_rules.md`、`project/40_testing_rules.md`、`project/50_ai_permissions.md` |
| **レビュー・承認** | `core/20_approval_and_review.md`、`project/20_workflow.md`、`project/25_review_policy.md`、`project/50_ai_permissions.md` |
| **補助コンテキスト** | `core/40_official_docs_and_context.md`、`project/10_document_structure.md`、`project/50_ai_permissions.md` |
| **記録・報告** | `core/50_records_and_reporting.md`、`project/10_document_structure.md`、`project/50_ai_permissions.md` |

（パスはすべて `docs/rules/` 配下です）

これは task プロンプトがない場合の入口にすぎません。**どの分類か判断できない場合、AIが勝手に決めず人間へ確認してください。**

---

## core / project / task の関係

```text
core     すべてのプロジェクトで守る安全境界（docs/rules/core/）
project  core の範囲内で、このキット固有の設定を具体化する（docs/rules/project/）
task     core と project の範囲内で、個別作業の手順を定める（prompts/*.md）
```

- **project は core を無効化・緩和できません。**
- **task は core や project を再定義できません。** task 固有の説明は、正本の判定値や原則を変更するものではありません。
- 三者が矛盾して読める場合、**AIは勝手に優先順位を決めません。** 矛盾箇所と影響を整理し、人間判断事項として報告してください。

---

## 作業完了時

`docs/rules/core/50_records_and_reporting.md` を確認し、少なくとも次を報告してください。

- 実際に変更したファイル
- 実施した確認・テスト
- 未対応事項／人間判断が必要な事項
- 更新しなかった関連資料と、その理由
- 次に必要な作業
- 指定された task プロンプトが求める追加報告

報告形式の詳細は `core/50_records_and_reporting.md` と各 task プロンプトを正本とします。

**ルール体系の索引 → `docs/rules/README.md`**
