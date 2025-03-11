## docker 실행
```bash
docker compose up --build -d  
```


## API 문서
- [Local Swagger](http://localhost:8000/docs)


## sample data DB 등록
- [Local Swagger API /import-csv](http://localhost:8000/docs#/COMPANY/post_import_csv_import_csv_post)


## 테스트 코드 실행
```bash
pytest tests/test_senior_app.py
```


## DB 설계
- company: 회사 기본정보 테이블 
```sql
CREATE TABLE `company` (
  `company_id` int NOT NULL AUTO_INCREMENT COMMENT '회사아이디',
  `registration_datetime` datetime NOT NULL DEFAULT (now()) COMMENT '등록일시',
  PRIMARY KEY (`company_id`)
)
```

- company_info: 회사명 정보 테이블 (다국어)
```sql
CREATE TABLE `company_info` (
  `company_id` int NOT NULL COMMENT '회사아이디',
  `language_type` varchar(10) NOT NULL COMMENT '언어유형',
  `company_name` varchar(200) NOT NULL COMMENT '회사이름',
  `registration_datetime` datetime NOT NULL DEFAULT (now()) COMMENT '등록일시',
  PRIMARY KEY (`company_id`,`language_type`)
)
```

- common_tag: 태그 정보 테이블 (다국어)
```sql
CREATE TABLE `common_tag` (
  `tag_id` int NOT NULL AUTO_INCREMENT COMMENT '태그아이디',
  `tag_group_id` int NOT NULL COMMENT '태그그룹아이디',
  `language_type` varchar(10) NOT NULL COMMENT '언어유형',
  `tag_name` varchar(200) NOT NULL COMMENT '태그이름',
  `registration_datetime` datetime NOT NULL DEFAULT (now()) COMMENT '등록일시',
  PRIMARY KEY (`tag_id`),
  UNIQUE KEY `ix_tag_name_language_type_unique` (`language_type`,`tag_name`)
)
```

- company_tag_mapping: 회사 태그 매핑 테이블
```sql
CREATE TABLE `company_tag_mapping` (
  `company_tag_mapping_id` int NOT NULL AUTO_INCREMENT COMMENT '회사태그맵핑아이디',
  `company_id` int NOT NULL COMMENT '회사아이디',
  `tag_id` int NOT NULL COMMENT '태그아이디',
  `registration_datetime` datetime NOT NULL DEFAULT (now()) COMMENT '등록일시',
  `delete_yn` enum('N','Y') NOT NULL DEFAULT 'N' COMMENT '삭제여부',
  `delete_datetime` datetime DEFAULT NULL COMMENT '삭제일시',
  PRIMARY KEY (`company_tag_mapping_id`)
)
```
