# Подготовка terraform конфигов для создания машин в Yacloud

## Подготовка провайдера
```bash
mv ~/.terraformrc ~/.terraformrc.old

tee ~/.terraformrc > /dev/null <<EOF 
provider_installation {
  network_mirror {
    url = "https://terraform-mirror.yandexcloud.net/"
    include = ["registry.terraform.io/*/*"]
  }
  direct {
    exclude = ["registry.terraform.io/*/*"]
  }
}
EOF
```

## Подготовка ssh agent
```bash
ssh-add check-assignment-github-key
```

## Создание SA
```bash
cd ~/check-assignment-yacloud-sa
#yc iam service-account create --name check-assignment-github-sa --format json > sa.json
yc iam service-account get --name check-assignment-github-sa --format json > sa.json
SA_ID=$(jq -r .id sa.json)
FOLDER_ID=$(jq -r .folder_id sa.json)

yc resource-manager folder add-access-binding $FOLDER_ID \
  --role admin \
  --subject serviceAccount:$SA_ID
```

Только для локального запуска
```bash
echo "export YC_TOKEN=$(yc iam create-token --impersonate-service-account-id $SA_ID)" > .env
echo "export YC_CLOUD_ID=$(yc config get cloud-id)"  >> .env
echo "export YC_FOLDER_ID=$(yc config get folder-id)" >> .env
echo "export TF_HTTP_TIMEOUT=240s" >> .env
```