# 実装・レビューの経緯

## 第1段階

### 実装前

README不足を調査し、次の方針を人間が確認した。

* READMEの役割は「説明・一覧・導線」
* ルールの正本は `docs/rules/`
* 既存文書との重複や二重管理を避ける
* いきなり作成せず、まず配置案と内容案を確認する

配置案の確認後、Codexへ実装を依頼した。

### 第1段階で追加したREADME

* `docs/README.md`
* `prompts/README.md`
* `docs/templates/README.md`
* `docs/tutorials/README.md`
* `tools/README.md`
* `quality/README.md`

### 第1段階で更新した既存ファイル

* `README.md`
* `docs/common/README.md`
* `docs/how_to_use_prompts.md`

Codexの報告では、

* prompt 26件
* template 21件
* tutorial 4件

をそれぞれの索引へ収録した。

`docs/how_to_use_prompts.md` にあった26 promptの一覧は削除し、`prompts/README.md` への導線に変更した。

### 第1段階の検証報告

Codexは全18 READMEの相対リンクを確認し、リンク切れなしと報告した。

pytestでは、最高で20件成功・1件失敗となった。

失敗は `cli_hello_greeting` のsubprocess結合試験で発生する既知のWindows環境依存エラー `WinError 6` と報告された。

今回コード・テストは変更しておらず、READMEのリンク・網羅性確認には影響しないものとして、README整理と切り分けた。

## 第1段階後の人間側レビュー

新規READMEの配置と内容は概ね意図どおりだった。

一方で、README全体を確認すると、ルートREADMEなどに正本と重複するルール本文が多数残っていた。

特にルートREADMEには、

* 実装責務
* 承認ゲート
* 変更ルート
* バグ修正フロー
* テスト条件
* AIの変更範囲

など、単なる入口説明を越える内容が残っていた。

このため、第1段階の「入口追加」はGOとしつつ、README原則を全体へ適用する第2段階が必要と判断した。

## Git状態確認で起きた確認ミス

第1段階のレビュー時、確認側AIはアップロードされたZIPの状態を見て、「README作業以外の既存変更も多数残っている」可能性を指摘した。

その後、人間が実際の作業ツリーで `git status` を実行した結果、未コミット変更は次の9ファイルだけだった。

変更済み:

* `README.md`
* `docs/common/README.md`
* `docs/how_to_use_prompts.md`

未追跡:

* `docs/README.md`
* `docs/templates/README.md`
* `docs/tutorials/README.md`
* `prompts/README.md`
* `quality/README.md`
* `tools/README.md`

したがって、「他の未コミット変更が多数ある」という確認は、アップロードZIPの状態と実際のGit作業ツリーを混同したものだった。

以後、第2段階の依頼では、人間が提示したこのGit状態を開始点として明示した。

### 次回への注意

アーカイブ内のファイル状態だけから、実際のGit差分や未コミット状態を推定しない。

Git状態については、

* 実際の `.git` を確認できる環境
* 人間が実行した `git status`
* 作業側AIが実リポジトリで実行した結果

のいずれかを根拠にする。

## 第2段階

第2段階では、既存READMEを棚卸しし、正本と重複する正式な条件や判断を正本への導線へ置き換えるようCodexへ依頼した。

更新対象となったのは次の5ファイルだった。

* `README.md`
* `docs/rules/README.md`
* `docs/context/README.md`
* `docs/context/work_notes/README.md`
* `docs/context/ai_work_logs/README.md`

第1段階の変更は維持した。

### 正本へ委譲した主な内容

Codex報告では、次の内容をREADMEから正本へ委譲した。

* 開発者の責務・実装制約
* 承認・レビュー・次工程移行判定
* 変更区分・整合性確認
* テスト方針・検証方法
* 文書構造・テンプレート対応
* AIの変更範囲・保護対象
* contextの扱い・競合時の判断
* work noteの配置・命名・更新方法
* 旧AI作業ログの凍結・更新制約

READMEには、それぞれの領域の意味、現在ある内容、正本へのリンクを残した。

## 第2段階の実ファイル確認

アップロードされた第2段階の文書一式を確認した。

ルート `README.md` は、第1段階時点の466行から119行になった。

単純に文章量を削っただけではなく、

* リポジトリの目的
* 体験できること
* 主要領域
* docs・src・testsの関係の概要
* 作業の全体像
* 初めて読む人向けの導線
* サンプル

を残し、正式な条件は各ルール正本へ誘導する構成になっていた。

`docs/rules/README.md` も、個別ルールの本文ではなく、

* 読み始める場所
* core / project / taskの関係
* 各ルール正本の索引

を中心とする構成へ整理された。

context系READMEも同様に、ディレクトリの用途と読む入口を中心とする構成になった。

## 第2段階の検証

Codex報告:

* 全18 READMEの相対リンク: 正常
* 一般README 12ファイルの見出し・末尾空白: 正常
* 第1段階の追加6 README: 維持
* `docs/how_to_use_prompts.md` の第1段階変更: 維持
* 指定外README追加: なし
* `git diff --check`: エラーなし
* ソース、テスト、prompt、template、quality report: 第2段階では変更なし
* pytest: 第2段階では未実行

第2段階はREADMEのみの整理であり、第1段階で確認された `WinError 6` を追跡することは今回の品質確認へ直接寄与しないと判断して、pytestを必須にしなかった。

## 最終Git状態

Codexが最後に報告した `git status` は次のREADME関連変更のみだった。

変更済み:

* `README.md`
* `docs/common/README.md`
* `docs/context/README.md`
* `docs/context/ai_work_logs/README.md`
* `docs/context/work_notes/README.md`
* `docs/how_to_use_prompts.md`
* `docs/rules/README.md`

未追跡:

* `docs/README.md`
* `docs/templates/README.md`
* `docs/tutorials/README.md`
* `prompts/README.md`
* `quality/README.md`
* `tools/README.md`

コミット・pushは行われていない。

このGit状態は、こちらでは `.git` を直接確認しておらず、Codexおよび人間が提示した結果に基づく。

## 最終レビュー

最終レビューでは、今回の対象についてGOと判断した。

目標としていた関係は次の形になった。

```text
README
  ↓
何であるか・何があるか・どこを見るか

docs/rules/
  ↓
正式に何をしなければならないかを判断する正本
```

## 今回の作業から得た注意点

### 「READMEを追加する」と「既存READMEを整理する」は別の作業になり得る

入口不足だけを見ていると、新規READMEの追加で作業を終えやすい。

しかしREADMEの責務を定義し直した場合、既存READMEも同じ基準で棚卸ししないと、古い役割分担が残る。

今回は第1段階後のレビューでこれに気づき、第2段階が必要になった。

### 実装依頼の範囲が狭いと、AIはその範囲で正しく完了する

第1段階では `docs/common/README.md` の薄型化は明示したが、その他の既存README全体の棚卸しを明示しなかった。

Codexは指示された範囲を実装したため、後から追加作業になった。

「同じ原則を既存資産全体にも適用するか」を実装依頼時に確認すると、同様の手戻りを減らせる。

### READMEの短さではなく、責務境界を見る

行数を減らすこと自体を目標にしない。

全体像の理解に必要な説明はREADMEに残し、正式な判断条件だけを正本へ委譲する。

### Git状態とアーカイブの状態を混同しない

アップロードされたZIPは内容確認には使えるが、そのまま現在のGit差分を表すとは限らない。

作業ツリーの状態を論じる場合は、Gitの実行結果を別途確認する。
