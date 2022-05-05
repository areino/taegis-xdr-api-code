CREATE TABLE `alert` (
  `id` varchar(45) NOT NULL,
  `alert_type` varchar(100) DEFAULT NULL,
  `confidence` float DEFAULT NULL,
  `severity` float DEFAULT NULL,
  `creator` varchar(45) DEFAULT NULL,
  `tenant_id` int(11) DEFAULT NULL,
  `message` varchar(200) DEFAULT NULL,
  `insert_timestamp` timestamp NULL DEFAULT NULL,
  `domain_registration_date` timestamp NULL DEFAULT NULL,
  `username` varchar(200) DEFAULT NULL,
  `source_ip` varchar(45) DEFAULT NULL,
  `destination_ip` varchar(45) DEFAULT NULL,
  `source_port` int(11) DEFAULT NULL,
  `destination_port` int(11) DEFAULT NULL,
  `blacklist_name` varchar(45) DEFAULT NULL,
  `blacklist_reason` varchar(100) DEFAULT NULL,
  `domain` varchar(45) DEFAULT NULL,
  `timestamp` timestamp NULL DEFAULT NULL,
  `attack_categories` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `alert_asset` (
  `alert_id` varchar(45) DEFAULT NULL,
  `asset_id` varchar(50) DEFAULT NULL,
  `tenant_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `alert_investigation` (
  `alert_id` varchar(45) NOT NULL,
  `investigation_id` varchar(45) NOT NULL,
  `tenant_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `asset` (
  `id` varchar(50) NOT NULL,
  `tenant_id` int(11) DEFAULT NULL,
  `architecture` varchar(45) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  `endpoint_platform` varchar(45) DEFAULT NULL,
  `endpoint_type` varchar(45) DEFAULT NULL,
  `system_type` varchar(45) DEFAULT NULL,
  `host_id` varchar(45) DEFAULT NULL,
  `hostnames` varchar(100) DEFAULT NULL,
  `users` varchar(100) DEFAULT NULL,
  `ip_addresses` varchar(100) DEFAULT NULL,
  `ingest_time` timestamp NULL DEFAULT NULL,
  `kernel_release` varchar(45) DEFAULT NULL,
  `kernel_version` varchar(45) DEFAULT NULL,
  `os_codename` varchar(45) DEFAULT NULL,
  `os_family` varchar(45) DEFAULT NULL,
  `os_release` varchar(45) DEFAULT NULL,
  `os_version` varchar(45) DEFAULT NULL,
  `sensor_id` varchar(45) DEFAULT NULL,
  `sensor_tenant` varchar(45) DEFAULT NULL,
  `sensor_version` varchar(45) DEFAULT NULL,
  `tags` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `asset_health` (
  `id` varchar(50) NOT NULL,
  `color` varchar(45) DEFAULT 'UNKNOWN',
  `actual_isolation_status` tinyint(4) DEFAULT 0,
  `desired_isolation_status` tinyint(4) DEFAULT 0,
  `first_connect_time` timestamp NULL DEFAULT NULL,
  `last_connect_address` varchar(45) DEFAULT NULL,
  `last_connect_server` varchar(45) DEFAULT NULL,
  `last_connect_time` timestamp NULL DEFAULT NULL,
  `last_crash_check` timestamp NULL DEFAULT NULL,
  `last_module_status_time` timestamp NULL DEFAULT NULL,
  `procwall_enabled` tinyint(4) DEFAULT NULL,
  `procwall_last_predicate_time` timestamp NULL DEFAULT NULL,
  `procwall_last_running_time` timestamp NULL DEFAULT NULL,
  `procwall_color` varchar(45) DEFAULT 'UNKNOWN',
  `cyclorama_enabled` tinyint(4) DEFAULT 0,
  `cyclorama_last_predicate_time` timestamp NULL DEFAULT NULL,
  `cyclorama_last_running_time` timestamp NULL DEFAULT NULL,
  `cyclorama_color` varchar(45) DEFAULT 'UNKNOWN',
  `groundling_enabled` tinyint(4) DEFAULT 0,
  `groundling_last_predicate_time` timestamp NULL DEFAULT NULL,
  `groundling_last_running_time` timestamp NULL DEFAULT NULL,
  `groundling_color` varchar(45) DEFAULT 'UNKNOWN',
  `inspector_result_enabled` tinyint(4) DEFAULT 0,
  `inspector_result_last_predicate_time` timestamp NULL DEFAULT NULL,
  `inspector_result_last_running_time` timestamp NULL DEFAULT NULL,
  `inspector_result_color` varchar(45) DEFAULT 'UNKNOWN',
  `inspector_control_enabled` tinyint(4) DEFAULT 0,
  `inspector_control_last_predicate_time` timestamp NULL DEFAULT NULL,
  `inspector_control_last_running_time` timestamp NULL DEFAULT NULL,
  `inspector_control_color` varchar(45) DEFAULT 'UNKNOWN',
  `lacuna_enabled` tinyint(4) DEFAULT 0,
  `lacuna_last_predicate_time` timestamp NULL DEFAULT NULL,
  `lacuna_last_running_time` timestamp NULL DEFAULT NULL,
  `lacuna_color` varchar(45) DEFAULT 'UNKNOWN',
  `authtap_enabled` tinyint(4) DEFAULT 0,
  `authtap_last_predicate_time` timestamp NULL DEFAULT NULL,
  `authtap_last_running_time` timestamp NULL DEFAULT NULL,
  `authtap_color` varchar(45) DEFAULT 'UNKNOWN',
  `mukluk_enabled` tinyint(4) DEFAULT 0,
  `mukluk_last_predicate_time` timestamp NULL DEFAULT NULL,
  `mukluk_last_running_time` timestamp NULL DEFAULT NULL,
  `mukluk_color` varchar(45) DEFAULT 'UNKNOWN',
  `fcm_enabled` tinyint(4) DEFAULT 0,
  `fcm_last_predicate_time` timestamp NULL DEFAULT NULL,
  `fcm_last_running_time` timestamp NULL DEFAULT NULL,
  `fcm_color` varchar(45) DEFAULT 'UNKNOWN',
  `entwine_enabled` tinyint(4) DEFAULT 0,
  `entwine_last_predicate_time` timestamp NULL DEFAULT NULL,
  `entwine_last_running_time` timestamp NULL DEFAULT NULL,
  `entwine_color` varchar(45) DEFAULT 'UNKNOWN',
  `hostel_enabled` tinyint(4) DEFAULT 0,
  `hostel_last_predicate_time` timestamp NULL DEFAULT NULL,
  `hostel_last_running_time` timestamp NULL DEFAULT NULL,
  `hostel_color` varchar(45) DEFAULT 'UNKNOWN',
  `ignition_enabled` tinyint(4) DEFAULT 0,
  `ignition_last_predicate_time` timestamp NULL DEFAULT NULL,
  `ignition_last_running_time` timestamp NULL DEFAULT NULL,
  `ignition_color` varchar(45) DEFAULT 'UNKNOWN',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `asset_investigation` (
  `investigation_id` varchar(45) NOT NULL,
  `asset_id` varchar(45) NOT NULL,
  `tenant_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `asset_tag` (
  `asset_id` varchar(50) DEFAULT NULL,
  `tag` varchar(500) DEFAULT NULL,
  `tenant_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `history` (
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `tenant_id` int(11) DEFAULT NULL,
  `asset_count` int(11) DEFAULT NULL,
  `alert_count` int(11) DEFAULT NULL,
  `investigation_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `investigation` (
  `id` varchar(100) NOT NULL,
  `tenant_id` int(11) DEFAULT NULL,
  `priority` int(11) DEFAULT NULL,
  `status` varchar(45) DEFAULT NULL,
  `latest_activity` varchar(45) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  `description` varchar(500) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `deleted_at` timestamp NULL DEFAULT NULL,
  `notified_at` timestamp NULL DEFAULT NULL,
  `created_by_scwx` varchar(10) DEFAULT NULL,
  `events_count` int(11) DEFAULT NULL,
  `alerts_count` int(11) DEFAULT NULL,
  `assets_count` int(11) DEFAULT NULL,
  `contributors_count` int(11) DEFAULT NULL,
  `genesis_alerts_count` int(11) DEFAULT NULL,
  `genesis_events_count` int(11) DEFAULT NULL,
  `assignee_email` varchar(45) DEFAULT NULL,
  `assignee_roles` varchar(45) DEFAULT NULL,
  `acknowledge_time` timestamp NULL DEFAULT NULL,
  `initial_acknowledge_time` timestamp NULL DEFAULT NULL,
  `acknowledged` varchar(10) DEFAULT NULL,
  `acknowledged_at_least_once` varchar(10) DEFAULT NULL,
  `handed_off` varchar(10) DEFAULT NULL,
  `handed_off_at_least_once` varchar(10) DEFAULT NULL,
  `handoff_time` timestamp NULL DEFAULT NULL,
  `initial_handoff_time` timestamp NULL DEFAULT NULL,
  `resolved` varchar(10) DEFAULT NULL,
  `resolved_at_least_once` varchar(10) DEFAULT NULL,
  `resolution_time` timestamp NULL DEFAULT NULL,
  `initial_resolution_time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `tenant` (
  `id` int(10) unsigned NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `api_client_id` varchar(45) DEFAULT NULL,
  `api_client_secret` varchar(100) DEFAULT NULL,
  `enabled` tinyint(4) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
