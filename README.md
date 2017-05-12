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

<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25979901/33de6a80-3706-11e7-8c7c-c5c444430816.png">
</p>

## Grandient Tree Boosting
Gradient Boostingを効率的に扱う式として、このような式が提案された。  
<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25983596/c49f8eb8-3720-11e7-97b8-8c9db39d6113.png">
</p>
x_i, y~\_iを最小化するような木を構築した後、 w\_jをこの式を最小化するのだが、この式が解析的に解ける場合  
<p aling="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25983615/df04bcb0-3720-11e7-9781-f4c4f79b0c53.png">
</p>
これを最小化すればいい  

## Learning Rate
<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25983653/13a4f6ce-3721-11e7-87b0-1dd94be3a289.png">
</p>

このような式で更新するのだが、ηが学習率に相当して、0.01~0.005がよいということになている。  

## Newton Boosting
最小化に使うアルゴリズムはGradient DescentではなくてNewton法を用いる  
<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25981189/a1efc5a2-370e-11e7-8663-11629d9d59e7.png">
</p>
この式を直接最小化する  

二次近似するとこのようになる  
<p align="center">
 <img src="https://cloud.githubusercontent.com/assets/4949982/25981221/d80c3134-370e-11e7-8f12-8e7b72c9cdbc.png">
</p>

これで、f_T(x_i)を求めることが可能になる
<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25981262/185ee22c-370f-11e7-91e6-e2c45776325a.png">
</p>


## XGBoost

Tは回帰儀、wは葉の重み  
この式を近似して回帰着を構築する  

<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25982957/d3728e86-371b-11e7-80c4-e02413569dc4.png">
</p>

# 図解によるイメージ
- このようになっているとイメージすると良いかもしれない
<p align="center">
  <img src="https://cloud.githubusercontent.com/assets/4949982/25983556/7b481a96-3720-11e7-8189-f75dc35d0a78.png">
</p>
