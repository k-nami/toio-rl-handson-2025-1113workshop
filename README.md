
# toio-rl-handson-for-workshop1112

## 準備

- 必要なアプリケーションの確認とインストールは，[環境構築](supplementary/build_env_note.md)を参照してください．
- 仮想環境で必要なパッケージをダウンロードしてください．

### venvの場合
```bash
python -m venv venv

# 仮想環境に入る
# windowsの場合
venv\Scripts\activate

# mac/ubuntuの場合
source venv/bin/activate

pip install -r requirements.txt

# 仮想環境から出る
deactivate
```

### condaの場合
```bash
conda env create -f environment.yml

# doneと表示されたのち、下記コマンドで「toio_rl」があればOK
conda env list
# conda environments:
#
toio_rl               *  /home/staff/<User>/.conda/envs/toio_rl
base                     /usr/local/anaconda3
python311                /usr/local/anaconda3/envs/python311

# 仮想環境に入る（実行後，冒頭に(toio_rl) と表示されればOK）
conda activate toio_rl

# 仮想環境から出る
conda deactivate
```

## 実行方法

* 実行前に仮想環境環境を有効化してください

```bash
# windowsの場合
cd toio_RL\d1_workshop1113
# mac/ubuntuの場合
cd toio_RL/d1_workshop1113

python demo1_adapt.py
```


