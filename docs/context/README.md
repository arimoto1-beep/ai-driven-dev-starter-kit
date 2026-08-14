# docs/context（補助コンテキスト）

`docs/context/` は、会議メモ、チャット補足、過去の判断、未決事項、却下案、注意事項などを横断的に集める場所です。現在の正式資料だけでは分からない背景や、反映漏れの候補を探す手掛かりとして利用できます。

ここには、決まったこと、まだ決まっていないこと、採用しなかったことが混在します。正式資料との関係や扱い方は、下記のルール正本を参照してください。

## 内容

| 場所 | 内容 |
|---|---|
| [`rejected_verbose_option.md`](rejected_verbose_option.md) | `--verbose` オプションを追加しないとした経緯 |
| [`ai_work_logs/`](ai_work_logs/README.md) | 旧方式のAI作業ログ |
| [`work_notes/`](work_notes/README.md) | 作業の経緯、判断、手戻り、現在地を残す作業メモ |

## どこから読むか

- 特定の補助メモを確認する場合は、上の一覧から対象ファイルへ進みます。
- 旧AI作業ログが残っている理由と現在の位置づけは、[`ai_work_logs/README.md`](ai_work_logs/README.md) を参照してください。
- 作業メモの構成と入口は、[`work_notes/README.md`](work_notes/README.md) を参照してください。
- 関連する補助コンテキストを横断して探すtaskは、[`prompts/review_context.md`](../../prompts/review_context.md) を参照してください。

## メモを追加するときの入口

補助コンテキスト用のひな形は [`docs/templates/context_note_template.md`](../templates/context_note_template.md) です。メモの種別や確定状況を記載する欄があります。

ファイル名は、一覧から内容を識別できる名前を目安にします。例として、`2026-06-04_kickoff_meeting.md`、`undecided_output_format.md` のような名前があります。

## 関連するルール

- 正式資料と補助コンテキストの関係: [`rules/core/40_official_docs_and_context.md`](../rules/core/40_official_docs_and_context.md)
- 補助記録の配置: [`rules/project/10_document_structure.md`](../rules/project/10_document_structure.md)
- AIの更新権限: [`rules/project/50_ai_permissions.md`](../rules/project/50_ai_permissions.md)
- 作業メモの参照と運用: [`rules/project/60_work_notes.md`](../rules/project/60_work_notes.md)
