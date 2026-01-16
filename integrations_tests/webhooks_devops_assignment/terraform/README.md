# Локальный запуск

```bash
. ~/check-assignment-yacloud-sa/.env

export TF_VAR_run=local
terraform init
terraform plan
terraform apply
```

# Удалить ресурсы
```bash
terraform state rm yandex_vpc_subnet.subnet || true
terraform destroy
```