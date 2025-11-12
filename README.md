#     Doro_Repacker_EX

```
用于NIKKE Outdated Mod的repack项目，在daso132版和KXDƎ版上增强了对mod处理的健壮性，支持对UABEA无法读取的mod进行处理
可于该仓库中直接下载使用

Credits：
	KXDƎ - Doro-Tools & NLBMM		[codeberg.org/kxdekxde/doro-tools]
	daso132 - Doro_Repacker_modified_final		[mega.nz/folder/a2p02Sgb#iAZcsTJWR9WbRRhu2a6B2g]
	Danieru - Nikke Mod Manager		[nikke-modding-wiki.vercel.app/]
	Na0h - Nikke Mod Manager+		[discord.com/channels/968096627002851379/1041202670620397589]
	a1teri - Nikke File Finder		[https://a1ter00.github.io/nikke-file-finder/]
	bingle - Nikke Asset Unpacker	[nikke-modding-wiki.vercel.app/downloads/NAU.rar]
	aelurum - AssetStudioMod		[github.com/aelurum/AssetStudio]
	nikke-modding-wiki				[nikke-modding-wiki.vercel.app]
	nikke-modding-discord			[discord.gg/nikke]
	...

感谢nikke社区和广大mod社区中各位大佬的付出

```
![](https://i2.hdslb.com/bfs/new_dyn/a87c01732811df31f40a9753effc669f19505257.jpg)
> 立个娜由塔，无为竞癫疯！ 	(artist: SOLar)
#  Doro_Repacker_EX 

## 工具介绍

*本repack程序在daso132的Doro_Repacker_modified_final上改进*

   **①支持对UABEA（UnityPy）无法处理的mod进行repack处理**；
	
   **②无论使用下划线还是连字符，都能成功匹配**（NLBMM采用"-"，Na0h-NMM采用"_"，现统一都可读取了）
	
放入mod后按顺序执行脚本便能以一条龙形式repack所有outdated mods。  
（个人删除了daso132提供的exe，因为逐条执行python文件已经很便捷了，通过exe执行反而失去了很多调试的空间）

## 使用说明
1. 安装pycharm等IDE（或用CMD的python），进入到Doro_Repacker_EX的目录。

2. （可选操作，使用conda创建nikke环境）

   ```
   conda create -n nikke python=3.9
   ...
   conda init
   ...
   conda activate nikke
   ```

3. 安装脚本必备的环境(建议在虚拟环境中操作，不影响你计算机的环境)：

   ```
   pip install -r requirements.txt
   ```

   同时**需要安装.NET 桌面运行时 .9.0**（AssetStudioModCLI需要，[下载链接](https://dotnet.microsoft.com/zh-cn/download/dotnet/9.0)）  

   好像也要安装.NET 桌面运行时 .8.0（好像NAU需要？还是UABEA需要，如果没报错就不用下载，[下载链接](https://dotnet.microsoft.com/zh-cn/download/dotnet/8.0)）

4. **按顺序执行Z0 → Z1 → Z2 → Z3 (→ Z4）**，看每个脚本输出的调试信息去评估处理情况。

5. Repack完毕！Repacked文件夹里已经有最终的mod了，可以用AssetStudioGUI和UABEA看看mod的内部数据，也可以用SpineViewer和Na0h-NMM去预览mod的实际效果

## 注意事项
#### ①命名问题

**Idle类mod命名格式：****{角色编号}** _ **{服装编号}** _ **{standing/cover/aim}** _ {作者} _ {其他}

例子：

- c511_01_standing_Na0h_辛德瑞拉
- c194_00_aim_Seireiko_T1-圣鲁
- c015_00_cover_117il3_泳装阿妮斯(去武器)

**SkillCut类mod命名格式：** **{角色编号}** _ **{服装编号}** _ **{lobby/burst}** _ {作者} _ {其他} || **{角色编号}** - **{服装编号}** - **{lobby/burst}** - {作者} - {其他}

例子：

- c330_01_lobby_Na0h_皇冠的新衣-Topless 

- c330_01_burst_Na0h_皇冠的新衣-Topless

- c330-01-burst-Na0h-皇冠的新衣-Topless

#### ②其他mod的repack
很遗憾，目前还没找到对**珍藏品动画**（favourite，可以是standing也可以是lobby）和**活动壁纸**（event lobby）的repack，但是鉴于这类mod本身很稀缺，想必手动repack便可完事了。  
同时，**妮姬的头像/缩略图（portraits）不需要做repack**，依然可用。  
SWAP mod有专属的维护人员，可以看doro-tools或订阅Na0h获取NMM-SWAP
Voice和Emotion等就十分少见了...


#### ③JSON文件的更新
比较大的麻烦吧：Addressables JSON里的json文件我并不清楚怎么获得，可通过脚本获取的json只包括standing、cover、aim和portraits，而且这个还是根据catalog_db.json和catalog_db_URL.json才能获取。（需要借助Nikke File Finder）  
没有一劳永逸的办法，如果JSON过期了又需要repack的话，多逛逛discord吧。


## 其他
①这只是一个短期的打包工具，并非LTS版本，当然我希望之后需要repack时它依然有用。目前来看，它是解决Idle mod和SkillCut mod相关repack问题的最优解（因为支持处理某类顽固mod）  
②珍藏品动画目前需要Na0h版nmm_v2.5以上才可以打mod  
③这一篇没怎么介绍Nikke Mod相关的内容，需要的话请私讯我让我知道这是有必要的

致谢：  
	KXDE：doro tools 和 doro repacker 的原作者  
	daso132：Doro_Repacker_modified_final  
	Discord：https://discord.gg/nikke
	
> 水母女儿收尾 	(artist: SOLar)
![](https://i2.hdslb.com/bfs/new_dyn/bd678029f226de9593e5266a27f9775219505257.jpg)
