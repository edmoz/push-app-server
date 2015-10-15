drop table if exists urls;
create table urls (
  id integer primary key autoincrement,
  url text not null,
  delay int not null,
  repeat int not null
);