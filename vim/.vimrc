highlight colorcolumn ctermbg=235 guibg=#2c2d27
let &colorcolumn="80,".join(range(100,999),",")
set linebreak
set nolist  " list disables linebreak
set relativenumber
set pastetoggle=<F12>

" Plugins
 call plug#begin()
 Plug 'jeffkreeftmeijer/vim-numbertoggle'
 Plug 'tpope/vim-sensible'
 Plug 'scrooloose/nerdtree'
 Plug 'junegunn/vim-easy-align'
 Plug 'Townk/vim-autoclose'
 Plug 'vim-scripts/python_calltips'
 call plug#end()

" Key Mappings
map <C-J> <C-W>j
map <C-K> <C-W>k
map <C-L> <C-W>l
map <C-H> <C-W>h

" Formatting
set shiftwidth=2
set expandtab
