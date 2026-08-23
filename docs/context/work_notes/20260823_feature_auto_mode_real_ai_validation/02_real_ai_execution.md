# 実AI通し試験

## 対象feature

今回の再試験には、

`cli_text_masker/ascii_digit_masker`

を使用した。

ASCII数字 `0`〜`9` だけを `*` に置換する
小さなfeatureである。

全角数字やUnicode数字、
空文字列なども仕様で明示し、
単純ながら境界条件を確認できる題材とした。

## Spec Review単独実行

最初に、

`--spec-review`

を実行した。

Reviewerは `20_spec.md` のみを対象としてレビューし、
FINDING 0件でCP1 PASSとなった。

この時点では、

- `21_design.md`
- `22_flow.md`

は存在しなかった。

つまり、
Spec Reviewを実行しただけでは
AI製造工程へ入らないことを実際に確認できた。

## CP1人間承認

Spec Review結果を確認した後、
CP1 Gate記録の人間確認欄で仕様を承認した。

今回の検証では、
必要な関係者は検証者本人のみとして扱った。

この承認後に通常のrunnerを実行した。

## G1

CP1承認後、
初めてG1 Workerが起動した。

G1では、

- `21_design.md`
- `22_flow.md`

が生成された。

ReviewerはREQ-001〜006を確認し、
要求カバレッジ6/6でPASSした。

この時点で、
承認前に設計を生成しないという新しい工程境界が
実AIでも成立していることを確認できた。

## G2

G1 PASS後、
runnerはそのままG2へ進んだ。

G2では、

- `23_test_plan.md`
- `24_review_checklist.md`

が生成された。

Reviewerはテスト設計を確認し、

- 要求カバレッジ 6/6
- テスト観点カバレッジ 6/6

でPASSした。

人間による追加判断は発生しなかった。

## CP3

G2 PASS後、
CP3 Workerが実装とテストコードを生成した。

実装では、
ASCII数字判定に

`'0' <= char <= '9'`

を使用した。

`str.isdigit()` や `str.isnumeric()` は
全角数字等も真になるため使用していない。

テストはTV-001〜TV-006に対応する6件が作られた。

ここまでは仕様・設計・テスト計画と整合していた。

## 正常系だけでは終わらなかった

実装そのものには大きな問題はなかったが、
この後、

- Claude CodeのBash実行権限
- AIによる範囲外ファイル変更

という、
単体テストだけでは見つからなかった問題が発生した。

今回の実AI試験では、
むしろこの停止と復旧が
feature auto modeの重要な検証材料になった。