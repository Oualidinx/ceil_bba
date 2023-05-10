create table session
(
    id          serial
        primary key,
    label       varchar(50),
    start_date  date,
    end_date    date,
    is_active   boolean,
    is_disabled boolean
);

alter table session
    owner to postgres;

