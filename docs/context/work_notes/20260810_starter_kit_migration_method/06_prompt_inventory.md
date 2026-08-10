# 今回作成・検証したmigration promptの棚卸し

## このファイルの目的

今回の作業では複数のmigration用promptを作成・調整・検証した。

ただし、このwork note作成時点では、
それらすべてがスターターキット内の正式promptとして配置済みとは限らない。

正確なprompt本文が正式資産として存在する場合は、
そちらを正本とする。

存在しないものについて、
このwork noteでは「作成・検証した」という事実と設計要件を残す。

記憶だけをもとに「正式path」を捏造しない。

---

## 1. Claude Code向け rules移行影響調査prompt

### 目的

既存利用者環境を新版へ移行する前に、
ファイルを変更せず影響を調査する。

### 入力モデル

- A: 旧版スターターキット基準
- B: A + 利用者固有変更
- C: 新版スターターキット基準

### 必須観点

- A / B / Cのcommitを機械的に確認
- A→Bから利用者固有変更を意味単位で抽出
- A→Cから新版構造変更を確認
- 利用者固有意図ごとに新版での吸収状態を判定
- 意味だけでなく拘束力・適用範囲・発動条件も比較
- rule / prompt / template / index等の依存を確認
- 新版作者の履歴と再利用資産を区別
- unrelatedな新版変更を移行対象へ混ぜない
- 衝突・判断不能を人間へ返す
- 読み取り専用
- STOPを許容

### 検証環境

Claude Code

- Opus 5
- Effort Max
- Thinking enabled

### 検証結果

利用者意図のsilent lossを防ぐという目的を満たした。

モデル独自の分類粒度はあるが、
移行前調査として利用可能と判断した。

---

## 2. Codex向け rules移行影響調査prompt

### 目的

Claude Code版と同じ。

ただしCodexの調査傾向に合わせ、
「新版に似た記述があるだけで吸収済みにしない」ことを特に強くした。

### 必須観点

Claude版と同様。

特に、

- route guarantee
- 部分吸収
- 拘束力低下
- trigger/frequency差
- 作者履歴除外

を明示的に見る。

### 検証環境

Codex

- GPT-5.6 Sol
- reasoning Extra High
- speed Normal

### 検証結果

Claude版とは利用者意図件数や人間判断件数が一致しなかった。

ただし、

- silent lossなし
- 部分吸収を検出
- conflictを人間へ返す
- unrelated履歴を除外

という目的は満たした。

結果の完全一致は必須ではないと判断した。

---

## 3. 人間判断後の rules移行実行prompt

### 目的

影響調査結果と人間判断を入力として、
新版構造へ実際に移行する。

### 前提

影響調査を省略していきなり実行しない。

人間が少なくとも、

- conflictの採否
- 利用者ルールを残すか
- 新版側へ寄せるか
- どのlayerへ配置するか

を確認したあとに使う。

### 必須要件

- Cを特定commit/tagへ固定
- 利用者固有意図のtraceabilityを維持
- core / project / taskの責務を壊さない
- 新版側のrule / prompt / template依存を同期
- 作者自身の履歴やunrelated変更を混入させない
- 不明点を勝手に解決しない
- commitしない
- 実施後に変更ファイルと未解決事項を報告

### 検証状況

初期版に相当する実移行は実施した。

独立レビューで一度STOPとなり、
修正後OK / GOまで到達した。

ただし、
「最終3段promptチェーンをあらゆる環境でend-to-end検証済み」
という意味ではない。

---

## 4. rules移行結果の独立レビューprompt

### 目的

移行担当AIとは別AIで結果を検証する。

### 主な確認事項

- 利用者固有意図がすべて追跡できるか
- 「確認する」が「必要に応じて」等へ弱まっていないか
- conflictが隠れていないか
- ruleだけ追加してprompt/template側に出力先がない状態がないか
- project/core/taskの責務境界が崩れていないか
- dependency ruleが矛盾していないか
- unrelated変更が入っていないか
- test結果
- 人間判断が必要な事項

### 実績

初回レビューはSTOP。

そのSTOPによって、
移行結果に残っていた複数の問題を検出できた。

修正後はOK / GO。

独立レビューを移行フローへ残す判断につながった。

---

## 5. context / work_notes移行実行prompt

### 目的

rules/work notes機構は新版導入済みだが、
`docs/context/` が旧運用の既存環境を新運用へ切り替える。

### 今回の実験で固定した変更

変更:

- `docs/context/README.md`
- `docs/context/ai_work_logs/README.md`
- `docs/context/work_notes/README.md`

保持:

- 既存contextメモ
- 既存ai_work_logs
- path
- 過去の記録内容

禁止:

- 旧ai_work_logsのwork_notes化
- 移動
- 再生成
- 削除
- 新版作者work noteのコピー
- context外変更

### 検証環境

実装:

Sonnet 5

### 検証結果

想定3ファイルだけ変更。

過去履歴は保持された。

---

## 6. context移行結果の独立レビューprompt

### 目的

context移行が「過去を壊していない」ことを別AIで確認する。

### 主な確認事項

- 変更が3ファイルだけ
- 新版3ファイルと一致
- 既存履歴3ファイルが移行前blobと一致
- work_notes配下がREADMEだけ
- 作者work note 12件がない
- rule / prompt / template参照先が存在
- context外変更なし
- 過去ログの再分類・変換なし

### 検証結果

成果物自体は問題なし。

レビュー結果:

- 軽微な指摘あり
- 条件付きGO

条件はcommit操作上の注意で、
移行内容の修正要求ではなかった。

その後3ファイルだけを明示stageし、
実験結果をcommitした。

---

# 最終的なpromptチェーン

## rules

```text
影響調査
  ↓
人間判断
  ↓
移行実行
  ↓
別AIによる独立レビュー
````

影響調査でSTOPしても、
人間判断が必要な問題を正しく出せていれば成功。

## context

```text
既存履歴を保護
  ↓
運用READMEだけ切替
  ↓
新work_notes README追加
  ↓
独立レビューで履歴不変を確認
```

rulesほど大規模な意味変換は行わない。

---

# 正式資産化について

この作業時点では、
上記prompt群をすべて正式な `prompts/` 資産として配置することまでは決めていない。

正式化する場合は、

* どのAI環境向けか
* 固定commit/tagをどう入力させるか
* A/B/Cをどう指定するか
* 読み取り専用と実装taskをどう分離するか
* 人間判断をどこで要求するか
* 独立レビューをどう接続するか

を改めて正式ruleとの整合を確認する。

今回のwork noteでは、
「この方法とprompt群を検討・実験した」という経緯を保存する。
