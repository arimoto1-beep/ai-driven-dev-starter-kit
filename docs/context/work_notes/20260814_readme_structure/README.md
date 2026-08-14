# 作業メモ: README構成と主要導線の整理

## 目的

主要ディレクトリのREADME不足を整理し、初見の人間やAIが「何がどこにあり、次にどこを読めばよいか」を把握しやすくする。

同時に、READMEへルールや仕様が複製されて二重管理になることを避け、ルールの正本を `docs/rules/` に維持する。

## 状態

完了

README整理の実装とレビューは完了している。

2026-08-14時点で変更は未コミットであり、コミットは人間が行う。

## 現在地

READMEの役割を次の3つに限定する方針で整理した。

* 説明
* 一覧
* 導線

第1段階では、入口が不足していた主要6ディレクトリへREADMEを追加し、既存の一覧を局所READMEへ集約した。

その後のレビューで、ルートREADMEや既存のcontext・rules系READMEに、正本と重複するルール本文が残っていることが分かったため、第2段階として既存READMEも薄型化した。

最終レビューでは、今回の対象について「READMEを読めば何であるか・何があるか・次にどこを見るかが分かり、正式な判断は `docs/rules/` を参照する」状態になったと判断した。

## 決定事項

* READMEの役割は「説明・一覧・導線」に限定する。
* 正式な判断基準、制約、工程、権限などのルール正本は `docs/rules/` に置く。
* READMEへ正本の内容をコピーせず、必要な概要と正本へのリンクを置く。
* READMEがないディレクトリすべてへ機械的に追加しない。
* 親READMEや既存の設計入口で十分な場所にはREADMEを追加しない。
* 新規READMEは次の6か所とした。

  * `docs/README.md`
  * `prompts/README.md`
  * `docs/templates/README.md`
  * `docs/tutorials/README.md`
  * `tools/README.md`
  * `quality/README.md`
* `docs/rules/core/`、`docs/rules/project/`、`src/`、`tests/`、各command/app配下などには今回READMEを追加しない。
* prompt・template・tutorialの一覧は、それぞれの局所READMEを主な索引とする。
* `docs/context/README.md` に残った「一覧から内容を識別できるファイル名を目安にする」という表現は、強制ルールではなく案内として扱い、今回ルール正本へ昇格させない。
* READMEだけの第2段階では、全体pytestを完了条件としない。リンク、差分、正本との重複確認を優先する。

詳細な判断経緯は [`decision_history.md`](decision_history.md) を参照する。

## 未決事項

今回のREADME整理に関する必須の未決事項はなし。

将来検討できる事項として、次がある。

* `docs/how_to_use_prompts.md` などREADME以外の人向け説明文書と、ルール正本との境界を別作業で確認するか。
* `docs/context/README.md` のファイル名案内を、将来強制的な命名規則にする必要が生じた場合に、どの正本へ置くか。

いずれも今回の完了条件には含めない。

## 次に行うこと

* 人間が最終差分を必要に応じて確認し、今回のREADME関連変更をコミットする。

## 付随ファイル

| ファイル                                                   | 内容                                |
| ------------------------------------------------------ | --------------------------------- |
| [`decision_history.md`](decision_history.md)           | READMEの役割、配置、不採用案、第2段階が必要になった経緯   |
| [`implementation_review.md`](implementation_review.md) | Codexへの2段階の依頼、実装結果、検証、手戻り、確認上の注意点 |

## 作業期間

* 開始: 2026-08-14
* 終了: 2026-08-14

## 関連する正式文書

README整理の判断そのものをこの作業メモから正本化しない。現在有効なルールは、用途に応じて `docs/rules/` 配下の正本を参照する。

今回の作業メモ運用に関係する正本:

* `docs/rules/core/40_official_docs_and_context.md`
* `docs/rules/core/60_work_notes.md`
* `docs/rules/project/10_document_structure.md`
* `docs/rules/project/50_ai_permissions.md`
* `docs/rules/project/60_work_notes.md`
