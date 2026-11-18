# GuideHollow 썰툰 (`toon.guidehollow.com`)

사이다 공감 썰툰 10편 연재관 + 무료 브라우저 4컷·6컷·9:16 쇼츠 스토리툰 제작 스튜디오 정적 포털입니다.

## 광고 모드 (쿠팡 파트너스 임시 배너 -> 애드센스 원클릭 전환)
- 기본 모드(`--ad-mode coupang`): 비-OpenAPI 검증 완료 `ghshopping` 쿠팡 파트너스 검색/카테고리/맞춤 상품 배너 + 대가성 고지 표시
- 애드센스 승인 후 전환:
  ```sh
  python3 tools/build.py --ad-mode adsense
  ```
- 라이브 미리보기 전환 테스트: 아무 URL 뒤에 `?ad_mode=adsense` 또는 `?ad_mode=coupang` 추가
