#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

alias ls='ls --color=auto'
alias grep='grep --color=auto'
PS1='[\u@\h \W]\$ '
export PATH="$HOME/bin:$PATH"
alias dotfiles='/usr/bin/git --git-dir=/home/zcxdr/.dotfiles/ --work-tree=/home/zcxdr'
