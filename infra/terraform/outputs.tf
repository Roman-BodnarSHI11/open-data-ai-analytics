output "public_ip" {
  value       = azurerm_public_ip.pip.ip_address
  description = "Публічна IP-адреса віртуальної машини"
}

output "web_url" {
  value       = "http://${azurerm_public_ip.pip.ip_address}:8080"
  description = "URL для доступу до веб-інтерфейсу"
}

output "ssh_private_key" {
  value     = tls_private_key.ssh.private_key_pem
  sensitive = true
}