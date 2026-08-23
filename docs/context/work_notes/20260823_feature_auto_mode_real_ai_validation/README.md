# feature auto mode 実AI検証

## 目的

feature auto mode を実際のAIで動かし、

- AI製造開始前に人間が仕様を承認できること
- 承認後は G1 → G2 → CP3 を自動で進められること
- 問題発生時には安全に停止できること
- 原因解消後に適切な位置から復旧できること
- 最後は人間の受け入れ判断へ戻ってくること

を確認する。

単に正常系を完走できるかだけではなく、
実AIが途中でどのような動きをするか、
停止・復旧を含めて確認することを目的とした。

## 状態

完了

## 作業日

2026-08-23

## 対象

`cli_text_masker/ascii_digit_masker`

## 現在地

新しいfeature auto modeを実AIで通し実行し、
最終的にCP3 PASS、人間による受け入れ後、
runnerが「完了しました。」と認識するところまで確認した。

最終結果:

- CP1: Spec Review PASS、人間による仕様承認
- G1: PASS
- G2: PASS
- CP3: PASS
- 要求カバレッジ: 6 / 6
- テスト観点カバレッジ: 6 / 6
- pytest: 6 passed
- 最終Human Gate: 人間が受け入れ
- runner: 完了認識

途中では正常系だけでなく、

- AI実行権限不足
- `BLOCKED(state_error)`
- `--retry-blocked`
- 範囲外変更
- `BLOCKED(guard_violation)`
- 人間による原因解消
- `--review-current CP3`

も実際に発生した。

## 決定事項

### CP1はAI製造開始前の人間境界とする

`20_spec.md` は人間側で確定する仕様とし、
CP1で人間が承認するまで、
`21_design.md` 以降のAI製造成果物を作らない。

AIはCP1前にSpec Reviewを行い、
矛盾・曖昧さ・未決事項・下流で判断が必要になる空白を確認する。

CP1承認後は、承認済み仕様をbaselineとして
AI製造工程へ進む。

### BLOCKEDの履歴は残す

途中で停止したGate記録は上書きしない。

原因を解消した後も、
過去のBLOCKED記録は実行履歴として残す。

### 再実行方法を使い分ける

AIの作業そのものをやり直す必要がある場合は、

`--retry-blocked`

を使用する。

現在の成果物を変更せず、
Reviewerだけに再判定させたい場合は、

`--review-current <stage>`

を使用する。

今回の最終復旧では
`--review-current CP3` を使用した。

### stage × role の変更範囲ガードは維持する

AIが問題解決のために作成したファイルであっても、
担当stageの許可範囲外なら自動的に正当化しない。

内容の良否ではなく、
変更範囲という別の観点で停止させる。

## 未決事項

### `human_decision_required` の意味

CP1やCP3はHuman Gateである一方、
Gate front matterでは
`human_decision_required: 0`
となるケースが確認された。

runnerの動作には影響していないが、
フィールド名または値の意味が直感的ではない。

整理するかは未決。

### 新規appの初期骨格をどこで作るか

今回、CP3 Workerはテスト環境を成立させる過程で
featureの許可範囲外となるファイルへ変更を加えた。

新規app作成時に事前にどこまで初期骨格を用意するか、
feature Workerの責務をどこまでにするかは未整理。

なお、今回の事象が単純に初期骨格不足だけで発生したと
確定したわけではない。

### CP3 Worker自身のテスト成功を必須にするか

最初のCP3実行では、
Workerがテストを実行できない状態でもReviewerへ進んだ。

Reviewerで最終確認する現在の方式で十分か、
Worker自身のテスト成功を進行条件にするかは未決。

## 次に行うこと

今回の実AI検証結果をもとに、
未決事項を必要なものから個別に検討する。

修正する場合も、
今回の実験記録を残した状態で別作業として扱う。

## 付随ファイル

- `01_background_and_boundary.md`
  - CP1をAI製造前へ移した背景と設計上の考え方

- `02_real_ai_execution.md`
  - 新フローによる実AI通し試験の実行経緯

- `03_blocked_and_recovery.md`
  - 実際に発生した停止、guard、復旧方法

- `04_findings_and_remaining.md`
  - 実験から得た知見、未決事項、今後への注意点

## この作業メモの位置づけ

この作業メモは正式仕様・正式設計・ルールの正本ではない。

今回の設計が現在の形になった理由、
実AIで何が起きたか、
どこで人間判断が必要になったかを
後から人間とAIが追跡するための記録である。