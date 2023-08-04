# all_execute.py

## 概要
異なるMax utilizationごとのフォルダにある、dagファイルのフォルダに対し、シミュレータをまとめて実行する

## 実行方法

### 準備
以下の各コマンドをすべてのコンフィグファイルに対して実行する

- dagファイルを生成(zipファイルでは作成済み)

  `python3 run_generator.py -c ./config/basic_chain_based-OX.yaml -d simulator/DAGs/Max_utilization-O.X`

- 作業場所に移動

  `cd simulator/sourcecode`

- devide_files.pyを用い、以下のようにdagファイルを配置する(zipファイルではアルゴリズム名のフォルダまで作成済み)

  `python3 devide_files.py -s ../DAGs/Max_utilization-O.X/DAGs/ -n 1000 -o {アルゴリズム名}/UsedDag/Max_utilization-O.X`

- configファイルを移動

  `cp ../config/basic_chain_based-OX.yaml 2014_ECRTS_federated_original/UsedDag/Max_utilization-O.X`

最終的に以下のようにファイルが配置される

```
simulator
 L sourcecode
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
シミュレータ実行場所のパス(-e)・実行対象ディレクトリのパス(-d)・コア数(-c)を指定する

- 実行対象ディレクトリのパスは、異なるMax utilizationごとのフォルダを含むフォルダ
  - 上記の例ならUsedDag

```
python3 all_execute.py -e {シミュレータ実行場所のパス} -d {アルゴリズム名}/UsedDag/ -c {コア数}
```

シミュレータの実行結果は、コア数ごとに`sourcecode/{アルゴリズム名}/SchedResult`のディレクトリに作成される

```
simulator
 L sourcecode
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
`devide_files.py`の入力をオプションに変更しました。
- 詳細は一番下


- - -

# result_check.py

## 概要
シミュレータの結果から、受理率と利用率のグラフを作成する

## 実行方法

### 準備
all_execute.pyを実行し、結果のファイルを作成(上記参照)

### 実行
outputsにあるコア数ごとのフォルダのパスを指定する

`python3 result_check.py {アルゴリズム名}/SchedResult/{コア数}-cores`

### 出力
ディレクトリごと及び全体に対し、以下の内容を表示
- Max utilization: コンフィグファイルで設定した利用率
- Number of .yaml files: 対象yamlファイルの数
- Number of schedulable: Schedulableの数
- Number of unschedulable: Unschedulableの数
- Acceptance of schedulable: Schedulableの割合

グラフを作成し、表示/保存する
- 縦軸：受理率 [resultがtrueの数/全体の数]
- 横軸：利用率 [0.6 ~ 1.0]
- 保存場所は `sourcecode/{アルゴリズム名}/OutputsResult`
- ファイル名は `plot_accept_{アルゴリズム名}_{コア数}-cores.png`

```
simulator
 L sourcecode
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

# devide_files.py

## 概要
- 任意のファイル群を任意のフォルダ数に均等に分ける
  - 例：100ファイルあった場合：10フォルダ10ファイルや5フォルダ20ファイルに分ける

## 実行方法
以下を実行すると、入力で指定したフォルダに分割されたファイル群のフォルダが作成される
- 入力はオプションで指定
- フォルダの作成場所を指定しない場合、分割したいファイル群があるフォルダに作成される

`python3 devide_files.py -s ${ファイル群のフォルダパス} -n ${フォルダ数} [-o ${フォルダの作成場所のパス}]`

## 備考
- 指定されたフォルダに対象ファイルが存在しない場合、以下が出力される
  - "dag_"から始まるファイルのみを対象としている

  `No files starting with 'dag_' found in ${ファイル群のフォルダパス}. Nothing to split.`