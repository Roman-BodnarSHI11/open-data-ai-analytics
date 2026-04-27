variable "resource_group_name" {
  default = "lab-rg"
}

variable "location" {
  default = "westeurope"
}

variable "admin_username" {
  default = "azureuser"
}

variable "vm_size" {
  description = "Розмір віртуальної машини Azure"
  default     = "Standard_B2s"
}

variable "repo_url" {
  default = "https://github.com/Roman-BodnarSHI11/open-data-ai-analytics.git"
}