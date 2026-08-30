# バグ修正フローのチュートリアル

このチュートリアルでは、実装済みサンプル `cli_text_counter` を題材に、バグを見つけたときにいきなり修正せず、報告、調査、修正計画、人間承認、実装の順に進める流れを確認します。

> **このチュートリアルはマニュアルモードです。** 人間が個別プロンプトを1つずつ実行します。
> **feature 新規開発とは別のフロー**なので、その feature をオートモードで作った場合でも、この流れで進められます。
> 進め方の位置づけは [`../rules/project/20_workflow.md`](../rules/project/20_workflow.md)、
> オートモードでの feature 新規開発は [`005_automode_first_feature.md`](005_automode_first_feature.md) を参照してください。

このチュートリアルは、バグ修正フローの説明が目的です。`src/`、`tests/`、`docs/cli_text_counter/features/` は変更しません。

`docs/cli_text_counter/bugs/bug_001/` 配下には、このフローを実際に回したサンプルドキュメント（`10_bug_report.md`、`20_bug_investigation.md`、`30_bug_fix_plan.md`）が配置済みです。各ステップの説明と合わせて参照してください。

---

## このチュートリアルの目的

バグ修正では、発見した問題をすぐにコードで直したくなります。

しかし、このスターターキットでは、AIが勝手に原因を決めたり、ついで修正を混ぜたりしないように、次の順番で作業を分けます。

1. バグ報告書を作成する
2. バグ調査書を作成する
3. バグ修正計画書を作成する
4. 人間が修正計画を承認する
5. 承認済み計画に従って修正する

この流れにすると、何が起きたのか、どこまで調べたのか、どのファイルを直してよいのか、誰が実装に進む判断をしたのかを後から追いやすくなります。

---

## 030_update_existing_feature.md との違い

`030_update_existing_feature.md` は、実装済み feature に対する追加修正全般を扱います。

たとえば、仕様変更、軽微な機能追加、レビュー指摘の反映、バグ修正など、既存 feature を変更するときの影響範囲確認が中心です。

このチュートリアルでは、その中でも **バグ修正専用の流れ** に絞ります。

| 観点 | 030_update_existing_feature.md | 040_bug_fix_flow.md |
|---|---|---|
| 主な対象 | 既存 feature の追加修正全般 | バグ修正 |
| 最初に作るもの | 影響範囲の整理 | バグ報告書 |
| 使う主なプロンプト | 変更内容に応じて選ぶ | `create_bug_report.md`、`investigate_bug.md`、`create_bug_fix_plan.md`、`implement_bug_fix.md` |
| 実装開始条件 | 変更内容に応じて判断 | 人間が `30_bug_fix_plan.md` を承認した後 |
| 強調すること | 変更要求と影響範囲の整理 | 修正計画にないついで修正をしないこと |

---

## 今回使う想定バグ

題材は `cli_text_counter` です。

想定バグ:

```text
cli_text_counter で、空文字列を渡したときに 0 を返すべきところ、エラーになる
```

この想定バグが、現在の実装に実際に存在するかどうかは問いません。

このチュートリアルでは、あくまで `bug_001` という想定バグを使って、バグ修正フローを説明します。実際の修正やテスト追加は行いません。

---

## 参照する題材

`cli_text_counter` は、入力文字列の文字数を数えるシンプルなCLIです。

主なファイル:

この表では、バグ修正フローで主に参照するファイルだけを掲載しています。

| ファイル | 役割 |
|---|---|
| `docs/cli_text_counter/10_overview.md` | command/app 全体の目的と責務 |
| `docs/cli_text_counter/features/text_counter/20_spec.md` | `text_counter` feature の仕様 |
| `docs/cli_text_counter/features/text_counter/21_design.md` | 関数設計 |
| `docs/cli_text_counter/features/text_counter/22_flow.md` | 呼び出し定義 |
| `docs/cli_text_counter/features/text_counter/23_test_plan.md` | feature 単体テスト計画 |
| `src/cli_text_counter/features/text_counter.py` | feature 実装 |
| `src/cli_text_counter/entrypoint.py` | CLI入口 |
| `tests/cli_text_counter/features/test_text_counter.py` | feature 単体テスト |
| `tests/cli_text_counter/test_entrypoint_text_counter.py` | entrypoint テスト |
| `tests/cli_text_counter/test_integration_text_counter.py` | 結合試験 |

---

## bug_001 の作業フォルダ構成

バグ管理ドキュメントは、対象 command/app の `bugs/<bug_id>/` に配置します。

今回の想定バグでは、次の構成になります。

```text
docs/
  cli_text_counter/
    bugs/
      bug_001/
        10_bug_report.md
        20_bug_investigation.md
        30_bug_fix_plan.md
```

それぞれの役割は次のとおりです。

| ファイル | 役割 |
|---|---|
| `10_bug_report.md` | 現象、期待動作、実際の動作、再現手順を整理する。原因断定や修正はしない |
| `20_bug_investigation.md` | 仕様、設計、実装、テストを読み、原因仮説と影響範囲を整理する。修正はしない |
| `30_bug_fix_plan.md` | 修正方針、修正対象ファイル、追加・更新するテスト、確認コマンド、人間承認欄を整理する。まだ修正はしない |

---

## 全体の流れ

バグ修正は、次の順に進めます。

```text
1. prompts/create_bug_report.md で 10_bug_report.md を作成する
2. prompts/investigate_bug.md で 20_bug_investigation.md を作成する
3. prompts/create_bug_fix_plan.md で 30_bug_fix_plan.md を作成する
4. 人間が 30_bug_fix_plan.md の承認欄を確認する
5. prompts/implement_bug_fix.md で承認済み計画に従って修正する
```

ポイントは、調査や計画の段階では `src/` や `tests/` を変更しないことです。

---

## 1. バグ報告書を作成する

最初に、`prompts/create_bug_report.md` を使って `10_bug_report.md` を作成します。

この段階では、原因を断定しません。実装コードもテストコードも変更しません。利用者から得た情報をもとに、現象、期待動作、実際の動作、再現手順、不足情報を整理します。

チャット例:

```text
prompts/create_bug_report.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
バグID: bug_001
バグ報告書の出力先: docs/cli_text_counter/bugs/bug_001/10_bug_report.md

バグ報告の内容:
- 現象: cli_text_counter で空文字列を渡したときにエラーになる
- 期待動作: 空文字列は有効な入力として扱い、0 を出力する
- 実際の動作: エラーになる
- 再現手順:
  1. python src/cli_text_counter/entrypoint.py --text "" を実行する
  2. 0 が出力されることを期待する
  3. 実際にはエラーになる
- 入力例: 空文字列
- 出力例: 0
- エラーログ: 現時点では未取得

補足条件:
- この段階では原因を断定しないでください。
- src/、tests/、docs/cli_text_counter/features/ は変更しないでください。
- 20_bug_investigation.md と 30_bug_fix_plan.md はまだ作成しないでください。
```

作成後は、`10_bug_report.md` に不足情報が残っていないか確認します。不足情報があっても、調査に進めるだけの再現手順がある場合は、次の調査段階で確認します。

---

## 2. バグ調査書を作成する

次に、`prompts/investigate_bug.md` を使って `20_bug_investigation.md` を作成します。

この段階では、バグ報告書に加えて、仕様、設計、フロー、テスト計画、実装、テストを読みます。原因仮説を整理しますが、まだ修正しません。

チャット例:

```text
prompts/investigate_bug.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
バグID: bug_001
バグ報告書: docs/cli_text_counter/bugs/bug_001/10_bug_report.md
バグ調査書の出力先: docs/cli_text_counter/bugs/bug_001/20_bug_investigation.md
対象機能フォルダ: docs/cli_text_counter/features/text_counter/
実装ファイル: src/cli_text_counter/features/text_counter.py
テストファイル: tests/cli_text_counter/features/test_text_counter.py

補足条件:
- 仕様、設計、フロー、テスト計画、実装、テストを確認してください。
- 必要に応じて docs/cli_text_counter/10_overview.md、src/cli_text_counter/entrypoint.py、docs/cli_text_counter/11_integration_test_plan.md、entrypoint テスト、結合試験も確認してください。
- この段階では src/、tests/、docs/cli_text_counter/features/ を変更しないでください。
- 30_bug_fix_plan.md はまだ作成しないでください。
- 仕様通りに動いているが期待と違う場合は、バグではなく仕様変更候補として扱ってください。
```

調査書では、次のような観点を分けて記録します。

- 仕様バグ: 仕様自体に誤りや不足がある
- 実装バグ: 仕様は正しいが実装が従っていない
- テストバグ: 仕様と実装は正しいがテストが誤っている
- ドキュメント不整合: 仕様、設計、実装の間に矛盾がある

`20_bug_investigation.md` の「調査段階の判定」が `調査完了` になっている場合だけ、修正計画に進みます。

`追加調査が必要` または `仕様確認待ち` の場合は、修正計画を作らずに STOP します。

---

## 3. バグ修正計画書を作成する

調査段階の判定が `調査完了` になったら、`prompts/create_bug_fix_plan.md` を使って `30_bug_fix_plan.md` を作成します。

この段階でも、まだ実装コードやテストコードは変更しません。

チャット例:

```text
prompts/create_bug_fix_plan.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
バグID: bug_001
バグ報告書: docs/cli_text_counter/bugs/bug_001/10_bug_report.md
バグ調査書: docs/cli_text_counter/bugs/bug_001/20_bug_investigation.md
バグ修正計画書の出力先: docs/cli_text_counter/bugs/bug_001/30_bug_fix_plan.md
対象機能フォルダ: docs/cli_text_counter/features/text_counter/

補足条件:
- 20_bug_investigation.md の調査段階の判定が「調査完了」の場合のみ、修正計画を作成してください。
- 修正対象ファイルと変更してはいけないファイルを明記してください。
- 追加・更新するテストを明記してください。
- 実行する確認コマンドは python -m pytest としてください。
- 仕様・設計・テスト計画の更新が必要な場合は、実装修正とは別作業として明記してください。
- この段階では src/、tests/、docs/cli_text_counter/features/ を変更しないでください。
- 修正計画にないついで修正やリファクタリングを含めないでください。
```

修正計画書では、次の点を特に確認します。

- 修正対象ファイルが具体的に書かれているか
- 変更してはいけないファイルが明確か
- 追加または更新するテストが明確か
- 仕様、設計、テスト計画への反映要否が整理されているか
- 別作業が必要な事項がある場合、実装修正と混ざっていないか
- 人間承認欄が残っているか

---

## 4. 人間承認欄を確認する

`30_bug_fix_plan.md` には、人間承認欄があります。

実装に進む前に、人間が以下を確認します。

```text
- [ ] 修正方針を確認した
- [ ] 修正対象ファイルを確認した
- [ ] 変更してはいけないファイルを確認した
- [ ] 追加・更新するテストを確認した
- [ ] 仕様・設計・テスト計画への反映要否を確認した
- [ ] 別作業事項を確認した
- [ ] 上記をすべて確認し、実装に進むことを承認する
```

すべてのチェックが入るまで、AIは実装を開始しません。

承認欄に未確認の項目がある場合は STOP します。AIが「たぶん大丈夫」と判断して実装に進んではいけません。

---

## 5. 承認済み計画に従って修正する

人間が `30_bug_fix_plan.md` を承認した後、`prompts/implement_bug_fix.md` を使って実装します。

この段階で変更してよいのは、修正計画書の「修正対象ファイル」に記載されたファイルだけです。

チャット例:

```text
prompts/implement_bug_fix.md を参照してください。

対象 command/app: cli_text_counter
対象 feature: text_counter
バグID: bug_001
バグ修正計画書: docs/cli_text_counter/bugs/bug_001/30_bug_fix_plan.md

補足条件:
- 30_bug_fix_plan.md は人間承認済みです。
- 承認欄にすべてチェックが入っていることを確認してから実装してください。
- 修正計画書の「修正対象ファイル」に記載されたファイルのみ変更してください。
- 修正計画にないついで修正やリファクタリングは行わないでください。
- 仕様・設計・テスト計画の更新が必要と判明した場合は、実装を中断して STOP し、別作業として報告してください。
- 作業後に python -m pytest を実行してください。
- tasks.md は直接更新しないでください。必要な場合は作業報告に「tasks.md 更新候補」として記載してください。
```

`implement_bug_fix.md` では、`tasks.md` を直接更新しません。

`tasks.md` の更新が必要だと判断した場合は、作業報告に更新候補として書きます。実際の `tasks.md` 更新は、人間が確認したうえで別作業として扱います。

---

## 仕様・設計・テスト計画の更新が必要な場合

調査や実装中に、仕様、設計、テスト計画の更新が必要だと分かることがあります。

その場合は、実装修正の中で勝手に `20_spec.md`、`21_design.md`、`22_flow.md`、`23_test_plan.md` を変更しません。

たとえば、次のように扱います。

| 分かったこと | 扱い |
|---|---|
| 仕様に空文字列の扱いが書かれていない | 仕様更新が必要な別作業として記録する |
| 設計上、空文字列を許可しない方針になっている | 設計確認または仕様確認待ちとして STOP する |
| テスト計画に空文字列の境界値がない | テスト計画更新が必要な別作業として記録する |
| 修正計画にないファイル変更が必要 | 実装を中断して STOP する |

バグ修正の目的は、承認済みの計画に沿って問題を直すことです。仕様変更や設計変更が必要な場合は、別の作業として切り分けます。

---

## 障害対応でコードを先に直した場合

実務では、障害対応などで、上記のフローより先にコードを直さざるをえない場合があります。

このキットでは、**コード先行そのものを禁止していません。** ただし、次を守ります。

- **コード先行を選ぶのは人間です。** AIが自ら「緊急だからコード先行にする」と判断して、上記の基本ルートを迂回することはありません。
- **通常のフローが不要になるわけではありません。** 緊急バイパス用のプロンプトや、承認を簡単に回避できる仕組みは用意していません。

事後には、次を行います。

```text
1. prompts/analyze_code_change_impact.md に、実施済みの変更（Git差分）を入力して、
   正式資料への反映要否を整理する
2. 人間が、反映先と反映順を確認する
3. 反映が必要な資料を、別作業として更新する
4. 必要なテストを実施する
5. 必要なレビューを行う
6. 未了項目を残課題として明示する
```

事後に通常のバグ管理文書（`10_bug_report.md`、`20_bug_investigation.md`、`30_bug_fix_plan.md`）を作成するかどうかは、人間が判断します。

**未反映事項を残したまま、作業を完了として扱いません。**

なお、正式資料が意味を定義していない実装詳細だけを直した場合（変更ルートA）は、正式資料への反映は不要です。この場合と、「反映が必要だが順序が後になった」コード先行の状態を混同しないでください。**コード先行は変更ルートではなく実施状態です。** 判断は `prompts/analyze_code_change_impact.md` の変更ルートと実施状態で整理します。

---

## このチュートリアルでは src/ と tests/ を変更しない

このチュートリアルは、バグ修正フローの説明です。

次のファイルは変更しません。

- `src/cli_text_counter/features/text_counter.py`
- `src/cli_text_counter/entrypoint.py`
- `tests/cli_text_counter/features/test_text_counter.py`
- `tests/cli_text_counter/test_entrypoint_text_counter.py`
- `tests/cli_text_counter/test_integration_text_counter.py`
- `docs/cli_text_counter/features/` 配下の既存ドキュメント

`docs/cli_text_counter/bugs/bug_001/` 配下の3ファイル（`10_bug_report.md`、`20_bug_investigation.md`、`30_bug_fix_plan.md`）は、このフローを実際に回したサンプルとしてリポジトリに配置済みです。各ステップの説明と合わせて参照してください。

---

## 作業後に確認すること

実際のバグ修正作業では、最後に次の点を確認します。

- `10_bug_report.md`、`20_bug_investigation.md`、`30_bug_fix_plan.md` が順番に作成されているか
- 調査段階で実装やテストを変更していないか
- 修正計画が人間承認済みか
- 修正対象ファイル以外を変更していないか
- 修正計画にないついで修正やリファクタリングをしていないか
- 仕様・設計・テスト計画の更新が必要な場合、別作業として記録されているか
- `tasks.md` を `implement_bug_fix.md` の中で直接更新していないか
- `python -m pytest` の結果が報告されているか
- 作業報告に、変更したファイル、変更内容、テスト結果、未対応事項が書かれているか

---

## 次の発展

このチュートリアルの発展として、次の作業が考えられます。

- 承認済み修正計画に従って、実際のバグ修正例を `src/` と `tests/` に追加する

これはこのチュートリアルでは扱いません。
