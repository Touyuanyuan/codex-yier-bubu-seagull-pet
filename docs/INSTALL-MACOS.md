# 牵手海鸥一二布布 · Mac 安装

先确认已安装 Codex 桌面端，设置中能看到「Mini 与虚拟宠物」或「Pets」。

1. 解压 Mac 安装包，打开解压后的普通文件夹。
2. 双击 **install.command**，等待「牵手海鸥一二布布安装完成」。
3. 回到 Codex：设置 → Mini 与虚拟宠物 / Pets → 刷新 ↻ → 选择「牵手海鸥一二布布」。

使用 macOS 自带 Bash 和工具，不需要管理员权限、Python、Node.js、Homebrew 或联网。

若双击打不开，打开「终端」，输入 `/bin/bash `（末尾留空格），把解压后的 `install.command` 拖入终端，再按回车。

默认写入 `~/.codex/pets/yier-bubu-handholding-seagull/`，内含 `pet.json` 和 `spritesheet.webp`。也可以手动把包内 `pet` 文件夹复制到 `~/.codex/pets/` 并重命名为 `yier-bubu-handholding-seagull`。

设置了 `CODEX_HOME` 时使用该目录；也可运行 `/bin/bash install.sh "/path/to/codex-home"` 指定。该目录应与桌面客户端实际使用的目录一致。

重复运行遇到不同版本时，会先在同级 `pet-backups` 文件夹保存旧文件，再更新本宠物。其他宠物和当前选择不变。卸载前先选其他宠物，再移走本宠物文件夹。
