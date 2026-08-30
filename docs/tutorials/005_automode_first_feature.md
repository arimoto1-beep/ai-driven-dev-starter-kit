<!--
このチュートリアルは、オートモードで feature を1つ最後まで作る流れを体験するためのものです。
オートモードの全機能を説明する文書ではありません。詳細は docs/rules/project/70_feature_loop.md を参照してください。
-->

# オートモードで最初の feature を作る

## このチュートリアルで体験すること

**人間が仕様を書き、AIが設計から実装まで進め、人間が受け入れる**という一周を体験します。

```text
1. 人間が仕様（20_spec.md）を書く
2. AIが仕様をレビューする
3. ★ 人間が仕様を承認する            … CP1
4. AIが設計・テスト設計・実装・レビューを進める
5. ★ 人間が受け入れを判断する         … CP3
6. 完成
```

**通常フローで必ず人間が判断する固定ポイントは、★の2か所（CP1 と CP3）**です。
その間は基本的に AI が進めますが、**AI だけで決められない事項が出れば人間へ戻ります。**

このチュートリアルは**正常系の一周**に集中します。差し戻しや停止からの復旧は、
最後の「うまく進まないとき」で入口だけ示します。

---

## 他のチュートリアルとの違い

| チュートリアル | 進め方 | 何を学ぶか |
|---|---|---|
| **このチュートリアル** | **オートモード** | runner が各AI工程で Worker と Reviewer を分離して起動し、Gate で判定する流れ |
| [`010_simple_calculator.md`](010_simple_calculator.md) | マニュアルモード | 個別プロンプトを1つずつ実行し、工程を細かく確認する流れ |
| [`020_create_new_sample_from_scratch.md`](020_create_new_sample_from_scratch.md) | マニュアルモード | コマンド／アプリと複数 feature の文書構造をゼロから組み立てる |
| [`030_update_existing_feature.md`](030_update_existing_feature.md) | マニュアルモード | 実装済み feature の変更で、影響と反映先を整理する |
| [`040_bug_fix_flow.md`](040_bug_fix_flow.md) | マニュアルモード | バグ報告から修正までの流れ |

**マニュアルモードは旧式ではありません。** 工程を1つずつ確認したい場合は、新しい feature でもマニュアルモードを選べます。
2つの進め方の位置づけは [`../rules/project/20_workflow.md`](../rules/project/20_workflow.md) を参照してください。

---

## 前提

### 実行環境

- Python を実行できる環境
- **runner から非対話で起動できる AI CLI**

AI CLI には次が必要です。特定のベンダーやツールには限定しません。

- 1回の指示を渡して**非対話で実行できる**こと
- 使う**モデルをコマンドライン引数で指定できる**こと
- リポジトリ内のファイルを**読み書きできる**こと
- **テスト実行コマンドを許可できる**こと（CP3 で AI がテストを実行するため）

最後の1つは見落としやすい点です。テスト実行が許可されていないと、CP3 で AI がテストを完了できず、
runner が停止します。

### 設定

実行前に、[`../rules/project/70_feature_loop.md`](../rules/project/70_feature_loop.md) の設定ブロックへ次を記入します。

- `model_cheap` / `model_standard` / `model_strong`：使うモデル名
- `ai_command`：AI を起動するコマンド（カンマ区切りの argv テンプレート）

`ai_command` は次の形です。指示文が入る位置を `{instruction}`、モデル名が入る位置を `{model}` で示します。

```text
ai_command = <AI CLI>,<非対話実行のオプション>,{instruction},<モデル指定のオプション>,{model},<テスト実行を許可するオプション>
```

リポジトリへコミットしたくない場合は、同じ形式で `tools/feature_loop.local` へ書けます。
記入例と詳しい手順は [`../../tools/README.md`](../../tools/README.md) を参照してください。

> **AI CLI をまだ用意していない場合**：具体例として Claude Code のインストールと認証の手順が
> [`../../README.md`](../../README.md) に、`ai_command` と `model_*` の設定例が
> [`../../tools/README.md`](../../tools/README.md) にあります。
> **このスターターキットは特定のAI CLI 専用ではありません。**

### 設定できているかの確認

設定が終わったら、まず何も実行しない確認から始めます。このチュートリアルでは、
以降 `<app>` と `<feature>` を実際の名前に置き換えてください。

```bash
python tools/feature_runner.py --feature <app>/<feature> --status
```

`--status` は AI を起動しません。エラーになる場合は、設定か feature フォルダのパスを確認してください。

---

## 作る題材

**入力された文字列を逆順にして返す CLI** を題材にします。

```text
コマンド／アプリ名: cli_text_reverser
feature 名:        reverser
```

この題材を選ぶ理由は、**実装そのものより工程を学びやすい**ことです。

- 要求が少ない（2件）
- 入力と出力が一目で分かる
- 境界条件（空文字列）が1つだけある
- 実装が短いので、AI が何を作ったかを人間が読んで確認できる

**名前は変えても構いません。** ただし、既存のサンプル（`cli_hello_greeting`、`cli_simple_calculator`、
`cli_text_counter`）と同じ名前は使わないでください。既存のサンプルを上書きしてしまいます。

---

## 初期状態：何を用意し、何をまだ作らないか

**このチュートリアルで人間が用意するのは、次の2ファイルだけです。**

```text
docs/cli_text_reverser/
├─ 10_overview.md                          ← 人間が用意する
└─ features/reverser/
   └─ 20_spec.md                           ← 人間が用意する（最初の入力）
```

次のファイルは、**まだ作りません。AI が後で作ります。**

```text
docs/cli_text_reverser/features/reverser/
├─ 21_design.md            ← AI が作る（G1）
├─ 22_flow.md              ← AI が作る（G1）
├─ 23_test_plan.md         ← AI が作る（G2）
├─ 24_review_checklist.md  ← AI が作る（G2）
├─ 25_review_result.md     ← AI が作る（CP3）
└─ gates/                  ← runner と AI が作る（判定の記録）

src/cli_text_reverser/features/reverser.py         ← AI が作る（CP3）
tests/cli_text_reverser/features/test_reverser.py  ← AI が作る（CP3）
```

### `10_overview.md` と `20_spec.md` の関係

**feature 開発として AI へ渡す最初の入力は `20_spec.md` です。** 設計書やレビュー観点を先に作る必要はありません。

`10_overview.md` は feature の成果物ではなく、**その feature が属するコマンド／アプリ全体の入口**です。

| 状況 | 用意するもの |
|---|---|
| 既存のコマンド／アプリへ feature を追加する | **`20_spec.md` だけ。** `10_overview.md` は既にある |
| コマンド／アプリ自体を新しく作る（**このチュートリアル**） | 全体の入口として `10_overview.md` も先に用意し、そのうえで `20_spec.md` を書く |

このチュートリアルは新しいコマンド／アプリを作るため、手順1で `10_overview.md`、手順2で `20_spec.md` を用意します。

---

## 1. コマンド／アプリの入口を用意する

まず `10_overview.md` を作ります。仕様レビューのとき、AI がこのファイルを読んで
「feature が全体の目的とずれていないか」を確認します。

ひな形は [`../templates/10_overview_template.md`](../templates/10_overview_template.md) です。
このチュートリアルでは、次の程度で構いません。

```bash
mkdir -p docs/cli_text_reverser/features/reverser
```

`docs/cli_text_reverser/10_overview.md`：

```markdown
# cli_text_reverser

## 目的

入力された文字列を逆順にして返す CLI。

## 機能一覧

| feature | 役割 |
|---|---|
| reverser | 文字列を文字単位で逆順にする |

## Boundary

- 対象: 文字列の逆順変換のみ
- 対象外: ファイル入出力、外部連携
```

---

## 2. `20_spec.md` を用意する

**ここが最初の入力です。** 人間が仕様を確定します。

ひな形は [`../templates/20_spec_template.md`](../templates/20_spec_template.md) です。
見出し構成を維持して `docs/cli_text_reverser/features/reverser/20_spec.md` を作ります。

必須要件には **`REQ-001` の形式で ID** を振ってください。AI はこの ID を使って、
設計・テスト・実装が要求を満たしているかを追跡します。

```markdown
# reverser

## 作りたいもの

入力された文字列を、文字単位で逆順にした文字列を返す。

## 実行イメージ

reverse_text("abc")

## 期待する出力

"cba"

## 必須要件

- REQ-001: 与えられた文字列を、文字単位で逆順にした文字列を返す
- REQ-002: 空文字列を与えた場合は、空文字列を返す

## 入力

- text: 文字列

## 出力

- 逆順にした文字列

## エラー扱い

- 今回は例外を送出しない

## 今回やらないこと

- 文字列以外の入力の扱い
- サロゲートペアや結合文字を1文字として扱う特別処理
- CLI 引数の解析（entrypoint は今回作らない）

## レビュー観点

- 空文字列で期待どおり動くか

## 補足

なし
```

### AI に作成を手伝わせてもよい

仕様の下書きを AI に手伝わせることはできます。

```text
prompts/create_feature_spec.md を参照してください。

対象機能フォルダ: docs/cli_text_reverser/features/reverser/
コマンド/アプリ名: cli_text_reverser
対象機能名: reverser
作りたいもの: 入力された文字列を逆順にして返す
補足条件: なし
```

**ただし、AI が書いた仕様をそのまま承認しないでください。** 内容を読み、
自分が受け入れられる仕様になっているかを確認してから次へ進みます。**仕様を確定させるのは人間です。**

---

## 3. Spec Review を実行する

仕様を AI にレビューさせます。**この段階では、AI は仕様書を書き換えません。読んで判定するだけです。**

```bash
python tools/feature_runner.py --feature cli_text_reverser/reverser --spec-review
```

- **何度でも実行できます。** 製造工程は始まりません
- 実行するたびに新しい Gate記録が `features/reverser/gates/` に作られます
- 上長や顧客のレビューを挟んでから再実行することもできます

実行前に何が起きるか確認したい場合は `--dry-run` を付けます（AI を起動しません）。

```bash
python tools/feature_runner.py --feature cli_text_reverser/reverser --spec-review --dry-run
```

### 結果を読む

作られた Gate記録（`gates/` の中で連番が最大のファイル）を開き、front matter の `verdict` を見ます。

| `verdict` | 意味 | 次にすること |
|---|---|---|
| `PASS` | 仕様レビューを通過した | 手順4へ進む |
| `RETURN` / `BLOCKED` | 仕様に問題がある、または人間が決める事項がある | 記録の「差し戻し／停止の理由」と「人間確認欄」を読み、`20_spec.md` を直して再実行する |

`PASS` 以外だった場合も、**`20_spec.md` を直して `--spec-review` を実行し直すだけ**です。
記録は上書きされず、履歴として積み上がります。

---

## 4. ★ CP1：人間が仕様を承認する

**ここが1つ目の人間の判断ポイントです。**

`verdict: PASS` の CP1 Gate記録を開き、次を確認します。

- 「判定サマリ」と「FINDING」を読み、指摘が解消しているか
- 「人間確認欄」の**「判断してほしいこと」**に回答する

確認できたら、同じファイルの **「仕様承認（CP1 のみ）」** の欄にチェックを入れます。

```markdown
### 仕様承認（CP1 のみ）

- [x] 上記の判断事項に回答した
- [x] 必要な関係者の確認が完了している
- [x] この仕様を baseline として確定し、AI製造工程へ進むことを承認する
```

**この欄にチェックを入れるのは人間だけです。AI はチェックしません。**

この承認は、**その `PASS` の Gate記録でレビューされた `20_spec.md` を人間が承認する**という意味です。
承認された仕様が、以降の工程の **baseline** になります。

runner は製造を始める前に、**現在の `20_spec.md` が承認したときの内容と一致するか**を自動で確認します。
一致しない場合、製造は始まりません。

以降 AI は、**承認された仕様を超えて仕様を追加できません。**
不足を見つけた場合は、勝手に補わず仕様工程へ差し戻します。

> **承認後に `20_spec.md` を変更すると、この承認は無効になります。**
> 変更した場合は `--spec-review` でレビューし直し、新しい記録で承認し直してください。

承認できたか確認します。

```bash
python tools/feature_runner.py --feature cli_text_reverser/reverser --status
```

```text
仕様 baseline:
  人間の仕様承認: docs/cli_text_reverser/features/reverser/gates/0001_..._cp1.md
  製造開始条件: 満たしている
...
次の動作: run (stage=G1)
```

`次の動作: run (stage=G1)` になっていれば、次へ進めます。

---

## 5. runner を実行する

```bash
python tools/feature_runner.py --feature cli_text_reverser/reverser
```

runner は次の順に AI を起動し、**人間の判断が必要になるところまで進めます。**

```text
G1  設計         → 21_design.md、22_flow.md
G2  テスト設計    → 23_test_plan.md、24_review_checklist.md
CP3 実装・レビュー → 実装ファイル、テストファイル、25_review_result.md
```

各段階で、AI は**作る役（Worker）とレビューする役（Reviewer）に分かれて動きます。**
Reviewer は Worker とは別のプロセスとして起動されるため、Worker の会話履歴を引き継ぎません。
指摘があれば、Worker が修正して Reviewer が再確認します。

### 1段階ずつ確認しながら進めたい場合

初回は `--once` を付けて、1段階ずつ止めながら進めると、何が起きているか追いやすくなります。

```bash
python tools/feature_runner.py --feature cli_text_reverser/reverser --once
```

1段階終わるたびに、生成されたファイルと Gate記録を読んでから次を実行できます。

### 進行状況を見る

```bash
python tools/feature_runner.py --feature cli_text_reverser/reverser --status
python tools/feature_runner.py --feature cli_text_reverser/reverser --history
```

`--history` は、Gate記録がどの順に作られ、どこで差し戻しがあったかを一覧で表示します。

---

## 6. ★ CP3：人間が受け入れを判断する

CP3 まで進むと、runner は次のように表示して停止します。

```text
CP3 で停止しました。人間の判断が必要です。
...
Gate記録の人間確認欄へ回答し、承認欄にチェックを入れてから再実行してください。
```

**ここが2つ目の人間の判断ポイントです。**

最新の CP3 Gate記録を開き、次を確認します。

- **「feature 要約」**：この feature が何をするか、どこに判断ロジックがあるか、**保証していない範囲**は何か
- 「判定サマリ」と「FINDING」
- 「人間確認欄」の「判断してほしいこと」

あわせて、実際に生成されたコードとテストを読んでください。**内容を理解したうえで受け入れることが、
このキットの目的です。**

```bash
python -m pytest
```

確認できたら、**「受け入れ判断（CP3 のみ）」** の欄にチェックを入れます。

```markdown
### 受け入れ判断（CP3 のみ）

- [x] feature 要約を読み、内容を理解した
- [x] 残課題と、保証していない範囲を確認した
- [x] この feature を完成成果物として受け入れる
```

**この欄も、チェックを入れるのは人間だけです。**

---

## 7. 完了を確認する

```bash
python tools/feature_runner.py --feature cli_text_reverser/reverser
```

```text
完了しました。
```

`--status` でも確認できます。

```bash
python tools/feature_runner.py --feature cli_text_reverser/reverser --status
```

```text
次の動作: done
```

`done` になれば一周完了です。

---

## 実行後に何が残ったか

```text
docs/cli_text_reverser/
├─ 10_overview.md                              人間が用意
└─ features/reverser/
   ├─ 20_spec.md                               人間が用意（承認済み baseline）
   ├─ 21_design.md                             AI が作成（G1）
   ├─ 22_flow.md                               AI が作成（G1）
   ├─ 23_test_plan.md                          AI が作成（G2）
   ├─ 24_review_checklist.md                   AI が作成（G2）
   ├─ 25_review_result.md                      AI が作成（CP3）
   ├─ tasks.md                                 AI が作成（作業メモ）
   └─ gates/
      ├─ 0001_..._cp1.md                       仕様レビューの判定＋人間の仕様承認
      ├─ 0002_..._g1.md                        設計の判定
      ├─ 0003_..._g2.md                        テスト設計の判定
      └─ 0004_..._cp3.md                       完成の判定＋人間の受け入れ

src/cli_text_reverser/features/reverser.py     AI が作成（CP3）
tests/cli_text_reverser/features/test_reverser.py  AI が作成（CP3）
```

**`gates/` が、この feature をどう判断して進めたかの記録です。**

- 各段階の判定（`verdict`）と、その根拠
- 人間が承認した事実と、承認した時点の仕様
- 途中で止まった場合は、その理由

確定した Gate記録は書き換えません。やり直した場合も、**新しい記録が追加される**だけです。
後から「なぜこの成果物になったのか」を追跡できます。

Gate記録の項目の意味は [`../templates/gate_record_template.md`](../templates/gate_record_template.md)、
判定値の定義は [`../rules/project/70_feature_loop.md`](../rules/project/70_feature_loop.md) を参照してください。

---

## うまく進まないとき

**最初の一周では、次を覚える必要はありません。** 止まったときに、この節へ戻ってきてください。

| 状況 | 意味 | 入口 |
|---|---|---|
| `RETURN` で前の段階へ戻った | 問題が、通過済みの成果物にある。runner がその段階から自動で再実行する | そのまま実行を続ける |
| `BLOCKED` で止まった | AI だけでは決められない、または実行環境に問題がある | Gate記録の `blocked_reason` と停止理由を読む。原因を解消したうえで `--retry-blocked` |
| 通過済みのファイルを人間が直した | runner が変更を検出して停止する | 人間の修正を活かすなら `--review-current <stage>`、AI に作り直させるなら `--rework <stage>` |

**`BLOCKED` は自動では再開しません。** 原因を解消したことを人間が確認してから、明示的に再試行します。

オプションの一覧と使い分けは [`../../tools/README.md`](../../tools/README.md)、
判定値と復旧の正本は [`../rules/project/70_feature_loop.md`](../rules/project/70_feature_loop.md) にあります。

---

## 次に読むもの

| 知りたいこと | 入口 |
|---|---|
| オートモードの仕組み（stage、Gate、判定値、モデル選択） | [`../rules/project/70_feature_loop.md`](../rules/project/70_feature_loop.md) |
| runner のオプション一覧 | [`../../tools/README.md`](../../tools/README.md) |
| 工程を1つずつ手で進める方法 | [`010_simple_calculator.md`](010_simple_calculator.md) |
| 実装済み feature を変更する方法 | [`030_update_existing_feature.md`](030_update_existing_feature.md) |
| バグ対応の流れ | [`040_bug_fix_flow.md`](040_bug_fix_flow.md) |
| 完成した feature の成果物の例 | [`../cli_hello_greeting/10_overview.md`](../cli_hello_greeting/10_overview.md) |
| **実AIでオートモードを実行したときの Gate記録の実物** | [`../cli_text_masker/README.md`](../cli_text_masker/README.md) |

---

## 進めるときの注意

- **`gates/` の確定した記録を書き換えないでください。** やり直しても新しい記録が追加されます
- **承認欄にチェックを入れるのは人間だけです。** AI に代わりにチェックさせないでください
- **承認後に `20_spec.md` を変更したら、再レビューと再承認が必要です**
- 生成されたコードとテストは、受け入れる前に必ず読んでください。**理解できないものを受け入れないことが、このキットの目的です**
- AI が範囲外のファイルを変更した場合、runner が検出して停止します。これは異常ではなく、
  変更範囲を守るための仕組みです
