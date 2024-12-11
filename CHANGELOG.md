# CHANGELOG



## v0.4.0 (2024-12-11)

### Feature

* feat(ClassificationAnnotations): stack multiple dots ([`4cabc19`](https://github.com/Kitware/trame-annotations/commit/4cabc1997d06545baa7ae87b5909a0a378d8bf03))

* feat(ImageDetection): show score as percentage ([`ba2aad1`](https://github.com/Kitware/trame-annotations/commit/ba2aad1fbeed5b262e9beeb8411640d765f1e2aa))

* feat(ImageDetection): red reserved for missing category annotations ([`23d812e`](https://github.com/Kitware/trame-annotations/commit/23d812e77b4469cf010837f2c8ea0ab87955ee01))

* feat(ImageDetection): add score threshold prop

Filters annotations. ([`e229398`](https://github.com/Kitware/trame-annotations/commit/e2293988c2c33bd1804c1514dc2024854490a869))

* feat(ImageDetection): add 4 more category colors ([`e1465db`](https://github.com/Kitware/trame-annotations/commit/e1465dbeafc3a617a249d8d0e8ba409e36d1c476))

* feat(ImageDetection): show score for annotations ([`4eccedf`](https://github.com/Kitware/trame-annotations/commit/4eccedfb0fe33cc2841c41564ae62aaea76a1a6c))

* feat(ImageDetection): hover over dot to see classes ([`867f415`](https://github.com/Kitware/trame-annotations/commit/867f415c2edc5fb59aec01d8660ae99f6e82e8ba))

### Fix

* fix(ImageDetection): emit hover event in mouseleave function

There is an error in Javascript that borks client side trame code
when calling emit(&#39;hover&#39;) in a watchEffect.  Steps
1. In nrtk-explorer
2. Turn on Model Inference
3. Switch to Grid view for image list
4. Error in JS console:
NotReadableError: The requested file could not be read, typically due to permission problems that have occurred after a reference to a file was acquired.
in
t.onmessage = async u =&gt; {
        const p = await c.processChunk(u.data, h);
        p &amp;&amp; l(p)
    } ([`d38cd84`](https://github.com/Kitware/trame-annotations/commit/d38cd84c7f4777cd43b4e6ef70221d2f5ccb90c4))

### Refactor

* refactor(ImageDetection): extract BoxAnnotations component ([`784aedb`](https://github.com/Kitware/trame-annotations/commit/784aedb4f986bfd57b0bff61f1eb4c66d4dfa4ba))

* refactor(ImageDetection): extract ClassificationAnnotations component ([`f974fcf`](https://github.com/Kitware/trame-annotations/commit/f974fcfe15b99a3e3e13abd4560f7a311b54b621))

* refactor(ImageDetection): extract AnnotationPopup component ([`49d6871`](https://github.com/Kitware/trame-annotations/commit/49d6871cc21026979903525e57570e94537f910d))

* refactor(ImageDetection): declarative style for mouse events ([`8faee9a`](https://github.com/Kitware/trame-annotations/commit/8faee9a2690bee984853a32e383bc7b728464ad4))

### Unknown

* Merge pull request #7 from Kitware/hover-classes

Hover over dot to show image classifications ([`f18eb65`](https://github.com/Kitware/trame-annotations/commit/f18eb656496ce862122123d2f0ca38937a325627))


## v0.3.0 (2024-11-22)

### Feature

* feat(ImageDetection): add whole image classification support ([`3177d19`](https://github.com/Kitware/trame-annotations/commit/3177d19327947fd8f91927bbec14767ce1f4236a))

### Unknown

* Merge pull request #5 from Kitware/classes

feat(ImageDetection): add whole image classification support ([`0ba98f3`](https://github.com/Kitware/trame-annotations/commit/0ba98f33515ba4dcd0205a95740d385430b0b25e))


## v0.2.0 (2024-11-14)

### Feature

* feat(ImageDetection): additive blend mode for annotations ([`873accc`](https://github.com/Kitware/trame-annotations/commit/873accc072760681dfb9ad9ae4fcce9e980dc25e))

* feat(ImageDetection): add line_width and line_opacity props ([`ea6aaa3`](https://github.com/Kitware/trame-annotations/commit/ea6aaa303f388a7e461d3c0aab7dcf1ac9dafaa2))

### Fix

* fix(ImageDetection): fallback to line width default correctly ([`cb3c237`](https://github.com/Kitware/trame-annotations/commit/cb3c237529740a420ecb97046ef5a6ec750c834e))

* fix(ImageDetection): set bbox line width in display pixels

If an image was large, but displayed at a smaller size,
the bounding box line was very thin and hard to see. ([`fd74d92`](https://github.com/Kitware/trame-annotations/commit/fd74d92c5a6c88725de37708b9a2f5a702e59731))

### Unknown

* Merge pull request #4 from Kitware/line-width

Box line width in display pixels ([`71f4d5a`](https://github.com/Kitware/trame-annotations/commit/71f4d5aa8640f580c1a1399bb8d9c6f7e1bf34d8))


## v0.1.1 (2024-11-01)

### Fix

* fix(ImageDetection): increase annotation line width

Also, factor window DPI into line width. ([`c019056`](https://github.com/Kitware/trame-annotations/commit/c019056be5793074bb196e6224a543bbcbc7d086))

### Refactor

* refactor(vue-components): dont allow any type ([`e28ad57`](https://github.com/Kitware/trame-annotations/commit/e28ad57e16910e9eab7fae137b0e04189dcff506))

* refactor(vue-components): flatten directory structure ([`f1d999f`](https://github.com/Kitware/trame-annotations/commit/f1d999fa52061eb380dec55f8130ebc8ebeb6c98))

* refactor(ImageDetection): typecheck files and update npm dependencies ([`39ac0a0`](https://github.com/Kitware/trame-annotations/commit/39ac0a081ea5e131e0d5d2813dd44811e25d592e))

### Unknown

* Merge pull request #3 from Kitware/mor-colors

Increase annotation line width ([`715aa58`](https://github.com/Kitware/trame-annotations/commit/715aa58e9a51fb3d33ecb63987c54c19f79cfd27))


## v0.1.0 (2024-10-31)

### Chore

* chore(vue-components): dev build watch and sourcemaps ([`927456d`](https://github.com/Kitware/trame-annotations/commit/927456d8428da918692411bca4476485219b1cbb))

* chore(ci): setup node for pre-commit checks ([`39f382c`](https://github.com/Kitware/trame-annotations/commit/39f382c29c3c4428f9b71351c7608f249b9f6521))

* chore(pre-commit): add &#34;npm run lint&#34; check ([`d22e1b4`](https://github.com/Kitware/trame-annotations/commit/d22e1b487f302a70b19256104cc7f095e8a49444))

### Documentation

* docs(examples): add ImageDetection widget example ([`d06938f`](https://github.com/Kitware/trame-annotations/commit/d06938f1387bca22640441da7711a5cdd5b768e1))

### Feature

* feat(ImageDetection): outline for annotation instead of filled rectangle ([`4d0ea1e`](https://github.com/Kitware/trame-annotations/commit/4d0ea1e9b181c9e62c9ccaaa7dd8455d5cfa7b3b))

### Style

* style(vue-components): style with default prettier ([`937f318`](https://github.com/Kitware/trame-annotations/commit/937f31897402d57592d1abe08f7c0816c2f9fa8c))

### Unknown

* Merge pull request #2 from Kitware/outline

feat(ImageDetection): outline for annotation instead of filled rectangle ([`e934f78`](https://github.com/Kitware/trame-annotations/commit/e934f78851a92f8381365c1c16bb59348ce01483))

* Merge pull request #1 from Kitware/example

docs(examples): add ImageDetection widget example ([`ab53c71`](https://github.com/Kitware/trame-annotations/commit/ab53c71ae22f84351b0090164dccbc55f2aba0b4))


## v0.0.2 (2024-10-25)

### Fix

* fix(publish): update ci to publish ([`5e9a39d`](https://github.com/Kitware/trame-annotations/commit/5e9a39d6cdffbab39ab173be2b7ab94b7db51657))


## v0.0.1 (2024-10-25)

### Chore

* chore(py): fix widget api ([`53e15bc`](https://github.com/Kitware/trame-annotations/commit/53e15bc60ec6afb3def031b7568bdfb020ea6c48))

* chore(build): add missing build script ([`325c436`](https://github.com/Kitware/trame-annotations/commit/325c43639254904a7fb94edcd55189ae1e7bd382))

* chore(code): get initial code in ([`9834180`](https://github.com/Kitware/trame-annotations/commit/98341806d8f10f5e665df3984c590b07fc484242))

### Ci

* ci: try to get semantic release to work ([`12362b2`](https://github.com/Kitware/trame-annotations/commit/12362b2afa4967174640c03ed401cd857ee5da96))

* ci: semantic release workflow ([`897379e`](https://github.com/Kitware/trame-annotations/commit/897379e0fea86a83abdaf7ca69c8296a04da708d))

* ci: remove windows for now ([`ed5f78b`](https://github.com/Kitware/trame-annotations/commit/ed5f78b93fd9bcde203e4e7c0fd0ca85dcd125b6))

* ci: tests ([`5503899`](https://github.com/Kitware/trame-annotations/commit/5503899679edcf610707dfe9976268af5a972aa5))

* ci: try to get things setup ([`0dafb1d`](https://github.com/Kitware/trame-annotations/commit/0dafb1d773ef0ca54051aceae84dc6a4a0da7373))

### Fix

* fix(py): register package properly ([`34b02fa`](https://github.com/Kitware/trame-annotations/commit/34b02fa26439b1358b843e9c5aab6830fa3b8d37))

* fix(js): lint and dep ([`a6ceea8`](https://github.com/Kitware/trame-annotations/commit/a6ceea869e10850b3ebb9f14b032f8ac9aae95c4))
