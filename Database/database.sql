create table file_name IF NOT EXISTS
(
  key       serial       not null
    constraint file_name_pkey
    primary key,
  file_name varchar(255) not null
);

alter table file_name
  owner to ;

--owner 이름 넣기

create unique index file_name_file_name_uindex
  on file_name (file_name);