alter table if exists crypto.keys
add column if not exists storage_mode text not null default 'customer_managed';

alter table if exists crypto.keys
add column if not exists private_key_exported boolean not null default false;

alter table if exists analytics.api_usage
add column if not exists operation text,
add column if not exists response_time_ms integer,
add column if not exists success boolean,
add column if not exists error_type text;
