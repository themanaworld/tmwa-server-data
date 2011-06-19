Changing stuff into subdirectories has several problems:
1. There are files that are copied 
2. You may need to change
3. git submodules don't automatically work the way you think they should - you have to add a git hook manually. Unfortunately, there is no hook at all for git reset --hard (use git checkout -B instead)

problem 2 will be solved (or at least ameliorated) by creating scripts in the root (which may conflict with existing names, but hey! I need your attention)
problems 1 and 3 should be solved by running a script
Stuff to do manually:
* put login-server, char-server, map-server binaries in /usr/local/bin (or some other location callable from the scripts)
Stuff to do later:
* change the client-data submodule to track the main project and delete the testing repository for client data

Stuff to do much later:
* move login/ to the server repository
* Store stuff in a well-known directory
* create a 'make install' target
* create /etc/init.d scripts and get packaged

-o11c


Useful commands:
git submodule update            lose changes in submodule and reset to upstream
git submodule update --merge    merge changes in submodule from upstream
git submodule update --rebase   rebase local changes on top of upstream
        (use this, for the same reason you should use git pull --rebase instead of just git pull - but remember that it's dangerous)
git submodules sync             change the url of the submodule (when testing is deleted)
git config --global url.git@gitorious.org:.pushInsteadOf git://gitorious.org
                                for people with push access: don't pull via ssh (which is slower anyway), required for submodules to work properly
git checkout HEAD^ -B master    completely roll back the latest commit
git reset HEAD^                 undo the last commit but keep changes
