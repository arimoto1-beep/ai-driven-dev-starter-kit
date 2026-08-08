# entrypoint を実装してテストを作成してください

あなたは、このリポジトリのAI駆動開発ルールに従う開発補助者です。

このプロンプトは、コマンド/アプリ単位の `entrypoint.py` と、そのテストを作成または更新するためのものです。

`entrypoint.py` は、外部から呼ばれる入口です。  
feature 固有のロジックは `features/` 配下に置き、`entrypoint.py` は薄く保ってください。

このプロンプトファイルは直接書き換えず、チャットでこのファイルのパスと「利用者が指定する項目」を指定して使います。

## 必須参照ルール

この節は、この task で必ず読むルール文書**一覧**の正本です。各ルールの**内容**は、ここに列挙したルール文書を正本とします。このプロンプトが core や project を再定義するものではありません。

`## 参照するファイル` は今回の作業対象資料であり、このルール文書一覧とは役割が異なります。

### 作業開始時に読む

- `docs/rules/core/10_workflow.md`（入口処理と業務ロジックの責務を分ける）
- `docs/rules/core/30_change_safety.md`（作業対象外を変更しない）
- `docs/rules/project/30_development_rules.md`
- `docs/rules/project/40_testing_rules.md`

### 作業完了時に読む

- `docs/rules/core/50_records_and_reporting.md`

---

## 利用者が指定する項目

利用者は、チャットで以下を指定します。

- コマンド/アプリ名: `<command_or_app_name>`
- 対象 overview: `docs/<command_or_app_name>/10_overview.md`
- 対象 entrypoint: `src/<command_or_app_name>/entrypoint.py`
- 作成または更新するテストファイル: `tests/<command_or_app_name>/test_entrypoint_<short_name>.py`
- 対象 feature: `必要に応じて feature 名を書く。全体対象の場合は「10_overview.md の機能一覧に従う」`
- short_name: `単一 feature の command/app では feature 名。複数 feature を束ねる command/app では command/app を短く表す名前`
- 補足条件: `必要に応じて書く。なければ「なし」`

## 参照するファイル

- `docs/<command_or_app_name>/10_overview.md`

必要に応じて、以下も参照してください。

- `docs/<command_or_app_name>/features/<feature_name>/20_spec.md`
- `docs/<command_or_app_name>/features/<feature_name>/21_design.md`
- `docs/<command_or_app_name>/features/<feature_name>/22_flow.md`
- `docs/<command_or_app_name>/features/<feature_name>/23_test_plan.md`
- `docs/<command_or_app_name>/features/<feature_name>/24_review_checklist.md`
- `src/<command_or_app_name>/features/<feature_name>.py`
- `tests/<command_or_app_name>/features/test_<feature_name>.py`

## 作成または更新するファイル

- `src/<command_or_app_name>/entrypoint.py`
- `tests/<command_or_app_name>/test_entrypoint_<short_name>.py`

## 変更してよいファイル

- `src/<command_or_app_name>/entrypoint.py`
- `tests/<command_or_app_name>/test_entrypoint_<short_name>.py`

## 変更してはいけないファイル

この節は、**今回の task で変更を許可されていないファイル**です。project が定める**保護対象**（`docs/rules/project/50_ai_permissions.md`）とは別のレイヤであり、両方を満たす必要があります。

明示指示がない限り、以下は変更しないでください。

- このプロンプトファイル
- `AGENTS.md`
- `README.md`
- `docs/overview.md`
- `docs/how_to_use_prompts.md`
- `docs/templates/`
- `docs/<command_or_app_name>/10_overview.md`
- `docs/<command_or_app_name>/11_integration_test_plan.md`
- `docs/<command_or_app_name>/features/`
- `src/<command_or_app_name>/features/`
- `src/common/`
- `tests/<command_or_app_name>/features/`
- `prompts/`
- 他のコマンド/アプリ配下
- CI/CD、デプロイ関連のファイル

## ファイル出力先と命名に関する追加ルール

- entrypoint テストの標準出力先は `tests/<command_or_app_name>/test_entrypoint_<short_name>.py` です。
- `<short_name>` は、単一 feature の command/app では feature 名を使います。複数 feature を束ねる command/app では、command/app を短く表す名前を使います。
- 利用者が指定した出力先パス（例: `src/<command_or_app_name>/entrypoint.py` および `tests/<command_or_app_name>/test_entrypoint_<short_name>.py`）は、AIの判断で変更してはいけません。
- `pytest` の `import` mismatch やテストファイル名の衝突が発生した場合でも、標準命名ルールと現状の差分を確認せずに、AI判断で別名ファイルを作成してはなりません。
- こういった問題が検出された場合は、ファイルを変更せずに「確認事項」として報告してください。確認事項には少なくとも以下を含めてください:
	- 発生した問題の簡潔な説明（例: import file mismatch）
	- 衝突している既存ファイルのパス
	- 利用者が指定した出力先パス
	- 標準命名ルールとの差分
	- 可能な代替案（例: 標準命名へのリネーム、`__init__.py` の追加など）
	- 推奨案（利点・欠点を簡潔に）
	- 人間による判断が必要な事項（どの案を採るか等）

 例: `import file mismatch` が発生した場合は、AIは代わりに別名ファイルを作らず、上記の確認事項を提示してユーザーの指示を待ちます。

## 作業範囲

1. `docs/<command_or_app_name>/10_overview.md` を確認してください
2. 必要に応じて対象 feature の仕様、設計、呼び出し定義、テスト計画を確認してください
3. `entrypoint.py` が担当すべき責務を整理してください
4. feature 固有のロジックが `entrypoint.py` に入らないようにしてください
5. `src/<command_or_app_name>/entrypoint.py` を作成または更新してください
6. `tests/<command_or_app_name>/test_entrypoint_<short_name>.py` を作成または更新してください
7. 実装後、可能であれば `python -m pytest` を実行してください
8. `python -m pytest` が環境理由で失敗する場合は、利用可能な Python 実体で代替実行してください
9. 実行したコマンドと結果を正確に報告してください

## entrypoint の実装方針

`entrypoint.py` は、CLI入口として薄くしてください。

entrypoint が担当すること:

- CLI引数を受け取る
- 必要な feature を呼び出す
- feature の結果を受け取る
- 結果を標準出力に出す
- 終了コードを返す

entrypoint に入れてはいけないこと:

- feature 固有の業務ロジック
- 複雑な変換処理
- feature 内部で判断すべき条件分岐
- 共通化候補の実装
- 仕様にない便利機能
- 外部API連携
- CI/CD やデプロイに関する処理

## feature との分担

feature 固有の処理は、以下に置きます。

- `src/<command_or_app_name>/features/<feature_name>.py`

entrypoint は、その feature を呼び出すだけにしてください。

feature 側が未実装、または設計と矛盾している場合は、勝手に feature 実装を変更しないでください。

その場合は、entrypoint 実装を止め、確認事項として報告してください。

## 複数 feature を束ねる場合

command/app が複数 feature を持つ場合は、以下の方針で実装してください。

- `argparse` の `subparsers` を使い、サブコマンド名と feature 呼び出しを1対1で対応させます
- サブコマンド名・引数名は `10_overview.md` の機能一覧・実行イメージに従います
- `10_overview.md` に記載のないサブコマンドや引数を勝手に追加しないでください
- 判断できない場合は、確認事項として報告し、実装で勝手に決めないでください

単一 feature の command/app では、無理に `subparsers` を使わず、通常の引数解析に従ってください。

複数 feature を束ねる entrypoint の完成サンプルはこのリポジトリには含まれていません。
参考にする場合は、既存の単一 feature サンプル（`cli_hello_greeting` など）の実装方針を応用してください。

## テスト実装の方針

`test_entrypoint_<short_name>.py` では、entrypoint の責務を確認してください。

確認すること:

- CLI引数または入力を受け取れること
- 対象 feature を呼び出せること
- feature の結果が標準出力に反映されること
- 正常終了時に期待する終了コードを返すこと
- 引数不足や不正入力時に期待する扱いになること

feature 内部の詳細ロジックを、`test_entrypoint_<short_name>.py` で過剰に確認しないでください。

feature 内部の詳細は、以下で確認します。

- `docs/<command_or_app_name>/features/<feature_name>/23_test_plan.md`
- `tests/<command_or_app_name>/features/test_<feature_name>.py`

## テスト実装の注意点

- `pytest` を使ってください
- 標準出力の確認が必要な場合は、`capsys` を使ってください
- サブプロセス実行が必要な場合は、標準ライブラリの `subprocess` を使ってください
- 外部APIや外部システムには接続しないでください
- 実ファイル操作が必要な場合は、`tmp_path` などの一時領域を使ってください
- 実行環境に依存しすぎるテストは避けてください
- テストを通すために feature 実装や `src/common/` を勝手に変更しないでください

## 情報不足時のルール

entrypoint を実装するには情報が不足している場合は、いきなり `entrypoint.py` や `test_entrypoint_<short_name>.py` を作成または更新しないでください。

先に「確認事項」として、不足している情報を箇条書きで提示してください。

特に以下が不明な場合は、確認を優先してください。

- コマンド/アプリとしての入力
- コマンド/アプリとしての出力
- 呼び出す feature
- feature に渡す値
- feature から受け取る値
- 標準出力の形式
- 終了コード
- エラー時の扱い
- `10_overview.md` の Boundary

ただし、`10_overview.md`、対象 feature の `20_spec.md`、`22_flow.md`、実装ファイルから明確に読み取れる場合は、それをもとに整理して構いません。

## entrypoint が作りにくい場合

entrypoint 実装中に、feature 実装や設計が entrypoint から呼び出しにくい構造だと判断した場合でも、勝手に `src/<command_or_app_name>/features/` を変更しないでください。

その場合は、以下を作業報告に記載してください。

- entrypoint が作りにくい理由
- 影響する feature
- 影響するファイル
- 見直し候補
- 実装側の変更が必要そうか

実装側の変更が必要かどうかは、人間レビューで判断します。

## 禁止事項

- 情報不足のまま `entrypoint.py` や `test_entrypoint_<short_name>.py` を作成しないでください
- `10_overview.md` と矛盾する entrypoint を作成しないでください
- feature の仕様や設計と矛盾する entrypoint を作成しないでください
- feature 固有ロジックを `entrypoint.py` に入れないでください
- テストを通すために feature 実装を変更しないでください
- `src/<command_or_app_name>/features/` を変更しないでください
- `src/common/` を作成・更新しないでください
- `docs/` を変更しないでください
- `AGENTS.md` を変更しないでください
- `prompts/` を変更しないでください
- CI/CD、デプロイ資産を追加しないでください
- 外部APIや外部システムへ接続する処理を追加しないでください
- 仕様にない便利機能を追加しないでください

## 作業後の報告

作業後は、以下を簡潔に報告してください。

- 作成または更新したファイル
- 参照したファイル
- 実装した entrypoint の概要
- 対象 feature
- 主な正常系
- 主な異常系
- `10_overview.md` との整合確認結果
- 対象 feature の `22_flow.md` との整合確認結果
- テストを実行した場合、そのコマンドと結果
- テストを実行できなかった場合、その理由
- 確認事項を提示した場合、その理由
- 仮定を置いた場合、その内容
- entrypoint が作りにくい点があった場合、その内容

## レビュー補助メモ

作業後の報告に、レビュー補助メモを含めてください。
記載項目とルールは `docs/rules/core/50_records_and_reporting.md` の「レビュー補助メモ」に従います（このプロンプトには定義を複製しません）。

レビュー補助メモは作業完了報告（チャット）に出力します。`tasks.md` には書きません。

## 作業後の tasks.md 更新候補

このプロンプトでは `tasks.md` を直接更新しません。

`tasks.md` の更新が必要と判断した場合は、作業報告に「tasks.md 更新候補」として記載してください。
`tasks.md` の実際の更新は、人間が確認したうえで別作業として行います。
