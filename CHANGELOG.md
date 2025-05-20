# Changelog

This project uses [towncrier](https://towncrier.readthedocs.io/) to generate changelogs.

The changes for the upcoming release can be found in
<https://github.com/ansys/grantami-recordlists/tree/main/doc/changelog.d/>.


## [1.3.0](https://github.com/ansys/grantami-recordlists/releases/tag/v1.3.0) - 2024-12-13


### Changed

- CI - Add changelog and deploy-changelog action [#243](https://github.com/ansys/grantami-recordlists/pull/243)
- Use ansys doc build action [#248](https://github.com/ansys/grantami-recordlists/pull/248)
- Only run labeler workflow on pull requests [#260](https://github.com/ansys/grantami-recordlists/pull/260)
- Don't generate changelog fragments for dependabot PRs [#266](https://github.com/ansys/grantami-recordlists/pull/266)
- Update changelog [#267](https://github.com/ansys/grantami-recordlists/pull/267)


### Fixed

- Exclude table with dynamic record count from tests [#251](https://github.com/ansys/grantami-recordlists/pull/251)


### Dependencies

- Update grantami-serverapi-openapi to 3.0.0 [#249](https://github.com/ansys/grantami-recordlists/pull/249)
- Update openapi-common to v2.0.1 [#253](https://github.com/ansys/grantami-recordlists/pull/253)
- Bump jupytext from 1.16.1 to 1.16.2 [#254](https://github.com/ansys/grantami-recordlists/pull/254)
- Bump ansys-openapi-common from 2.0.1 to 2.0.2 [#255](https://github.com/ansys/grantami-recordlists/pull/255)
- Bump jinja2 from 3.1.3 to 3.1.4 [#261](https://github.com/ansys/grantami-recordlists/pull/261)
- Re-organize documentation, add user guide [#268](https://github.com/ansys/grantami-recordlists/pull/268)
- Bump ServerAPI to 25R1 build [#315](https://github.com/ansys/grantami-recordlists/pull/315)
- Upgrade serverapi-openapi to 4.0.0 [#330](https://github.com/ansys/grantami-recordlists/pull/330)
- Bump grantami-serverapi-openapi to 4.0.0 release [#331](https://github.com/ansys/grantami-recordlists/pull/331)


### Miscellaneous

- Update openapi-common reference link [#256](https://github.com/ansys/grantami-recordlists/pull/256)
- [pre-commit.ci] pre-commit autoupdate [#276](https://github.com/ansys/grantami-recordlists/pull/276)


### Documentation

- Add link to supported authentication schemes [#321](https://github.com/ansys/grantami-recordlists/pull/321)
- Fix installation example for git dependency [#322](https://github.com/ansys/grantami-recordlists/pull/322)
- Add link to PyGranta version compatibility documentation [#323](https://github.com/ansys/grantami-recordlists/pull/323)
- Update Ansys documentation links to 2025 R1 [#337](https://github.com/ansys/grantami-recordlists/pull/337)
- Use public 2024 R2 Ansys documentation [#340](https://github.com/ansys/grantami-recordlists/pull/340)
- Revert required MI version bump to 2024 R2 [#351](https://github.com/ansys/grantami-recordlists/pull/351)


### Maintenance

- Don't create changelog fragments for pre-commit updates [#307](https://github.com/ansys/grantami-recordlists/pull/307)
- Add dependabot and pre-commit approve workflow [#314](https://github.com/ansys/grantami-recordlists/pull/314)
- Publish dev builds to private PyPI [#318](https://github.com/ansys/grantami-recordlists/pull/318)
- Use PyPI Trusted Publisher approach for releases [#320](https://github.com/ansys/grantami-recordlists/pull/320)
- Improve VM management in CI [#324](https://github.com/ansys/grantami-recordlists/pull/324)
- Update CONTRIBUTORS and AUTHORS to new format [#328](https://github.com/ansys/grantami-recordlists/pull/328)
- Use Production VM for CI on release branch [#335](https://github.com/ansys/grantami-recordlists/pull/335)
- Prepare v1.3.0 release [#349](https://github.com/ansys/grantami-recordlists/pull/349)

## grantami-recordlists 1.2.1, 2024-05-07

### Dependencies

* Update granta-serverapi-openapi to 3.0.0

### Contributors

* Andy Grigg (Ansys)
* Ludovic Steinbach (Ansys)
* Doug Addy (Ansys)


## grantami-recordlists 1.2.0, 2024-05-02

### New features

* [Issue #165](https://github.com/ansys/grantami-recordlists/issues/165),
  [Pull request #166](https://github.com/ansys/grantami-recordlists/pull/166): Add `get_resolvable_list_items` method.
* [Issue #195](https://github.com/ansys/grantami-recordlists/issues/195),
  [Pull request #207](https://github.com/ansys/grantami-recordlists/pull/207): Allow `match_all` and `match_any` in boolean criteria.

### Contributors

* Andy Grigg (Ansys)
* Ludovic Steinbach (Ansys)
* Doug Addy (Ansys)

## grantami-recordlists 1.1.0, 2024-01-17

### New features

* Add support for Python 3.12.
* Drop support for Python 3.8.

### Doc improvements

* Document use of the `pygranta` meta-package for managing compatibility between PyGranta and
  Granta MI.

### Contributors

* Doug Addy (Ansys)
* Andy Grigg (Ansys)
* Ludovic Steinbach (Ansys)
* Judy Selfe (Ansys)
