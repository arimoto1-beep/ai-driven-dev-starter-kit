# 実装済み feature に追加修正するチュートリアル

このチュートリアルでは、実装済み feature `cli_text_counter` を題材に、変更要求を受けたときの安全な進め方を体験します。

変更要求は、人から依頼される場合もあれば、コードを読んでいて自分で思いつく場合もあります。後者のように、バグなのか仕様変更なのか設計改善なのかが未確定な場合は、`prompts/analyze_code_change_impact.md` で分類と影響範囲を整理してから進めます。

---

## このチュートリアルの目的

既存コードをこっそり直接修正することではありません。

変更要求を受けたときに、**既存の docs / 実装 / テスト / tasks.md / レビュー結果を確認し、影響範囲を整理してから、AIに別作業として修正を依頼する流れ**を体験することです。

変更対象・変更理由・確認結果・未対応事項を作業報告として残すことで、AIと人間が同じ現在地を共有できます。

---

## 010 / 020 との違い

| | チュートリアル | 目的 | 開始状態 |
|---|---|---|---|
| [010](010_simple_calculator.md) | simple_calculator | 初期状態から単一 feature を設計・実装・テスト・レビューする | 仕様書と tasks.md のみ用意済み |
| [020](020_create_new_sample_from_scratch.md) | cli_text_tools（新規作成） | 新しい command/app と複数 feature の初期 docs 構造を作る | 完全にゼロから作る |
| **030（このチュートリアル）** | **cli_text_counter** | **実装済み feature に対して仕様変更・軽微な機能追加・内部設計の改善・リファクタリング・類似機能間の整合性改善・レビュー指摘反映を行う（バグ修正は 040 を参照）** | **docs / src / tests がすべて揃った完成済みサンプル** |

---

## 題材

### command/app

`cli_text_counter`

入力文字列の文字数を数えて返すシンプルな CLI です。

実行例:

```bash
python src/cli_text_counter/entrypoint.py --text "hello"
```

出力例:

```text
5
```

### 対象 feature

`text_counter` — 入力文字列の文字数を整数として返す feature です。

| ファイル | 役割 |
|---|---|
| `docs/cli_text_counter/10_overview.md` | command/app 全体の目的・責務分担 |
| `docs/cli_text_counter/tasks.md` | command/app 全体の現在地メモ |
| `docs/cli_text_counter/features/text_counter/tasks.md` | feature の現在地メモ |
| `docs/cli_text_counter/features/text_counter/20_spec.md` | feature の仕様 |
| `docs/cli_text_counter/features/text_counter/21_design.md` | 関数設計 |
| `docs/cli_text_counter/features/text_counter/22_flow.md` | 関数呼び出し定義 |
| `docs/cli_text_counter/features/text_counter/23_test_plan.md` | 単体テスト計画 |
| `docs/cli_text_counter/features/text_counter/24_review_checklist.md` | レビュー観点 |
| `docs/cli_text_counter/features/text_counter/25_review_result.md` | feature 単体レビュー結果 |
| `src/cli_text_counter/features/text_counter.py` | feature 実装 |
| `tests/cli_text_counter/features/test_text_counter.py` | feature 単体テスト |
| `src/cli_text_counter/entrypoint.py` | CLI入口 |
| `tests/cli_text_counter/test_entrypoint_text_counter.py` | entrypoint テスト |
| `tests/cli_text_counter/test_integration_text_counter.py` | 結合試験 |

---

## 変更作業の基本方針

### こっそり修正しない

設計・仕様・実装・テスト・`tasks.md` に影響する修正は、人間が直接ファイルを編集するのではなく、AIに別作業として依頼することを基本とします。

AIに直させること自体が目的ではありません。変更対象、変更理由、確認結果、未対応事項を作業報告として残し、AIと人間が同じ現在地を共有するためです。

AIも人間も、調査中・レビュー中・説明中に、ついで修正やこっそり修正を行いません。

### 正本を決めてから、上流から下流へ進む

変更前に、影響する資料を並べるだけで終わらせません。変更内容を正式に定義する資料（正本）を特定し、正本から下流へ順番に反映します。

正本とは、その変更内容を最初に定義し、下流資料や実装が参照・具体化する基準となる正式資料です。最も上流かつ役割の合う資料を選ぶという意味であり、上流資料をすべて変更するという意味ではありません。変更不要な上流資料は、理由を示して更新しません。

### 人間が反映対象を判断する

AIが出した修正候補や指摘をすべて反映するのではなく、人間が内容を確認したうえで反映する指摘と保留する指摘を判断します。

### AIに別作業として修正を依頼する

修正を依頼するときは、変更してよいファイルと変更してはいけないファイルを明示します。変更理由や確認結果も合わせて伝えると、AIが作業報告に残しやすくなります。

### 作業報告を残す

AIの作業後に、変更対象、変更理由、確認結果、未対応事項が作業報告に記録されていることを確認します。

### tasks.md は現在地メモとして必要最小限更新する

修正後に `tasks.md` を確認し、現在の状態と次にやることを短く更新します。仕様・設計・テスト計画・レビュー結果の詳細は `tasks.md` には書きません。

---

## 変更前に確認するファイル

変更要求を受けたとき、まず以下のファイルを確認します。

| ファイル | 確認のポイント |
|---|---|
| `10_overview.md` | 変更要求が command/app の責務範囲に収まるか |
| command/app `tasks.md` | command/app 全体の現在地・保留事項 |
| feature `tasks.md` | feature の現在地・次の作業 |
| `20_spec.md` | 現在の仕様・前提条件 |
| `21_design.md` | 変更対象の関数・責務 |
| `22_flow.md` | 呼び出し関係への影響 |
| `23_test_plan.md` | 既存のテスト観点との整合 |
| `24_review_checklist.md` | レビュー観点への影響 |
| `25_review_result.md` | 過去のレビュー指摘・改善候補 |
| feature 実装ファイル | 現在の実装内容 |
| feature 単体テストファイル | 現在のテスト内容 |
| `entrypoint.py` | 出力形式・引数への影響がないか |
| entrypoint テスト | entrypoint 側のテストへの影響 |
| 結合試験 | 結合試験への影響 |

---

## 変更パターン別の進め方

| 変更パターン | まず確認するもの | 更新候補 | 注意点 |
|---|---|---|---|
| **仕様変更** | `20_spec.md`、`10_overview.md` | `20_spec.md`、`21_design.md`、`22_flow.md`、`23_test_plan.md`、実装、テスト | 仕様変更は feature 全体に波及しやすい。正本は原則 `20_spec.md`。command/app の責務や feature 分割に影響する場合は `10_overview.md` から確認・更新する |
| **軽微な機能追加** | `20_spec.md`、`21_design.md`、`23_test_plan.md` | `20_spec.md`、`21_design.md`、`23_test_plan.md`、実装、テスト | feature 責務の範囲内か確認する。範囲を超える場合は仕様変更として扱う |
| **判定条件の変更** | `20_spec.md`、`23_test_plan.md` | `20_spec.md`、`23_test_plan.md`、実装、テスト | 境界値が変わる場合はテスト計画を先に整理する |
| **出力項目の追加** | `20_spec.md`、`22_flow.md`、`entrypoint.py`、結合試験 | `20_spec.md`、`21_design.md`、`22_flow.md`、実装、テスト、entrypoint、entrypoint テスト、結合試験 | feature の戻り値変更は entrypoint と結合試験に影響する可能性が高い |
| **内部設計の改善** | `21_design.md`、`22_flow.md`、feature 実装 | `21_design.md`、`22_flow.md`、実装、テスト | 外部動作が変わらなければ `21_design.md` を正本候補とし、`20_spec.md` は更新しない。呼び出し関係が変わる場合は `22_flow.md` へ反映する。設計書を先に更新してから実装する |
| **動作を変えないリファクタリング** | `21_design.md`、`23_test_plan.md`、feature 実装、feature 単体テスト | `21_design.md`、実装、必要に応じてテスト | 外部動作を変えないことを既存テストで確認する。テストが実装詳細に依存していないかも確認する |
| **類似機能間の実装方式の統一** | 対象と比較対象の `20_spec.md`、`21_design.md`、実装 | 統一対象に決めた feature の `21_design.md`、実装、テスト | 「他と違う」だけを理由に統一しない。差異が仕様由来かを先に確認し、どれを基準にするかは人間が決める。各 feature へ同じルールをばらまく前に、正本の配置を決める |
| **複数 feature にまたがる標準化** | `10_overview.md`、対象 feature 群の `21_design.md`、実装 | 対象 feature ごとの `21_design.md`、実装、テスト | 一度に全 feature を変更せず、feature 単位で順番に進める。一か所だけ変えて新たな不統一を作らない。正本の配置が決まるまで横断変更を始めない |
| **共通化候補** | `21_design.md`、`common_design/`、`docs/common/` | `docs/common/` の共通化提案 | AIが勝手に `src/common/` へ切り出さない。まず `docs/templates/30_common_proposal_template.md` で提案を整理し、人間が判断する。`common_design/` の役割（ファイル設計・データ設計・DB設計）に合わない内容を無理に入れない |
| **バグ修正** | → [040_bug_fix_flow.md](040_bug_fix_flow.md) を参照 | — | バグ修正は常に 040 のフロー（バグ報告→調査→修正計画→人間承認→実装）に従う。この表の対象外 |
| **レビュー指摘の反映** | `25_review_result.md`、`12_command_review_result.md` | 指摘内容による | 人間がどの指摘を反映するかを判断してからAIに依頼する |

既存 feature の変更全般はこのチュートリアルで扱います。ただし、バグ修正は軽微なものも含め、必ず [040_bug_fix_flow.md](040_bug_fix_flow.md) のフロー（バグ報告→調査→修正計画→人間承認→実装）に従ってください。このチュートリアルで直接バグを修正する簡易パスは設けません。

どの変更パターンに当たるか分からない場合は、この表で決め打ちせず、後述の「変更案の影響範囲を整理する」で `prompts/analyze_code_change_impact.md` を使って分類から整理してください。

変更内容を定義する適切な正本が現在の構成に見つからない場合は、各 feature へ同じルールを重複記載したり、新しい文書を作ったりせず、人間判断に戻してください。

---

## 例: 軽微な機能追加を行う

`cli_text_counter` を題材に、軽微な機能追加の例を示します。

### 変更要求

文字数カウントで、**空白を除外して数えるオプション**を追加したい。

### まず確認すること

1. `20_spec.md` を確認し、空白除外カウントが既存の責務内に収まるか判断する
2. `21_design.md` を確認し、既存の `count_characters` 関数に引数を追加するか、別関数にするかを考える
3. `23_test_plan.md` を確認し、空白除外に関するテスト観点を追加する必要があるか確認する
4. `entrypoint.py` を確認し、新しいCLI引数（例: `--exclude-spaces`）が必要になるか確認する
5. 結合試験への影響を確認する

### 進める順番の例

以下の順番で進めます。

この例では利用者から見える動作が変わるため、`20_spec.md` が正本候補になります。実装や設計より先に仕様を更新し、そこから下流へ進めます。`10_overview.md` は、feature 分割や command/app の責務が変わらないため更新しません。

```text
1. AIに影響範囲と正本・更新順を整理させる（analyze_code_change_impact.md を参照。ファイルを変更しない）
2. 人間が正本と更新順を確認し、修正対象を決める
3. 正本の 20_spec.md の更新をAIに依頼する（更新内容を人間が確認する）
4. 21_design.md の更新をAIに依頼する
5. 23_test_plan.md の更新をAIに依頼する
6. feature 実装と feature 単体テストの更新をAIに依頼する（implement_feature.md を参照）
7. feature ソースレビューを行う（review_feature_source.md を参照）
8. entrypoint と entrypoint テストの更新をAIに依頼する（影響がある場合）
9. 結合試験の更新をAIに依頼する（影響がある場合）
10. python -m pytest を実行する
11. 必要に応じて review_feature.md / review_command.md で再レビューする
```

---

## 変更案の影響範囲を整理する

変更作業の最初のステップです。`prompts/analyze_code_change_impact.md` を使って、AIに影響範囲を整理させます。**このステップではファイルを変更しません。**

このプロンプトは、変更案がバグなのか、仕様変更なのか、内部設計変更・リファクタリング・類似機能間の整合性改善・標準化・共通化候補なのかを分けて整理し、影響する資産と次に進むべきフローをチャットで報告します。

### 例1: 機能追加の影響範囲を整理する

```text
prompts/analyze_code_change_impact.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
変更したい内容: 文字数カウントで、空白を除外して数えるオプションを追加したい
変更したい理由または違和感: 利用者から「空白なし文字数も知りたい」という要望があった
関連する実装ファイル: src/cli_text_counter/features/text_counter.py
関連するテストファイル: tests/cli_text_counter/features/test_text_counter.py
類似機能または比較対象: なし
外部から見える動作を変えたいか: 変えたい
調査対象範囲: cli_text_counter 全体（entrypoint と結合試験を含む）
補足条件: 分析だけ行い、ファイルは変更しないでください。
```

### 例2: 正常に動いているコードの改善案を整理する

正常に動いていても、内部構造を改善したい場合や、類似機能と実装方式をそろえたい場合に使います。

```text
prompts/analyze_code_change_impact.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
変更したい内容: 入力チェックとエラーの返し方を、cli_hello_greeting の greeting と同じ方式にそろえたい
変更したい理由または違和感: 動作は仕様どおりだが、この feature だけ書き方が違って読みにくい
関連する実装ファイル: src/cli_text_counter/features/text_counter.py
関連するテストファイル: tests/cli_text_counter/features/test_text_counter.py
類似機能または比較対象: src/cli_hello_greeting/features/greeting.py
外部から見える動作を変えたいか: 変えたくない
調査対象範囲: cli_text_counter と cli_hello_greeting の feature 実装
補足条件: 分析だけ行い、ファイルは変更しないでください。
```

分析結果には、次の内容も含まれます。

- 変更内容の正本（変更内容を定義すべき最上流かつ役割の合う正式資料）
- 変更不要と判断した上流資料と、その理由
- 上流から下流への更新順
- 正本の配置に関する人間判断事項（適切な正本が存在しない場合を含む）

AIから分析結果（総合判定・変更の分類・影響する資産・変更の正本と更新順・推奨する次の作業）が報告されたら、人間が正本と更新順を確認して次のステップに進みます。

- バグ候補と分類された場合は、このチュートリアルではなく [040_bug_fix_flow.md](040_bug_fix_flow.md) のフローへ進みます
- 仕様変更・機能追加・内部設計変更・リファクタリング・整合性改善の場合は、このチュートリアルの以降の手順で進めます
- 共通化候補の場合は、`docs/templates/30_common_proposal_template.md` を使った提案作成を別作業として依頼します。AIが `src/common/` を勝手に変更することはありません

---

## 反映作業をAIに依頼するプロンプト例

影響範囲を人間が確認した後、具体的な修正をAIに依頼します。以下はチャット例です（このチュートリアルでは実際の修正は行いません）。

### 仕様・設計・テスト計画の更新を依頼する例

```text
AGENTS.md を確認したうえで、以下の変更を行ってください。

変更要求:
- text_counter feature に、空白を除外して文字数を数えるオプションを追加する
- 変更理由: 利用者から「空白なし文字数も知りたい」という要望があった

変更してよいファイル:
- docs/cli_text_counter/features/text_counter/20_spec.md
- docs/cli_text_counter/features/text_counter/21_design.md
- docs/cli_text_counter/features/text_counter/23_test_plan.md
- docs/cli_text_counter/tasks.md
- docs/cli_text_counter/features/text_counter/tasks.md

変更してはいけないファイル:
- src/cli_text_counter/features/text_counter.py（今回は docs のみ更新）
- tests/cli_text_counter/features/test_text_counter.py（今回は docs のみ更新）
- src/cli_text_counter/entrypoint.py
- tests/cli_text_counter/test_entrypoint_text_counter.py
- tests/cli_text_counter/test_integration_text_counter.py
- docs/templates/
- prompts/
- AGENTS.md
- README.md

補足条件: 仕様は 20_spec.md に先に反映してください。entrypoint への影響は後続の作業で扱います。
```

### feature 実装とテストの更新を依頼する例（docs 更新後）

```text
prompts/implement_feature.md を参照してください。

対象機能フォルダ: docs/cli_text_counter/features/text_counter/
コマンド/アプリ名: cli_text_counter
対象機能名: text_counter
実装ファイル: src/cli_text_counter/features/text_counter.py
テストファイル: tests/cli_text_counter/features/test_text_counter.py
作りたいもの: 空白を除外して文字数を数えるオプションを追加する
補足条件:
- 更新済みの 20_spec.md / 21_design.md / 23_test_plan.md に従って実装してください。
- 既存の count_characters 関数の動作は変えないでください。
- 変更対象と変更理由を作業報告に残してください。
```

### ソースレビューを依頼する例（feature 更新後）

```text
prompts/review_feature_source.md を参照してください。

対象機能フォルダ: docs/cli_text_counter/features/text_counter/
コマンド/アプリ名: cli_text_counter
対象機能名: text_counter
実装ファイル: src/cli_text_counter/features/text_counter.py
テストファイル: tests/cli_text_counter/features/test_text_counter.py
補足条件: ソースレビューだけ行い、実装ファイル・テストファイル・docs・tasks.md は変更しないでください。
```

---

## レビュー指摘を反映する場合

`25_review_result.md` または `12_command_review_result.md` に指摘がある場合は、以下の流れで進めます。

1. レビュー結果を人間が確認する
2. 反映する指摘と保留する指摘を人間が判断する
3. 反映する指摘を明示して、AIに別作業として修正を依頼する
4. AIが変更ファイル・変更理由・確認結果・未対応事項を作業報告として残す
5. `python -m pytest` を実行する
6. 必要に応じて `prompts/review_feature.md` または `prompts/review_command.md` で再レビューする

### レビュー指摘の反映を依頼するチャット例

```text
AGENTS.md を確認したうえで、以下のレビュー指摘を反映してください。

反映する指摘:
- docs/cli_text_counter/features/text_counter/25_review_result.md の「改善候補」に記載の内容

変更してよいファイル:
- 指摘内容に応じて判断（AIが提示する）

変更してはいけないファイル:
- docs/cli_text_counter/features/text_counter/25_review_result.md（このファイルは再レビュー時に上書きされる）
- prompts/
- AGENTS.md
- README.md
- docs/templates/

補足条件:
- 変更対象と変更理由を作業報告に残してください。
- 作業後に python -m pytest を実行してください。
```

---

## 作業後に確認すること

- 変更対象と変更理由が作業報告に残っているか
- `tasks.md` が現在地メモとして必要最小限更新されているか（詳細は書かれていないか）
- 仕様・設計・テスト計画・実装・テストのズレがないか
- ついで修正やこっそり修正がないか（変更してよいファイル以外が変更されていないか）
- `python -m pytest` が通っているか
- 必要なレビューを行ったか（`review_feature_source.md`、必要に応じて `review_feature.md` / `review_command.md`）

---

## 進めるときの注意

- 影響範囲の確認ステップではファイルを変更しません
- `prompts/*.md` は直接編集しません
- チャットでは、参照するプロンプトのパス、変更対象、変更理由、今回だけの補足条件を渡します
- feature の変更が entrypoint に影響する場合は、entrypoint の修正も別作業として依頼します
- 変更後は必ず `python -m pytest` を実行します
- `tasks.md` には仕様・設計・テスト計画・レビュー結果の詳細を書きません
- 変更要求が feature の責務を超える場合は、`10_overview.md` に戻って feature 分割から見直します
