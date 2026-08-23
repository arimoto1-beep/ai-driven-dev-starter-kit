# 補助ツール案内

## このディレクトリについて

`tools/` には、検証結果の記録と品質情報の集約を補助するツールがあります。判定値や品質基準の正本はここではなく、関連する [`docs/rules/`](../docs/rules/README.md) 配下にあります。

## 内容

| ツール | 目的 | 主な入力・確認対象 | 主な出力先 |
|---|---|---|---|
| [`quality_run.py`](quality_run.py) | 指定した検証コマンドを実行し、その開始と結果を記録する | task ID、実行するコマンド | [`quality/events/`](../quality/events/) 配下の JSON Lines ファイル |
| [`quality_report.py`](quality_report.py) | 検証記録とレビュー結果を集約する | `quality/events/` と `docs/` 配下のレビュー結果 | [`quality/report.md`](../quality/report.md) |
| [`feature_runner.py`](feature_runner.py) | feature オートモードの runner。Worker と Reviewer を別プロセスで交互に起動し、Gate記録で状態遷移する | `docs/rules/project/70_feature_loop.md` の設定ブロック、対象 feature の `gates/` | 対象 feature の `gates/` 配下の Gate記録 |

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

# この実行だけモデルクラスを上書きする
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --role-design strong --role-review strong

# マニュアル介入からの復帰（Worker を起動せず、現在の成果物を Reviewer が見直す）
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --review-current G2

# BLOCKED からの復旧（原因を解消したあと、その stage を明示的に再試行する）
python tools/feature_runner.py --feature <command_or_app_name>/<feature_name> --retry-blocked
```

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
- オートモード（stage、Gate、モデル役割、Gate記録）: [`docs/rules/project/70_feature_loop.md`](../docs/rules/project/70_feature_loop.md)
