create table payment_receipt
(
    id           serial
        primary key,
    payment_date timestamp,
    amount       double precision
);

alter table payment_receipt
    owner to postgres;

