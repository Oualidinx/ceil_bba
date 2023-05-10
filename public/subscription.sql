create table subscription
(
    id                    serial
        primary key,
    fk_student_id         integer
        references "user",
    fk_course_id          integer
        references course,
    is_waiting            boolean,
    is_accepted           integer,
    subscription_date     timestamp,
    charges_paid          boolean,
    fk_payment_receipt_id integer
        references payment_receipt,
    course_day            varchar(15),
    course_periode        varchar(10),
    note                  varchar(1500),
    on_test               boolean
);

alter table subscription
    owner to postgres;

