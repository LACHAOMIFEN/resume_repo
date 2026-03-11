# BanG Dream Rhythm Game

## 运行
```bash
cd /Users/bkb/.openclaw/workspace/bangdream-rhythm
python -m http.server 8790
```
打开 http://127.0.0.1:8790

## 键位
- D F J K
- 也支持点击轨道

## 资源接口
在 `js/game.js` 里：
- `const url=''` 改成你有授权的歌曲文件地址，如 `./source/song.mp3`

当前已带：
- `source/img_game_6th.jpg` 背景图
- `source/167802__menegass__nord-drum-zip_1.wav` 可作为后续打击音效素材
