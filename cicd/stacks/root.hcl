# Configuración del backend remoto para Terraform
# Nota: Los buckets específicos se configuran en cada terragrunt.hcl individual

# Configuración base común para todos los entornos
inputs = {
  region = "us-central1"
  zone   = "us-central1-a"
}