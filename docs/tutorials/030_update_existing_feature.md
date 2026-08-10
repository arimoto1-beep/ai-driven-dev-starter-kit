# 実装済み feature に追加修正するチュートリアル

このチュートリアルでは、実装済み feature `cli_text_counter` を題材に、変更要求を受けたときの進め方を体験します。

変更要求は、人から依頼される場合もあれば、コードを読んでいて自分で思いつく場合もあります。どの場合でも、中心となる問いは同じです。

```text
この変更は、正式資料で意味を定義・維持する必要があるか。
```

---

## このチュートリアルの目的

**変更をどこまで正式な意味として残すかを判断し、必要な範囲だけ反映する流れ**を体験することです。

すべての変更を仕様書から始めるわけではありません。実装詳細だけで完結する変更もあれば、正式資料から反映すべき変更もあります。**その見極めがこのチュートリアルの中心です。**

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

### 変更の意味を見極める

中心の問いは「この変更は、正式資料で意味を定義・維持する必要があるか」です。

**「どこから変更を始めたか」や「人間が直したか、AIが直したか」を中心にはしません。**

判断には**2つの異なる軸**を使います。混同しないでください。

- **変更ルート**：この変更を、正式資料でどう扱うべきか
- **実施状態**：この変更が、実際にどこまで進んでいるか

少なくとも次の変更ルートがあります。

| ルート | 内容 | 進み方 |
|---|---|---|
| **A. 実装詳細で完結する変更** | 正式資料が意味を定義していない範囲だけが変わる（可読性の改善、冗長な処理の整理、局所的なリファクタリングなど） | 正式資料を無理に更新しない。コードとテストの整合・検証・レビュー・報告は行う |
| **B. 正式資料から下流へ反映する変更** | 正式資料で定義すべき意味が変わる（外部動作、責務、制約、処理フロー、共通設計など） | 正本を特定し、そこから下流へ反映する |
| **C. コードから正式資料へ逆反映する変更** | コードを読んだ結果、今後も守るべき仕様・設計・共通方針だと分かった | 役割の合う正式資料へ、別作業として反映する |
| **判断不能** | 上記を確定できない | 人間判断へ戻す |

実施状態は、未着手・一部実施・実施済みに加えて、**コード先行**（障害対応などで正式資料への反映より先にコードを変更した状態）の有無を確認します。

**コード先行は、変更ルートB・Cのいずれでも起こりえます。独立した変更ルートではありません。** コード先行がある場合は、後から正式資料へ反映し、必要なテストとレビューを行います。

判断に迷う場合は、`prompts/analyze_code_change_impact.md` で整理します。**このプロンプトは、変更する前でも、変更した後でも使えます。**

ルール上の正本は `docs/rules/core/10_workflow.md` です。

### 未記載と矛盾を分ける

- **未記載**（正式資料が実装詳細を規定していないが、意味には反していない）… **それだけでは不整合ではありません**
- **矛盾**（正式資料が定義している意味とコードが食い違っている）… **従来どおり問題です**

生成AIが書いたコードには、同じ仕様・設計でも実装上の揺らぎ（関数の切り方、変数名、局所的な書き方など）があります。**これらをすべて設計書へ書き写す必要はありません。** 設計書が実装詳細の写経になると、かえって保守できなくなります。

一方で、仕様にない便利機能、外部から見える動作の変更、責務としての意味の変更は、「未記載だから問題なし」とはしません。

### 人間がコードを直接修正してもかまいません

**人間がソースコードを直接修正することは禁止されていません。** 修正した後で、その変更が上記のどの変更ルートに当たるかを確認します。あわせて、実施状態（すでに直したこと、コード先行かどうか）も確認します。**変更ルートと実施状態は別の軸です。**

- 実装詳細で完結する変更（ルートA）なら、正式資料の更新は不要です
- 正式資料へ反映すべき意味を含む場合（ルートB・C）は、別作業として反映します。すでにコードを先行して直している場合は、後追いで反映します
- 判断に迷う場合は `prompts/analyze_code_change_impact.md` に、実施済みの変更（Git差分）を入力して整理できます

**このために、新しい承認工程や毎回の記録作成といった重い運用は設けていません。** Git差分、通常のコミット履歴、テスト、レビュー、既存の作業報告で足りる場合はそれを使います。

### ただし、AIの権限は変わりません

**人間がコードを直接修正してよいことと、AIが自由にコードを修正してよいことは、別の問題です。**

AIは引き続き、次を守ります。

- その task で許可された範囲だけを変更する
- 調査中・レビュー中・説明中に、ついで修正やこっそり修正をしない
- 保護対象を人間の明示指示なしに変更しない
- 人間判断事項を確定しない
- 変更ルートを「実装詳細で完結する（ルートA）」と判断したことを理由に、自分の作業範囲を広げない

これは人間にも当てはまります。**調査中・レビュー中・説明中のついで修正は、人間も行いません。**

### 人間が反映対象を判断する

AIが出した修正候補や指摘をすべて反映するのではなく、人間が内容を確認したうえで反映する指摘と保留する指摘を判断します。

### AIに修正を依頼する場合

修正を依頼するときは、変更してよいファイルと変更してはいけないファイルを明示します。変更理由や確認結果も合わせて伝えると、AIが作業報告に残しやすくなります。

### 作業報告を残す

AIの作業後に、変更対象、変更理由、確認結果、未対応事項が作業報告に記録されていることを確認します。正式資料を更新しなかった場合は、**更新不要と判断した理由**が残っていることを確認します。

### tasks.md は現在地メモとして必要最小限更新する

修正後に `tasks.md` を確認し、現在の状態と次にやることを短く更新します。仕様・設計・テスト計画・レビュー結果の詳細は `tasks.md` には書きません。

---

## 変更の意味を確認するために見るファイル

変更要求を受けたとき、または変更した後で意味を確認するとき、以下のファイルを見ます。

**すべてを毎回更新するわけではありません。** 何を更新するかは、変更の型によって決まります。

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

この表の「変更ルート」は `docs/rules/core/10_workflow.md` が定める A（実装詳細で完結）／B（正式資料から下流へ）／C（コードから逆反映）のいずれかです。**「コード先行」（正式資料への反映より先にコードを変更した状態）は変更ルートではなく実施状態であり、B または C のどちらのルートでも起こりえます。** 障害対応でコードを先に直した場合は、まずこの表でルートを判定したうえで、下記「コードを先に変更した場合」もあわせて確認してください。

| 変更パターン | 変更ルート | まず確認するもの | 更新候補 | 注意点 |
|---|---|---|---|---|
| **仕様変更** | B | `20_spec.md`、`10_overview.md` | `20_spec.md`、`21_design.md`、`22_flow.md`、`23_test_plan.md`、実装、テスト | 仕様変更は feature 全体に波及しやすい。正本は原則 `20_spec.md`。command/app の責務や feature 分割に影響する場合は `10_overview.md` から確認・更新する |
| **軽微な機能追加** | B | `20_spec.md`、`21_design.md`、`23_test_plan.md` | `20_spec.md`、`21_design.md`、`23_test_plan.md`、実装、テスト | feature 責務の範囲内か確認する。範囲を超える場合は仕様変更として扱う |
| **判定条件の変更** | B | `20_spec.md`、`23_test_plan.md` | `20_spec.md`、`23_test_plan.md`、実装、テスト | 境界値が変わる場合はテスト計画を先に整理する |
| **出力項目の追加** | B | `20_spec.md`、`22_flow.md`、`entrypoint.py`、結合試験 | `20_spec.md`、`21_design.md`、`22_flow.md`、実装、テスト、entrypoint、entrypoint テスト、結合試験 | feature の戻り値変更は entrypoint と結合試験に影響する可能性が高い |
| **内部設計の改善**（設計書が定めた責務や呼び出しの意味が変わる） | B | `21_design.md`、`22_flow.md`、feature 実装 | `21_design.md`、`22_flow.md`、実装、テスト | 外部動作が変わらなければ `21_design.md` を正本候補とし、`20_spec.md` は更新しない。呼び出し関係として維持すべき意味が変わる場合は `22_flow.md` へ反映する |
| **動作も設計上の意味も変えないリファクタリング** | **A** | feature 実装、feature 単体テスト、`21_design.md`（矛盾しないことの確認） | **実装、必要に応じてテストのみ** | **`21_design.md` を無理に更新しない。** 関数の切り方や局所的な書き方の変更は、設計書が定めた責務・呼び出しの意味を変えない限り、正式資料への反映は不要。外部動作を変えないことを既存テストで確認する |
| **類似機能間の実装方式の統一** | A・B・Cいずれもあり得る（起点による） | 対象と比較対象の `20_spec.md`、`21_design.md`、実装 | 差異の性質による | **「他と違う」だけを理由に統一しない。** 差異が仕様由来かを先に確認する。単なる実装上の揺らぎをそろえるだけで、正式な意味として維持しないならルートA（実装だけ）で足りる。人間が先に「今後はこの方式を正式な標準にする」と決めて正式資料から変更するならルートB。コードを比較・修正している途中で「今後も共通して守るべきだ」と気づいたならルートC。**変更内容だけで固定せず、正式な意味として維持するか・どこを起点に決まったかで判定する。** すべての統一を正式資料へ残す方向にはしない |
| **複数 feature にまたがる標準化** | BまたはC（起点による） | `10_overview.md`、対象 feature 群の `21_design.md`、実装 | 正式化する場合の反映先、対象 feature ごとの実装 | **「標準化だから常にC」ではありません。** 先に人間が「今後この方式を正式ルールにする」と決めて正式資料から変更する場合はルートB、コードを比較していて気づいた場合はルートCです。判定基準は「どこでその正式な意味を定義することになったか」。一度に全 feature を変更せず、feature 単位で順番に進める。一か所だけ変えて新たな不統一を作らない。正本の配置が決まるまで横断変更を始めない |
| **共通化候補** | BまたはC（起点による） | `21_design.md`、`common_design/`、`docs/common/` | `docs/common/` の共通化提案 | AIが勝手に `src/common/` へ切り出さない。まず `docs/templates/30_common_proposal_template.md` で提案を整理し、人間が判断する。`common_design/` の役割（ファイル設計・データ設計・DB設計）に合わない内容を無理に入れない |
| **バグ修正** | — | → [040_bug_fix_flow.md](040_bug_fix_flow.md) を参照 | — | バグ修正は常に 040 のフロー（バグ報告→調査→修正計画→人間承認→実装）に従う。この表の対象外 |
| **レビュー指摘の反映** | 指摘内容による | `25_review_result.md`、`12_command_review_result.md` | 指摘内容による | 人間がどの指摘を反映するかを判断してからAIに依頼する |

既存 feature の変更全般はこのチュートリアルで扱います。ただし、バグ修正は軽微なものも含め、必ず [040_bug_fix_flow.md](040_bug_fix_flow.md) のフロー（バグ報告→調査→修正計画→人間承認→実装）に従ってください。このチュートリアルで直接バグを修正する簡易パスは設けません。

### 障害対応でコードを先に直した場合

これは変更パターンではなく、**実施状態（コード先行）** です。上の表で該当する変更ルート（多くは B または C）を判定したうえで、次を確認します。

- **人間がコード先行を選んだ場合に限ります。AIが自ら選ぶことはありません。**
- 実施済みの差分と、対応する正式資料を確認します
- 後追いで反映すべき資料、必要なテストを整理します
- 未了項目を残課題として明示します

どの変更パターンに当たるか分からない場合は、この表で決め打ちせず、後述の「変更の意味と変更ルートを整理する」で `prompts/analyze_code_change_impact.md` を使って整理してください。

**正本が見つからないこと自体は、作業を止める理由になりません。** 正式資料が意味を定義していない実装詳細であれば、ルートAとしてコードとテストだけで完結できます。ただし、本来正式資料へ残すべき意味なのに置き場がない場合は、各 feature へ同じルールを重複記載したり新しい文書を作ったりせず、人間判断に戻してください。

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

この例では利用者から見える動作が変わります。したがって**変更ルートB（正式資料を正本として下流へ反映）**であり、`20_spec.md` が正本候補になります。実装や設計より先に仕様を更新し、そこから下流へ進めます。`10_overview.md` は、feature 分割や command/app の責務が変わらないため更新しません。

```text
1. AIに変更の意味と変更ルートを整理させる（analyze_code_change_impact.md を参照。ファイルを変更しない）
2. 人間が変更ルート・正本・更新順を確認し、修正対象を決める
3. 正本の 20_spec.md の更新をAIに依頼する（更新内容を人間が確認する）
4. 21_design.md の更新をAIに依頼する
5. 23_test_plan.md の更新をAIに依頼する
6. 24_review_checklist.md を確認し、人間が実装着手承認欄にチェックを入れる
7. feature 実装と feature 単体テストの更新をAIに依頼する（implement_feature.md を参照）
8. feature ソースレビューを行う（review_feature_source.md を参照）
9. entrypoint と entrypoint テストの更新をAIに依頼する（影響がある場合）
10. 結合試験の更新をAIに依頼する（影響がある場合）
11. python -m pytest を実行する
12. 必要に応じて review_feature.md / review_command.md で再レビューする
```

### ルートAだった場合はどうなるか

同じ `cli_text_counter` でも、たとえば「`count_characters` の内部で使っている一時変数の名前を分かりやすくする」「同じ意味の分岐をまとめる」といった変更なら、**変更ルートA（正式資料への反映不要）**になります。

```text
1. AIに変更の意味と変更ルートを整理させる（analyze_code_change_impact.md を参照。ファイルを変更しない）
2. 人間がルートAであることを確認する
   → 20_spec.md、21_design.md、22_flow.md、23_test_plan.md は更新しない
3. 24_review_checklist.md の実装着手承認欄を人間が確認する（ルートAでも省略しない）
4. feature 実装（必要ならテスト）の更新をAIに依頼する
5. feature ソースレビューを行う（review_feature_source.md を参照）
6. python -m pytest を実行する
7. 作業報告に、正式資料を更新しない理由が残っていることを確認する
```

**設計書へ「一時変数の名前」や「分岐のまとめ方」を書き写す必要はありません。** これらは正式資料が意味を定義していない実装詳細です。

ただし、この変更で `21_design.md` が定めた責務や `20_spec.md` が定めた外部動作が変わってしまう場合は、ルートAではありません。

---

## 変更の意味と変更ルートを整理する

`prompts/analyze_code_change_impact.md` を使って、AIに変更の意味を整理させます。**このステップではファイルを変更しません。**

**このプロンプトは、変更する前でも、変更した後でも使えます。**

分析結果では、変更点ごとに次の**変更ルート**と根拠、および**実施状態**が報告されます。この2つは別の軸です。

**変更ルート:**

- A. 正式資料への反映不要（実装詳細で完結する）
- B. 正式資料を正本として下流へ反映
- C. コード起点の知見を正式資料へ逆反映
- 判断不能

**実施状態:**

- 未着手／一部実施／実施済み
- コード先行の有無（ある場合、ルートB・Cのどちらでも起こりえます）

### 例1: これから行う機能追加を整理する

```text
prompts/analyze_code_change_impact.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
実施状態: 未着手
変更内容: 文字数カウントで、空白を除外して数えるオプションを追加したい
変更の理由または違和感: 利用者から「空白なし文字数も知りたい」という要望があった
関連する実装ファイル: src/cli_text_counter/features/text_counter.py
関連するテストファイル: tests/cli_text_counter/features/test_text_counter.py
類似機能または比較対象: なし
外部から見える動作を変えるか: 変える
調査対象範囲: cli_text_counter 全体（entrypoint と結合試験を含む）
補足条件: 分析だけ行い、ファイルは変更しないでください。
```

この例は外部から見える動作が変わるため、**変更ルートB** になる見込みです。

### 例2: 正常に動いているコードの改善案を整理する

正常に動いていても、内部構造を改善したい場合や、類似機能と実装方式をそろえたい場合に使います。

```text
prompts/analyze_code_change_impact.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
実施状態: 未着手
変更内容: 入力チェックとエラーの返し方を、cli_hello_greeting の greeting と同じ方式にそろえたい
変更の理由または違和感: 動作は仕様どおりだが、この feature だけ書き方が違って読みにくい
関連する実装ファイル: src/cli_text_counter/features/text_counter.py
関連するテストファイル: tests/cli_text_counter/features/test_text_counter.py
類似機能または比較対象: src/cli_hello_greeting/features/greeting.py
外部から見える動作を変えるか: 変えない
調査対象範囲: cli_text_counter と cli_hello_greeting の feature 実装
補足条件: 分析だけ行い、ファイルは変更しないでください。
```

この例は、内容によって **ルートA**（実装方式の揺らぎにすぎない）にも **ルートC**（今後も守るべき方針として正式化したい）にもなりえます。**どちらかを人間が判断します。**

### 例3: すでに直したコードを確認する

人間が直接修正した後、正式資料へ反映すべき内容が含まれていないか確認する場合です。

```text
prompts/analyze_code_change_impact.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
実施状態: 実施済み
変更実施者: 人間
変更内容: 冗長だった分岐を整理し、変数名を分かりやすくした
変更の理由または違和感: 読みにくかったため
変更差分の指定: git diff
コード先行: なし
すでに実施した検証: python -m pytest（全件成功）
外部から見える動作を変えるか: 変えていないつもり
補足条件: 分析だけ行い、ファイルは変更しないでください。正式資料へ反映すべき内容が含まれていないか確認してください。
```

**人間が直したかAIが直したかで、分析の結論は変わりません。** 判断するのは変更の意味です。

### 分析結果を受け取った後

AIから分析結果（総合判定・変更点ごとの変更ルートと根拠・実施状態・影響する資産・推奨する次の作業）が報告されたら、人間がルートの採否を判断して次のステップに進みます。

- **ルートA** の場合は、正式資料の更新作業を行いません。実装とテストの変更、検証、ソースレビューへ進みます
- **ルートB** の場合は、正本と更新順を確認して、このチュートリアルの以降の手順で進めます
- **ルートC** の場合は、正式化するかどうかと反映先を人間が判断してから、別作業として反映します
- **コード先行がある場合**（ルートB・Cのいずれか）は、後追い反映順に従って反映し、未了項目を残課題として明示します
- **判断不能** の場合は、何が分かれば確定できるかを確認します
- バグ候補と分類された場合は、このチュートリアルではなく [040_bug_fix_flow.md](040_bug_fix_flow.md) のフローへ進みます
- 共通化候補の場合は、`docs/templates/30_common_proposal_template.md` を使った提案作成を別作業として依頼します。AIが `src/common/` を勝手に変更することはありません

### 現在の正式資料とコードの整合そのものを確認したい場合

変更の話ではなく、「今の設計書と今のコードがずれていないか」を確認したい場合は、別のプロンプトを使います。

```text
prompts/review_design_code_consistency.md を参照してください。

対象 scope の種別: feature
対象 scope:
- 対象機能フォルダ: docs/cli_text_counter/features/text_counter/
- 実装ファイル: src/cli_text_counter/features/text_counter.py
- テストファイル: tests/cli_text_counter/features/test_text_counter.py
重点的に確認したい観点: なし
除外したい範囲: なし
補足条件: 確認だけ行い、ファイルは変更しないでください。
```

このプロンプトは、「意味上の矛盾」と「正式資料には未記載だが問題ではない実装詳細」を分けて報告します。**未記載であること自体は指摘になりません。**

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
- docs/rules/
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
- docs/rules/
- README.md
- docs/templates/

補足条件:
- 変更対象と変更理由を作業報告に残してください。
- 作業後に python -m pytest を実行してください。
```

---

## 作業後に確認すること

- 変更対象と変更理由が作業報告に残っているか
- **正式資料を更新しなかった場合、更新不要と判断した理由が残っているか**
- `tasks.md` が現在地メモとして必要最小限更新されているか（詳細は書かれていないか）
- **正式資料が定義している意味と、実装が矛盾していないか**（正式資料に書かれていない実装詳細が存在すること自体は問題ではありません）
- 正式資料へ反映すべき意味が、未反映のまま残っていないか
- ついで修正やこっそり修正がないか（変更してよいファイル以外が変更されていないか）
- `python -m pytest` が通っているか
- 必要なレビューを行ったか（`review_feature_source.md`、必要に応じて `review_feature.md` / `review_command.md`）

---

## 進めるときの注意

- 分析・確認のステップ（`analyze_code_change_impact.md`、`review_design_code_consistency.md`）ではファイルを変更しません
- `prompts/*.md` は直接編集しません
- チャットでは、参照するプロンプトのパス、変更対象、変更理由、今回だけの補足条件を渡します
- feature の変更が entrypoint に影響する場合は、entrypoint の修正も別作業として依頼します
- 変更後は必ず `python -m pytest` を実行します
- `tasks.md` には仕様・設計・テスト計画・レビュー結果の詳細を書きません
- 変更要求が feature の責務を超える場合は、`10_overview.md` に戻って feature 分割から見直します
- **実装詳細で完結する変更（ルートA）でも、実装着手承認欄の確認は通常どおり必要です。** ルートAであることは、承認ゲートを省略する理由になりません
- **AIに実装を依頼する場合、AIの変更範囲は task プロンプトが定めた範囲のままです。** 変更の型がAだからといって、AIが範囲外を直してよいことにはなりません
