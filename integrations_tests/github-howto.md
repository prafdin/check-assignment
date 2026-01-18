## Настройки GitHub для запуска тестов

Для запуска terraform в workflow выпускается jwt токен, который обменивается на IAM токен в Yandex Cloud. 
Чтобы это для всех веток, в GitHub для данного репозитория настроен custom sub атрибут в JWT токене. 
```bash
gh api   --method PUT   -H "Accept: application/vnd.github+json"   -H "X-GitHub-Api-Version: 2022-11-28"   /repos/prafdin/check-assignment/actions/oidc/customization/sub   --input - <<< '{
  "use_default": false,
  "include_claim_keys": [
    "repo"
  ]
}'

```

В Yandex Cloud настроен федеративный SA аккаунт на claim Sub = repo:prafdin/for-test-only.

Полезные ссылки:
- https://yandex.cloud/ru/docs/iam/tutorials/wlif-github-integration
- https://docs.github.com/en/actions/reference/security/oidc
- https://docs.github.com/en/actions/concepts/security/openid-connect