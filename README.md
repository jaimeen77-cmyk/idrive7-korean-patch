# iDrive 7 한국어 번역 패치

[패치 ZIP 다운로드](https://github.com/jaimeen77-cmyk/idrive7-korean-patch/archive/refs/heads/main.zip)

BMW MGU / iDrive 7용 [원본 idrive7-apps](https://github.com/cauliflowermossgrape/idrive7-apps)에
적용하는 한국어 번역 패치입니다. **이 저장소에는 앱 전체 소스와 `apps/` 폴더가 없습니다.**
BMW `oap-sdk`, 설치용 `.mgu`, Doom 데이터와 차량별 진단 데이터도 포함하지 않습니다.
이 ZIP만으로 앱을 실행하거나 빌드할 수는 없으며, 원본 소스에 적용한 뒤 사용합니다.

## 포함 파일

- `payload/kit/runtime/locales/ko.tsv`, `ko.json`: 한국어 번역 1,774개.
- `payload/kit/localization/fonts/`: 한글 글꼴 아틀라스와 OFL 라이선스.
- `payload/kit/tools/`: 한글 글꼴 생성 도구와 한국어 검사 도구.
- `patches/korean-support.patch`: 공통 런타임·빌드 도구와 Service 날짜·AA Companion
  동적 문구에 필요한 차이 패치. 앱 파일 전체를 배포하지 않습니다.
- `apply.py`, `manifest.json`: 원본 파일과 패치의 해시를 확인하고 적용하는 도구.

## 적용 가능한 원본

검증 기준 커밋: **`68368fdb7d4c86a0164e9131f386baa08264f733`**.

원본의 다른 버전에서는 변경 대상 파일이 달라졌을 수 있습니다. 적용 도구는 예상과
다른 파일을 발견하면 변경 전에 중단합니다. 기존에 한국어 지원이 포함된 버전에는
이 패치를 추가로 덮어쓰지 말고 해당 버전의 `--language ko`를 사용하세요.

Python 3.9 이상, Git, Node.js 14 이상이 필요합니다.
일반 적용·검사에는 SDK, Pillow나 별도 글꼴 설치가 필요 없습니다.

## 적용 방법

아래처럼 원본과 패치를 나란히 준비하세요. ZIP을 받아 압축을 푼 경우도 같은 방식입니다.

```text
작업 폴더/
  idrive7-apps/                 원본 소스
  idrive7-korean-patch/         이 패치
```

검증된 원본을 새로 준비하는 예:

```sh
git clone https://github.com/cauliflowermossgrape/idrive7-apps.git
git -C idrive7-apps checkout 68368fdb7d4c86a0164e9131f386baa08264f733
git clone https://github.com/jaimeen77-cmyk/idrive7-korean-patch.git
```

패치 폴더에서 실행합니다. Windows는 `python`, macOS/Linux는 필요하면 `python3`를 사용하세요.

```sh
cd idrive7-korean-patch
python apply.py --check ../idrive7-apps
python apply.py ../idrive7-apps
```

`--check`는 적용 가능 여부만 확인하며 파일을 바꾸지 않습니다.
이미 같은 패치가 적용된 경우 다시 실행해도 파일을 바꾸지 않습니다.
수정할 파일은 모두 사전 검사하며, 적용 도중 오류가 나면 원래 파일을 복원합니다.

이후 **원본 프로젝트 폴더**로 이동해서 검사·미리보기·빌드를 실행하세요.

```sh
cd ../idrive7-apps
python kit/tools/test_ko.py
python kit/tools/build.py --language ko --preview-only redline service car_vitals aa_cluster_companion
node kit/tools/preview.js dist/redline preview/ko/redline render --set renderer=software
```

검사 마지막에 `PASS: 15 Korean app layouts ... 1774 translations ...`가 나오면 통과입니다.
`ko-kr`, `ko-KR`, `ko_KR`도 같은 한국어 빌드 태그로 지원합니다.

차량 설치 파일은 소유 차량에서 추출한 SDK를 원본의 `oap-sdk/`에 넣은 뒤 만듭니다.

```sh
python kit/tools/build.py --language ko
```

`dist/`에 앱별 `-ko.1.mgu`가 생성됩니다. 설치 도구·렌더러가 포함된 키트는
`python kit/tools/make_kit.py --language ko`로 만듭니다.
차량 설치와 제거는 [원본 안내](https://github.com/cauliflowermossgrape/idrive7-apps#3-quick-start)를 따르세요.

## 검증과 업데이트

이 저장소의 **Actions → Validate Korean patch**는 검증 기준 원본을 별도로 내려받아
패치 적용과 한국어·기존 언어·Service 검사를 실행합니다.
원본 앱은 검사 중에만 내려받으며 이 저장소에 올리지 않습니다.

