create table course
(
    id            serial
        primary key,
    label         varchar(100),
    price         double precision,
    is_disabled   boolean,
    fk_session_id integer
        references session,
    description   varchar(2500)
);

alter table course
    owner to postgres;

