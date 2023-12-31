# How to cut a new release
1. Make certain your branch is in sync with head and then create a new release branch:

        git pull origin main
        git switch -c version_0.2.0

2. Update version to, e.g. 0.2.0 in `package.json`

3. Make sure that proptypes in `fragments/Vega.react.js` and `components/Vega.react.js` are in sync

4. Build new version and test it
        npm install
        npm run build

        python example_app.py

5. Commit changes and push:

        git add . -u
        git commit -m "MAINT: Bump version to 0.2.0"
        git push

6. Merge release branch into main, make sure that all required checks pass

7. On main, build source & wheel distributions:

        git checkout main
        git pull

        rm -rf dist
        python setup.py sdist bdist_wheel

8. Publish to PyPI (Requires correct PyPI owner permissions):

        twine upload dist/*

9. On main, tag the release:

        git tag -a v0.2.0 -m "Version 0.2.0 release"
        git push origin v0.2.0

10. Add release in https://github.com/binste/dash-vega-components/releases and select the version tag

11. Update version to e.g. 0.3.0dev in `package.json` in new branch

        git switch -c maint_0.3.0dev
        # Change version, then:
        npm install
        npm run build

12. Commit change and push:

        git add . -u
        git commit -m "MAINT: Bump version to 0.3.0dev"
        git push

13. Merge maintenance branch into main