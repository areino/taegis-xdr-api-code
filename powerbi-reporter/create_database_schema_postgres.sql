CREATE TABLE IF NOT EXISTS public.alert (
  id character varying(45) NOT NULL,
  alert_type character varying(100) DEFAULT NULL,
  confidence real DEFAULT NULL,
  severity real DEFAULT NULL,
  creator character varying(45) DEFAULT NULL,
  tenant_id int DEFAULT NULL,
  message character varying(200) DEFAULT NULL,
  insert_timestamp timestamp NULL DEFAULT NULL,
  domain_registration_date timestamp NULL DEFAULT NULL,
  username character varying(200) DEFAULT NULL,
  source_ip character varying(45) DEFAULT NULL,
  destination_ip character varying(45) DEFAULT NULL,
  source_port int DEFAULT NULL,
  destination_port int DEFAULT NULL,
  blacklist_name character varying(45) DEFAULT NULL,
  blacklist_reason character varying(100) DEFAULT NULL,
  domain character varying(45) DEFAULT NULL,
  timestamp timestamp NULL DEFAULT NULL,
  attack_categories character varying(100) DEFAULT NULL,
  CONSTRAINT alert_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.alert_asset (
  alert_id character varying(45) DEFAULT NULL,
  asset_id character varying(50) DEFAULT NULL,
  tenant_id int DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS public.alert_investigation (
  alert_id character varying(45) NOT NULL,
  investigation_id character varying(45) NOT NULL,
  tenant_id int NOT NULL
);

CREATE TABLE IF NOT EXISTS public.asset (
  id character varying(50) NOT NULL,
  tenant_id int DEFAULT NULL,
  architecture character varying(45) DEFAULT NULL,
  created_at timestamp NULL DEFAULT NULL,
  updated_at timestamp NULL DEFAULT NULL,
  deleted_at timestamp NULL DEFAULT NULL,
  endpoint_platform character varying(45) DEFAULT NULL,
  endpoint_type character varying(45) DEFAULT NULL,
  system_type character varying(45) DEFAULT NULL,
  host_id character varying(45) DEFAULT NULL,
  hostnames character varying(100) DEFAULT NULL,
  users character varying(100) DEFAULT NULL,
  ip_addresses character varying(100) DEFAULT NULL,
  ingest_time timestamp NULL DEFAULT NULL,
  kernel_release character varying(45) DEFAULT NULL,
  kernel_version character varying(45) DEFAULT NULL,
  os_codename character varying(45) DEFAULT NULL,
  os_family character varying(45) DEFAULT NULL,
  os_release character varying(45) DEFAULT NULL,
  os_version character varying(45) DEFAULT NULL,
  sensor_id character varying(45) DEFAULT NULL,
  sensor_tenant character varying(45) DEFAULT NULL,
  sensor_version character varying(45) DEFAULT NULL,
  tags character varying(500) DEFAULT NULL,
  CONSTRAINT asset_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.asset_health (
  id character varying(50) NOT NULL,
  color character varying(45) DEFAULT 'UNKNOWN',
  actual_isolation_status smallint DEFAULT 0,
  desired_isolation_status smallint DEFAULT 0,
  first_connect_time timestamp NULL DEFAULT NULL,
  last_connect_address character varying(45) DEFAULT NULL,
  last_connect_server character varying(45) DEFAULT NULL,
  last_connect_time timestamp NULL DEFAULT NULL,
  last_crash_check timestamp NULL DEFAULT NULL,
  last_module_status_time timestamp NULL DEFAULT NULL,
  procwall_enabled smallint DEFAULT NULL,
  procwall_last_predicate_time timestamp NULL DEFAULT NULL,
  procwall_last_running_time timestamp NULL DEFAULT NULL,
  procwall_color character varying(45) DEFAULT 'UNKNOWN',
  cyclorama_enabled smallint DEFAULT 0,
  cyclorama_last_predicate_time timestamp NULL DEFAULT NULL,
  cyclorama_last_running_time timestamp NULL DEFAULT NULL,
  cyclorama_color character varying(45) DEFAULT 'UNKNOWN',
  groundling_enabled smallint DEFAULT 0,
  groundling_last_predicate_time timestamp NULL DEFAULT NULL,
  groundling_last_running_time timestamp NULL DEFAULT NULL,
  groundling_color character varying(45) DEFAULT 'UNKNOWN',
  inspector_result_enabled smallint DEFAULT 0,
  inspector_result_last_predicate_time timestamp NULL DEFAULT NULL,
  inspector_result_last_running_time timestamp NULL DEFAULT NULL,
  inspector_result_color character varying(45) DEFAULT 'UNKNOWN',
  inspector_control_enabled smallint DEFAULT 0,
  inspector_control_last_predicate_time timestamp NULL DEFAULT NULL,
  inspector_control_last_running_time timestamp NULL DEFAULT NULL,
  inspector_control_color character varying(45) DEFAULT 'UNKNOWN',
  lacuna_enabled smallint DEFAULT 0,
  lacuna_last_predicate_time timestamp NULL DEFAULT NULL,
  lacuna_last_running_time timestamp NULL DEFAULT NULL,
  lacuna_color character varying(45) DEFAULT 'UNKNOWN',
  authtap_enabled smallint DEFAULT 0,
  authtap_last_predicate_time timestamp NULL DEFAULT NULL,
  authtap_last_running_time timestamp NULL DEFAULT NULL,
  authtap_color character varying(45) DEFAULT 'UNKNOWN',
  mukluk_enabled smallint DEFAULT 0,
  mukluk_last_predicate_time timestamp NULL DEFAULT NULL,
  mukluk_last_running_time timestamp NULL DEFAULT NULL,
  mukluk_color character varying(45) DEFAULT 'UNKNOWN',
  fcm_enabled smallint DEFAULT 0,
  fcm_last_predicate_time timestamp NULL DEFAULT NULL,
  fcm_last_running_time timestamp NULL DEFAULT NULL,
  fcm_color character varying(45) DEFAULT 'UNKNOWN',
  entwine_enabled smallint DEFAULT 0,
  entwine_last_predicate_time timestamp NULL DEFAULT NULL,
  entwine_last_running_time timestamp NULL DEFAULT NULL,
  entwine_color character varying(45) DEFAULT 'UNKNOWN',
  hostel_enabled smallint DEFAULT 0,
  hostel_last_predicate_time timestamp NULL DEFAULT NULL,
  hostel_last_running_time timestamp NULL DEFAULT NULL,
  hostel_color character varying(45) DEFAULT 'UNKNOWN',
  ignition_enabled smallint DEFAULT 0,
  ignition_last_predicate_time timestamp NULL DEFAULT NULL,
  ignition_last_running_time timestamp NULL DEFAULT NULL,
  ignition_color character varying(45) DEFAULT 'UNKNOWN',
  CONSTRAINT asset_health_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.asset_investigation (
  investigation_id character varying(45) NOT NULL,
  asset_id character varying(45) NOT NULL,
  tenant_id int NOT NULL
);

CREATE TABLE IF NOT EXISTS public.asset_tag (
  asset_id character varying(50) DEFAULT NULL,
  tag character varying(500) DEFAULT NULL,
  tenant_id int DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS public.history (
  timestamp timestamp NOT NULL,
  tenant_id int DEFAULT NULL,
  asset_count int DEFAULT NULL,
  alert_count int DEFAULT NULL,
  investigation_count int DEFAULT NULL,
  CONSTRAINT history_pkey PRIMARY KEY (timestamp)
);
ALTER TABLE public.history ALTER COLUMN timestamp SET DEFAULT now();



CREATE TABLE IF NOT EXISTS public.investigation (
  id character varying(100) NOT NULL,
  tenant_id int DEFAULT NULL,
  priority int DEFAULT NULL,
  status character varying(45) DEFAULT NULL,
  latest_activity character varying(45) DEFAULT NULL,
  type character varying(45) DEFAULT NULL,
  description character varying(500) DEFAULT NULL,
  created_at timestamp NULL DEFAULT NULL,
  updated_at timestamp NULL DEFAULT NULL,
  deleted_at timestamp NULL DEFAULT NULL,
  notified_at timestamp NULL DEFAULT NULL,
  created_by_scwx character varying(10) DEFAULT NULL,
  events_count int DEFAULT NULL,
  alerts_count int DEFAULT NULL,
  assets_count int DEFAULT NULL,
  contributors_count int DEFAULT NULL,
  genesis_alerts_count int DEFAULT NULL,
  genesis_events_count int DEFAULT NULL,
  assignee_email character varying(45) DEFAULT NULL,
  assignee_roles character varying(45) DEFAULT NULL,
  acknowledge_time timestamp NULL DEFAULT NULL,
  initial_acknowledge_time timestamp NULL DEFAULT NULL,
  acknowledged character varying(10) DEFAULT NULL,
  acknowledged_at_least_once character varying(10) DEFAULT NULL,
  handed_off character varying(10) DEFAULT NULL,
  handed_off_at_least_once character varying(10) DEFAULT NULL,
  handoff_time timestamp NULL DEFAULT NULL,
  initial_handoff_time timestamp NULL DEFAULT NULL,
  resolved character varying(10) DEFAULT NULL,
  resolved_at_least_once character varying(10) DEFAULT NULL,
  resolution_time timestamp NULL DEFAULT NULL,
  initial_resolution_time timestamp NULL DEFAULT NULL,
  CONSTRAINT investigation_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.tenant (
  id int NOT NULL,
  name character varying(100) DEFAULT NULL,
  api_client_id character varying(45) DEFAULT NULL,
  api_client_secret character varying(100) DEFAULT NULL,
  enabled smallint DEFAULT 0,
  CONSTRAINT tenant_pkey PRIMARY KEY (id)
);
