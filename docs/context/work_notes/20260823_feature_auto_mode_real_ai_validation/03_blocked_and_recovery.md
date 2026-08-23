# BLOCKEDと復旧

## 1. pytest実行権限で停止

最初のCP3 Workerは実装とテストコードを作成したが、
Claude Codeの非対話実行環境では
pytestを実行するためのBash権限が不足していた。

Workerはテストを実行できず、
Reviewerもpytest実行時に人間の許可を要求した。

非対話実行のため許可操作を行えず、
ReviewerはGate記録を完成できなかった。

runnerはこれを、

`BLOCKED(state_error)`

として記録して停止した。

### 対応

Claude Codeの実行設定へ、
pytestだけを許可する設定を追加した。

すべてのBashを無条件に許可するのではなく、
必要なテスト実行だけを許可する方針とした。

## 2. --retry-blocked

権限問題を解消した後、

`--retry-blocked`

でCP3から再開した。

このとき、

- 過去のBLOCKED記録は変更しない
- G1/G2からやり直さない
- 停止したCP3を再試行する

という動作を確認できた。

途中復旧用として実装していた仕組みを、
実AI試験で実際に使うことになった。

## 3. AIが範囲外ファイルを変更

再試行後、
Workerはテスト実行環境を成立させるために
担当範囲外のファイルへ変更を加えた。

検出された主なファイルは、

- `conftest.py`
- `src/cli_text_masker/__init__.py`

だった。

実装とテスト自体は6件PASSしていた。

しかしstage × roleの変更範囲では
CP3 Workerが変更できる場所が限定されているため、
runnerはこれらを範囲外変更として検出した。

Reviewerは内容が妥当そうかどうかで解除せず、

`BLOCKED(guard_violation)`

とした。

## 4. conftest.pyは不要だった

人間側で `conftest.py` を削除し、
対象テストを再実行した。

結果は、

`6 passed`

だった。

つまり、
AIがテスト環境を成立させるために追加したファイルは、
実際には必要ではなかった。

AIが問題を見つけて自力で解決しようとしたこと自体は確認できたが、
その解決策が最小とは限らなかった。

## 5. retry時の範囲外変更

その後、
`--retry-blocked` をもう一度実行した。

今回はWorkerが
`src/cli_text_masker/__init__.py`
を削除した。

実行後にはファイルが存在しなかったため、
一見すると範囲外変更がないようにも見えた。

しかしrunnerは実行前後の差分で変更を検出するため、
許可範囲外ファイルを削除したこと自体を
guard violationとして検出した。

Reviewerも現在ファイルが存在しないことを確認したうえで、
runnerから渡されたguard violationを勝手に無効化せず、

`BLOCKED(guard_violation)`

とした。

この挙動は意図した変更範囲ガードと一致していた。

## 6. --retry-blockedではなく--review-currentへ

この時点では、

- 実装済み
- テスト6件PASS
- 不要ファイルは削除済み
- 現在の成果物をWorkerに変更させる必要はない

という状態だった。

それにもかかわらず
`--retry-blocked`
を使うとWorkerがもう一度起動し、
新しい変更を発生させる可能性がある。

そこで、

`--review-current CP3`

を使用することにした。

まずdry-runし、

- Workerは起動しない
- 現在の成果物をそのままReviewerへ渡す
- Reviewerだけが起動する
- CP3はHuman Gate

であることを確認した。

## 7. CP3 PASS

`--review-current CP3`

を本実行した。

結果:

- guard violation 0
- FINDING 0
- 要求カバレッジ 6/6
- テスト観点カバレッジ 6/6
- pytest 6 passed
- CP3 PASS / GO

となった。

その後、
人間がCP3の受け入れ判断を行った。

通常のrunnerを再度実行すると、

`完了しました。`

と表示された。

これにより、
最終Human Gateを含めて
feature auto modeの実AI通し試験が完走した。

## --retry-blockedと--review-currentの使い分け

今回の実運転で、
両者は用途が異なることが明確になった。

### --retry-blocked

AI作業そのものをやり直す必要がある場合に使う。

例:

- 実行環境の問題を解消した
- Workerの処理をもう一度走らせる必要がある

### --review-current

現在の成果物をそのまま保持し、
Reviewerだけに再判定してほしい場合に使う。

例:

- 人間が外部要因を解消した
- Workerの再実行は不要
- 現在の成果物のGate判定だけ取り直したい

今回の最終復旧では、
後者が適切だった。