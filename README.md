# XGBoostで日経平均の株価を新聞からもとめる

## はじめに
- Decision TreeのBoostingのRegressionは一度やっておこうと思った。
- 予想する問題に対して、素性の数が極めて大きい予想問題で、XGBoostの最適化手法を見ているとある程度、ロバストに動作するかもしれないという観測があり、今回のタスクは評価に適切だった
- 株を買って一山当てるのは、誰もが夢見ることであろう

## Boostingの基礎理論
非常に丁寧にかつよくまとまっているサイトがあるので、体系的に理解したい人は、リンクからたどると良い。
[zaburo-ch.github.io](https://zaburo-ch.github.io/post/xgboost/)

何をやっているかというと、弱い決定木を前の出力を次の出力に合算して、次の決定木に引き継がせているのだが、次の式で最小化すべき目的関数を構築している。

<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25950213/1ca9754c-3695-11e7-8d94-c8c4aca56642.png">
</p>

N個のデータがあった場合、各データについてFという関数を仮定して、最小化していく問題とみなせる（ここはよくある問題設定）

t番目のデータを次のような微分が成り立つはずである

<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25950236/2e7ac898-3695-11e7-8a66-9d3705210dad.png">
</p>

この微分をされている要素をyiとすると、次の値を最小化すれば良いことがわかる
<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25950261/47d3caf6-3695-11e7-80b9-e2f4d8572b36.png">
</p>

これをT回反復を終えるまで回すとすると、次の式になる
FT(x)=f0(x)+∑t=1Tαtft(x)
