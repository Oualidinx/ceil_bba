create table "user"
(
    id             serial
        primary key,
    first_name     varchar(100),
    last_name      varchar(100),
    birthday       date,
    role           varchar(10),
    fk_category_id integer
        references category,
    is_deleted     smallint,
    email          varchar(100) not null,
    phone_number   varchar(10),
    password_hash  varchar(256) not null,
    birthplace     varchar(100),
    is_verified    boolean,
    birth_city     varchar(100)
);

alter table "user"
    owner to postgres;

