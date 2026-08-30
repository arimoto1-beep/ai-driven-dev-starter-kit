# Claude Code のセットアップ導線を追加する

## 目的

**README で「非対話で起動できるAI CLI が必要」と説明していたが、
「では何をインストールし、どう設定すれば動くのか」まで到達できる具体例がなかった。**

そこで、**Claude Code を具体例として、インストールからスターターキットの設定までの最小導線**を追加した。

`starter-kit-47-auto-mode-document-refresh`（commit `492bda3`）の**追加改訂**である。

## 状態

進行中（変更完了。人間の差分確認と commit / tag / push が未実施）

## 作業日

2026-08-30

## 背景

Phase 1〜5 のドキュメント刷新では、オートモードに必要なAI CLI の**条件**を書いた。

```text
1回の指示を渡して非対話で実行できる
使うモデルをコマンドライン引数で指定できる
リポジトリ内のファイルを読み書きできる
テスト実行コマンドを許可できる
```

**条件は書いたが、それを満たす具体的なツールと手順を1つも示していなかった。**
初めて使う人は「AI CLI が必要」で止まってしまう。

## 基本方針

- **Claude Code は「利用できるAI CLI の一例」として示す。** 専用キットにはしない
- **外部ツールの仕様をキット内へコピーしない。** 正本は Anthropic 公式ドキュメント
- README は「入れる → 確認する → 認証する → 設定は tools/README へ」まで
- `ai_command` や permission の詳細は `tools/README.md` に置く
- **permission は慎重に扱う。** `bypassPermissions` を既定として推奨しない
- 005 チュートリアルの本題は変更しない

## 変更したファイル

| ファイル | 変更 |
|---|---|
| `README.md` | 「想定する利用環境」へ小節「Claude Code を使う場合の例」を追加（インストール／確認／認証／次の設定への導線） |
| `tools/README.md` | 設定記入の案内の直後へ小節「Claude Code を使う場合の設定例」を追加（オプション／`ai_command`／`model_*`／permission の考え方） |
| `docs/tutorials/005_automode_first_feature.md` | 「設定」節へ導線を1か所追加（引用ブロック4行） |

**それ以外のファイルは変更していない。**

## 公式ドキュメントとの照合

**記憶ではなく、作業時点（2026-08-30）の公式ドキュメントと、インストール済み CLI で確認した。**

| 確認項目 | 結果 |
|---|---|
| Windows PowerShell インストール | `irm https://claude.ai/install.ps1 \| iex`（公式のとおり） |
| macOS / Linux / WSL | `curl -fsSL https://claude.ai/install.sh \| bash` |
| **Git for Windows** | **必須ではない。** 公式に「optional」と明記。導入すると Bash ツール（Git Bash）が使え、未導入なら PowerShell ツールが使われる |
| `claude --version` | 存在。バージョン文字列を表示 |
| `claude doctor` | 存在。**「セッションを開始せず読み取り専用で診断を表示する」**と公式に明記 |
| 認証 | `claude` を起動しブラウザの案内に従う。**対応プランの契約が必要で、無料プランには含まれない** |
| 非対話実行 | `-p`（`--print`）。ローカル CLI の `--help` でも確認 |
| モデル指定 | `--model`。**エイリアス（`haiku` / `sonnet` / `opus` / `fable`）と正式名の両方**を受け付ける |
| permission mode | `--permission-mode`。値は `default` / `acceptEdits` / `plan` / `auto` / `dontAsk` / `bypassPermissions` / `manual` |
| ツール許可 | `--allowedTools`（`--allowed-tools`）。`Bash(git log *)` のようなパターン |
| Windows のシェルツール名 | **Git Bash あり → `Bash(...)`／なし → `PowerShell(...)`** |

ローカルの Claude Code は `2.1.227 (Claude Code)`。`claude --help` で
`-p, --print` / `--model` / `--permission-mode` / `--allowedTools, --allowed-tools` の存在を確認した。

**`claude` セッションは起動していない。** 実AI呼び出しも行っていない。

## 既存設定との整合

`tools/README.md` に載せた `ai_command` は、**このリポジトリで実際に使われている
`tools/feature_loop.local` の設定と同じ形**である。想像で argv 順序を作っていない。

```text
ai_command = claude,-p,{instruction},--model,{model},--permission-mode,acceptEdits,--allowedTools,Bash(python -m pytest *)
```

この設定は、`20260823_feature_auto_mode_real_ai_validation` と
`20260829_model_auto_selection` の実AI検証で実際に動作した実績がある。

## 決定事項

### 1. `model_*` の例はエイリアスを主に示す

`--model` がエイリアス（`haiku` / `sonnet` / `opus`）を受け付けるため、**エイリアスを主な例**とした。
モデル名が更新されても設定を書き換えずに済む。

正式名の例（`claude-haiku-4-5` など）も併記したが、
**「モデル名と利用できるモデルは時期や契約によって変わる。実際に利用できるモデル名へ置き換える」**
と明記した。**特定モデルをキット仕様として固定していない。**

### 2. permission は「必要な操作だけ許可する」形で説明する

`--permission-mode acceptEdits` と `--allowedTools "Bash(python -m pytest *)"` が
それぞれ何を許可するのかを表で分けて説明した。

そのうえで次を明記した。

- 非対話実行では**確認プロンプトに答えられない**ため、事前に許可が必要であること
- **`bypassPermissions` などの無条件許可を既定として推奨しないこと**
- **必要以上に強い権限を与えないこと**
- **これは設定例であり、許可範囲は各環境で確認して決めること**

### 3. Windows のシェルツールの違いを1行だけ補足する

**Git Bash の有無で許可ルールの書式が `Bash(...)` と `PowerShell(...)` に変わる。**
このリポジトリの例は `Bash(...)` を使っているため、**未導入の環境ではそのままでは効かない。**
`claude doctor` で確認できることも添えた。

### 4. 外部ツールの仕様は正本へ逃がす

README に [setup](https://code.claude.com/docs/en/setup)、
`tools/README.md` に [CLI リファレンス](https://code.claude.com/docs/en/cli-reference) へのリンクを置いた。
**インストール手順やオプションの全仕様をキット内へコピーしていない。**

## 作業中に見つかったが、今回直さなかったもの

**なし。** 今回の変更範囲で、既存文書との不整合は見つからなかった。

## 次に行うこと

1. **人間が差分を確認する**
2. commit / tag / push（**未実施**）
   - 新 tag 候補：`starter-kit-47-auto-mode-document-refresh-r2`
   - **既存の `starter-kit-47-auto-mode-document-refresh` は動かさない**

## 関連する作業メモ

- `20260830_v2_document_refresh`（Phase 1〜5 のドキュメント刷新。この作業の前提）
- `20260823_feature_auto_mode_real_ai_validation`（`ai_command` の動作実績）
- `20260829_model_auto_selection`（モデル選択と `model_*` の扱い）

## 付随ファイル一覧

なし（この README のみ）。
