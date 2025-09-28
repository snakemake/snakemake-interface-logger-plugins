# Changelog

## [2.0.0](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v1.2.5...v2.0.0) (2025-09-28)


### ⚠ BREAKING CHANGES

* All LogHandlerBase subclasses must now implement the emit() method.

### Features

* Add test baseclass ([#39](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/39)) ([1b4f2b2](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/1b4f2b29e5bd28d9a079cc51fe56dffe3089dbe1))


### Bug Fixes

* require emit() method implementation in LogHandlerBase ([#41](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/41)) ([f3d56fe](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/f3d56fee72902734797f9ae9b81afabbeb2631c9))

## [1.2.5](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v1.2.4...v1.2.5) (2025-09-28)


### Bug Fixes

* call logging.Handler init in base class ([#34](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/34)) ([a3bd247](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/a3bd247824f2800e454730b82001f826ad073799))
* Require emit() method implementation ([#35](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/35)) ([71e6372](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/71e6372d5c5a3a895de47d41015553987d044103))


### Documentation

* add basefilename requirement ([#38](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/38)) ([38d2993](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/38d29934521734fc16f97a4505a0c88361075bdd)), closes [#37](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/37)

## [1.2.4](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v1.2.3...v1.2.4) (2025-06-05)


### Documentation

* update readme ([#29](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/29)) ([88fe3b7](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/88fe3b799f5566d96a876e69be449c20b6961bde))

## [1.2.3](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v1.2.2...v1.2.3) (2025-03-20)


### Miscellaneous Chores

* Release 1.2.3 ([#26](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/26)) ([29f7c22](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/29f7c2269b5ba25aacf66c8de23add1578ce1182))

## [1.2.2](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v1.2.1...v1.2.2) (2025-03-17)


### Bug Fixes

* remove lockfile, update gha  ([#23](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/23)) ([03f23f5](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/03f23f52dfe41b79dbf24dc386ca417a0519bded))

## [1.2.1](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v1.2.0...v1.2.1) (2025-03-16)


### Bug Fixes

* force release-please ([#21](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/21)) ([a6570a3](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/a6570a384d18eeebe64bbf0388aa33a72b643faf))

## [1.2.0](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v1.1.0...v1.2.0) (2025-03-14)


### Features

* add pixi config  ([#18](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/18)) ([a365379](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/a365379a813a19e89cae4a69f734760a0308617b))

## [1.1.0](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v1.0.0...v1.1.0) (2025-03-12)


### Features

* add rulegraph property and event, add error event ([#16](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/16)) ([f63bc86](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/f63bc86f454a333b4bc64739f6c58841c9f6bbb3))

## [1.0.0](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v0.3.0...v1.0.0) (2025-03-10)


### ⚠ BREAKING CHANGES

* :pencil2: fix typo in post init ([#13](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/13))

### Features

* add logevent to common ([#14](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/14)) ([5593a4e](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/5593a4e9dde5522c34d18657f4752cc49ab6a6c1))


### Code Refactoring

* :pencil2: fix typo in post init ([#13](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/13)) ([1d6e966](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/1d6e966a0aa009b3a8f72592d022689bf76f95d0))

## [0.3.0](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v0.2.0...v0.3.0) (2025-02-18)


### Features

* add OutputSettingsLoggerInterface and abstract methods to LogHandlerBase ([#11](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/11)) ([f659f82](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/f659f82d461f9d1972ce9b56e4325564a4dd6e8c))

## [0.2.0](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v0.1.3...v0.2.0) (2025-02-12)


### ⚠ BREAKING CHANGES

* API simplification ([#9](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/9))

### Features

* API simplification ([#9](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/9)) ([977fb94](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/977fb946adcb42c9cb6a57f3891a56ebb166ad67))


### Miscellaneous Chores

* Release 0.2.0 ([31c6530](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/31c653060363826f0335ead90c8432aaa9397117))

## [0.1.3](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/v0.1.2...v0.1.3) (2025-02-11)


### Bug Fixes

* get release-please to run properly by updating GitHub Actions versions ([#5](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/5)) ([c26b9a3](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/c26b9a328cd3b5839f4fe18474b6595f6f1af955))
* use release-please python ([#7](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/7)) ([2e1c9b2](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/2e1c9b2c2864d255d0181a575158b34204f875d9))

## [0.1.2](https://github.com/snakemake/snakemake-interface-logger-plugins/compare/0.1.1...v0.1.2) (2025-02-11)


### Miscellaneous Chores

* release 0.1.2 ([#3](https://github.com/snakemake/snakemake-interface-logger-plugins/issues/3)) ([f6ca2a7](https://github.com/snakemake/snakemake-interface-logger-plugins/commit/f6ca2a7e5d92b35772ec884577920bfcd40d6b9b))

## [0.1.1] - 2025-15-01
- Rename LoggerPluginBase to LogHandlerBase

## [0.1.0] - 2024-11-03

- Initial release.
