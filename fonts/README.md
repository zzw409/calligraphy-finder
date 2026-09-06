开源中文字体（来自 Google Fonts，OFL 协议）

首次启动前请自行下载到本目录：

1. 马善政  MaShanZheng-Regular.ttf  https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf
2. 龙藏   LongCang-Regular.ttf     https://github.com/google/fonts/raw/main/ofl/longcang/LongCang-Regular.ttf
3. 刘建毛草 LiuJianMaoCao-Regular.ttf https://github.com/google/fonts/raw/main/ofl/liujianmaocao/LiuJianMaoCao-Regular.ttf
4. 站酷快乐体 ZCOOLKuaiLe-Regular.ttf https://github.com/google/fonts/raw/main/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf

可在 PowerShell 里一行下载：

```powershell
$root = ".\fonts"
New-Item -ItemType Directory -Force -Path $root | Out-Null
$src = @{
  "MaShanZheng.ttf"  = "https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf"
  "LongCang.ttf"      = "https://github.com/google/fonts/raw/main/ofl/longcang/LongCang-Regular.ttf"
  "LiuJianMaoCao.ttf" = "https://github.com/google/fonts/raw/main/ofl/liujianmaocao/LiuJianMaoCao-Regular.ttf"
  "ZCOOLKuaiLe.ttf"   = "https://github.com/google/fonts/raw/main/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf"
}
$src.Keys | ForEach-Object {
  Invoke-WebRequest -Uri $src[$_] -OutFile (Join-Path $root $_) -UseBasicParsing
}
```

或在 Git Bash / WSL：

```bash
cd fonts
curl -L -o MaShanZheng.ttf   https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf
curl -L -o LongCang.ttf      https://github.com/google/fonts/raw/main/ofl/longcang/LongCang-Regular.ttf
curl -L -o LiuJianMaoCao.ttf https://github.com/google/fonts/raw/main/ofl/liujianmaocao/LiuJianMaoCao-Regular.ttf
curl -L -o ZCOOLKuaiLe.ttf   https://github.com/google/fonts/raw/main/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf
```
