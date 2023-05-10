create table course_language
(
    id                     serial
        primary key,
    fk_level_id            integer
        references level,
    limit_number           integer,
    actual_students_number integer,
    fk_language_id         integer
        references language,
    fk_course_id           integer
        references course
);

alter table course_language
    owner to postgres;

