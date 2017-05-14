# XGBoostで日経平均の株価を新聞からもとめる

## はじめに
- Decision TreeのBoostingのRegressionは一度やっておこうと思った。
- 予想する問題に対して、素性の数が極めて大きい予想問題で、XGBoostの最適化手法を見ているとある程度、ロバストに動作するかもしれないという観測があり、今回のタスクは評価に適切だった
- 株を買って一山当てるのは、誰もが一度は夢見ることであろう

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
<p align="center">
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

# Step By Step解説

## step.1 
新聞の記事を分かち書きにする
```sh
$ python3 deal.py --step1
```

## step.2
単語をindex化する
```sh
$ python3 deal.py --step2
```

## step.3
日経平均のデータから目的となる数字を計算する
```sh
$ python3 deal.py --step3
```

## step.4
XGBoost(バイナリ)で読める形に変換します
```sh
$ python3 deal.py --step4
```
なお、次の日のKPIを予想するのにこのようなオプションも使えます
```sh
$ python3 deal.py --step4alt
```
## step.5
教師データとテストデータに分割します
```sh
$ python3 deal.py --step5
```

## step.6
学習します
```sh
$ python3 deal.py --step6
```

## step.7
モデルをダンプします
```sh
$ python3 deal.py --step7
```

## step.8
f値を出力します
f値は何回判別の基準となる素性として選択されたかで、その事象を説明する大きさを示しはしませんが、その組成で決定木を作ると、うまく切れるということを示しています。
```sh
$ python3 deal.py --step8 | less
```

# 結果
4年分ぐらいのデータに関して、検証を行いました。
8割を学習用データ、2割をテストデータとして、ランダムに分割したものです

ROUND300, max_depth=3000000, eta = 0.025, regresion:linearでRSMEと呼ばれる誤差は980程度まで下げることができました。  
悪くないように見えますが、どのような素性が反応しているのでしょうか、見てみましょう。

```sh
。 517.0
私 307.0
2015年 286.0
月 269.0
する 245.0
なっ 229.0
2012年 175.0
05 165.0
・ 164.0
さ 155.0
2017年 151.0
よう 145.0
た 144.0
2011年 141.0
（ 131.0
2013年 128.0
優勝 120.0
粘り 118.0
いう 113.0
02 112.0
日 109.0
せ 104.0
２ 104.0
で 103.0
04 101.0
い 96.0
2016年 92.0
03 92.0
モデル 89.0
」 88.0
-1 86.0
さん 83.0
06 80.0
12月 80.0
```
しょうもない素性に反応しているのがよくわかりますね  
確かに、年によるトレンドはあるので、何か商品やサービスが流行ると言うより、年代によるトレンドの変化に見えます。  
ちなみに、名詞だけで行ったらどうなるのでしょうか。  

### 名詞だけでXGBoostで回帰する
精度だけ見るとずっと落ちてしまうことがわかりました  
rmseも1500ぐらいまでしか下がりません  
反応する素性はこのうになっております  

```sh
告示 57.0
おり 57.0
市 56.0
よ 55.0
注文 55.0
学校 54.0
面接 54.0
万 54.0
面 54.0
思い 53.0
元 53.0
黄身 52.0
的 52.0
指定席 52.0
合わせ 51.0
なり 50.0
合成洗剤 50.0
練習 49.0
ＢＢ 49.0
編集部 49.0
水泳部 48.0
歳 48.0
自信 48.0
湯たんぽ 47.0
氏 47.0
同 47.0
多く 46.0
たい 46.0
今後 46.0
店 44.0
機関士 44.0
今 43.0
同胞 43.0
グリー 42.0
ハゼ 42.0
強 42.0
```
数字でないので、企業名がおおくでるかと思いましたが、そのようなことはないようです。 

## 自己回帰のように予想する
つまり、前日までの株価が既知だとします。    
前日までの情報がわかっていれば、何らか簡単に次の日の株価を新聞の情報と加えて予想することができそうです  
F(n)はn日の予想株価  
Rはn日の実測値  
Sはn日の新聞紙面  
```sh
F(n) = R(n-1) + S(n-1)
```
つまり、これを予想するタスクとします。  

RMSEは200程度まで下がることを確認しました。 
つまり、平均200円前後しか、ずれずに予想できると言うことです。  
一番性能が良いモデルです。  
```sh
__SELF_PREV__ 18957.0
dBanner 515.0
中 340.0
以上 119.0
の 112.0
前 104.0
近道 78.0
ば 73.0
や 72.0
まし 62.0
米 60.0
い 50.0
化 50.0
よう 49.0
ページ 47.0
面倒 46.0
領収書 46.0
異例 45.0
者 44.0
感じ 43.0
ます 39.0
私 37.0
さ 37.0
一方 37.0
さん 36.0
宙 35.0
へ 35.0
なり 34.0
会長 34.0
思い 34.0
企画 34.0
運転 33.0
...
```
うーん、ライターの書く記事のボキャブラリーのズレを見ているような気がします。(つまり、文章の内容でなくて、書き手は年代で変わるので、それを特徴としている)  

ちなみに、前日のデータだけでやってみましょう。  

## 前日の株価から次の日の株価を予想する
新聞の素性を削り取り、翌日の株価を当てに行くと、簡単にフィットすることがわかりました。  
しかも、精度も悪くないです... 
RMSE200程度（日に200円程度しかずれない）  

え、新聞の情報なくてもいけますね...

## 結論

新聞のコンテンツから、予想することもできるが、自己回帰予想が良さそうに見えるけど、新聞を入れても変わらないので、新聞は特徴量として役不足感がある。  
xgboostのチューニングやアルゴリズムを工夫して、素性選択を頑張るより、大量の素性を入れていくことで精度を上げて行くほうが筋が良いように見えて、TVya
日経新聞、インターネット記事などをとにかく量を放り込んで予想するのがよいのかなぁって思ってます（かなり長い期間必要ですが）  

自動売買プログラムでは、買うタイミングと売るタイミングが分かればよいから、別の問題になるがそういうタスクでは有効かもしれない。  


## fscoreはレグレッションなどにおいて、大きいほど主要因を占めるものというわけでない
fscoreは、何回決定木の決定要素になったかをかを、定量的に確認するものであり、レグレッションのタスクにおいて数が大きいからその問題において主要な影響力を持つというわけではありません  
一回しか選択されなくても全体を説明してしまうこともあれば、何回も選択されているのに、重要な影響力を持つわけでなく、微細な調整に使われる素性もあります  
つまり、今回の株価予想において株価は上がったり下がったりするのですが、そういう変化を表す素性として企業名だったり、その時の経済の状況だったりは重要な素性になりうるはずですが、日付によく反応してしまうことからも、日経平均は大雑把に丸められすぎてて、一企業の影響力が現れにくいような状態になっていそうです  
p値とのこのfscore（決定木における特徴量重要度）に関して、調べたかたがいらっしゃったのでご紹介いたします。[1]
 
## 参考文献
[1] [ランダムフォレスト系ツールで特徴量の重要度を測る](http://qiita.com/TomokIshii/items/290adc16e2ca5032ca07)  
[2] [Gradient Boosted Tree (Xgboost) の取り扱い説明書](http://qiita.com/nykergoto/items/7922a8a3c1a7b622b935)
 　
 

