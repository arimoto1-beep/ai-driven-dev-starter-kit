# 新しいサンプルを1から作るチュートリアル

このチュートリアルでは、新しい CLI アプリ `cli_text_tools` を1から作ります。

主目的は、docs / features / tasks.md の構造をゼロから作れるようにすることです。
実装まで完走させることが目的ではありません。
`10_overview.md` で command/app 全体を整理し、2つの feature に分ける初期ドキュメント構造を作るところまでを体験します。
その後の設計・実装・テスト・レビューは、既存の `prompts/*.md` を使って進める導線にします。

チュートリアル専用プロンプトは使いません。
`prompts/` 直下の汎用プロンプトを参照し、チャットで「参照するプロンプトのパス」と「対象情報」を渡して進めます。

---

## 010_simple_calculator.md との違い

| | 010_simple_calculator.md | このチュートリアル（020） |
|---|---|---|
| 開始状態 | 既存の初期状態サンプルから始める | 完全にゼロから作る |
| feature 数 | 単一 feature（calculator） | 複数 feature（text_counter + text_upper） |
| 体験すること | 設計 → 実装 → テスト → レビューの全工程を段階的に進める | 10_overview.md で全体を整理し、複数 feature に分ける初期構造を作る |
| 実装コード | 扱う | このチュートリアルでは扱わない（後続 prompts への導線のみ） |
| tasks.md | 進行に伴い更新する | 作り方と使い方を体験する |

どちらも `prompts/` の汎用プロンプトを使う方針は同じです。
010 を先に進めてプロンプトの使い方に慣れてからこのチュートリアルに取り組むと、よりスムーズです。

なお、このチュートリアルには複数 feature を束ねる entrypoint の完成見本は含まれていません。
entrypoint 実装まで進める場合は、`010_simple_calculator.md` や既存サンプルの実装を参考にしてください。
既存の完成サンプル（`cli_hello_greeting`・`cli_text_counter`）は単一 feature の完成形例であり、複数 feature を束ねる完成例ではありません。
複数 feature を持つ command/app の完成サンプルは、今後の改善候補として検討中です。

---

## 前提

このチュートリアルを始める前に、以下を確認してください。

- `README.md` で全体像を確認済み
- `AGENTS.md`（AIの薄い入口）を一読済み
- `docs/rules/README.md` でルール体系の全体像を確認済み
- `docs/how_to_use_prompts.md` を一読済み

完成形の参考として、以下を確認しておくと理解が深まります（任意）。

- `docs/cli_text_counter/10_overview.md`（単一 feature の完成形例）
- `docs/cli_text_counter/tasks.md`
- `docs/cli_text_counter/features/text_counter/20_spec.md`

---

## 新しいサンプル名と feature 名の決め方

このチュートリアルでは、以下の名前を使います。

| 種別 | 名前 |
|---|---|
| コマンド/アプリ名 | `cli_text_tools` |
| feature 1 | `text_counter` |
| feature 2 | `text_upper` |

実際に自分のアプリを作る場合は、以下を参考に名前を決めてください。

**コマンド/アプリ名**

- `cli_<名前>` 形式にする（例: `cli_text_tools`、`cli_file_sorter`）
- 機能のまとまりを表す名前にし、個別処理の名前は使わない

**feature 名**

- 機能単位の名前にし、関数名や実装上の処理名は使わない
  - 例: `text_counter` は feature 名として適切、`count_chars` は関数名候補であり feature 名としては不適切
- 1つの feature が担当する責務を1語〜2語で表せる粒度にする
- 関連する複数の操作をひとまとめにできるなら1つの feature にまとめる

---

## command/app 全体と feature 分割の考え方

`cli_text_tools` は、テキスト操作に関する小さな CLI です。

このチュートリアルでは、以下の2つの feature を持たせます。

| feature | 役割 | 想定する実行例 |
|---|---|---|
| `text_counter` | 入力文字列の文字数を数えて整数として返す | `count --text hello` → `5` |
| `text_upper` | 入力文字列を大文字に変換して返す | `upper --text hello` → `HELLO` |

`10_overview.md` では、この CLI が担当することと担当しないことを整理します。
feature 分割案は AI と確認しながら決めます。

entrypoint の責務は、CLI引数を受け取り feature を呼び出し、結果を標準出力に表示することです。
文字数の計算や大文字変換のロジックは entrypoint に入れず、それぞれの feature に閉じます。

---

## 作成するドキュメント構成

このチュートリアルで作成する最終的な構成は、以下です。

```text
docs/cli_text_tools/
├─ 10_overview.md
├─ tasks.md
└─ features/
   ├─ text_counter/
   │  ├─ tasks.md
   │  └─ 20_spec.md
   └─ text_upper/
      ├─ tasks.md
      └─ 20_spec.md
```

この時点では、以下はまだ作りません。

- `21_design.md`、`22_flow.md`、`23_test_plan.md`、`24_review_checklist.md`
- `25_review_result.md`、`11_integration_test_plan.md`、`12_command_review_result.md`
- `src/` 配下の実装ファイル
- `tests/` 配下のテストファイル

これらは、後続の `prompts/*.md` を使って必要なタイミングで作成します。

---

## tasks.md の使い方

このチュートリアルで作成する `tasks.md` は2種類あります。

**command/app 単位の tasks.md**（`docs/cli_text_tools/tasks.md`）

- `cli_text_tools` 全体の現在地を記録する
- 「どこまで進んでいるか」「次に何をするか」だけを短く書く
- feature の詳細な仕様・設計内容はここには書かない

**feature 単位の tasks.md**（`docs/cli_text_tools/features/<feature_name>/tasks.md`）

- 各 feature の現在地を個別に記録する
- 「この feature の仕様が確認済みか」「次に何を作るか」だけを短く書く
- 仕様（20_spec.md）や設計（21_design.md）の代わりにしない

`tasks.md` は AI 用 TODO ではなく、人間と AI が現在地を共有するためのメモです。
各ステップ後に AI が tasks.md を更新しますが、詳細な仕様や設計内容が書き込まれていた場合は削除してください。

---

## 1. 10_overview.md と command/app tasks.md を作成する

`prompts/create_overview.md` を参照して、`cli_text_tools` の 10_overview.md を作成します。
`create_overview.md` の「変更してよいファイル」に `tasks.md` が含まれているため、このステップで command/app 単位の tasks.md も作成されます。

チャット例:

```text
prompts/create_overview.md を参照してください。

コマンド/アプリ名: cli_text_tools
種別: cli
作りたいもの: テキスト操作をまとめた小さな CLI ツール。文字数カウントと大文字変換の2つの機能を持つ。
実行イメージ:
  python src/cli_text_tools/entrypoint.py count --text hello
  → 5
  python src/cli_text_tools/entrypoint.py upper --text hello
  → HELLO
今回やらないこと: 小文字変換、単語数カウント、行数カウント、ファイル入力、対話式入力、外部API連携
補足条件: 2つの feature（text_counter と text_upper）に分ける構成にしてください。feature 分割案も提示してください。
tasks.md も作成し、現在地と次に確認することを短く記録してください。
```

作成または更新されるファイル:

```text
docs/cli_text_tools/10_overview.md
docs/cli_text_tools/tasks.md
```

### 10_overview.md の確認ポイント

- `cli_text_tools` の目的と担当範囲が書かれているか
- `text_counter` と `text_upper` が feature として分かれているか
- entrypoint と features の責務が分かれているか
- 担当しないことが明記されているか（小文字変換、ファイル入力など）

### command/app tasks.md の確認ポイント

tasks.md に以下が含まれているか確認してください。

- command/app 名と現在の状態
- 完了した作業（10_overview.md 作成済み）
- 次に確認すること（feature の 20_spec.md 作成）

仕様の詳細や feature 設計内容が書き込まれていた場合は、削除してください。

tasks.md の内容例:

```text
## 現在の状態
- command/app: cli_text_tools
- 状態: 10_overview.md 作成済み
- 最終更新: YYYY-MM-DD

## 作業メモ
- [x] 10_overview.md を作成する
- [ ] text_counter の 20_spec.md を作成する
- [ ] text_upper の 20_spec.md を作成する

## 次に確認すること
- text_counter の 20_spec.md を作成する
```

---

## 2. text_counter の 20_spec.md と tasks.md を作成する

`prompts/create_feature_spec.md` を参照して、`text_counter` feature の仕様を作成します。
`create_feature_spec.md` の「変更してよいファイル」に feature 単位の `tasks.md` が含まれているため、このステップで feature tasks.md も作成されます。

チャット例:

```text
prompts/create_feature_spec.md を参照してください。

対象機能フォルダ: docs/cli_text_tools/features/text_counter/
コマンド/アプリ名: cli_text_tools
対象機能名: text_counter
作りたいもの: 入力文字列の文字数を数えて整数として返す機能
実行イメージ:
  python src/cli_text_tools/entrypoint.py count --text hello
  → 5
今回やらないこと: 単語数カウント、行数カウント、ファイル入力
補足条件: feature は文字数を整数として返す。標準出力は entrypoint の責務とする。空文字列は 0 を返す。
feature 単位の tasks.md も作成してください。
```

作成または更新されるファイル:

```text
docs/cli_text_tools/features/text_counter/20_spec.md
docs/cli_text_tools/features/text_counter/tasks.md
docs/cli_text_tools/tasks.md
```

### 20_spec.md の確認ポイント

- feature の責務（文字数を整数として返す）が明確か
- 空文字列の扱いが明記されているか
- CLI引数解析や標準出力が feature に入っていないか
- 10_overview.md の内容と矛盾していないか

### feature tasks.md の確認ポイント

- feature 名と現在の状態が短く書かれているか
- 次に確認すること（21_design.md の作成など）が書かれているか
- 仕様の詳細が書き込まれていないか

---

## 3. text_upper の 20_spec.md と tasks.md を作成する

`prompts/create_feature_spec.md` を参照して、`text_upper` feature の仕様を作成します。

チャット例:

```text
prompts/create_feature_spec.md を参照してください。

対象機能フォルダ: docs/cli_text_tools/features/text_upper/
コマンド/アプリ名: cli_text_tools
対象機能名: text_upper
作りたいもの: 入力文字列を大文字に変換して返す機能
実行イメージ:
  python src/cli_text_tools/entrypoint.py upper --text hello
  → HELLO
今回やらないこと: 小文字変換、タイトルケース変換、ファイル入力
補足条件: feature は変換後の文字列を返す。標準出力は entrypoint の責務とする。空文字列は空文字列を返す。
feature 単位の tasks.md も作成してください。
```

作成または更新されるファイル:

```text
docs/cli_text_tools/features/text_upper/20_spec.md
docs/cli_text_tools/features/text_upper/tasks.md
docs/cli_text_tools/tasks.md
```

### 20_spec.md の確認ポイント

- feature の責務（大文字変換した文字列を返す）が明確か
- 空文字列の扱いが明記されているか
- CLI引数解析や標準出力が feature に入っていないか
- 10_overview.md の内容と矛盾していないか

---

## 4. 作成後に確認するポイント

3つのステップが完了したら、ドキュメント構成全体を確認します。

チャット例:

```text
AGENTS.md を確認したうえで、以下のドキュメントが正しく作成されているか確認してください。

確認対象:
- docs/cli_text_tools/10_overview.md
- docs/cli_text_tools/tasks.md
- docs/cli_text_tools/features/text_counter/20_spec.md
- docs/cli_text_tools/features/text_counter/tasks.md
- docs/cli_text_tools/features/text_upper/20_spec.md
- docs/cli_text_tools/features/text_upper/tasks.md

確認してほしいこと:
- 2つの feature の責務が分かれているか
- 10_overview.md の担当範囲と各 20_spec.md が矛盾していないか
- tasks.md に仕様の詳細や設計内容が書き込まれていないか
- command/app 単位と feature 単位の tasks.md の役割が分かれているか

このステップではファイルを変更しないでください。
```

---

## 5. 次に使う prompts/*.md への導線

複数 feature を持つ command/app では、先に各 feature の設計・実装・単体レビューを完了させてから、entrypoint と結合試験に進みます。
entrypoint は feature を束ねる入口であり、feature 固有ロジックを実装する場所ではありません。

初期ドキュメント構成ができたら、以下の順番で続きを進められます。

各 feature に対して繰り返す作業（feature ごとに順番に進める）:

```text
prompts/create_function_design.md    → 21_design.md を作成する
prompts/create_function_call_flow.md → 22_flow.md を作成する
prompts/create_test_design.md        → 23_test_plan.md を作成する
prompts/create_review_checklist.md   → 24_review_checklist.md を作成する（実装着手承認欄は未チェックで作成される）
【人間作業】24_review_checklist.md の実装着手承認欄を確認し、すべてチェックを入れる（AIはチェックを入れない）
prompts/implement_feature.md         → feature 実装と単体テストを作成する（承認欄未チェックの場合 STOP）
prompts/review_feature_source.md     → 実装直後のソースレビューを行う（修正はしない。修正候補をチャットで報告）
prompts/review_feature.md            → feature 単体レビューを行い 25_review_result.md を作成する
```

feature がそろってから進む作業:

```text
prompts/implement_entrypoint.md          → entrypoint.py と entrypoint テストを作成する
prompts/create_integration_test_plan.md  → 11_integration_test_plan.md を作成する
prompts/implement_integration_test.md    → 結合試験を実装する
prompts/review_command.md                → command/app 全体レビューを行い 12_command_review_result.md を作成する
```

各 prompts のチャット例は `010_simple_calculator.md` も参考にしてください。
feature が複数ある場合は、feature ごとに `create_function_design.md` から `review_feature.md` までを繰り返してから entrypoint 以降に進みます。

---

## 進めるときの注意

- `prompts/*.md` は直接編集しません
- チャットでは、参照するプロンプトのパス、対象情報、今回だけの補足条件を短く渡します
- tasks.md には仕様の詳細・設計内容・レビュー結果を書き込まないでください
- 複数 feature を進める場合、feature ごとに別チャットで作業するときは tasks.md で現在地を確認します
- feature 分割を変更したくなった場合は、10_overview.md に戻って整理してから進めます
- 共通化候補があっても、勝手に `src/common/` へ切り出しません
- 仕様にない便利機能を追加しません
- entrypoint に feature 固有ロジックを入れません

---

10_overview.md / tasks.md / features 配下の 20_spec.md と tasks.md が整った時点で、このチュートリアルの目的は達成です。
設計・実装・テスト・レビューへの続きは、上記の「5. 次に使う prompts/*.md への導線」を参照してください。
