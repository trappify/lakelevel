# Releasing

1. Decide on the next semantic version (major.minor.patch) for both the Python package and the Home Assistant integration.
2. Update `pyproject.toml` and `custom_components/lakelevel/manifest.json` with the new version.
3. Record the changes in `CHANGELOG.md`.
4. Commit the version bump and changelog updates.
5. Tag the commit using `git tag vX.Y.Z` and push with `git push && git push --tags`.
6. Create a GitHub release referencing the tag. HACS users can point to the repository URL directly (custom repository).

HACS installation requires users to add `https://github.com/trappify/lakelevel` as a custom repository under the **Integration** category.
