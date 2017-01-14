---
layout: post
title: vim插件使用经验
tags: vim
datetime: 2017-1-14 22:50
---

{{ page.title }}
================
# vimrc plugins
includes:
* 'VundleVim/Vundle.vim'
* 'Valloric/YouCompleteMe'
* 'SirVer/ultisnips'
* 'majutsushi/tagbar'
* 'terryma/vim-multiple-cursors'
* 'vim-airline/vim-airline'
* 'vim-airline/vim-airline-themes'
* 'kien/ctrlp.vim'
* 'uguu-org/vim-matrix-screensaver'
* 'scrooloose/nerdtree'
* 'mileszs/ack.vim'

## Vundle
vim 插件管理器，安装vundle:

> git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim'

安装插件项目参考：<a href="https://github.com/layjump/vimrc.git">vim配置和插件安装</a>

## YouCompleteMe
和ultisnips一起用来代码补全，代码跳转。
需要vim 7.4以上，最好安装完整版本。

> apt-get install vim-nox

vundle安装完之后，需要进入目录安装，例如：

> ./install.py --help
> ./install.py --clang-compiler

### 配置

> " for ycm
> let g:ycm_error_symbol = '>>'
> let g:ycm_warning_symbol = '>*'
> nnoremap <leader>gl :YcmCompleter GoToDeclaration<CR>
> nnoremap <leader>gf :YcmCompleter GoToDefinition<CR>
> nnoremap <leader>gg :YcmCompleter GoToDefinitionElseDeclaration<CR>
> nmap <F4> :YcmDiags<CR>

### 用法
\<Leader\>默认是"\"键。

> \gl "跳转到声明处

## Tagbar
代码定位，查找和跳转，需要安装ctags

> sudo apt-get install ctags

### 配置

> map <F8> :TagbarToggle<CR>
> let g_tagbarautoclose = 1 "按Enter跳转之后tagbar窗口自动关闭。
> let g_tagbarautofocus = 1 "按F8打开tagbar窗口之后光标自动跳转到tagbar窗口。

### 用法

> F8+Enter

## vim-multiple-cursors
多光标同时操作
### 配置

> let g:multi_cursor_use_default_mapping=0
> let g:multi_cursor_next_key='<C-n>'
> let g:multi_cursor_prev_key='<C-p>'
> let g:multi_cursor_skip_key='<C-x>'
> let g:multi_cursor_quit_key='<Esc>'
> let g:multi_cursor_start_key='<C-n>'
> let g:multi_cursor_start_word_key='g<C-n>'

### 用法
Ctrl+n开启多光标操作，Ctrl+n同时选取下一个keyword，Esc退出。
选取完作用目标之后Ctrl+c删除，然后重新编辑。

## Ack.vim
文本查找，支持递归和正则
### 配置

> nnoremap <Leader>a :Ack!<Space>

### 用法

> :Ack! keyword
> \\a keyword

## ctrlp.vim
文件查找，支持递归
### 用法

> Ctrl+p

## nerdtree
文件夹浏览器
### 配置

> nnoremap <F2> :NERDTreeToggle<Enter>

## vim-matrix-screensaver
屏保，纯装逼用。。
### 用法

> :Matrix

