# 検証方法（既存履歴を壊さないために）

## 前提として守ったこと

既存の実AI検証履歴は immutable な記録として扱い、削除も書き換えもしない。

- `cli_text_masker/ascii_digit_masker`（Gate記録7件）
- `cli_uppercase_text/uppercase`（Gate記録3件）

修正フローの検証は、**完成済み feature を後から変更する**という性質上、
必ず成果物と Gate記録に手を入れることになる。そのため既存 feature を直接使えない。

## 採った方法：検証用サンドボックスへの複製

完成済みの `cli_text_masker/ascii_digit_masker` を、docs / src / tests ごと
`cli_mask_rework` という別アプリ名へ複製した。

```text
docs/cli_text_masker/           → docs/cli_mask_rework/
src/cli_text_masker/            → src/cli_mask_rework/
tests/cli_text_masker/          → tests/cli_mask_rework/
```

複製したのは 24 ファイル。大規模なコピーではない。

### なぜ別 app にしたか

同じ app の中に別 feature 名でコピーする案もあったが、その場合
実装ファイル（`src/<app>/features/<feature>.py`）が存在しない状態になり、
CP3 Worker に実装をゼロから書かせることになる。

**検証したいのは「完成済み feature を修正したとき」なので、
出発点は「実装もテストも揃って動いている状態」でなければならない。**

app ごと複製すれば、コード・テスト・ドキュメント・Gate記録がすべて整合した
完成状態から出発できる。

## 途中で起きた自分のミス（1）: sed による行末変換

最初、アプリ名の置換に `sed -i` を使った。

これにより CRLF が LF へ正規化され、**内容は同じなのに `20_spec.md` の
内容ハッシュが変わってしまった**。

その結果、複製直後の状態がこうなった。

```text
製造開始条件: 満たしていない
  承認時: 18e7b3fb600c
  現在  : 3d12c4c5b3d5
```

これは検証の準備段階のミスだが、**同時に最初の発見でもあった。**
このとき runner は「製造開始条件: 満たしていない」と表示しながら、
`次の動作: done` のままだった。

その後、Python でバイト単位の置換をやり直した。
`20_spec.md` はアプリ名を含まないためバイト同一となり、
CP1 記録 0001 の `spec_hash` と一致する「完成済み feature」として起動できた。

```text
仕様書: docs/cli_mask_rework/features/ascii_digit_masker/20_spec.md（18e7b3fb600c...）
製造開始条件: 満たしている
次の動作: done (stage=CP3)
pytest: 6 passed
```

## 途中で起きた自分のミス（2）: heredoc による制御文字の混入

検証2で `23_test_plan.md` へ TV-007 を追加する際、シェルの heredoc 経由で
Python を実行したところ、**エスケープしたつもりの `\n` と `\t` が
生の改行・タブとして埋め込まれ**、Markdown のテーブル行が4行に分断された。

このミスは、後述するとおり **G2 Reviewer が検出した**（`02_findings.md` を参照）。

その後、Edit ツールで直接書き換える方式に切り替えて修正した。

**教訓**: Markdown 成果物を編集するときに、シェルの heredoc を経由しない。

## 各検証の前に baseline へ戻す

検証1〜4は、それぞれ同じ「完成済み」状態から始める必要がある。
そのため、スクラッチパッドへ baseline のコピーを取り、各検証の前に復元した。

```text
scratchpad/baseline/{docs,src,tests}/cli_mask_rework/
```

各検証の証跡（生成された Gate記録、テストコード）は
`scratchpad/exp1/`、`scratchpad/exp2/` へ退避してから復元した。

## 実AIを使った範囲と、使わなかった範囲

**runner の状態遷移そのものは、実AIなしで測定できる。**
`--status` と `--dry-run` は AI を起動しない。

そのため次のように使い分けた。

| 確認したいこと | 方法 |
|---|---|
| runner が変更を検出できるか | 実AIなし（`--status` / 通常実行） |
| 下流の再実行が起きるか | 実AI |
| 新しいテスト観点がテストコードへ入るか | 実AI |
| Reviewer が `artifacts_hash` を転記するか | 実AI |
| 実装した修正の網羅的な確認 | 自動テスト（AI擬似） |

**実AIは、AIの判断が結果を左右する部分にだけ使った。**
状態遷移の確認まで実AIで回すと、時間もコストも判断のぶれも増える。

## 既存履歴が無傷であることの確認

検証の終了時点で、既存 feature の Gate記録は一切変更していない。

```text
docs/cli_text_masker/features/ascii_digit_masker/gates/  7件（無変更）
docs/cli_uppercase_text/features/uppercase/gates/        3件（無変更）
```

git status 上でも、これらのディレクトリに変更は出ていない。
