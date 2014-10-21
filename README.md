## 关于 - About
CodeExcerpt-实现Editplus素材功能的Sublime插件。可读取Editplus里的素材片断（ctl文件），并插入到选区（支持多选区插入）。不需要修改ctl文件的内容格式.

预设的快捷键： `ctrl + alt + s`

插件适用对象：从Editplus转向Sublime，但并不打算放弃Editplus的人 ( 当然凡事无绝对，参见本页最下端的备注所述)

Git链接: [https://github.com/icefate/Sublime-CodeExcerpt](https://github.com/icefate/Sublime-CodeExcerpt)

插件官网: [http://ce.buckethead.cn](http://ce.buckethead.cn) 

Email: i@buckethead.cn

##  演示 - Gif

录制的文件较大，建议花几分钟，耐心看完：
* <a href="http://ce.buckethead.cn/0.gif" target="_blank">安装 - 0.gif</a>
* <a href="http://ce.buckethead.cn/1.gif" target="_blank">常见情形 - 1.gif</a>
* <a href="http://ce.buckethead.cn/2.gif" target="_blank">单选区 / 多选区 - 2.gif</a>
* <a href="http://ce.buckethead.cn/3.gif" target="_blank">各种选取情况 - 3.gif</a>
* <a href="http://ce.buckethead.cn/4.gif" target="_blank">打开chm文件 - 4.gif</a>


## 配置 - Config
`codeexcerpt.sublime-settings` 有备注

有个 chm文件目录 的配置，可以打开常用的chm手册

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


