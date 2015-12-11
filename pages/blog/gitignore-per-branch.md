title: '.gitignore per branch'
published: 2015-05-18
tags: [git]
refs:
    - '[Git excludesfile for a
      branch](http://stackoverflow.com/a/29583813/192916) (Stack Overflow)'

Git does not support to ignore files based on the current branch.  Patterns
listed in any `.gitignore` file as well as in `.git/info/exclude` are always
applied.  A workaround is possible by creating per-branch ignore/exclude
files, and automatically symlinking the correct one using Git’s
[post-checkout hook][1]:

> This hook is invoked when a git checkout is run after having updated the
> worktree. The hook is given three parameters: the ref of the previous HEAD,
> the ref of the new HEAD (which may or may not have changed), and a flag
> indicating whether the checkout was a branch checkout (changing branches,
> flag=1) or a file checkout (retrieving a file from the index, flag=0). This
> hook cannot affect the outcome of git checkout.

For example, the following script looks if there is a file named
`exclude.<branchname>` in the `.git/info` directory, and uses this as link
target for `.git/info/exclude`.  If there is no branch-specific exclude file,
it will symlink `exclude.__default__` instead.

    :::shell-script
    #!/bin/sh

    old_ref=$1
    new_ref=$2
    branch_switched=$3

    if [[ $branch_switched != '1' ]]
    then
        exit 0
    fi

    current_branch=$(git rev-parse --abbrev-ref HEAD)
    hook_dir=$(dirname $0)
    info_dir=$(realpath "$hook_dir/../info")

    exclude_target='__default__'
    if [[ -f "$info_dir/exclude.$current_branch" ]]
    then
        exclude_target=$current_branch
    fi
    cd $info_dir
    rm exclude
    ln -s exclude.$exclude_target exclude

Modify this script as needed, save it as `.git/hooks/post-checkout`, and make
it executable—et voilà.

[1]: http://git-scm.com/docs/githooks#_post_checkout
