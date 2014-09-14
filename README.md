## 关于 - About
CodeExcerpt插件实现Editplus里的素材功能，读取素材片断，并插入到选区（支持多选区插入）
直接读取Editplus里的ctl文件，而不需要修改内容格式。 基本可以实现

预设的快捷键： `ctrl+alt+s`

插件适用对象：从Editplus转向Sublime，但并不打算放弃Editplus的人

Git链接:  https://github.com/icefate/Sublime-CodeExcerpt

插件官网: [http://ce.buckethead.cn](http://ce.buckethead.cn) 

Email: <span style="color: green;">i@buckethead.cn</span>


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
* 此插件并没有包含对ctl文件编辑管理的功能，所以你仍然需要在Editplus里进行管理。