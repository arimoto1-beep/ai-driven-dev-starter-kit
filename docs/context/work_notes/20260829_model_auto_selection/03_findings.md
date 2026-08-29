# 実装中に見つかった想定外

設計時（調査・設計検討フェーズ）には分からなかったことを残す。

## 1. Worker のモデルクラスが Gate記録に残っていなかった（既存不具合・確認済みの事実）

これは設計検討フェーズの調査で発見し、今回の修正対象として人間が承認した。

### 事実

`70_feature_loop.md` には次の記述があった。

> 実際に使ったクラスは Gate記録へ必ず記録します。

しかし実際には成立していなかった。runner は `build_reviewer_instruction()` へ
**Reviewer のクラスしか渡していなかった**ため、Worker のクラスは Reviewer に届いていなかった。

結果、実在するすべての Gate記録が次の状態だった。

```yaml
model_design:            # 空
model_build:             # 空
model_review: standard   # Reviewer 自身の分だけ
```

runner が作る BLOCKED記録も、3キーを空で固定していた。

### 対応

新しい4キーでは、runner が Worker のクラスも Reviewer へ渡す。
`test_worker_model_class_is_empty_without_worker` で、
「Worker を起動しない実行では空」という正しい空も区別できるようにした。

## 2. 実リポジトリの `tools/feature_loop.local` に `role_*` が残っている（確認済みの事実）

### 事実

このリポジトリのローカル設定に `role_*` 3行がある。

```text
role_design    = standard
role_build     = cheap
role_review    = standard
```

判定は「マージ後の設定に `role_` で始まるキーがあるか」であるため、
**標準の設定ブロックから `role_*` を削除しても、この作業環境は従来方式で動き続ける。**

### なぜ想定外だったか

設計時は「新規利用者は自動選択、既存利用者は従来方式」という分岐だけを見ていた。
**このリポジトリ自身が既存利用者側に該当する**ことを、実際に動かすまで具体的に意識していなかった。

`.gitignore` 対象のため、AIが削除するとローカル環境の設定を勝手に変えることになる。
人間の指示により削除していない。手順は `05_real_ai_validation_prep.md` に残した。

### 副作用として見つかったテストの問題（1件目・実装中に発見）

`read_config()` は `feature_loop.local` をマージするため、
「標準の設定ブロックが自動選択であること」を `read_config()` で検証すると
**ローカル設定の影響でテストが落ちる**（実際に落ちた）。

ルール文書のフェンスブロックだけを直接読むよう修正した。
`test_every_stage_prompt_has_a_base_level` は逆に、実際に動く設定を見るべきなので
`read_config()` のままにしてある。

### 同種の問題をもう1件見落としていた（2件目・実AI検証後に人間が検出）

**2026-08-29、人間が実AI検証後に全テストを実行して発覚した。**

`test_read_config_from_actual_rule_document` が、実リポジトリの設定に対して
`role_build == "cheap"` を検証していた。

```python
config = fr.read_config(REPO_ROOT)
assert config["role_build"] == "cheap"
```

人間が `feature_loop.local` から `role_*` を削除した（意図した操作）ことで、
`KeyError: 'role_build'` となった。

#### なぜ実装時のテストで検出できなかったか

**当時は `feature_loop.local` に `role_*` が残っていたため、`read_config()` の
マージ結果にたまたま `role_build` が存在し、テストが通ってしまっていた。**

つまり、このテストは実装完了時点で**すでに壊れていたが、ローカル設定に隠されていた。**
1件目と同じ原因であり、AIは1件目を修正した際に同種の箇所を横断確認していなかった。

#### 報告との食い違い

前回のAI報告には「ルール文書のフェンスブロックだけを直接読む形に修正した」とあるが、
**それは `test_standard_config_has_no_role_fixed_setting`（新規追加したテスト）についての記述**であり、
`test_read_config_from_actual_rule_document`（既存テスト）は修正していなかった。
報告が、対応した範囲より広く読める書き方になっていた。

#### 対応

このテストが確認すべきなのは「実際のルール文書から設定を読めること」である。
`role_build` は単なるサンプルキーだったため、新標準の項目へ置き換えた。

```python
assert config["base_level_implement_feature"] == "1"
assert config["base_level_review_stage"] == "2"
```

`read_config()` を使う形は維持した。この関数自体（フェンスの解析、文書パスの解決）を
実データで検証する価値があるためである。

検証対象の値はすべてルール文書側で定める項目に限定し、
`role_*` の有無で結果が変わらないことを確認した。docstring にもその方針を明記した。

## 3. `pytest` の既定の一時ディレクトリが使えなかった（環境要因・このリポジトリの問題ではない）

### 事実

`python -m pytest` をそのまま実行すると、144 件が次のエラーで失敗した。

```text
PermissionError: [WinError 5] アクセスが拒否されました:
  'C:\Users\...\AppData\Local\Temp\pytest-of-...'
```

`tmp_path` fixture の生成時点で失敗しており、テストコードの中身には到達していない。

### 確認したこと

`--basetemp` を書き込み可能なディレクトリへ向けると 264 件すべて成功する。
**今回の変更が原因ではない。**

### 未確認

この実行環境固有の制約か、恒常的なものかは確認していない。
人間が通常の端末で実行した場合に同じ現象が起きるかは未検証である。

## 4. `stage_*_worker_role` / `reviewer_role` が宙に浮いた（設計上の帰結）

### 事実

基礎レベルをプロンプト単位にしたことで、`stage_cp1_worker_role` などの role 割り当ては
**従来方式（`role_fixed`）のときにしか使われなくなった。**

削除はしていない。従来方式が動くために必要であり、
人間の指示（「role 概念そのものの削除」は第一段階では実装しない）にも従っている。

設定ブロックへ「従来のモデル固定設定でのみ使用する」と注記した。

### 派生した設計判断

`uses_role_fixed()` を「`role_` で始まるキーの有無」で判定するため、
`stage_g1_worker_role` や `reviewer_role` が誤検出されないことを確認する必要があった。
どちらも `role_` で始まらないため問題ないが、**将来キー名を変えると静かに壊れる**ので
テストで固定した（`test_uses_role_fixed_ignores_stage_role_assignment`）。

## 5. `normal` が従来既定と一致することを、実データで確認できた（設計どおり）

想定外ではないが、記録しておく価値がある事実。

実リポジトリの設定から `role_*` だけを除いて選択を実行したところ、
既存 feature（CP1 記録に `feature_difficulty` なし → `normal`）では
**従来とまったく同じクラスが選ばれた。**

移行時に既存 feature の挙動が変わらないことを、実データで確認できた。
