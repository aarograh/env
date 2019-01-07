# .bashrc
 
# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi
# Uncomment the following line if you don't like systemctl's auto-paging feature:
# export SYSTEMD_PAGER=

# Set up modules
export MODULEPATH=/opt/modules/modulefiles:${MODULEPATH}
module purge
module load casl_tools/gcc-5.4.0

# Modify paths
export DATA=~/master/SCALE_test_data
export MPACT_ADD_REPO_CLASS=Continuous
export PATH=/opt/bin:$PATH
export PATH=~/env/scripts/postprocessing:$PATH
export PATH=~/env/scripts/build_scripts:$PATH
export PATH=~/env/scripts/run_scripts:$PATH
export PATH=~/env/scripts/MCFR:$PATH
export MPACT_DATA=~/master/VERAData/MPACT
export MPACT_ADD_URL_REPO_BASE=repos@gad.ornl.gov:
 
# User specific aliases and functions
alias ll='ls -lFh'
alias la='ll -a'
alias ml='module list'
alias ma='module avail'
 
# Color command prompt
PS1='\[\033[1;36m\]\u\[\033[1;31m\]@\[\033[1;32m\]\h:\[\033[1;35m\]\w\[\033[1;31m\]\$\[\033[0m\] '
