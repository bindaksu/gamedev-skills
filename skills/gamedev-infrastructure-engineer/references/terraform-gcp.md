# Terraform Skeleton — GKE for a Live Game (GCP)

Read when bootstrapping or reviewing IaC for a game cluster. Provider arguments change between `google` provider major versions; pin versions and check the provider changelog (as of 2026-10; verify). AWS teams: the same structure maps to EKS + managed node groups + security groups.

## Layout

```
infra/
  modules/
    gke-cluster/        # cluster + node pools
    game-network/       # VPC, subnets, firewall for UDP range
    cloudsql-shard/     # one module instance per logical-shard group
    memorystore/
  envs/
    prod-euw1/          # one state per env per region
    prod-usc1/
    staging-euw1/
```

## State backend (locking)

```hcl
terraform {
  required_version = ">= 1.6"
  backend "gcs" {
    bucket = "acme-tfstate-prod"
    prefix = "game/prod-euw1"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"   # pin; verify current major
    }
  }
}
```

## Cluster and node pools

```hcl
resource "google_container_cluster" "game" {
  name                     = "game-prod-euw1"
  location                 = "europe-west1"          # regional control plane
  remove_default_node_pool = true
  initial_node_count       = 1
  networking_mode          = "VPC_NATIVE"
  network                  = var.network
  subnetwork               = var.subnetwork

  release_channel {
    channel = "REGULAR"
  }

  workload_identity_config {
    workload_pool = "${var.project}.svc.id.goog"
  }

  maintenance_policy {
    recurring_window {
      start_time = "2026-01-06T02:00:00Z"            # low-traffic window for this region
      end_time   = "2026-01-06T06:00:00Z"
      recurrence = "FREQ=WEEKLY;BYDAY=TU,WE"
    }
  }
}

resource "google_container_node_pool" "agones_system" {
  name     = "agones-system"
  cluster  = google_container_cluster.game.id
  node_count = 1

  node_config {
    machine_type = "e2-standard-4"
    labels       = { "agones.dev/agones-system" = "true" }
    taint {
      key    = "agones.dev/agones-system"
      value  = "true"
      effect = "NO_EXECUTE"
    }
  }
}

resource "google_container_node_pool" "gameservers" {
  name    = "gameservers"
  cluster = google_container_cluster.game.id

  autoscaling {
    min_node_count = 3
    max_node_count = 300
  }

  management {
    auto_upgrade = true      # constrained by the maintenance window above
    auto_repair  = true
  }

  node_config {
    machine_type = "c3-standard-8"   # compute-optimized; benchmark server frame time per machine family
    tags         = ["game-server"]
    labels       = { role = "gameserver" }
    taint {
      key    = "role"
      value  = "gameserver"
      effect = "NO_SCHEDULE"
    }
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
}

resource "google_compute_firewall" "gameserver_udp" {
  name    = "gameserver-udp-euw1"
  network = var.network

  allow {
    protocol = "udp"
    ports    = ["7000-8000"]     # Agones default port range
  }

  target_tags   = ["game-server"]
  source_ranges = ["0.0.0.0/0"]
}
```

Install Agones with Helm (v1.61 requires Helm v4 tooling) from CI, version-pinned, after the cluster apply — keep the chart version in the env folder so upgrades are reviewed diffs.

## Database (Cloud SQL Postgres, one shard group)

```hcl
resource "google_sql_database_instance" "ledger_shard" {
  for_each         = toset(var.shard_groups)        # e.g. ["sg00", "sg01", ...]
  name             = "ledger-${each.key}-euw1"
  region           = "europe-west1"
  database_version = "POSTGRES_16"                  # verify supported versions
  deletion_protection = true

  settings {
    tier              = var.ledger_tier
    availability_type = "REGIONAL"                  # synchronous standby in another zone

    backup_configuration {
      enabled                        = true
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.network_id
    }

    insights_config {
      query_insights_enabled = true
    }
  }
}
```

## Review checklist

- [ ] Every env/region has its own state prefix; CI holds apply credentials, humans do not
- [ ] `deletion_protection` on all stateful resources; `prevent_destroy` lifecycle on the ledger
- [ ] Provider and module versions pinned; upgrades via PR with plan output attached
- [ ] Maintenance windows set per region to that region's lowest-traffic hours
- [ ] Firewall rules scoped by tag, not applied to all nodes
- [ ] Workload Identity used; no exported service-account keys in CI or pods
- [ ] Secrets in Secret Manager, referenced, never in tfvars committed to Git
