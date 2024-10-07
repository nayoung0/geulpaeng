# 글팽이

<img src="./assets/geulpaeng_v2.jpg" width="100" height="100"/>


## Introduction
글팽이는 [글또](https://www.notion.so/zzsza/ac5b18a482fb4df497d4e8257ad4d516) 커뮤니티를 위해 만들어진 슬랙봇입니다. 자세한 사용 방법은 [Usage guide](#usage-guide)를 참고해주세요!

* **이모지 체크**
  * 누군가를 태그한 메시지 내에서 스레드로  `@글팽이` 태그와 함께 `체크` 키워드를 포함한 메시지를 입력해주세요.


## Requirements
* Python3.11+
* Poetry
* AWS Credentials
* Slackbot OAuth Tokens


## How to start
### Set up env variables
아래의 파일을 작성하여 `s3://zappa-geulpaeng/env.json` 위치에 업로드 해주세요. `BOT_USERS`는 멘션에서 제외할 유저의 목록입니다. 해당하는 값이 없는 경우엔 `"[]"`로 입력해주세요.
```json
{
  "TOKEN": "your_slackbot_token",
  "BOT_USERS": "[\"BOTUSER_ID\"]"
}
```


### Deploy

```shell
$ git clone git@github.com:nayoung0/geulpaeng.git
$ cd geulpaeng && poetry install
$ zappa deploy test
```


## Usage guide
### 이모지 체크
* 태그된 사람이 이모지를 달지 않은 경우

https://github.com/user-attachments/assets/f3fa3698-2968-4178-b538-8a0587cffd24



* 태그된 사람이 모두 이모지를 단 경우


https://github.com/user-attachments/assets/2e79da7f-1106-4d00-96e8-3576e2450bfe


## Contact
* [Github Issues](https://github.com/nayoung0/geulpaeng/issues)으로 제보해주세요.
* `nayoung.tech@gmail.com` 으로 문의해주세요!
