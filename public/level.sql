create table level
(
    id    serial
        primary key,
    label varchar(100)
);

alter table level
    owner to postgres;

