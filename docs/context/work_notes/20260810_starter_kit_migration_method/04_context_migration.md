# context移行

## rulesと同じ方法が必要だと思っていた

rules移行の検証後、
次に既存環境の `docs/context/` をどう扱うか考えた。

新版では `work_notes` を導入し、
旧 `ai_work_logs` を凍結する。

最初は、

> contextもrulesと同じように旧形式から新版形式へ移行する必要があるのではないか

と考えた。

特に既存環境には、

- `docs/context/rejected_verbose_option.md`
- `docs/context/ai_work_logs/20260704_T-030_add_ai_work_logs.md`
- `docs/context/ai_work_logs/20260726_T-031_add_code_change_impact_prompt.md`

といった履歴が存在する。

旧AI作業ログを `work_notes` 形式へ変換する案も考えた。

## 過去ログを変換しないことにした

検討した結果、その案は採用しなかった。

rulesとcontextでは資産の性質が違う。

rulesは、

> 現在・これからAIがどう振る舞うか

を決める。

そのため、利用者が追加した意味を新版へ移す必要がある。

一方contextは、

> その当時、何が記録されていたか

そのものに価値がある。

旧AI作業ログを新しい形式へ再構成すると、

- 当時の記録形式
- 当時重視していた情報
- 当時残していなかった情報
- 当時の言葉
- 当時の判断の粒度

を後から再解釈することになる。

AIに変換させれば、
要約・補完・整理が入り込む可能性もある。

過去履歴については、

> きれいな新形式に揃えること

より、

> 当時の記録を壊さないこと

を優先した。

## contextは「既存保持＋新運用追加型」

最終的にcontext移行は、

- 既存履歴はそのまま保持
- 旧 `ai_work_logs` の新規作成を停止
- 今後は `work_notes` を使用
- 運用READMEだけ新版へ切り替える

という方式にした。

rulesのような意味変換は行わない。

整理すると、

> rulesは「今の動き方」を移行する。
>
> contextは「これまでの記録」を守りつつ、
> 「これからの残し方」を変える。

という違いになった。

## context移行fixture

rules/work notes機構は新版だが、
`docs/context/` だけ旧状態というfixtureを作った。

開始commit:

`9e90542dc38f9a94a30256c0cae613d943faea58`

この時点で、

- `docs/rules/core/60_work_notes.md`
- `docs/rules/project/60_work_notes.md`
- `docs/templates/work_note_readme_template.md`
- `prompts/prepare_work_note.md`

などは存在する。

一方、

`docs/context/`

だけは旧版と一致させた。

これにより、

> work notes機構は導入済みだが、context運用だけ旧版

という状態から移行を検証できた。

## 新版contextとの差分

新版Cと比較すると、contextには13ファイルの追加・変更候補があった。

運用として必要なのは3ファイル。

- `M docs/context/README.md`
- `M docs/context/ai_work_logs/README.md`
- `A docs/context/work_notes/README.md`

それ以外に、新版作者自身のwork noteが12ファイルあった。

### `20260802_agents_rule_refactor/`

6ファイル。

AGENTS.md分割作業の経緯・判断・却下案など。

### `20260802_work_note_system/`

6ファイル。

work notes機能そのものを設計・実装した際の作業記録。

これらは仕組みの一部ではなく、
スターターキット作者自身の履歴。

利用者プロジェクトの履歴ではないため、
移行対象から除外した。

「新版に入っているから」
「参考になりそうだから」

という理由だけで利用者contextへコピーしない。

## Sonnet 5による実装

context移行の実装はSonnet 5で行った。

指示した変更は3ファイルだけ。

### 置換

- `docs/context/README.md`
- `docs/context/ai_work_logs/README.md`

### 新規追加

- `docs/context/work_notes/README.md`

変更禁止:

- `docs/context/rejected_verbose_option.md`
- 既存 `ai_work_logs` 2件

また、

- 旧ログをwork notesへ移動しない
- 変換しない
- 再生成しない
- 削除しない
- 新版作者のwork noteをコピーしない
- context外を変更しない

ことを明示した。

Sonnet 5の実装結果は想定通り3ファイルだけだった。

## 途中で起きたworktree取り違え

最初の実行では、AIが、

- `docs/rules/` が存在しない
- AGENTS.mdも未移行
- このままcontextだけ入れると参照切れになる

としてSTOPした。

fixtureをPowerShell側で確認すると、

- branchは `migration-test-context`
- HEADは `9e90542...`
- `docs/rules/` は存在
- `core/60_work_notes.md` も存在

していた。

原因はGit fixtureではなかった。

PowerShellは新しいcontext用worktreeへ移動していたが、
VS Codeを以前のworktreeで開いたままだった。

AIはVS Code側の別リポジトリを見ていた。

VS Codeを正しいworktreeで開き直すことで解消した。

このとき、
開始状態をcommitで固定していたため、

> fixtureがおかしいのか
> AIが別の場所を見ているのか

を比較的簡単に切り分けられた。

移行実験では、
prompt内容だけでなく「AIがどのworktreeを見ているか」も確認事項になる。

## 独立レビュー

実装後はcommitせず、別AIで読み取り専用レビューを行った。

確認内容:

- 変更が3ファイルだけか
- 3ファイルが新版参照commitと完全一致するか
- 既存履歴3ファイルが移行前と一致するか
- `work_notes/` がREADMEだけか
- 新版作者のwork note 12件が混入していないか
- READMEから参照されるrule / prompt / templateが存在するか
- 過去contextの再分類・変換が発生していないか
- context外へ余計な変更がないか

結果:

- 変更3件のみ
- 新版3ファイルとblob hash・バイト単位で一致
- 過去履歴3ファイルはGit blobが移行前と一致
- `work_notes/` 配下はREADMEだけ
- 作者work note混入なし
- 参照先リンク切れなし
- 過去contextの変換・再分類なし

レビュー結果は、

**軽微な指摘あり / 条件付きGO**

だった。

ただし指摘は成果物の欠陥ではなく、

- 新規 `work_notes/README.md` をcommit時にaddし忘れない
- 一時的に存在した `docs/context.zip` を誤ってcommitしない
- WindowsのCRLF差に注意

といったcommit操作上の内容だった。

## 実験結果

3ファイルだけを明示stageし、

`git diff --cached --check`

も問題なし。

最終commit:

`0e7d2b33e6859dd80171a2dd693cb4d040bc16fd`

commit message:

`test: migrate legacy context to work notes`

これで、

> 過去contextを変更せず、
> 今後の記録方式だけwork notesへ切り替えられる

ことを実験で確認した。