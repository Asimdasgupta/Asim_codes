CREATE TABLE IF NOT EXISTS medical_profile (
  id TEXT PRIMARY KEY,
  updated_at TEXT NOT NULL,
  json_blob TEXT NOT NULL,
  json_blob_compressed BLOB
);

CREATE TABLE IF NOT EXISTS daily_entry (
  id TEXT PRIMARY KEY,
  entry_date TEXT NOT NULL,
  created_at TEXT NOT NULL,
  json_blob TEXT NOT NULL,
  json_blob_compressed BLOB
);

CREATE INDEX IF NOT EXISTS idx_daily_entry_date ON daily_entry(entry_date);

CREATE TABLE IF NOT EXISTS daily_entry_features (
  entry_id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  features_json TEXT NOT NULL,
  features_json_compressed BLOB
);

CREATE INDEX IF NOT EXISTS idx_daily_entry_features_created_at ON daily_entry_features(created_at);
