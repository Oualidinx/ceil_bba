create table language
(
    id    serial
        primary key,
    label varchar(100)
);

alter table language
    owner to postgres;

