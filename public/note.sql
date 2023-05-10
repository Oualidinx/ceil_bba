create table note
(
    id             serial
        primary key,
    student_id     integer
        references "user",
    fk_level_id    integer
        references level,
    fk_language_id integer
        references language,
    mark           double precision
);

alter table note
    owner to postgres;

