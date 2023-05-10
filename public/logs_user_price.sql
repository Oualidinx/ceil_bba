create table logs_user_price
(
    id                serial
        primary key,
    fk_category_id    integer
        references category,
    previous_value    double precision,
    last_modification timestamp,
    updated_by        integer
        references "user"
);

alter table logs_user_price
    owner to postgres;

