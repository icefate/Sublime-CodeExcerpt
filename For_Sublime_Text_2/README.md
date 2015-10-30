## 关于 - About
CodeExcerpt-实现Editplus素材功能的Sublime Text 2插件。可读取Editplus里的素材片断（ctl文件），并插入到选区（支持多选区插入）。不需要修改ctl文件的内容格式. 

插件适用对象：从Editplus转向Sublime，但并不打算放弃Editplus的人 ( 当然凡事无绝对，参见本页最下端的备注所述)

Git链接: [https://github.com/icefate/Sublime-CodeExcerpt](https://github.com/icefate/Sublime-CodeExcerpt)

插件官网: [http://ce.buckethead.cn](http://ce.buckethead.cn) 

Email：i#buckethead.cn (请将#改为@)

##  演示 - Gif

录制的文件较大，建议花几分钟，耐心看完：

使用快捷键：`ctrl + alt + s`
* <a href="https://raw.githubusercontent.com/icefate/Sublime-CodeExcerpt/master/gif/0.gif" target="_blank">安装 - 0.gif</a>
* <a href="https://raw.githubusercontent.com/icefate/Sublime-CodeExcerpt/master/gif/1.gif" target="_blank">常见情形 - 1.gif</a>
* <a href="https://raw.githubusercontent.com/icefate/Sublime-CodeExcerpt/master/gif/2.gif" target="_blank">单选区 / 多选区 - 2.gif</a> 
* <a href="https://raw.githubusercontent.com/icefate/Sublime-CodeExcerpt/master/gif/3.gif" target="_blank">各种选取情况 - 3.gif</a> 
* <a href="https://raw.githubusercontent.com/icefate/Sublime-CodeExcerpt/master/gif/4.gif" target="_blank">打开chm文件 - 4.gif</a> 


使用快捷键：`ctrl + alt + d`  可以一次性装载所有素材：
* <a href="https://raw.githubusercontent.com/icefate/Sublime-CodeExcerpt/master/gif/5.gif" target="_blank">一次性装载所有素材 - 5.gif</a>


## 配置 - Config
`codeexcerpt.sublime-settings` 有备注

有个 chm文件目录 的配置，可以打开常用的chm手册


## 快捷键 - Key

预设的快捷键有两个, 你也可以自行修改：

* `ctrl + alt + s` ：先装载素材文件，选择后 再装载，素材文件内的素材。
* `ctrl + alt + d` ：一次性装载全部的素材。 注意是键盘上横排的数字键0   而不是数字键区的0


## 兼容 - Compatible 

以下是经过测试的平台环境

* 操作系统：Windows XP & Windows 7
* Sublime版本： Sublime Text 2
* Editplus版本： EditPlus 3.51

非Windows系统 和 Sublime Text 3 没有经过测试, 未知是否可用

## 备注  -  Remarks

* Editplus的ctl文件编码基本上是`ANSI`, 都可以顺利读取到. 但有特殊字符的,例如`Code.ctl`这个文件,里面的有很多特殊字符,是无法读取到的。
* 如果在打开sublime情况下，新增了新的素材文件，你可能需要重启软件才能加载。
* 此插件并没有包含对ctl文件编辑管理的功能，所以你仍然需要在Editplus里进行管理。当然，你也可以放弃使用Editplus，将ctl文件抽出来独立使用于sublime. 那么ctl 文件就需要你自己管理了，手工编辑，又或者你可以考虑写个软件来管理.  要注意的是本插件是遵循Editplus的ctl文件语法来进行字符处理的。





