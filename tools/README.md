# 補助ツール案内

## このディレクトリについて

`tools/` には、検証結果の記録と品質情報の集約を補助するツールがあります。判定値や品質基準の正本はここではなく、関連する [`docs/rules/`](../docs/rules/README.md) 配下にあります。

## 内容

| ツール | 目的 | 主な入力・確認対象 | 主な出力先 |
|---|---|---|---|
| [`quality_run.py`](quality_run.py) | 指定した検証コマンドを実行し、その開始と結果を記録する | task ID、実行するコマンド | [`quality/events/`](../quality/events/) 配下の JSON Lines ファイル |
| [`quality_report.py`](quality_report.py) | 検証記録とレビュー結果を集約する | `quality/events/` と `docs/` 配下のレビュー結果 | [`quality/report.md`](../quality/report.md) |
| [`feature_runner.py`](feature_runner.py) | feature オートモードの runner。Worker と Reviewer を別プロセスとして分離して起動し、Gate記録で状態遷移する | `docs/rules/project/70_feature_loop.md` の設定ブロック、対象 feature の `gates/` | 対象 feature の `gates/` 配下の Gate記録 |

生成物の見方と各ファイルの位置づけは、[`quality/README.md`](../quality/README.md) を参照してください。ツールの引数や読み取り処理の詳細は各スクリプト自身にあります。

## feature_runner.py の使い方

すべて Python 標準ライブラリのみで動作します。追加の依存はありません。

```bash
# 仕様書（20_spec.md）のAIレビューだけを単独実行する（何度でも実行できる）
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --spec-review

# 現在状態を表示する（仕様承認の有無と製造開始条件も表示される）
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --status

# Gate記録の連鎖（因果）を表示する
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --history

# 実行せず、次の動作と組み立てたコマンドを表示する
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --dry-run

# 1 stage だけ進める
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --once

# 人間 Gate（CP1 / CP3）で自動停止するまで進める
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name>

# この実行だけモデルクラスを固定する（通常は指定しません）
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --model-class strong

# マニュアル介入からの復帰（Worker を起動せず、現在の成果物を Reviewer が見直す）
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --review-current G2

# BLOCKED からの復旧（原因を解消したあと、その stage を明示的に再試行する）
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --retry-blocked

# 通過済み stage のやり直し（完成後の修正。Worker から作り直す）
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --rework G2
```

### 完成後の修正（通過済み stage の変更）

**Gate を通過した後に成果物を変更すると、runner はそれを検出して停止します。**
古い `PASS` をそのまま完成扱いにしないためです。

```text
$ python tools/feature_runner.py --feature cli_demo/sample
通過済み stage の成果物が、その stage の判定後に変更されています。
  変更が検出された stage: G2
  再確認が必要な下流 stage: CP3

古い判定を完成扱いにしないため、ここで停止します。
どちらで再開するかは人間が決めてください。
  成果物を人間が直した場合   : --review-current G2
  AIに作り直させる場合       : --rework G2
```

戻り先は「誰が変更したか」ではなく、**どの工程で決める内容を変更したか**で決まります。

| 変更したもの | 戻る stage |
|---|---|
| 仕様・期待動作（`20_spec.md`） | `CP1` |
| 設計・処理方式（`21_design.md`、`22_flow.md`） | `G1` |
| 試験項目・試験観点（`23_test_plan.md`、`24_review_checklist.md`） | `G2` |
| 実装コード・テストコード | `CP3` |

- 検出は、Gate記録の `artifacts_hash`（runner が計算し、runner が照合する）で行います
- **`artifacts_hash` を持たない過去の Gate記録は「判定不能」として扱い、停止しません**（後方互換）
- **runner は自動で再開しません。** Worker を無条件に再実行すると人間の修正を上書きするおそれがあるため、どちらで再開するかは人間が決めます
- どちらの操作でも、その stage の新しい Gate記録が「全stage横断で最新の1件」になるため、以降は通常の stage 順で下流が再実行されます

`--status` では stage ごとの状態を確認できます。

```text
stage 成果物の baseline:
  CP1  上記の仕様 baseline で判定
  G1   通過時と同じ
  G2   **通過後に変更あり**
  CP3  通過時と同じ
```

### 3つの復旧操作の使い分け

**用途が違います。混同しないでください。**

| 操作 | 前提 | Worker | 用途 |
|---|---|---|---|
| `--retry-blocked` | 最新が `BLOCKED` | 起動する | **停止からの復旧**。原因を解消したあとの再試行 |
| `--review-current <stage>` | いつでも | 起動しない | **現在の成果物の再確認**。人間の修正を維持したまま判定し直す |
| `--rework <stage>` | いつでも | 起動する | **通過済み stage のやり直し**。AIに作り直させる |

- `--retry-blocked` は `BLOCKED` 専用です。完成後の修正には使えません（最新が `BLOCKED` でなければ拒否されます）
- `--rework` を製造 stage に使っても Manufacturing Preflight は働きます。仕様が未承認なら製造は始まりません
- `--rework CP1` を指定しても、**CP1 の人間承認は消えません。** 仕様レビュー後、承認待ちで停止します
- 4つの操作（`--spec-review` を含む）は同時に指定できません

### BLOCKED からの復旧

**`BLOCKED` は自動では再開しません。原因を解消しても、そのまま再実行すると同じ停止が続きます。**
権限不足や環境の不備で停止した場合も同じです。復旧には `--retry-blocked` の明示が必要です。

```text
0001_..._g1.md   verdict: BLOCKED / blocked_reason: state_error
        ↓  --retry-blocked
0002_..._g1.md   同じ stage を再実行した新しい記録
                 triggered_by: RETRY_BLOCKED
                 triggered_by_record: 0001_..._g1.md
```

- **過去の BLOCKED記録は削除も上書きもしません。** 履歴として残ります
- 最新 Gate が `BLOCKED` のときだけ受け付けます。それ以外の状態で指定すると、AIを起動せずエラーで停止します
- 再試行の後は、通常のオートモードへ戻ります
- `--review-current` とは同時に指定できません

人間 Gate の記録に「気になる点」を自然文で書いて再実行すると、**承認待ちより先に Reviewer が起動し**、現 stage 内修正・`RETURN`・`BLOCKED` のいずれかを根拠つきで判定します。処理済みのコメントは二重処理されません。

runner 自身が処理継続を禁止した場合（Reviewer の変更範囲違反、`max_rounds` 超過、`max_returns_per_gate` 超過、状態遷移の異常）も、`recorded_by: runner` の `BLOCKED` Gate記録を新規作成します。**画面出力ではなくファイルが正式記録です。**

**実行前に、[`docs/rules/project/70_feature_loop.md`](../docs/rules/project/70_feature_loop.md) の設定ブロックへ `model_cheap` / `model_standard` / `model_strong` と `ai_command` を記入してください。**
リポジトリへコミットしたくない場合は、同じ形式で `tools/feature_loop.local` へ書くと上書きされます（`.gitignore` 対象）。

### Claude Code を使う場合の設定例

条件を満たすAI CLI の**一例**です。**このスターターキットは Claude Code 専用ではありません。**
インストールと認証の手順は [リポジトリの README](../README.md) を参照してください。

#### 必要なオプション

| 用途 | Claude Code のオプション |
|---|---|
| 非対話で1回だけ実行する | `-p`（`--print`） |
| 使うモデルを指定する | `--model` |
| 確認プロンプトなしで許可する操作を決める | `--permission-mode`、`--allowedTools` |

オプションの正本は [Claude Code の CLI リファレンス](https://code.claude.com/docs/en/cli-reference) です。

#### `ai_command` の例

以下は、Git for Windowsを導入し、Claude CodeがBash toolを使う環境での例です。

```text
ai_command = claude,-p,{instruction},--model,{model},--permission-mode,acceptEdits,--allowedTools,Bash(python -m pytest *)
```

- カンマ区切りの argv テンプレートです。**shell を経由しないため、クォートは不要**です
- `{instruction}` に指示文、`{model}` に実モデル名が入ります

#### `model_*` の例

`--model` はモデルのエイリアス（`haiku` / `sonnet` / `opus` など）と正式名のどちらも受け付けます。
**エイリアスを使うと、モデル名が更新されても設定を書き換えずに済みます。**

```text
model_cheap    = haiku
model_standard = sonnet
model_strong   = opus
```

正式なモデルIDで固定することもできます。
利用できるモデルIDは時期や契約によって変わるため、現在の Claude Code CLI リファレンス で確認してください。

どのクラスにどのモデルを割り当てるかは利用者が決めます。

#### 権限（permission）の考え方

**オートモードでは、AI がファイルを読み書きし、CP3 ではテストを実行します。**
非対話実行（`-p`）では**確認プロンプトに答えられない**ため、必要な操作を事前に許可しておく必要があります。
許可がないと、AI が作業を完了できず runner が停止します。

上記の例では、`acceptEdits` で作業ディレクトリ内のファイル編集などを自動承認し、
`--allowedTools` で pytest の実行を追加で許可しています。

| 指定 | 役割 |
|---|---|
| `--permission-mode acceptEdits` | ファイル編集や一部の一般的なファイル操作を自動承認する |
| `--allowedTools "Bash(python -m pytest *)"` | `python -m pytest` に一致する Bash コマンドを追加で許可する |

`acceptEdits` はファイル編集だけに限定されません。
作業ディレクトリ内では `mkdir`、`touch`、`mv`、`cp` など一部の一般的なファイルシステム操作も自動承認されます。
正確な範囲は Claude Code の公式permission仕様を確認してください。

**すべてを無条件に許可する設定（`bypassPermissions` など）を既定として推奨しません。**
必要な操作だけを許可し、**必要以上に強い権限を与えないでください。**

> **これは設定例です。許可範囲は、各利用環境で確認して決めてください。**
> 変更範囲のガードは runner 側でも働きますが（`stage_*_worker` / `stage_*_reviewer`）、
> AI CLI に与える権限は利用者の責任で決める設定です。

**Windows でネイティブに使う場合の注意**：Claude Code が実際にテスト実行に使うshellに合わせて、
`Bash(...)` または `PowerShell(...)` の許可ルールを設定してください。

Git for Windows を導入すると Bash tool を利用できます。
未導入の場合は PowerShell tool が使われます。
Git for Windows がある環境でも PowerShell tool を利用できる場合があるため、
単純に「Git Bash がある＝Bashだけ」とは限りません。

利用環境は `claude doctor` などで確認してください。

権限モードと許可ルールの書式の正本は、Claude Code の公式ドキュメントです。

### モデル選択

**どのモデルクラスを使うかは runner が決めます。利用者が役割ごとに決める必要はありません。**

```text
プロンプトの基礎レベル  +  feature 難易度  =  最終レベル
        ↓
1 → cheap ／ 2 → standard ／ 3 → strong
```

- feature 難易度（`easy` / `normal` / `hard`）は、**CP1 の仕様レビューで1回だけ**判定され、CP1 Gate記録に残ります。モデル選択のために別のAIを呼びません
- G1 / G2 / CP3 では再判定しません。`20_spec.md` を変更して再レビューになった場合だけ、判定し直されます
- プロンプトごとの基礎レベルは設定ブロックの `base_level_*` です。通常は変更しません
- 実際に使ったクラスは Gate記録（`worker_model_class` / `reviewer_model_class` / `model_selection`）に残ります

今回だけ固定したい場合は `--model-class` を指定します。指定すると難易度と基礎レベルは使いません。

```bash
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --model-class strong
```

`--dry-run` で、実行前に選択結果を確認できます。

```text
--- dry-run: stage=G1 kind=run mode=create
モデル選択: auto（feature_difficulty=normal）
Worker   base=2  class=standard  model=<設定した実モデル>
  使用prompt: prompts/create_function_design.md, prompts/create_function_call_flow.md
Reviewer base=2  class=standard  model=<設定した実モデル>
  使用prompt: prompts/review_stage.md
```

定義の正本は [`docs/rules/project/70_feature_loop.md`](../docs/rules/project/70_feature_loop.md) の「モデル選択」です。

### 人間側の仕様と、AI製造側の境界

**`20_spec.md` までが人間側の成果物、`21_design.md` 以降が AI 製造側の成果物です。**

```text
20_spec.md を用意する
        ↓
--spec-review で仕様レビュー（何度でも。製造は始まらない）
        ↓
人間・PJ上位者・顧客のレビュー（runner の外の工程を含む）
        ↓
CP1 Gate記録の「仕様承認」にチェックを入れる    ← baseline 確定
        ↓
runner を起動する
        ↓
Manufacturing Preflight（runner が自動確認）
        ↓
21_design.md / 22_flow.md → テスト設計 → 実装
```

Manufacturing Preflight が確認するのは次の3つです。**人間が手作業で確認する必要はありません。**

1. 仕様レビューが `PASS` していること
2. 人間による仕様承認が存在すること
3. 承認対象の `20_spec.md` と現在の `20_spec.md` が**同一 baseline**であること（内容ハッシュで判定）

**承認後に `20_spec.md` を変更すると、その承認は無効になります。** `--spec-review` で再レビューし、承認し直してください。

**製造開始後、AIは承認済み仕様を超えて仕様判断を追加できません。** 不足を見つけた場合は補完せず、
不足の種類に応じて現 stage 内修正 / `RETURN(G2)` / `RETURN(G1)` / `RETURN(CP1)` / `BLOCKED` のいずれかになります。

## 関連するルール

- テストの実行方法: [`docs/rules/project/40_testing_rules.md`](../docs/rules/project/40_testing_rules.md)
- レビュー結果と集計の運用: [`docs/rules/project/25_review_policy.md`](../docs/rules/project/25_review_policy.md)
- 次工程移行判定: [`docs/rules/core/20_approval_and_review.md`](../docs/rules/core/20_approval_and_review.md)
- オートモード（stage、Gate、モデル選択、Gate記録）: [`docs/rules/project/70_feature_loop.md`](../docs/rules/project/70_feature_loop.md)
