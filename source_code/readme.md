# run_simulation.py

## 概要
DAGファイルの生成，シミュレータの実行・評価までをまとめて行う

## 実行方法

### 準備
DAGファイル生成に用いるconfigファイルを以下の通りに配置する
- configファイルの末尾の数字は最大利用率を表す

```
evaluator
 L source_code
   - run_simulation.py
   L libs
     - batch_simulation.py
     - divide_files.py
     - result_check.py
 L config
   - basic_chain_based-10.yaml
   - basic_chain_based-09.yaml
   - basic_chain_based-08.yaml
   - basic_chain_based-07.yaml
   - basic_chain_based-06.yaml
```

### 実行
DAGファイル生成アルゴリズムの実行フォルダパス(-d)，シミュレータ実行場所のパス(-s)，シミュレータ実行時のコア数(-c)を指定する

```
python3 run_simulation.py -d {DAGファイル生成アルゴリズムの実行フォルダパス} -s {シミュレータ実行場所のパス} -c {シミュレータ実行時のコア数}
```

### 出力
configファイルごと及び全体に対し，以下の内容を表示
- Max utilization: configファイルで設定した最大利用率
- Number of .yaml files: 対象ログyamlファイルの数
- Number of schedulable: Schedulableの数
- Number of unschedulable: Unschedulableの数
- Acceptance of schedulable: Schedulableの割合

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

## 備考
一度実行した後でもコア数を変えて同様に実行することで，異なるコア数の評価も取ることができる
 - その際，DAGファイルの生成をスキップする

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

- divide_files.pyを用い，以下のようにdagファイルを配置する

  `python3 divide_files.py -s ../DAGs/Max_utilization-O.X/DAGs/ -n 1000 -o {アルゴリズム名}/UsedDag/Max_utilization-O.X`

- configファイルを移動

  `cp ../config/basic_chain_based-OX.yaml 2014_ECRTS_federated_original/UsedDag/Max_utilization-O.X`

最終的に以下のようにファイルが配置される

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

### 実行
シミュレータ実行場所のパス(-e)・実行対象DAGディレクトリ群のパス(-d)・コア数(-c)を指定する

- 実行対象DAGディレクトリ群のパスは，異なるMax utilizationごとのフォルダを含むフォルダ
  - 上記の例ならUsedDag

```
python3 batch_simulation.py -e {シミュレータ実行場所のパス} -d {アルゴリズム名}/UsedDag/ -c {コア数}
```

### 出力
シミュレータの実行結果は，コア数ごとに`source_code/{アルゴリズム名}/SchedResult`のディレクトリに作成される

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
```


## 備考


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
- Number of schedulable: Schedulableの数
- Number of unschedulable: Unschedulableの数
- Acceptance of schedulable: Schedulableの割合

グラフを作成し，表示/保存する
- 縦軸：受理率 [resultがtrueの数/全体の数]
- 横軸：利用率 [0.6 ~ 1.0]
- 保存場所は `source_code/{アルゴリズム名}/OutputsResult`
- ファイル名は `plot_accept_{アルゴリズム名}_{コア数}-cores.png`

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