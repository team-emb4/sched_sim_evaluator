# run_evaluator.py

## 概要
DAGファイルの生成，シミュレータの実行・評価までをまとめて行う

## 実行方法

### 準備
- DAGファイル生成に用いるconfigファイルを以下の通りに配置する
  - configファイルの末尾の数字は最大利用率を表す

```
evaluator
 L source_code
   - run_evaluator.py
   L libs
     - batch_simulation.py
     - divide_files.py
     - result_check.py
     - util.py
 L config
   - basic_chain_based-10.yaml
   - basic_chain_based-09.yaml
   - basic_chain_based-08.yaml
   - basic_chain_based-07.yaml
   - basic_chain_based-06.yaml
```

- 使用するアルゴリズムのプロパティを設定する
  - libsの中のutil.pyにある`algorithm_list`に書き込む
  - プロパティ項目
    - 入力DAGの形式："input"
      - "DAG"：入力がDAGファイル
      - "DAGSet"：入力がDAGフォルダ
    - 実行モードが何種類あるか："preemptive"
      - "false"：NonPreemptiveで実行
      - "true"：PreemptiveとNonPreemptiveで実行
    - 結果の形式："result"
      - "schedulability"：resultがSchedulableまたはUnschedulableで表される場合
      - "boolean"：resultがtrueまたはfalseで表される場合

### 実行
DAGファイル生成アルゴリズムの実行フォルダパス(-d)，シミュレータ実行場所のパス(-s)，シミュレータ実行時のコア数(-c)を指定する
- すでにDAGファイルが生成済みの場合は，-dを指定しなくてもよい

```
python3 run_evaluator.py [-d {DAGファイル生成アルゴリズムの実行フォルダパス}] -s {シミュレータ実行場所のパス} -c {シミュレータ実行時のコア数}
```

### 出力
configファイルごと及び全体に対し，以下の内容を表示
- Max utilization: configファイルで設定した最大利用率
- Number of .yaml files: 対象ログyamlファイルの数
- Number of schedulable(true): Schedulable(true)の数
- Number of unschedulable(false): Unschedulable(false)の数
- Acceptance of schedulable(true): Schedulable(true)の割合

グラフを作成し，表示/保存する
- 縦軸：受理率 [resultがtrueの数/全体の数]
- 横軸：利用率 [0.6 ~ 1.0]
- 保存場所は `source_code/{アルゴリズム名}/OutputsResult`
- ファイル名は `plot_accept_{アルゴリズム名}_{コア数}-cores.png`

```
evaluator
 L source_code
   L libs
   L {アルゴリズム名}
     L UsedDag (フォルダ分割後のDAGファイル)
       L Max_utilization-1.0
         - config.yaml
         L DAGs_0
           - dag_OOOO.yaml
         L DAGs_1
       L Max_utilization-0.9
       L Max_utilization-0.8
       L Max_utilization-0.7
       L Max_utilization-0.6
     L SchedResult (シミュレータ実行結果)
       L {使ったコア数}-cores
         L Max_utilization-1.0
           -2023-07... (スケジュール結果.yaml)
           -2023-07... 
         L Max_utilization-0.9
         L Max_utilization-0.8
         L Max_utilization-0.7
         L Max_utilization-0.6
     L Log (シミュレータ実行ログ)
       -2023-07... (ログ.txt)
       -2023-07... 
     L OutputsResult (評価結果)
       - plot_accept_{アルゴリズム名}_{コア数}-cores.png
 L config (configファイル)
   - basic_chain_based-10.yaml
   - basic_chain_based-09.yaml
   - basic_chain_based-08.yaml
   - basic_chain_based-07.yaml
   - basic_chain_based-06.yaml
 L DAGs (生成したDAGファイル)
   L Max_utilization-1.0
     L DAGs
      - DAGs_OOOO.yaml
   L Max_utilization-0.9
   L Max_utilization-0.8
   L Max_utilization-0.7
   L Max_utilization-0.6
```
いくつかのアルゴリズムは，構造が若干異なる
- ["preemptive": "true"]であるアルゴリズム
  - `SchedResult`の中に`Preemptive`と`NonPreemptive`フォルダがある
```
evaluator
 L source_code
   L {アルゴリズム名}
     L UsedDag (フォルダ分割後のDAGファイル)
     L SchedResult (シミュレータ実行結果)
       L Preemptive
         L {使ったコア数}-cores
           L Max_utilization-1.0
             -2023-07... (スケジュール結果.yaml)
             -2023-07... 
           L Max_utilization-0.9
           L Max_utilization-0.8
           L Max_utilization-0.7
           L Max_utilization-0.6
       L NonPreemptive
         L {使ったコア数}-cores
     L Log (シミュレータ実行ログ)
     L OutputsResult (評価結果)
       - plot_accept_{アルゴリズム名}_Preemptive_{コア数}-cores.png
       - plot_accept_{アルゴリズム名}_NonPreemptive_{コア数}-cores.png       
```
- ["input": "DAG"]であるアルゴリズム
  - `UsedDag`の各利用率のフォルダの中に，DAGファイルがそのまま置いてある
```
evaluator
 L source_code
   L {アルゴリズム名}
     L UsedDag (フォルダ分割後のDAGファイル)
       L Max_utilization-1.0
         - config.yaml
         - dag_OOOO.yaml
       L Max_utilization-0.9
       L Max_utilization-0.8
       L Max_utilization-0.7
       L Max_utilization-0.6     
     L SchedResult (シミュレータ実行結果)
     L Log (シミュレータ実行ログ)
     L OutputsResult (評価結果)
```


## 備考
- 2023/09/15時点では，["input": "DAG"]かつ["preemptive": "true"]であるアルゴリズムのシミュレータの動作確認は行っていません

- すでにDAGファイルやUseDagファイルが生成済みの場合は，生成をスキップする

- すでに指定したコア数のディレクトリがSchedResultに存在している場合，実行を続けるかどうかを確認する
  - 続ける場合
    - 現在存在しているディレクトリを削除し，始めから実行する
  - 続けない場合
    - プログラムが終了する

- - -
- - -
# **libs**

# batch_simulation.py

## 概要
複数のDAGSetの入力に対し，シミュレータを連続実行する

詳細：異なるMax utilizationごとのフォルダにある，dagファイルの全てのフォルダに対し，シミュレータを連続実行する

## 実行方法

### 準備
以下の各コマンドをすべてのconfigファイルに対して実行する

- dagファイルを生成

  `python3 run_generator.py -c ./config/basic_chain_based-OX.yaml -d evaluator/DAGs/Max_utilization-O.X`

- 作業場所に移動

  `cd evaluator/source_code`

- ["input": "DAGSet"]であるアルゴリズムはdivide_files.pyを用い，以下のようにdagファイルを配置する
  - ["input": "DAG"]であるアルゴリズムはdivide_files.pyを用いず，DAGファイルをそのまま配置する

  `python3 divide_files.py -s ../DAGs/Max_utilization-O.X/DAGs/ -n 1000 -o {アルゴリズム名}/UsedDag/Max_utilization-O.X`

- configファイルを移動

  `cp ../config/basic_chain_based-OX.yaml 2014_ECRTS_federated_original/UsedDag/Max_utilization-O.X`

最終的に以下のようにファイルが配置される

- ["input": "DAGSet"]であるアルゴリズム
```
evaluator
 L source_code
   L {アルゴリズム名}
     L UsedDag
       L Max_utilization-1.0
         - config.yaml
         L DAGs_0
           - dag_1.yaml
           - dag_2.yaml
         L DAGs_1
       L Max_utilization-0.9
       L Max_utilization-0.8
       L Max_utilization-0.7
       L Max_utilization-0.6
```
- ["input": "DAG"]であるアルゴリズム
```
evaluator
 L source_code
   L {アルゴリズム名}
     L UsedDag
       L Max_utilization-1.0
         - config.yaml
         - dag_1.yaml
         - dag_2.yaml
       L Max_utilization-0.9
       L Max_utilization-0.8
       L Max_utilization-0.7
       L Max_utilization-0.6
```

### 実行
シミュレータ実行場所のパス(-e)・実行対象DAGディレクトリ群のパス(-d)・コア数(-c)を指定する

- 実行対象DAGディレクトリ群のパスは，異なるMax utilizationごとのフォルダを含むフォルダ
  - 上記の例ならUsedDag

```
python3 batch_simulation.py -e {シミュレータ実行場所のパス} -d {アルゴリズム名}/UsedDag/ -c {コア数}
```

### 出力
シミュレータの実行結果は，コア数ごとに`source_code/{アルゴリズム名}/SchedResult`のディレクトリに作成される
- ["preemptive": "true"]であるアルゴリズムは，`SchedResult`の中に`Preemptive`と`NonPreemptive`のフォルダがそれぞれ作成される

```
evaluator
 L source_code
   L {アルゴリズム名}
     L UsedDag
       L Max_utilization-1.0
       L Max_utilization-0.9
       L Max_utilization-0.8
       L Max_utilization-0.7
       L Max_utilization-0.6
     L SchedResult
       L {使ったコア数}-cores
          L Max_utilization-1.0
            -2023-07... (スケジュール結果.yaml)
            -2023-07... 
          L Max_utilization-0.9
          L Max_utilization-0.8
          L Max_utilization-0.7
          L Max_utilization-0.6
     L Log (シミュレータ実行ログ)
       -2023-07... (ログ.txt)
       -2023-07... 
```
- ["preemptive": "true"]であるアルゴリズム
```
evaluator
 L source_code
   L {アルゴリズム名}
     L UsedDag
       L Max_utilization-1.0
       L Max_utilization-0.9
       L Max_utilization-0.8
       L Max_utilization-0.7
       L Max_utilization-0.6
     L SchedResult (シミュレータ実行結果)
       L Preemptive
         L {使ったコア数}-cores
           L Max_utilization-1.0
             -2023-07... (スケジュール結果.yaml)
             -2023-07... 
           L Max_utilization-0.9
           L Max_utilization-0.8
           L Max_utilization-0.7
           L Max_utilization-0.6
       L NonPreemptive
         L {使ったコア数}-cores
     L Log (シミュレータ実行ログ)
       -2023-07... (ログ.txt)
       -2023-07... 
```

## 備考
- 2023/09/15時点では，["input": "DAG"]かつ["preemptive": "true"]であるアルゴリズムのシミュレータの動作確認は行っていません

- すでに指定したコア数のディレクトリがSchedResultに存在している場合，実行を続けるかどうかを確認する
  - 続ける場合
    - 現在存在しているディレクトリを削除し，始めから実行する
  - 続けない場合
    - プログラムが終了する


- - -

# result_check.py

## 概要
複数のシミュレータログファイルから，受理率と利用率のグラフを作成する

## 実行方法

### 準備
batch_simulation.pyを実行し、SchedResultに利用率ごとの複数のログファイルを生成(上記参照)

### 実行
SchedResultにあるコア数ごとのフォルダのパスを指定する

`python3 result_check.py {アルゴリズム名}/SchedResult/{コア数}-cores`

### 出力
ディレクトリごと及び全体に対し，以下の内容を表示
- Max utilization: コンフィグファイルで設定した利用率
- Number of .yaml files: 対象yamlファイルの数
- Number of schedulable(true): Schedulable(true)の数
- Number of unschedulable(false): Unschedulable(false)の数
- Acceptance of schedulable(true): Schedulable(true)の割合

グラフを作成し，表示/保存する
- 縦軸：受理率 [resultがtrueの数/全体の数]
- 横軸：利用率 [0.6 ~ 1.0]
- 保存場所は `source_code/{アルゴリズム名}/OutputsResult`
- ファイル名は `plot_accept_{アルゴリズム名}_{コア数}-cores.png`
  - ["preemptive": "true"]であるアルゴリズムは，`Preemptive`と`NonPreemptive`の2つのグラフが生成される

```
evaluator
 L source_code
   L {アルゴリズム名}
     L UsedDag
       L Max_utilization-1.0
         - config.yaml
         L DAGs_0
           - dag_1.yaml
           - dag_2.yaml
         L DAGs_1
       L Max_utilization-0.9
       L Max_utilization-0.8
       L Max_utilization-0.7
       L Max_utilization-0.6
     L SchedResult
       L {使ったコア数}-cores
          L Max_utilization-1.0
            -2023-07... (スケジュール結果.yaml)
            -2023-07... 
          L Max_utilization-0.9
          L Max_utilization-0.8
          L Max_utilization-0.7
          L Max_utilization-0.6
     L Log (シミュレータ実行ログ)
       -2023-07... (ログ.txt)
       -2023-07... 
     L OutputsResult
       - plot_accept_{アルゴリズム名}_{コア数}-cores.png
```

## 備考


- - -

# divide_files.py

## 概要
- 任意のファイル群を任意のフォルダ数に均等に分ける
  - 例：100ファイルあった場合：10フォルダ10ファイルや5フォルダ20ファイルに分ける

## 実行方法

### 実行
ファイル群のフォルダパス(-s)・フォルダ数(-n)・フォルダの作成場所のパス(-o)を指定する
- フォルダの作成場所を指定しない場合，分割したいファイル群があるフォルダに作成される

`python3 divide_files.py -s ${ファイル群のフォルダパス} -n ${フォルダ数} [-o ${フォルダの作成場所のパス}]`

### 出力
入力で指定したフォルダに，分割されたファイル群のフォルダが作成される

```
{指定したフォルダの作成場所}
 L {元フォルダ名}_0
   - 対象ファイル_0
   - 対象ファイル_1
   - ...
 L {元フォルダ名}_1
 L {元フォルダ名}_2
 L ...
 L {元フォルダ名}_{フォルダ数-1}

```

## 備考
- 指定されたフォルダに対象ファイルが存在しない場合，以下が出力される
  - "dag_"から始まるファイルのみを対象としている

  `No files starting with 'dag_' found in ${ファイル群のフォルダパス}. Nothing to divide.`