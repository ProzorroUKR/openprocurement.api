#!/usr/bin/env bash

if [ ${SANDBOX_MODE} ]
then
    exit
fi

DOCS_ACC='ProzorroUKR'
DOCS_REPO='prozorro-docs'
CUR_DIR="${PWD##*/}"
SOURCES="../$CUR_DIR/docs/source"
TARGET_DIR='docs/source/http'

# getting current branch name with changes (which's different on Travis for pull requests and direct merges)
if [ -z ${TRAVIS_PULL_REQUEST_BRANCH} ]  # if it's empty (not a pull request)
then
    BRANCH=${TRAVIS_BRANCH}  # the name of the triggered (by merge or tag) branch
else
    BRANCH=${TRAVIS_PULL_REQUEST_BRANCH}  #  the name of the branch from which the PR originated
fi

cd ..

# prepare rep and branch
git clone "https://github.com/$DOCS_ACC/$DOCS_REPO.git"
cd "$DOCS_REPO"
git checkout "$BRANCH" || git checkout -b "$BRANCH"

# move files
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"
cp -R "$SOURCES/tutorial" "$TARGET_DIR"
cp -R "$SOURCES/qualification" "$TARGET_DIR"
cp -R "$SOURCES/complaints" "$TARGET_DIR"

# commit and push files
git add "$TARGET_DIR"
git commit -a -m "Auto http-files update from $TRAVIS_REPO_SLUG branch=$BRANCH travis-build=$TRAVIS_BUILD_NUMBER"
git push "https://$GIT_USER:$GIT_TOKEN@github.com/$DOCS_ACC/$DOCS_REPO.git" "$BRANCH"