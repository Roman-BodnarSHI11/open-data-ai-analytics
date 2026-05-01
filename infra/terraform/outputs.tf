output "public_ip" {
  value       = azurerm_public_ip.pip.ip_address
  description = "Публічна IP-адреса віртуальної машини"
}

output "web_url" {
  value       = "http://${azurerm_public_ip.pip.ip_address}:8080"
  description = "URL для доступу до веб-інтерфейсу"
}

output "argocd_url" {
  value       = "http://${azurerm_public_ip.pip.ip_address}:30443"
  description = "URL для доступу до Argo CD UI"
}

output "app_url" {
  value       = "http://${azurerm_public_ip.pip.ip_address}:30080"
  description = "URL для доступу до GitOps-застосунку (NodePort)"
}

output "ssh_private_key" {
  value     = tls_private_key.ssh.private_key_pem
  sensitive = true
}