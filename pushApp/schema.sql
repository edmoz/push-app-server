drop table if exists urls;
create table urls (
  id integer primary key autoincrement,
  url text not null,
  delay int DEFAULT 3,
  repeat int DEFAULT 1,
  ttl int DEFAULT 60
);