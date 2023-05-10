create table category
(
    id            serial
        primary key,
    label         varchar(100),
    price         double precision,
    price_letters varchar(1500)
);

alter table category
    owner to postgres;

