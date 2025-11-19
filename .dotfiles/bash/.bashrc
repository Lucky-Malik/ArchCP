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

#Load custom cp-tools functions
[ -f ~/.config/cp-tools/functions.sh ] && source ~/.config/cp-tools/functions.sh
export PATH="$HOME/.config/cp-tools/scripts:$PATH"
# Add custom scripts to PATH
export PATH="$HOME/.config/cp-tools/scripts:$HOME/.config/cp-app:$PATH"
