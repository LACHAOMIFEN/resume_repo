# BanG Dream Arcade Shooter

## 运行
在本目录启动静态服务器：

```bash
python -m http.server 8787
```

打开：`http://127.0.0.1:8787`

## 目录
- `index.html` 主页面
- `css/game.css` 样式
- `js/config.js` 资源接口（背景、BGM、语音、道具音效）
- `js/audio.js` 音频模块
- `js/game.js` 游戏逻辑
- `source/` 资源文件（你上传的图片/音频）

## 可改接口
编辑 `js/config.js`：
- `bgUrl` 背景图
- `bgmUrl` 背景音乐
- `voiceUrl` 技能语音
- `itemSfx` 每个道具独立音效
